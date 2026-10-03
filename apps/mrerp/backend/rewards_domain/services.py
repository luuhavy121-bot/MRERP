from datetime import datetime

from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from dashboard_domain.models import Notification
from dashboard_domain.services import notify_many
from people_domain.models import Employee
from people_domain.services import audit

from .access import can_grant_stars, can_recognize
from .models import Recognition, StarLedgerEntry, TeamStarAllowance
from .capabilities import GRANT_STARS_COMPANY, GRANT_STARS_SCOPED


def create_recognition(*, actor_user, recipients, category: str, message: str):
    actor = actor_user.employee_profile
    if not recipients:
        raise ValidationError({"recipient_uuids": "Chọn ít nhất một người nhận."})
    if any(target.employment_status not in ["probation", "official"] or not can_recognize(actor_user, target) for target in recipients):
        raise PermissionDenied("Bạn chỉ được ghi nhận người khác trong scope được cấp.")
    with transaction.atomic():
        recognition = Recognition.objects.create(sender=actor, category=category, message=message)
        recognition.recipients.set(recipients)
        notify_many(
            recipients=recipients,
            kind=Notification.Kind.RECOGNITION,
            title=f"{actor.display_name or actor.employee_code} đã ghi nhận bạn",
            body=f"{category}: {message[:240]}",
            target_type="recognition",
            target_uuid=recognition.pk,
            key_prefix=f"recognition:{recognition.pk}",
        )
        audit(
            actor=actor_user,
            action="rewards.recognition.created",
            target=recognition,
            changes={"recipient_count": len(recipients), "category": category},
        )
        return recognition


def star_balance(employee):
    return employee.star_ledger.aggregate(total=Sum("amount"))["total"] or 0


def create_star_entry(*, actor_user, employee, amount: int, reason: str, idempotency_key=None):
    if not actor_user.has_perm(GRANT_STARS_SCOPED) or not can_grant_stars(actor_user, employee):
        raise PermissionDenied("Bạn chỉ được cấp hoặc điều chỉnh sao trong scope được cấp.")
    if employee.employment_status not in ['probation', 'official']:
        raise ValidationError('Nhân sự không còn đủ điều kiện nhận sao.')
    if amount < 0 and not actor_user.has_perm(GRANT_STARS_COMPANY):
        raise PermissionDenied('Chỉ HR/CEO được điều chỉnh giảm sao.')
    if amount == 0 or abs(amount) > 1_000_000:
        raise ValidationError({"amount": "Số sao phải khác 0 và nằm trong giới hạn kỹ thuật."})
    if not reason.strip():
        raise ValidationError({"reason": "Lý do là bắt buộc."})
    normalized_key = idempotency_key or None
    if normalized_key:
        existing = StarLedgerEntry.objects.filter(idempotency_key=normalized_key).first()
        if existing:
            if existing.actor_id == actor_user.pk and existing.employee_id == employee.pk and existing.amount == amount and existing.reason == reason.strip():
                return existing
            raise ValidationError({"idempotency_key": "Khóa này đã được dùng cho giao dịch khác."})
    try:
        with transaction.atomic():
            Employee.objects.select_for_update().get(pk=employee.pk)
            if normalized_key:
                old = StarLedgerEntry.objects.filter(idempotency_key=normalized_key).first()
                if old:
                    if old.actor_id == actor_user.pk and old.employee_id == employee.pk and old.amount == amount and old.reason == reason.strip():
                        return old
                    raise ValidationError('Mã giao dịch đã dùng.')
            allowance = None
            if not actor_user.has_perm(GRANT_STARS_COMPANY):
                allowance = TeamStarAllowance.objects.select_for_update().filter(team_id=employee.team_id, month=timezone.localdate().replace(day=1)).first()
                if not allowance:
                    raise ValidationError('Team chưa được HR/CEO thiết lập hạn mức sao tháng này.')
                used = allowance.starledgerentry_set.aggregate(total=Sum('amount'))['total'] or 0
                if used + amount > allowance.limit:
                    raise ValidationError('Vượt hạn mức cấp sao của Team trong tháng.')
            current = star_balance(employee)
            if current + amount < 0:
                raise ValidationError({"amount": "Điều chỉnh không được làm số dư âm."})
            entry = StarLedgerEntry.objects.create(
                employee=employee,
                allowance=allowance,
                amount=amount,
                entry_type=StarLedgerEntry.EntryType.GRANT if amount > 0 else StarLedgerEntry.EntryType.ADJUSTMENT,
                reason=reason.strip(),
                actor=actor_user,
                idempotency_key=normalized_key,
            )
            audit(
                actor=actor_user,
                action="rewards.stars.recorded",
                target=entry,
                changes={"employee_uuid": str(employee.pk), "amount": amount, "reason": "provided"},
            )
            return entry
    except IntegrityError as exc:
        raise ValidationError({"idempotency_key": "Giao dịch trùng đã được xử lý."}) from exc


def leaderboard(period: str):
    today = timezone.localdate()
    if period == "month":
        start_date = today.replace(day=1)
    elif period == "quarter":
        start_month = ((today.month - 1) // 3) * 3 + 1
        start_date = today.replace(month=start_month, day=1)
    elif period == "year":
        start_date = today.replace(month=1, day=1)
    else:
        raise ValidationError({"period": "Chọn month, quarter hoặc year."})
    start = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    rows = list(
        StarLedgerEntry.objects.filter(created_at__gte=start, entry_type__in=["grant", "adjustment"])
        .values("employee_id", "employee__display_name", "employee__employee_code", "employee__team__name")
        .annotate(stars=Sum("amount"))
        .order_by("-stars", "employee__employee_code")
    )
    return [
        {
            "rank": index,
            "employee_uuid": row["employee_id"],
            "display_name": row["employee__display_name"],
            "employee_code": row["employee__employee_code"],
            "team_name": row["employee__team__name"],
            "stars": row["stars"],
        }
        for index, row in enumerate((row for row in rows if row["stars"] > 0), start=1)
    ]
