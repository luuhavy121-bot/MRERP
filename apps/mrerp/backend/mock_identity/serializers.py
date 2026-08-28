from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class SessionResponseSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField()
    username = serializers.CharField(required=False)
    employee_uuid = serializers.UUIDField(required=False, allow_null=True)
    employee_code = serializers.CharField(required=False, allow_null=True)
    display_name = serializers.CharField(required=False)
    rank = serializers.CharField(required=False, allow_null=True)
    capabilities = serializers.ListField(child=serializers.CharField(), required=False)
    csrf_token = serializers.CharField(required=False)
    mock_identity = serializers.BooleanField(required=False)
