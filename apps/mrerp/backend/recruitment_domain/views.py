from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.file_storage import protected_file_response
from people_domain.access import get_actor_employee
from people_domain.models import Team
from people_domain.serializers import ApiErrorSerializer, EmployeeHRSerializer
from people_domain.views import require_capability

from .access import can_view_candidate_files, visible_applications, visible_hiring_requests
from .capabilities import CREATE_REQUEST, MANAGE_CANDIDATES, VIEW_SCOPED_RECRUITMENT
from .models import Application, CandidateAttachment, HiringRequest, JobOpening
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationSerializer,
    ApplicationTransitionSerializer,
    CandidateAttachmentSerializer,
    CandidateAttachmentUploadSerializer,
    CandidateConvertResponseSerializer,
    CandidateConvertSerializer,
    HiringRequestCreateSerializer,
    HiringRequestReviewSerializer,
    HiringRequestSerializer,
    OpeningSerializer,
    RecruitmentOptionsSerializer,
)
from .services import (
    add_application_attachments,
    convert_application,
    create_application,
    create_hiring_request,
    review_hiring_request,
    transition_application,
)


class RecruitmentOptionsView(APIView):
    """Return only teams the current actor may use in a hiring request."""

    @extend_schema(responses={200: RecruitmentOptionsSerializer, 403: ApiErrorSerializer})
    def get(self, request):
        actor = get_actor_employee(request.user)
        require_capability(request.user, CREATE_REQUEST)
        if request.user.has_perm("recruitment_domain.view_company_recruitment"):
            teams = Team.objects.filter(is_active=True)
        else:
            teams = Team.objects.filter(is_active=True, leaderships__leader=actor)
        return Response({
            "teams": [
                {"uuid": str(team.pk), "code": team.code, "name": team.name}
                for team in teams.distinct().order_by("name")
            ]
        })


class HiringRequestViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = HiringRequestSerializer
    queryset = HiringRequest.objects.none()

    def get_queryset(self):
        require_capability(self.request.user, VIEW_SCOPED_RECRUITMENT)
        return visible_hiring_requests(self.request.user)

    @extend_schema(request=HiringRequestCreateSerializer, responses={201: HiringRequestSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def create(self, request):
        get_actor_employee(request.user)
        require_capability(request.user, CREATE_REQUEST)
        serializer = HiringRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = get_object_or_404(Team.objects.filter(is_active=True), pk=serializer.validated_data.pop("team_uuid"))
        hiring_request = create_hiring_request(actor_user=request.user, team=team, **serializer.validated_data)
        return Response(HiringRequestSerializer(hiring_request).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=HiringRequestReviewSerializer, responses={200: HiringRequestSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        hiring_request = self.get_object()
        serializer = HiringRequestReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = review_hiring_request(
            actor_user=request.user,
            hiring_request=hiring_request,
            decision=serializer.validated_data["decision"],
            note=serializer.validated_data.get("note", ""),
        )
        return Response(HiringRequestSerializer(updated).data)


class OpeningViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = OpeningSerializer
    queryset = JobOpening.objects.none()

    def get_queryset(self):
        get_actor_employee(self.request.user)
        request_ids = visible_hiring_requests(self.request.user).values_list("pk", flat=True)
        return JobOpening.objects.filter(hiring_request_id__in=request_ids).select_related("team", "hiring_request")


class ApplicationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ApplicationSerializer
    queryset = Application.objects.none()

    def get_queryset(self):
        require_capability(self.request.user, VIEW_SCOPED_RECRUITMENT)
        return visible_applications(self.request.user)

    @extend_schema(request=ApplicationCreateSerializer, responses={201: ApplicationSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def create(self, request):
        get_actor_employee(request.user)
        require_capability(request.user, MANAGE_CANDIDATES)
        serializer = ApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        opening = get_object_or_404(JobOpening, pk=serializer.validated_data.pop("opening_uuid"))
        application = create_application(actor_user=request.user, opening=opening, **serializer.validated_data)
        return Response(ApplicationSerializer(application, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=ApplicationTransitionSerializer, responses={200: ApplicationSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        application = self.get_object()
        serializer = ApplicationTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = transition_application(
            actor_user=request.user,
            application=application,
            to_stage=serializer.validated_data["stage"],
            note=serializer.validated_data.get("note", ""),
        )
        return Response(ApplicationSerializer(updated, context={"request": request}).data)

    @extend_schema(request=CandidateConvertSerializer, responses={201: CandidateConvertResponseSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"], url_path="convert-to-employee")
    def convert_to_employee(self, request, pk=None):
        application = self.get_object()
        serializer = CandidateConvertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee, temporary_password = convert_application(actor_user=request.user, application=application, **serializer.validated_data)
        return Response(
            {"employee": EmployeeHRSerializer(employee, context={"request": request}).data, "temporary_password": temporary_password},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=CandidateAttachmentUploadSerializer, responses={201: CandidateAttachmentSerializer(many=True), 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"])
    def attachments(self, request, pk=None):
        application = self.get_object()
        files = request.FILES.getlist("attachments")
        if not files:
            raise ValidationError({"attachments": "Chọn ít nhất một file."})
        attachments = add_application_attachments(actor_user=request.user, application=application, uploaded_files=files)
        return Response(CandidateAttachmentSerializer(attachments, many=True).data, status=status.HTTP_201_CREATED)


class CandidateAttachmentDownloadView(APIView):
    @extend_schema(responses={(200, "application/octet-stream"): bytes, 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    def get(self, request, attachment_uuid):
        get_actor_employee(request.user)
        attachment = get_object_or_404(CandidateAttachment.objects.select_related("application"), pk=attachment_uuid)
        if not can_view_candidate_files(request.user, attachment.application):
            raise PermissionDenied("Bạn không có quyền tải file ứng viên.")
        return protected_file_response(attachment.storage_key, attachment.original_name, attachment.content_type)
