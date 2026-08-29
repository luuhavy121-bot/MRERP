from rest_framework import serializers

from .models import Recognition, StarLedgerEntry


class RecognitionSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.display_name", read_only=True)
    sender_code = serializers.CharField(source="sender.employee_code", read_only=True)
    recipient_names = serializers.SlugRelatedField(source="recipients", slug_field="display_name", many=True, read_only=True)

    class Meta:
        model = Recognition
        fields = ["uuid", "sender", "sender_name", "sender_code", "recipients", "recipient_names", "category", "message", "created_at"]
        read_only_fields = fields


class RecognitionCreateSerializer(serializers.Serializer):
    recipient_uuids = serializers.ListField(child=serializers.UUIDField(), min_length=1, max_length=20)
    category = serializers.CharField(min_length=1, max_length=80, trim_whitespace=True)
    message = serializers.CharField(min_length=1, max_length=3000, trim_whitespace=True)


class StarEntrySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.display_name", read_only=True)
    actor_name = serializers.CharField(source="actor.employee_profile.display_name", read_only=True)
    entry_type_label = serializers.CharField(source="get_entry_type_display", read_only=True)

    class Meta:
        model = StarLedgerEntry
        fields = ["uuid", "employee", "employee_name", "amount", "entry_type", "entry_type_label", "reason", "actor_name", "created_at"]
        read_only_fields = fields


class StarEntryCreateSerializer(serializers.Serializer):
    employee_uuid = serializers.UUIDField()
    amount = serializers.IntegerField(min_value=-1_000_000, max_value=1_000_000)
    reason = serializers.CharField(min_length=1, max_length=500, trim_whitespace=True)
    idempotency_key = serializers.CharField(required=False, allow_blank=True, max_length=120, trim_whitespace=True)

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError("Số sao phải khác 0.")
        return value


class BalanceSerializer(serializers.Serializer):
    balance = serializers.IntegerField()
    ledger = StarEntrySerializer(many=True)


class LeaderboardRowSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    employee_uuid = serializers.UUIDField()
    display_name = serializers.CharField()
    employee_code = serializers.CharField()
    team_name = serializers.CharField(allow_null=True)
    stars = serializers.IntegerField()


class RewardAudienceMemberSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    employee_code = serializers.CharField()
    display_name = serializers.CharField()
    team_name = serializers.CharField(allow_null=True)
