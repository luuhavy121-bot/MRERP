from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from people_domain.access import get_actor_employee
from people_domain.models import Employee
from people_domain.services import audit
from .access import can_manage, eligible_employees, REOPEN, OWN
from .models import PerformanceReview, PerformanceKPI, PerformanceReviewRevision

class Conflict(APIException):
    status_code = 409
    default_detail = "Phiếu đã thay đổi. Hãy tải lại trước khi lưu."
    default_code = "conflict"


def create_review(user, employee_uuid, month):
    actor = get_actor_employee(user)
    try:
        with transaction.atomic():
            employee = Employee.objects.select_for_update().get(pk=employee_uuid)
            if not eligible_employees(user).filter(pk=employee.pk).exists():
                raise PermissionDenied("Chỉ đánh giá nhân sự đang làm việc trong Team mình lãnh đạo.")
            review = PerformanceReview.objects.create(employee=employee, team=employee.team, leader=actor, month=month)
            audit(actor=user, action="performance.review.created", target=review, changes={"month": str(month)})
            return review
    except Employee.DoesNotExist:
        raise PermissionDenied("Nhân sự không nằm trong phạm vi đánh giá.")
    except IntegrityError:
        raise Conflict("Nhân sự đã có phiếu đánh giá trong tháng này.")


def snapshot(review):
    return {"version": review.version, "month": str(review.month), "total_score": str(review.total_score) if review.total_score is not None else None,
        "leader_comment": review.leader_comment, "employee_feedback": review.employee_feedback,
        "leader_uuid": str(review.leader_id), "team_uuid": str(review.team_id),
        "kpis": [{"title": k.title, "description": k.description, "weight": str(k.weight), "completion": str(k.completion) if k.completion is not None else None, "comment": k.comment} for k in review.kpis.all()]}


@transaction.atomic
def change_review(user, review, data, command="update"):
    actor = get_actor_employee(user)
    locked = PerformanceReview.objects.select_for_update().select_related("employee").get(pk=review.pk)
    if command in {"update", "finalize"} and not can_manage(user, locked):
        raise PermissionDenied("Bạn không có quyền chấm phiếu này.")
    if command == "reopen" and not user.has_perm(REOPEN):
        raise PermissionDenied("Chỉ HR/CEO được mở lại phiếu.")
    if command == "acknowledge" and (not user.has_perm(OWN) or locked.employee_id != actor.pk):
        raise PermissionDenied("Chỉ được xác nhận phiếu của mình.")
    if data["version"] != locked.version:
        raise Conflict()
    if command in {"update", "finalize"}:
        if locked.status != "draft":
            raise ValidationError("Phiếu đã chốt, cần HR/CEO mở lại.")
        if command == "update":
            if "leader_comment" in data:
                locked.leader_comment = data["leader_comment"]
            if "kpis" in data:
                locked.kpis.all().delete()
                PerformanceKPI.objects.bulk_create([PerformanceKPI(review=locked, position=i, **item) for i, item in enumerate(data["kpis"])])
        else:
            kpis = list(locked.kpis.all())
            if not kpis or sum(k.weight for k in kpis) != Decimal(100) or any(k.completion is None for k in kpis) or not locked.leader_comment.strip():
                raise ValidationError("Cần KPI có tổng trọng số 100, đầy đủ mức hoàn thành và nhận xét tổng kết.")
            locked.total_score = (sum(k.weight * k.completion for k in kpis) / Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            locked.status = "finalized"
            locked.finalized_at = timezone.now()
        locked.leader = actor
    elif command == "reopen":
        if locked.status == "draft" or not data.get("reason", "").strip():
            raise ValidationError("Chỉ mở lại phiếu đã chốt và phải nhập lý do.")
        PerformanceReviewRevision.objects.create(review=locked, actor=user, event="reopened", reason=data["reason"], snapshot=snapshot(locked))
        locked.status = "draft"
        locked.total_score = None
        locked.employee_feedback = ""
        locked.finalized_at = None
        locked.acknowledged_at = None
    elif command == "acknowledge":
        if locked.status != "finalized":
            raise ValidationError("Chỉ xác nhận phiếu đã chốt, chưa xác nhận.")
        locked.employee_feedback = data.get("employee_feedback", "")
        locked.status = "acknowledged"
        locked.acknowledged_at = timezone.now()
    locked.version += 1
    locked.save()
    if command == "finalize":
        PerformanceReviewRevision.objects.create(review=locked, actor=user, event="finalized", snapshot=snapshot(locked))
    if command in {"finalize", "reopen", "acknowledge"}:
        from dashboard_domain.services import notify
        recipient = locked.leader if command == "acknowledge" else locked.employee
        notify(recipient=recipient, kind="performance", title={"finalize": "Đánh giá tháng đã chốt", "reopen": "Đánh giá được mở lại", "acknowledge": "Nhân sự đã xác nhận đánh giá"}[command], body=str(locked.month), target_type="performance", target_uuid=locked.pk, deduplication_key=f"performance:{locked.pk}:{command}:{locked.version}")
    audit(actor=user, action=f"performance.review.{command}", target=locked, changes={"version": locked.version})
    return locked
