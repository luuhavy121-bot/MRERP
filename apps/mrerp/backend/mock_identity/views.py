import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DebugSwitchRequestSerializer, LoginRequestSerializer, SessionResponseSerializer


logger = logging.getLogger(__name__)
DEBUG_PERSONAS = (
    {"username": "ceo.demo", "label": "CEO · Toàn quyền People"},
    {"username": "hr.demo", "label": "HR · People"},
    {"username": "leader.demo", "label": "Leader · Team Alpha"},
    {"username": "staff.demo", "label": "Staff · Team Alpha"},
    {"username": "other.demo", "label": "Staff · Team Beta"},
)


def debug_identity_enabled():
    return settings.APP_ENV in {"development", "test"} and settings.MOCK_IDENTITY_ENABLED


def actor_payload(user):
    employee = getattr(user, "employee_profile", None)
    payload = {
        "authenticated": user.is_authenticated,
        "username": user.username,
        "employee_uuid": str(employee.pk) if employee else None,
        "employee_code": employee.employee_code if employee else None,
        "display_name": (employee.display_name or employee.employee_code) if employee else user.username,
        "rank": employee.rank if employee else None,
        "capabilities": sorted(user.get_all_permissions()),
    }
    if debug_identity_enabled():
        payload["mock_identity"] = True
        payload["debug_personas"] = DEBUG_PERSONAS
    return payload


@method_decorator(ensure_csrf_cookie, name="dispatch")
class SessionView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=SessionResponseSerializer)
    def get(self, request):
        payload = actor_payload(request.user) if request.user.is_authenticated else {"authenticated": False}
        payload["csrf_token"] = get_token(request)
        payload["mock_identity"] = debug_identity_enabled()
        if debug_identity_enabled():
            payload["debug_personas"] = DEBUG_PERSONAS
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


class DebugSwitchView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=DebugSwitchRequestSerializer, responses=SessionResponseSerializer)
    def post(self, request):
        if not debug_identity_enabled():
            return Response({"detail": "Debug Identity không được bật."}, status=status.HTTP_404_NOT_FOUND)
        serializer = DebugSwitchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        allowed_usernames = {persona["username"] for persona in DEBUG_PERSONAS}
        username = serializer.validated_data["username"]
        if username not in allowed_usernames:
            return Response({"username": "Persona không nằm trong allow-list debug."}, status=status.HTTP_400_BAD_REQUEST)
        user = get_user_model().objects.filter(username=username, is_active=True).first()
        if user is None or not hasattr(user, "employee_profile"):
            return Response({"detail": "Persona debug chưa được seed hoặc không hợp lệ."}, status=status.HTTP_409_CONFLICT)
        source_username = request.user.username
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        logger.info("Mock Identity persona switched", extra={"source_username": source_username, "target_username": username})
        return Response(actor_payload(user))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
