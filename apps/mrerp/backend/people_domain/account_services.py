from django.contrib.auth.models import Group
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from .capabilities import MANAGE_ACCOUNT, RESET_PASSWORD
from .identity_adapter import change_password as adapter_change_password
from .identity_adapter import provision_account as adapter_provision_account
from .identity_adapter import reset_password as adapter_reset_password
from .identity_adapter import set_account_active
from .models import Employee, EmployeeAccountState, EmploymentTransition, TeamLeadership
from .services import audit


def can_reset_password(actor, target: Employee) -> bool:
    if (
        not actor.has_perm(RESET_PASSWORD)
        or target.pk == actor.employee_profile.pk
        or not target.identity_user_id
        or target.employment_status not in {Employee.EmploymentStatus.PROBATION, Employee.EmploymentStatus.OFFICIAL}
    ):
        return False
    if actor.has_perm(MANAGE_ACCOUNT):
        return True
    return bool(
        target.team_id
        and TeamLeadership.objects.filter(team_id=target.team_id, leader=actor.employee_profile).exists()
    )


def provision_employee_account(*, actor, employee: Employee, username: str):
    if employee.employment_status not in {Employee.EmploymentStatus.PROBATION, Employee.EmploymentStatus.OFFICIAL}:
        raise ValidationError({"employment_status": "Không thể cấp account cho employment không hoạt động."})
    with transaction.atomic():
        locked = Employee.objects.select_for_update().get(pk=employee.pk)
        user, password = adapter_provision_account(employee=locked, username=username)
        staff_group = Group.objects.get(name="People Staff")
        user.groups.add(staff_group)
        locked.identity_user = user
        locked.version += 1
        locked.save(update_fields=["identity_user", "version", "updated_at"])
        audit(actor=actor, action="people.account.provisioned", target=locked, changes={"username": username, "temporary_password": "returned_once"})
        return locked, password


def reset_employee_password(*, actor, employee: Employee) -> str:
    if not can_reset_password(actor, employee):
        raise PermissionDenied("Bạn chỉ được reset mật khẩu account trong scope được quản lý.")
    if employee.employment_status not in {Employee.EmploymentStatus.PROBATION, Employee.EmploymentStatus.OFFICIAL}:
        raise ValidationError({"employment_status": "Không reset mật khẩu cho employment không hoạt động."})
    password = adapter_reset_password(employee=employee)
    audit(actor=actor, action="people.account.password_reset", target=employee, changes={"temporary_password": "returned_once"})
    return password


def change_own_password(*, actor, current_password: str, new_password: str):
    employee = actor.employee_profile
    adapter_change_password(employee=employee, current_password=current_password, new_password=new_password)
    audit(actor=actor, action="people.account.password_changed", target=employee, changes={"self_service": True})


def set_employee_account_lock(*, actor, employee: Employee, locked: bool):
    if employee.pk == actor.employee_profile.pk:
        raise PermissionDenied("Không được tự khóa hoặc mở khóa account qua endpoint quản trị.")
    if not locked and employee.employment_status not in {Employee.EmploymentStatus.PROBATION, Employee.EmploymentStatus.OFFICIAL}:
        raise ValidationError({"employment_status": "Phải kích hoạt employment trước khi mở account."})
    set_account_active(employee=employee, active=not locked)
    audit(actor=actor, action="people.account.locked" if locked else "people.account.unlocked", target=employee, changes={"is_active": not locked})


def change_employment(*, actor, employee: Employee, command: str, note: str) -> Employee:
    if employee.pk == actor.employee_profile.pk:
        raise PermissionDenied("Không được tự thay đổi employment của chính mình.")
    if not note.strip():
        raise ValidationError({"note": "Ghi chú là bắt buộc."})
    with transaction.atomic():
        # PostgreSQL rejects FOR UPDATE on the nullable side of an outer join.
        # Load the optional Identity relation lazily after locking only Employee.
        locked = Employee.objects.select_for_update().get(pk=employee.pk)
        state, _ = EmployeeAccountState.objects.select_for_update().get_or_create(employee=locked)
        previous = locked.employment_status
        active_statuses = {Employee.EmploymentStatus.PROBATION, Employee.EmploymentStatus.OFFICIAL}
        if command == "pause":
            if previous not in active_statuses:
                raise ValidationError({"employment_status": "Chỉ employment đang hoạt động mới có thể tạm nghỉ."})
            state.previous_active_status = previous
            target_status = Employee.EmploymentStatus.PAUSED
        elif command == "terminate":
            if previous == Employee.EmploymentStatus.TERMINATED:
                raise ValidationError({"employment_status": "Employee đã nghỉ việc."})
            if previous in active_statuses:
                state.previous_active_status = previous
            target_status = Employee.EmploymentStatus.TERMINATED
        elif command == "reactivate":
            if previous not in {Employee.EmploymentStatus.PAUSED, Employee.EmploymentStatus.TERMINATED}:
                raise ValidationError({"employment_status": "Employment hiện không cần kích hoạt lại."})
            target_status = state.previous_active_status or Employee.EmploymentStatus.PROBATION
        else:
            raise ValidationError({"command": "Employment command không hợp lệ."})

        if locked.identity_user_id:
            if command == "terminate":
                state.revoked_group_names = list(locked.identity_user.groups.values_list("name", flat=True))
                locked.identity_user.groups.clear()
                set_account_active(employee=locked, active=False)
            elif command == "pause":
                set_account_active(employee=locked, active=False)
            elif command == "reactivate":
                if previous == Employee.EmploymentStatus.TERMINATED and state.revoked_group_names:
                    locked.identity_user.groups.set(Group.objects.filter(name__in=state.revoked_group_names))
                set_account_active(employee=locked, active=True)

        locked.employment_status = target_status
        locked.version += 1
        locked.save(update_fields=["employment_status", "version", "updated_at"])
        state.save(update_fields=["previous_active_status", "revoked_group_names", "updated_at"])
        EmploymentTransition.objects.create(
            employee=locked,
            from_status=previous,
            to_status=target_status,
            note=note.strip(),
            actor=actor,
            effective_at=timezone.now(),
        )
        audit(actor=actor, action="people.employment.changed", target=locked, changes={"from": previous, "to": target_status, "command": command, "note": "provided"})
        return locked
