from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from config.file_storage import delete_stored_file
from people_domain.services import audit
from .models import JobOpening, Candidate, Application, CandidateAttachment
from .uploads import save_cv


class PublicOpeningSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name")
    location = serializers.CharField(source="hiring_request.location")
    employment_type = serializers.CharField(source="hiring_request.employment_type")
    description = serializers.CharField(source="hiring_request.description")
    requirements = serializers.CharField(source="hiring_request.requirements")
    benefits = serializers.CharField(source="hiring_request.benefits")
    headcount = serializers.IntegerField(source="hiring_request.headcount")
    deadline = serializers.DateField(source="hiring_request.deadline")
    class Meta:
        model = JobOpening
        fields = ["slug", "title", "team_name", "location", "employment_type", "description", "requirements", "benefits", "headcount", "deadline", "published_at"]


class PublicApplicationSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=160)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")
    introduction = serializers.CharField(max_length=3000, required=False, allow_blank=True, default="")
    consent = serializers.BooleanField()
    cv = serializers.FileField()

    def validate(self, data):
        if not data["email"] and not data["phone"]:
            raise serializers.ValidationError("Cần ít nhất email hoặc số điện thoại.")
        if not data["consent"]:
            raise serializers.ValidationError({"consent": "Cần đồng ý lưu thông tin ứng tuyển."})
        return data


class ApplicationReceiptSerializer(serializers.Serializer):
    detail = serializers.CharField()


class ApplicationThrottle(SimpleRateThrottle):
    scope = "public_applications"
    rate = "5/hour"
    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class PublicOpeningViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = PublicOpeningSerializer
    lookup_field = "slug"
    queryset = JobOpening.objects.none()

    def get_queryset(self):
        return JobOpening.objects.filter(status="open", published_at__isnull=False, hiring_request__deadline__gte=timezone.localdate(), team__is_active=True).select_related("team", "hiring_request")

    @extend_schema(request=PublicApplicationSerializer, responses={201: ApplicationReceiptSerializer})
    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser], throttle_classes=[ApplicationThrottle])
    def applications(self, request, slug=None):
        if len(request.FILES.getlist("cv")) != 1:
            raise serializers.ValidationError({"cv": "Chỉ gửi đúng một CV."})
        serializer = PublicApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        metadata = None
        try:
            with transaction.atomic():
                opening = get_object_or_404(self.get_queryset().select_for_update(), slug=slug)
                metadata = save_cv(data.pop("cv"))
                data.pop("consent")
                introduction = data.pop("introduction")
                candidate = Candidate.objects.create(**data, source="Trang tuyển dụng")
                application = Application.objects.create(candidate=candidate, opening=opening, introduction=introduction, consent_at=timezone.now())
                CandidateAttachment.objects.create(application=application, **metadata)
                from .services import notify_recruitment_owners
                notify_recruitment_owners(opening.team_id, "Hồ sơ ứng tuyển mới", application.pk)
                audit(actor=None, action="recruitment.application.public_submitted", target=application, changes={"opening_uuid": str(opening.pk), "consent": True})
        except Exception:
            if metadata:
                delete_stored_file(metadata["storage_key"])
            raise
        return Response({"detail": "Đã nhận hồ sơ ứng tuyển. Công ty sẽ liên hệ qua thông tin bạn cung cấp."}, status=201)
