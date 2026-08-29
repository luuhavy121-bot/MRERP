from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from .capabilities import MANAGE_ACCESS, VIEW_AUDIT
from .models import AuditEvent, Employee
from .services import audit


BUNDLE_GROUPS = {
    "staff": "People Staff",
    "leader": "People Leader",
    "hr": "People HR",
    "ceo": "People CEO",
}


def access_projection():
    rows = []
    for employee in Employee.objects.select_related("identity_user", "team").order_by("employee_code"):
        user = employee.identity_user
        rows.append({
            "employee_uuid": employee.pk,
            "employee_code": employee.employee_code,
            "display_name": employee.display_name or employee.employee_code,
            "team_name": employee.team.name if employee.team else None,
            "username": user.username if user else None,
            "account_active": bool(user and user.is_active),
            "groups": list(user.groups.values_list("name", flat=True)) if user else [],
            "capabilities": sorted(user.get_all_permissions()) if user else [],
        })
    return rows


def set_access_bundle(*, actor, employee: Employee, bundle: str):
    if not actor.has_perm(MANAGE_ACCESS):
        raise PermissionDenied("Bạn không có capability quản lý access bundle.")
    if employee.pk == actor.employee_profile.pk:
        raise PermissionDenied("Không được tự thay đổi access bundle của chính mình.")
    if not employee.identity_user_id:
        raise ValidationError({"account": "Employee chưa có account."})
    group_name = BUNDLE_GROUPS[bundle]
    group = Group.objects.get(name=group_name)
    with transaction.atomic():
        before = list(employee.identity_user.groups.values_list("name", flat=True))
        employee.identity_user.groups.set([group])
        audit(actor=actor, action="people.access.bundle_changed", target=employee, changes={"from": before, "to": [group_name]})


def visible_audit_queryset(user):
    if not user.has_perm(VIEW_AUDIT):
        raise PermissionDenied("Bạn không có capability xem audit People.")
    queryset = AuditEvent.objects.select_related("actor", "actor__employee_profile")
    if user.has_perm(MANAGE_ACCESS):
        return queryset.filter(action__startswith="people.")
    allowed_prefixes = (
        "people.employee.",
        "people.account.",
        "people.employment.",
        "people.membership.",
    )
    condition = None
    from django.db.models import Q
    for prefix in allowed_prefixes:
        condition = Q(action__startswith=prefix) if condition is None else condition | Q(action__startswith=prefix)
    return queryset.filter(condition)
