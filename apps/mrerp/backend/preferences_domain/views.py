from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from people_domain.access import get_actor_employee
from people_domain.serializers import ApiErrorSerializer

from .capabilities import MANAGE_OWN_PREFERENCES
from .models import NotificationPreference
from .serializers import PreferenceSerializer, PreferenceUpdateSerializer


class MyPreferenceView(APIView):
    def _preference(self, request):
        actor = get_actor_employee(request.user)
        if not request.user.has_perm(MANAGE_OWN_PREFERENCES):
            raise PermissionDenied("Bạn không có quyền quản lý cài đặt cá nhân.")
        preference, _ = NotificationPreference.objects.get_or_create(employee=actor)
        return preference

    @extend_schema(responses={200: PreferenceSerializer, 403: ApiErrorSerializer})
    def get(self, request):
        return Response(PreferenceSerializer(self._preference(request)).data)

    @extend_schema(
        request=PreferenceUpdateSerializer,
        responses={200: PreferenceSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer},
    )
    def patch(self, request):
        preference = self._preference(request)
        serializer = PreferenceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        preference.social_notifications_enabled = serializer.validated_data["social_notifications_enabled"]
        preference.save(update_fields=["social_notifications_enabled", "updated_at"])
        return Response(PreferenceSerializer(preference).data)
