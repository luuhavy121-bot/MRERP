from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginRequestSerializer, SessionResponseSerializer


def actor_payload(user):
    employee = getattr(user, "employee_profile", None)
    return {
        "authenticated": user.is_authenticated,
        "username": user.username,
        "employee_uuid": str(employee.pk) if employee else None,
        "employee_code": employee.employee_code if employee else None,
        "display_name": (employee.display_name or employee.employee_code) if employee else user.username,
        "rank": employee.rank if employee else None,
        "capabilities": sorted(user.get_all_permissions()),
    }


@method_decorator(ensure_csrf_cookie, name="dispatch")
class SessionView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(responses=SessionResponseSerializer)
    def get(self, request):
        payload = actor_payload(request.user) if request.user.is_authenticated else {"authenticated": False}
        payload["csrf_token"] = get_token(request)
        payload["mock_identity"] = settings.MOCK_IDENTITY_ENABLED
        return Response(payload)


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(request=LoginRequestSerializer, responses=SessionResponseSerializer)
    def post(self, request):
        if not settings.MOCK_IDENTITY_ENABLED:
            return Response({"detail": "Mock Identity không được bật."}, status=status.HTTP_404_NOT_FOUND)
        username = str(request.data.get("username", "")).strip()
        password = str(request.data.get("password", ""))
        user = authenticate(request, username=username, password=password)
        if user is None or not user.is_active:
            return Response({"detail": "Tài khoản hoặc mật khẩu không đúng."}, status=status.HTTP_401_UNAUTHORIZED)
        if not hasattr(user, "employee_profile"):
            return Response({"detail": "Tài khoản chưa liên kết Employee."}, status=status.HTTP_403_FORBIDDEN)
        login(request, user)
        return Response(actor_payload(user))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
