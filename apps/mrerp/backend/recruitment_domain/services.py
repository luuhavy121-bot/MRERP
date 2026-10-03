from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from config.file_storage import delete_stored_file, save_upload
from dashboard_domain.models import Notification
from dashboard_domain.services import notify
from people_domain.models import Employee, Team, TeamLeadership
from people_domain.services import audit, create_probation_employee

from .capabilities import APPROVE_REQUEST, CONVERT_CANDIDATE, MANAGE_CANDIDATES, VIEW_COMPANY_RECRUITMENT
from .access import require_team_access
from .interviews import notify_recruitment_owners
from .models import (
    Application,
    ApplicationTransition,
    Candidate,
    CandidateAttachment,
    HiringRequest,
    JobOpening,
)


ALLOWED_TRANSITIONS = {
    Application.Stage.NEW: {Application.Stage.SCREENING, Application.Stage.REJECTED},
    Application.Stage.SCREENING: {Application.Stage.INTERVIEW, Application.Stage.REJECTED},
    Application.Stage.INTERVIEW: {Application.Stage.HIRED, Application.Stage.REJECTED},
    Application.Stage.HIRED: set(),
    Application.Stage.REJECTED: set(),
}


def _create_opening(hiring_request):
    opening, _ = JobOpening.objects.get_or_create(
        hiring_request=hiring_request,
        defaults={"team": hiring_request.team, "title": hiring_request.title},
    )
    return opening


def create_hiring_request(*, actor_user, team: Team, title: str, headcount: int, justification: str, utilization_plan: str = ""):
    actor = actor_user.employee_profile
    require_team_access(actor_user, team.pk)
    company_scope = actor_user.has_perm(VIEW_COMPANY_RECRUITMENT)
    if not company_scope and not TeamLeadership.objects.filter(team=team, leader=actor).exists():
        raise PermissionDenied("Leader chỉ được tạo yêu cầu tuyển cho Team mình lãnh đạo.")
    with transaction.atomic():
        auto_approved = False
        hiring_request = HiringRequest.objects.create(
            team=team, title=title, headcount=headcount, justification=justification, utilization_plan=utilization_plan,
            requester=actor, status=HiringRequest.Status.DRAFT,
        )
        audit(
            actor=actor_user,
            action="recruitment.request.created",
            target=hiring_request,
            changes={"team_uuid": str(team.pk), "headcount": headcount, "auto_approved": auto_approved},
        )
        return hiring_request


def review_hiring_request(*, actor_user, hiring_request, decision: str, note: str):
    require_team_access(actor_user, hiring_request.team_id)
    if not actor_user.has_perm(APPROVE_REQUEST):
        raise PermissionDenied("Bạn không có quyền duyệt yêu cầu tuyển dụng.")
    if hiring_request.status != HiringRequest.Status.PENDING:
        raise ValidationError({"status": "Chỉ yêu cầu đang chờ mới được duyệt."})
    if decision not in {HiringRequest.Status.APPROVED, HiringRequest.Status.REJECTED}:
        raise ValidationError({"decision": "Quyết định không hợp lệ."})
    with transaction.atomic():
        locked = HiringRequest.objects.select_for_update().get(pk=hiring_request.pk)
        if locked.status != HiringRequest.Status.PENDING:
            raise ValidationError({"status": "Yêu cầu đã được xử lý."})
        locked.status = decision
        locked.reviewer = actor_user
        locked.review_note = note.strip()
        locked.reviewed_at = timezone.now()
        locked.save(update_fields=["status", "reviewer", "review_note", "reviewed_at", "updated_at"])
        if decision == HiringRequest.Status.APPROVED:
            validate_publishable(locked)
            opening = _create_opening(locked)
            from django.utils.text import slugify
            opening.slug = f"{slugify(locked.title) or 'job'}-{opening.pk.hex[:12]}"
            opening.published_at = timezone.now()
            opening.save(update_fields=["slug", "published_at", "updated_at"])
        notify(
            recipient=locked.requester,
            kind=Notification.Kind.RECRUITMENT,
            title="Yêu cầu tuyển dụng đã được xử lý",
            body=f"{locked.title}: {locked.get_status_display()}",
            target_type="recruitment",
            target_uuid=locked.pk,
        )
        audit(
            actor=actor_user,
            action="recruitment.request.reviewed",
            target=locked,
            changes={"decision": decision, "note": "provided" if note.strip() else "empty"},
        )
        return locked


def create_application(*, actor_user, opening, full_name: str, email: str = "", phone: str = "", source: str = ""):
    require_team_access(actor_user, opening.team_id)
    if not actor_user.has_perm(MANAGE_CANDIDATES):
        raise PermissionDenied("Bạn không có quyền quản lý ứng viên.")
    if opening.status != JobOpening.Status.OPEN:
        raise ValidationError({"opening_uuid": "Vị trí tuyển dụng đã đóng."})
    with transaction.atomic():
        candidate = Candidate.objects.create(full_name=full_name, email=email, phone=phone, source=source)
        application = Application.objects.create(candidate=candidate, opening=opening, created_by=actor_user)
        audit(
            actor=actor_user,
            action="recruitment.application.created",
            target=application,
            changes={"opening_uuid": str(opening.pk), "candidate_pii": "stored_not_logged"},
        )
        notify_recruitment_owners(opening.team_id, "Hồ sơ ứng tuyển mới", application.pk)
        return application


def transition_application(*, actor_user, application, to_stage: str, note: str):
    require_team_access(actor_user, application.opening.team_id)
    if not actor_user.has_perm(MANAGE_CANDIDATES):
        raise PermissionDenied("Bạn không có quyền thay đổi pipeline.")
    if to_stage not in ALLOWED_TRANSITIONS.get(application.stage, set()):
        raise ValidationError({"stage": "Chuyển trạng thái pipeline không hợp lệ."})
    with transaction.atomic():
        locked = Application.objects.select_for_update().get(pk=application.pk)
        if to_stage not in ALLOWED_TRANSITIONS.get(locked.stage, set()):
            raise ValidationError({"stage": "Pipeline đã thay đổi. Hãy tải lại."})
        previous = locked.stage
        locked.stage = to_stage
        locked.version += 1
        locked.retention_until = timezone.now() + timedelta(days=183) if to_stage == Application.Stage.REJECTED else None
        locked.save(update_fields=["stage", "version", "retention_until", "updated_at"])
        ApplicationTransition.objects.create(
            application=locked,
            from_stage=previous,
            to_stage=to_stage,
            note=note.strip(),
            actor=actor_user,
        )
        audit(
            actor=actor_user,
            action="recruitment.application.transitioned",
            target=locked,
            changes={"from": previous, "to": to_stage, "note": "provided" if note.strip() else "empty"},
        )
        return locked


def convert_application(*, actor_user, application, employee_code: str, create_account: bool, username: str = ""):
    require_team_access(actor_user, application.opening.team_id)
    if not actor_user.has_perm(CONVERT_CANDIDATE):
        raise PermissionDenied("Bạn không có quyền chuyển ứng viên thành nhân sự.")
    if application.stage != Application.Stage.HIRED:
        raise ValidationError({"stage": "Chỉ ứng viên ở trạng thái Đã tuyển mới được chuyển."})
    if application.converted_employee_id:
        raise ValidationError({"application": "Ứng viên đã được chuyển thành nhân sự."})
    with transaction.atomic():
        locked = Application.objects.select_for_update().select_related("candidate", "opening__team").get(pk=application.pk)
        if locked.converted_employee_id or locked.stage != Application.Stage.HIRED:
            raise ValidationError({"application": "Application không còn hợp lệ để chuyển."})
        employee, temporary_password = create_probation_employee(
            actor=actor_user,
            employee_code=employee_code,
            create_account=create_account,
            username=username,
        )
        employee.display_name = locked.candidate.full_name
        employee.job_title = locked.opening.title
        employee.team = locked.opening.team
        employee.save(update_fields=["display_name", "job_title", "team", "updated_at"])
        locked.converted_employee = employee
        locked.version += 1
        locked.save(update_fields=["converted_employee", "version", "updated_at"])
        audit(
            actor=actor_user,
            action="recruitment.application.converted",
            target=locked,
            changes={"employee_uuid": str(employee.pk), "account_created": create_account},
        )
        return employee, temporary_password


def add_application_attachments(*, actor_user, application, uploaded_files):
    require_team_access(actor_user, application.opening.team_id)
    if not actor_user.has_perm(MANAGE_CANDIDATES):
        raise PermissionDenied("Bạn không có quyền tải CV.")
    if application.attachments.count() + len(uploaded_files) > 5:
        raise ValidationError({"attachments": "Mỗi hồ sơ ứng viên có tối đa 5 file."})
    created = []
    stored_keys = []
    try:
        with transaction.atomic():
            for uploaded_file in uploaded_files:
                from .uploads import save_cv
                metadata = save_cv(uploaded_file)
                stored_keys.append(metadata["storage_key"])
                created.append(CandidateAttachment.objects.create(
                    application=application,
                    uploaded_by=actor_user,
                    **metadata,
                ))
            audit(
                actor=actor_user,
                action="recruitment.attachments.added",
                target=application,
                changes={"count": len(created)},
            )
    except Exception:
        for storage_key in stored_keys:
            delete_stored_file(storage_key)
        raise
    return created


def anonymize_expired_candidates():
    applications = Application.objects.select_related("candidate").filter(
        stage=Application.Stage.REJECTED,
        retention_until__lte=timezone.now(),
        candidate__anonymized_at__isnull=True,
    )
    count = 0
    for application in applications:
        with transaction.atomic():
            candidate = Candidate.objects.select_for_update().get(pk=application.candidate_id)
            if candidate.anonymized_at:
                continue
            for attachment in application.attachments.all():
                delete_stored_file(attachment.storage_key)
            application.attachments.all().delete()
            candidate.full_name = "Ứng viên đã ẩn danh"
            candidate.email = ""
            candidate.phone = ""
            candidate.anonymized_at = timezone.now()
            application.introduction = ""
            application.interview_at = None
            application.interviewer_name = ""
            application.recruiter_note = ""
            application.save(update_fields=["introduction", "interview_at", "interviewer_name", "recruiter_note"])
            application.transitions.update(note="")
            candidate.save(update_fields=["full_name", "email", "phone", "anonymized_at", "updated_at"])
            count += 1
    return count


def validate_publishable(item):
    required = ["title", "location", "employment_type", "description", "requirements", "benefits", "deadline"]
    missing = {field: "Bắt buộc trước khi gửi duyệt." for field in required if not getattr(item, field)}
    if item.deadline and item.deadline < timezone.localdate():
        missing["deadline"] = "Hạn nhận hồ sơ phải từ hôm nay trở đi."
    if missing:
        raise ValidationError(missing)


@transaction.atomic
def edit_request(user, item, data=None, submit=False):
    from .capabilities import CREATE_REQUEST
    require_team_access(user, item.team_id)
    if not user.has_perm(CREATE_REQUEST):
        raise PermissionDenied("Bạn không có quyền tạo yêu cầu tuyển.")
    locked = HiringRequest.objects.select_for_update().get(pk=item.pk)
    if locked.status != HiringRequest.Status.DRAFT:
        raise ValidationError({"status": "Chỉ bản nháp được sửa hoặc gửi duyệt."})
    for key, value in (data or {}).items():
        setattr(locked, key, value)
    if submit:
        validate_publishable(locked)
        locked.status = HiringRequest.Status.PENDING
    locked.save()
    if submit:
        notify_recruitment_owners(locked.team_id, "Yêu cầu tuyển cần duyệt", locked.pk, approval=True)
    audit(actor=user, action="recruitment.request.submitted" if submit else "recruitment.request.updated", target=locked, changes={"fields": list(data or {})})
    return locked


@transaction.atomic
def close_opening(user, item):
    require_team_access(user, item.team_id)
    if not user.has_perm(MANAGE_CANDIDATES):
        raise PermissionDenied("Bạn không có quyền đóng tin.")
    locked = JobOpening.objects.select_for_update().get(pk=item.pk)
    locked.status = JobOpening.Status.CLOSED
    locked.closed_at = timezone.now()
    locked.save(update_fields=["status", "closed_at", "updated_at"])
    audit(actor=user, action="recruitment.opening.closed", target=locked, changes={})
    return locked
