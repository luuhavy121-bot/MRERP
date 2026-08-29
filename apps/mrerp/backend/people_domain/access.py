from rest_framework.exceptions import PermissionDenied

from .capabilities import VIEW_COMPANY_DIRECTORY, VIEW_HR_DETAIL
from .models import Employee


def get_actor_employee(user) -> Employee:
    if not user.is_authenticated or not user.is_active:
        raise PermissionDenied("Tài khoản không hợp lệ.")
    try:
        employee = user.employee_profile
    except Employee.DoesNotExist as exc:
        raise PermissionDenied("Tài khoản chưa được liên kết với nhân sự.") from exc
    if employee.employment_status not in {
        Employee.EmploymentStatus.PROBATION,
        Employee.EmploymentStatus.OFFICIAL,
    }:
        raise PermissionDenied("Trạng thái công việc không hợp lệ.")
    return employee


def visible_employee_queryset(user):
    actor = get_actor_employee(user)
    queryset = Employee.objects.select_related("identity_user", "department", "team")
    if user.has_perm(VIEW_HR_DETAIL) or user.has_perm(VIEW_COMPANY_DIRECTORY):
        return queryset
    if actor.team_id:
        return queryset.filter(team_id=actor.team_id)
    return queryset.filter(pk=actor.pk)


def can_view_hr_detail(user) -> bool:
    return user.has_perm(VIEW_HR_DETAIL)
