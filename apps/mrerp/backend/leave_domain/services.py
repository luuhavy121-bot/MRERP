import calendar
from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from people_domain.models import Employee
from people_domain.services import audit

from .access import can_edit_request, can_review_request
from .models import AttendanceAdjustment, LeaveRequest, PublicHoliday


def create_leave_request(*, actor, start_date: date, end_date: date, reason: str) -> LeaveRequest:
    actor_employee = actor.employee_profile
    with transaction.atomic():
        Employee.objects.select_for_update().get(pk=actor_employee.pk)
        overlaps = LeaveRequest.objects.filter(
            requester=actor_employee,
            status__in=[LeaveRequest.Status.PENDING, LeaveRequest.Status.APPROVED],
            start_date__lte=end_date,
            end_date__gte=start_date,
        ).exists()
        if overlaps:
            raise ValidationError({"dates": "Khoảng nghỉ bị trùng với một đơn đang chờ hoặc đã duyệt."})
        leave_request = LeaveRequest.objects.create(
            requester=actor_employee,
            requester_team=actor_employee.team,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )
        audit(
            actor=actor,
            action="leave.request.created",
            target=leave_request,
            changes={"start_date": str(start_date), "end_date": str(end_date), "status": LeaveRequest.Status.PENDING},
        )
        return leave_request


def update_leave_request(
    *, actor, leave_request: LeaveRequest, start_date: date, end_date: date, reason: str, expected_version: int
) -> LeaveRequest:
    if not can_edit_request(actor, leave_request):
        raise PermissionDenied("Chỉ đơn của bạn đang Chờ duyệt mới có thể sửa.")
    with transaction.atomic():
        locked = LeaveRequest.objects.select_for_update().get(pk=leave_request.pk)
        if locked.status != LeaveRequest.Status.PENDING:
            raise ValidationError({"status": "Đơn đã được xử lý nên không thể sửa."})
        if locked.version != expected_version:
            raise ValidationError({"expected_version": "Đơn đã thay đổi. Hãy tải lại trước khi sửa."})
        overlaps = LeaveRequest.objects.filter(
            requester=locked.requester,
            status__in=[LeaveRequest.Status.PENDING, LeaveRequest.Status.APPROVED],
            start_date__lte=end_date,
            end_date__gte=start_date,
        ).exclude(pk=locked.pk).exists()
        if overlaps:
            raise ValidationError({"dates": "Khoảng nghỉ bị trùng với một đơn đang chờ hoặc đã duyệt."})
        previous_dates = {"start_date": str(locked.start_date), "end_date": str(locked.end_date)}
        reason_changed = locked.reason != reason
        locked.start_date = start_date
        locked.end_date = end_date
        locked.reason = reason
        locked.version += 1
        locked.save(update_fields=["start_date", "end_date", "reason", "version", "updated_at"])
        audit(
            actor=actor,
            action="leave.request.updated",
            target=locked,
            changes={
                "before": previous_dates,
                "after": {"start_date": str(start_date), "end_date": str(end_date)},
                "reason_changed": reason_changed,
            },
        )
        return locked


def review_leave_request(*, actor, leave_request: LeaveRequest, decision: str, note: str = "") -> LeaveRequest:
    if not can_review_request(actor, leave_request):
        raise PermissionDenied("Leader chỉ được duyệt đơn của thành viên Team mình lãnh đạo.")
    with transaction.atomic():
        # requester_team is optional, so lock the request row without an outer join.
        locked = LeaveRequest.objects.select_for_update().get(pk=leave_request.pk)
        if locked.status != LeaveRequest.Status.PENDING:
            raise ValidationError({"status": "Đơn này đã được xử lý."})
        previous = locked.status
        locked.status = decision
        locked.reviewer = actor
        locked.review_note = note
        locked.reviewed_at = timezone.now()
        locked.version += 1
        locked.save(update_fields=["status", "reviewer", "review_note", "reviewed_at", "version", "updated_at"])
        audit(
            actor=actor,
            action="leave.request.reviewed",
            target=locked,
            changes={"from": previous, "to": decision, "note": "provided" if note else "empty"},
        )
        from dashboard_domain.models import Notification
        from dashboard_domain.services import notify
        notify(
            recipient=locked.requester,
            kind=Notification.Kind.LEAVE,
            title="Đơn nghỉ đã được duyệt" if decision == LeaveRequest.Status.APPROVED else "Đơn nghỉ bị từ chối",
            body=f"{locked.start_date} – {locked.end_date}",
            target_type="leave",
            target_uuid=locked.pk,
            deduplication_key=f"leave-reviewed:{locked.pk}:{locked.version}",
        )
        return locked


def month_bounds(month_value: str) -> tuple[date, date]:
    try:
        year_text, month_text = month_value.split("-", maxsplit=1)
        year, month = int(year_text), int(month_text)
        return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])
    except (TypeError, ValueError):
        raise ValidationError({"month": "Tháng phải có định dạng YYYY-MM."}) from None


def weekdays_between(start_date: date, end_date: date, holidays=None) -> int:
    holidays = holidays or set()
    days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5 and current not in holidays:
            days += 1
        current += timedelta(days=1)
    return days


def attendance_projection(month_value: str):
    month_start, month_end = month_bounds(month_value)
    holidays = set(PublicHoliday.objects.filter(is_active=True, date__range=(month_start, month_end)).values_list("date", flat=True))
    weekday_holidays = {holiday for holiday in holidays if holiday.weekday() < 5}
    scheduled = weekdays_between(month_start, month_end, weekday_holidays)
    employees = Employee.objects.select_related("team").order_by("employee_code")
    approved = LeaveRequest.objects.filter(
        status=LeaveRequest.Status.APPROVED,
        start_date__lte=month_end,
        end_date__gte=month_start,
    ).values("requester_id", "start_date", "end_date")
    leave_days = {}
    for item in approved:
        overlap_start = max(item["start_date"], month_start)
        overlap_end = min(item["end_date"], month_end)
        leave_days[item["requester_id"]] = leave_days.get(item["requester_id"], 0) + weekdays_between(overlap_start, overlap_end, weekday_holidays)
    adjustments = {
        item.employee_id: item
        for item in AttendanceAdjustment.objects.filter(month=month_start).select_related("employee")
    }
    return [
        _attendance_row(
            employee=employee,
            month_value=month_value,
            scheduled=scheduled,
            public_holiday_days=len(weekday_holidays),
            approved_leave_days=leave_days.get(employee.pk, 0),
            adjustment=adjustments.get(employee.pk),
        )
        for employee in employees
    ]


def _attendance_row(*, employee, month_value, scheduled, public_holiday_days, approved_leave_days, adjustment):
    adjustment_days = adjustment.days if adjustment else 0
    return {
            "employee_uuid": employee.pk,
            "employee_code": employee.employee_code,
            "display_name": employee.display_name or employee.employee_code,
            "team_name": employee.team.name if employee.team else None,
            "month": month_value,
            "scheduled_workdays": scheduled,
            "public_holiday_days": public_holiday_days,
            "approved_leave_days": approved_leave_days,
            "adjustment_days": adjustment_days,
            "adjustment_reason": adjustment.reason if adjustment else "",
            "projected_workdays": max(0, scheduled - approved_leave_days + adjustment_days),
        }


def adjust_attendance(*, actor, employee_uuid, month: str, days: int, reason: str):
    month_start, _ = month_bounds(month)
    with transaction.atomic():
        # Lock only the Employee row. PostgreSQL rejects FOR UPDATE when the
        # nullable Team outer join is part of the locked query.
        employee = Employee.objects.select_for_update().filter(pk=employee_uuid).first()
        if employee is None:
            raise NotFound("Không tìm thấy nhân sự cần điều chỉnh.")
        adjustment, created = AttendanceAdjustment.objects.select_for_update().get_or_create(
            employee=employee,
            month=month_start,
            defaults={"days": days, "reason": reason, "adjusted_by": actor},
        )
        previous_days = 0 if created else adjustment.days
        if not created:
            adjustment.days = days
            adjustment.reason = reason
            adjustment.adjusted_by = actor
            adjustment.save(update_fields=["days", "reason", "adjusted_by", "updated_at"])
        audit(
            actor=actor,
            action="attendance.adjusted",
            target=adjustment,
            changes={
                "employee_uuid": str(employee.pk),
                "month": month,
                "from_days": previous_days,
                "to_days": days,
                "reason": "provided",
            },
        )
    return next(row for row in attendance_projection(month) if row["employee_uuid"] == employee.pk)
