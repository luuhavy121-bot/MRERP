from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import NotificationPreference


class PreferenceSerializer(serializers.ModelSerializer):
    mandatory_notifications = serializers.SerializerMethodField()
    account_active = serializers.SerializerMethodField()
    employment_status = serializers.CharField(source="employee.employment_status", read_only=True)
    employment_status_label = serializers.CharField(source="employee.get_employment_status_display", read_only=True)
    must_change_password = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_mandatory_notifications(self, _preference):
        return ["account", "security", "task", "leave", "recruitment"]

    @extend_schema_field(serializers.BooleanField())
    def get_account_active(self, preference):
        user = preference.employee.identity_user
        return bool(user and user.is_active)

    @extend_schema_field(serializers.BooleanField())
    def get_must_change_password(self, preference):
        account_state = getattr(preference.employee, "account_state", None)
        return bool(account_state and account_state.must_change_password)

    class Meta:
        model = NotificationPreference
        fields = [
            "social_notifications_enabled",
            "mandatory_notifications",
            "account_active",
            "employment_status",
            "employment_status_label",
            "must_change_password",
            "updated_at",
        ]
        read_only_fields = [
            "mandatory_notifications",
            "account_active",
            "employment_status",
            "employment_status_label",
            "must_change_password",
            "updated_at",
        ]


class PreferenceUpdateSerializer(serializers.Serializer):
    social_notifications_enabled = serializers.BooleanField()
