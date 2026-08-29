import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import APIException, ValidationError

from .models import EmployeeAccountState


class IdentityAdapterUnavailable(APIException):
    status_code = 503
    default_detail = "Identity Provider production chưa được cấu hình."
    default_code = "identity_adapter_unavailable"


User = get_user_model()


def require_mock_adapter():
    if settings.APP_ENV not in {"development", "test"} or not settings.MOCK_IDENTITY_ENABLED:
        raise IdentityAdapterUnavailable()


def temporary_password() -> str:
    return f"Mre!{secrets.token_urlsafe(14)}"


def validate_new_password(password: str, user=None):
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise ValidationError({"new_password": list(exc.messages)}) from exc


def provision_account(*, employee, username: str) -> tuple[object, str]:
    require_mock_adapter()
    username = username.strip()
    if not username:
        raise ValidationError({"username": "Tài khoản không được để trống."})
    if employee.identity_user_id:
        raise ValidationError({"account": "Employee đã có tài khoản."})
    if User.objects.filter(username__iexact=username).exists():
        raise ValidationError({"username": "Tài khoản đã tồn tại."})
    password = temporary_password()
    user = User.objects.create_user(username=username, password=password, is_active=True)
    EmployeeAccountState.objects.update_or_create(employee=employee, defaults={"must_change_password": True})
    return user, password


def reset_password(*, employee) -> str:
    require_mock_adapter()
    if not employee.identity_user_id:
        raise ValidationError({"account": "Employee chưa có tài khoản."})
    password = temporary_password()
    employee.identity_user.set_password(password)
    employee.identity_user.save(update_fields=["password"])
    state, _ = EmployeeAccountState.objects.get_or_create(employee=employee)
    state.must_change_password = True
    state.save(update_fields=["must_change_password", "updated_at"])
    return password


def change_password(*, employee, current_password: str, new_password: str):
    require_mock_adapter()
    if not employee.identity_user_id or not employee.identity_user.check_password(current_password):
        raise ValidationError({"current_password": "Mật khẩu hiện tại không đúng."})
    validate_new_password(new_password, user=employee.identity_user)
    employee.identity_user.set_password(new_password)
    employee.identity_user.save(update_fields=["password"])
    state, _ = EmployeeAccountState.objects.get_or_create(employee=employee)
    state.must_change_password = False
    state.save(update_fields=["must_change_password", "updated_at"])


def set_account_active(*, employee, active: bool):
    require_mock_adapter()
    if not employee.identity_user_id:
        raise ValidationError({"account": "Employee chưa có tài khoản."})
    employee.identity_user.is_active = active
    employee.identity_user.save(update_fields=["is_active"])
