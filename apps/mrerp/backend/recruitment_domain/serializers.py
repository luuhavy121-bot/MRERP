from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from people_domain.serializers import EmployeeHRSerializer

from .capabilities import MANAGE_CANDIDATES
from .models import Application, CandidateAttachment, HiringRequest, JobOpening


class HiringRequestSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    requester_name = serializers.CharField(source="requester.display_name", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    opening_uuid = serializers.UUIDField(source="opening.uuid", read_only=True, allow_null=True)

    class Meta:
        model = HiringRequest
        fields = [
            "uuid", "team", "team_name", "title", "headcount", "justification",
            "requester_name", "status", "status_label", "review_note", "reviewed_at",
            "opening_uuid", "created_at", "updated_at",
        ]
        read_only_fields = fields


class HiringRequestCreateSerializer(serializers.Serializer):
    team_uuid = serializers.UUIDField()
    title = serializers.CharField(min_length=1, max_length=160, trim_whitespace=True)
    headcount = serializers.IntegerField(min_value=1, max_value=100)
    justification = serializers.CharField(min_length=1, max_length=3000, trim_whitespace=True)


class HiringRequestReviewSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=[HiringRequest.Status.APPROVED, HiringRequest.Status.REJECTED])
    note = serializers.CharField(required=False, allow_blank=True, max_length=500, trim_whitespace=True)


class OpeningSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = JobOpening
        fields = ["uuid", "hiring_request", "team", "team_name", "title", "status", "status_label", "created_at"]
        read_only_fields = fields


class CandidateAttachmentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_download_url(self, attachment):
        return f"/api/v1/recruitment/attachments/{attachment.pk}/download/"

    class Meta:
        model = CandidateAttachment
        fields = ["uuid", "original_name", "content_type", "size", "download_url", "created_at"]
        read_only_fields = fields


class CandidateAttachmentUploadSerializer(serializers.Serializer):
    attachments = serializers.ListField(child=serializers.FileField(), min_length=1, max_length=5)


class ApplicationTransitionProjectionSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    from_stage = serializers.CharField()
    to_stage = serializers.CharField()
    to_label = serializers.CharField()
    note = serializers.CharField()
    created_at = serializers.DateTimeField()


class ApplicationSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source="candidate.full_name", read_only=True)
    candidate_email = serializers.CharField(source="candidate.email", read_only=True)
    candidate_phone = serializers.CharField(source="candidate.phone", read_only=True)
    candidate_source = serializers.CharField(source="candidate.source", read_only=True)
    opening_title = serializers.CharField(source="opening.title", read_only=True)
    team_uuid = serializers.UUIDField(source="opening.team.uuid", read_only=True)
    team_name = serializers.CharField(source="opening.team.name", read_only=True)
    stage_label = serializers.CharField(source="get_stage_display", read_only=True)
    converted_employee_uuid = serializers.UUIDField(source="converted_employee.uuid", read_only=True, allow_null=True)
    attachments = CandidateAttachmentSerializer(many=True, read_only=True)
    transitions = serializers.SerializerMethodField()
    can_manage = serializers.SerializerMethodField()
    can_convert = serializers.SerializerMethodField()

    def _full_projection(self):
        request = self.context.get("request")
        return bool(request and request.user.has_perm(MANAGE_CANDIDATES))

    @extend_schema_field(ApplicationTransitionProjectionSerializer(many=True))
    def get_transitions(self, application):
        return [
            {
                "uuid": str(item.pk),
                "from_stage": item.from_stage,
                "to_stage": item.to_stage,
                "to_label": item.get_to_stage_display(),
                "note": item.note,
                "created_at": item.created_at,
            }
            for item in application.transitions.all()
        ]

    @extend_schema_field(serializers.BooleanField())
    def get_can_manage(self, _application):
        return self._full_projection()

    @extend_schema_field(serializers.BooleanField())
    def get_can_convert(self, application):
        request = self.context.get("request")
        return bool(
            request
            and request.user.has_perm("recruitment_domain.convert_candidate")
            and application.stage == Application.Stage.HIRED
            and not application.converted_employee_id
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self._full_projection():
            for field in ("candidate_email", "candidate_phone", "attachments"):
                data.pop(field, None)
        return data

    class Meta:
        model = Application
        fields = [
            "uuid", "candidate_name", "candidate_email", "candidate_phone", "candidate_source",
            "opening", "opening_title", "team_uuid", "team_name", "stage", "stage_label",
            "converted_employee_uuid", "version", "attachments", "transitions", "can_manage",
            "can_convert", "created_at", "updated_at",
        ]
        read_only_fields = fields


class ApplicationCreateSerializer(serializers.Serializer):
    opening_uuid = serializers.UUIDField()
    full_name = serializers.CharField(min_length=1, max_length=160, trim_whitespace=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32, trim_whitespace=True)
    source = serializers.CharField(required=False, allow_blank=True, max_length=120, trim_whitespace=True)


class ApplicationTransitionSerializer(serializers.Serializer):
    stage = serializers.ChoiceField(choices=Application.Stage.choices)
    note = serializers.CharField(required=False, allow_blank=True, max_length=500, trim_whitespace=True)


class CandidateConvertSerializer(serializers.Serializer):
    employee_code = serializers.CharField(min_length=1, max_length=64, trim_whitespace=True)
    create_account = serializers.BooleanField(default=False)
    username = serializers.CharField(required=False, allow_blank=True, max_length=150, trim_whitespace=True)

    def validate(self, attrs):
        if attrs.get("create_account") and not attrs.get("username"):
            raise serializers.ValidationError({"username": "Tài khoản là bắt buộc khi chọn tạo account."})
        return attrs


class CandidateConvertResponseSerializer(serializers.Serializer):
    employee = EmployeeHRSerializer()
    temporary_password = serializers.CharField(required=False, allow_null=True)


class RecruitmentOptionTeamSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()


class RecruitmentOptionsSerializer(serializers.Serializer):
    teams = RecruitmentOptionTeamSerializer(many=True)
