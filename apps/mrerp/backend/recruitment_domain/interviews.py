from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from dashboard_domain.services import notify_many
from people_domain.models import Employee, TeamLeadership
from people_domain.services import audit
from .access import require_team_access
from .capabilities import MANAGE_CANDIDATES, APPROVE_REQUEST
from .models import Application


class InterviewSerializer(serializers.Serializer):
    version = serializers.IntegerField(min_value=1)
    interview_at = serializers.DateTimeField(required=True, allow_null=True)
    interviewer_name = serializers.CharField(max_length=160, allow_blank=True)
    recruiter_note = serializers.CharField(max_length=2000, allow_blank=True)

    def validate(self, data):
        if data["interview_at"] and not data["interviewer_name"].strip():
            raise serializers.ValidationError({"interviewer_name": "Nhập tên người phụ trách phỏng vấn."})
        return data


class InterviewConflict(APIException):
    status_code = 409
    default_detail = "Hồ sơ đã thay đổi. Tải lại trước khi lưu."


@transaction.atomic
def update_interview(user, application, data):
    require_team_access(user, application.opening.team_id)
    if not user.has_perm(MANAGE_CANDIDATES):
        raise PermissionDenied("Bạn không có quyền quản lý ứng viên.")
    locked = Application.objects.select_for_update().get(pk=application.pk)
    if locked.version != data["version"]:
        raise InterviewConflict()
    if locked.candidate.anonymized_at or locked.stage in {"hired", "rejected"}:
        raise ValidationError("Hồ sơ đã kết thúc; không sửa lịch phỏng vấn/ghi chú.")
    for field in ("interview_at", "interviewer_name", "recruiter_note"):
        setattr(locked, field, data[field])
    locked.version += 1
    locked.save(update_fields=["interview_at", "interviewer_name", "recruiter_note", "version", "updated_at"])
    audit(actor=user, action="recruitment.application.interview_updated", target=locked, changes={"version": locked.version, "scheduled": bool(locked.interview_at), "note": "provided" if locked.recruiter_note else "empty"})
    return locked


def notify_recruitment_owners(team_id, title, target, approval=False):
    capability = APPROVE_REQUEST if approval else MANAGE_CANDIDATES
    employees = Employee.objects.select_related("identity_user").filter(
        employment_status__in=["probation", "official"], identity_user__is_active=True,
    )
    leaders = set(TeamLeadership.objects.filter(team_id=team_id).values_list("leader_id", flat=True))
    recipients = [e for e in employees if e.identity_user.has_perm(capability) and (
        e.pk in leaders or e.identity_user.has_perm("recruitment_domain.view_company_recruitment")
    )]
    notify_many(recipients=recipients, kind="recruitment", title=title, body="Mở Tuyển dụng để xử lý trong phạm vi được cấp quyền.", target_type="recruitment", target_uuid=target, key_prefix=f"recruitment:{title}:{target}")
