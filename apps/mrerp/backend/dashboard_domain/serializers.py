from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    kind_label = serializers.CharField(source="get_kind_display", read_only=True)
    is_read = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        fields = ["uuid", "kind", "kind_label", "title", "body", "target_type", "target_uuid", "is_read", "read_at", "created_at"]


class DashboardPostSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    author_name = serializers.CharField()
    content = serializers.CharField()
    is_official = serializers.BooleanField()
    attachment_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class DashboardSerializer(serializers.Serializer):
    general = serializers.DictField()
    private = serializers.DictField()
