from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from .capabilities import PROMOTE_ANY_EMPLOYEE, STAFF_GROUP
from .identity_adapter import provision_account
from .models import AuditEvent, Employee, EmploymentTransition, Team, TeamLeadership, TeamMembershipHistory

def audit(*, actor, action: str, target, changes: dict | None = None):
    return AuditEvent.objects.create(
        actor=actor,
        action=action,
        target_type=target.__class__.__name__,
        target_uuid=str(target.pk),
        changes=changes or {},
    )


def create_probation_employee(
    *, actor, employee_code: str, create_account: bool = True, username: str = ""
) -> tuple[Employee, str | None]:
    with transaction.atomic():
        try:
            employee = Employee.objects.create(
                employee_code=employee_code,
                employment_status=Employee.EmploymentStatus.PROBATION,
            )
        except IntegrityError as exc:
            raise ValidationError({"employee_code": "Mã nhân sự đã tồn tại."}) from exc
        temporary_password = None
        if create_account:
            identity_user, temporary_password = provision_account(employee=employee, username=username)
            employee.identity_user = identity_user
            employee.save(update_fields=["identity_user", "updated_at"])
            if identity_user:
                staff_group, _ = Group.objects.get_or_create(name=STAFF_GROUP)
                identity_user.groups.add(staff_group)
                audit(actor=actor, action="people.account.provisioned", target=employee, changes={"username": username, "temporary_password": "returned_once"})
        audit(actor=actor, action="people.employee.created", target=employee, changes={"employment_status": Employee.EmploymentStatus.PROBATION, "account_created": create_account})
        return employee, temporary_password


def update_employee_details(*, actor, employee: Employee, validated_data: dict) -> Employee:
    expected_version = validated_data.pop("expected_version")
    with transaction.atomic():
        locked = Employee.objects.select_for_update().get(pk=employee.pk)
        if locked.version != expected_version:
            raise ValidationError({"version": "Hồ sơ đã thay đổi. Hãy tải lại trước khi lưu."})
        changed = {}
        for field, value in validated_data.items():
            old_value = getattr(locked, field)
            if old_value != value:
                setattr(locked, field, value)
                if field in {"national_id", "date_of_birth", "address"}:
                    changed[field] = {"changed": True}
                else:
                    changed[field] = {"from": old_value, "to": value}
        if changed:
            locked.version += 1
            locked.full_clean()
            locked.save(update_fields=[*validated_data.keys(), "version", "updated_at"])
            audit(actor=actor, action="people.employee.updated", target=locked, changes=changed)
        return locked


def promote_employee(*, actor, target: Employee, note: str) -> Employee:
    actor_employee = actor.employee_profile
    has_company_promotion_scope = actor.has_perm(PROMOTE_ANY_EMPLOYEE)
    manages_target_team = bool(
        target.team_id and TeamLeadership.objects.filter(team_id=target.team_id, leader=actor_employee).exists()
    )
    if not has_company_promotion_scope and not manages_target_team:
        raise PermissionDenied("Leader chỉ được xác nhận nhân sự trong Team mình lãnh đạo.")
    if target.employment_status != Employee.EmploymentStatus.PROBATION:
        raise ValidationError({"employment_status": "Chỉ có thể chuyển từ Thử việc sang Chính thức."})
    if not note.strip():
        raise ValidationError({"note": "Ghi chú là bắt buộc."})

    with transaction.atomic():
        locked = Employee.objects.select_for_update().get(pk=target.pk)
        if locked.employment_status != Employee.EmploymentStatus.PROBATION:
            raise ValidationError({"employment_status": "Trạng thái đã thay đổi."})
        previous = locked.employment_status
        locked.employment_status = Employee.EmploymentStatus.OFFICIAL
        locked.version += 1
        locked.save(update_fields=["employment_status", "version", "updated_at"])
        EmploymentTransition.objects.create(
            employee=locked,
            from_status=previous,
            to_status=Employee.EmploymentStatus.OFFICIAL,
            note=note.strip(),
            actor=actor,
            effective_at=timezone.now(),
        )
        audit(
            actor=actor,
            action="people.employee.promoted",
            target=locked,
            changes={"from": previous, "to": Employee.EmploymentStatus.OFFICIAL, "note": "provided"},
        )
        return locked


def assign_team(*, actor, employee: Employee, team: Team | None) -> Employee:
    actor_employee = actor.employee_profile
    if employee.pk == actor_employee.pk:
        raise PermissionDenied("Không được tự thay đổi quan hệ Team của chính mình.")
    with transaction.atomic():
        locked = Employee.objects.select_for_update().get(pk=employee.pk)
        old_team = str(locked.team_id) if locked.team_id else None
        locked.team = team
        locked.department = None
        locked.version += 1
        locked.save(update_fields=["team", "department", "version", "updated_at"])
        TeamMembershipHistory.objects.create(
            employee=locked,
            from_team_id=old_team,
            to_team=team,
            actor=actor,
            effective_at=timezone.now(),
        )
        audit(
            actor=actor,
            action="people.membership.changed",
            target=locked,
            changes={"from_team": old_team, "to_team": str(team.pk) if team else None},
        )
        return locked


def update_self_profile(*, actor, validated_data: dict) -> Employee:
    return update_employee_details(actor=actor, employee=actor.employee_profile, validated_data=validated_data)
