from datetime import datetime
from decimal import Decimal
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import PerformanceReview, PerformanceKPI, PerformanceReviewRevision
from .access import can_manage, REOPEN, OWN

class MonthField(serializers.CharField):
    def to_internal_value(self, value):
        value = super().to_internal_value(value)
        try:
            if len(value) != 7:
                raise ValueError()
            return datetime.strptime(value, "%Y-%m").date().replace(day=1)
        except ValueError:
            raise serializers.ValidationError("Tháng phải có dạng YYYY-MM.")
    def to_representation(self, value):
        return value.strftime("%Y-%m")

class KPISerializer(serializers.ModelSerializer):
    completion = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal(0), max_value=Decimal(100), allow_null=True, required=False, default=None)
    weight = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal(0), max_value=Decimal(100))
    class Meta:
        model = PerformanceKPI
        fields = ["title", "description", "weight", "completion", "comment"]

class RevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReviewRevision
        fields = ["uuid", "event", "reason", "snapshot", "created_at"]
        read_only_fields = fields

class ReviewSerializer(serializers.ModelSerializer):
    month = MonthField(read_only=True)
    employee_name = serializers.CharField(source="employee.display_name", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    leader_name = serializers.CharField(source="leader.display_name", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    kpis = KPISerializer(many=True, read_only=True)
    revisions = RevisionSerializer(many=True, read_only=True)
    can_edit = serializers.SerializerMethodField()
    can_reopen = serializers.SerializerMethodField()
    can_acknowledge = serializers.SerializerMethodField()
    @extend_schema_field(serializers.BooleanField())
    def get_can_edit(self, obj):
        return obj.status == "draft" and can_manage(self.context["request"].user, obj)
    @extend_schema_field(serializers.BooleanField())
    def get_can_reopen(self, obj):
        return obj.status != "draft" and self.context["request"].user.has_perm(REOPEN)
    @extend_schema_field(serializers.BooleanField())
    def get_can_acknowledge(self, obj):
        user = self.context["request"].user
        return obj.status == "finalized" and user.has_perm(OWN) and obj.employee_id == user.employee_profile.pk
    class Meta:
        model = PerformanceReview
        fields = ["uuid", "employee", "employee_name", "employee_code", "team", "team_name", "leader_name", "month", "status", "status_label", "total_score", "leader_comment", "employee_feedback", "finalized_at", "acknowledged_at", "version", "kpis", "revisions", "can_edit", "can_reopen", "can_acknowledge"]
        read_only_fields = fields

class CreateReviewSerializer(serializers.Serializer):
    employee_uuid = serializers.UUIDField()
    month = MonthField()

class UpdateReviewSerializer(serializers.Serializer):
    version = serializers.IntegerField(min_value=1)
    leader_comment = serializers.CharField(max_length=5000, allow_blank=True, required=False)
    kpis = KPISerializer(many=True, required=False, allow_empty=True, max_length=50)

class CommandSerializer(serializers.Serializer):
    version = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    employee_feedback = serializers.CharField(max_length=5000, required=False, allow_blank=True)

class ContextQuerySerializer(serializers.Serializer):
    employee_uuid = serializers.UUIDField()
    month = MonthField()


class KPISourceSerializer(serializers.Serializer):
    month = serializers.CharField()
    kpis = KPISerializer(many=True)

class ReviewEmployeeSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    display_name = serializers.CharField()
    employee_code = serializers.CharField()
    team_name = serializers.CharField()

class TaskContextSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    title = serializers.CharField()
    due_at = serializers.DateTimeField()
    progress = serializers.IntegerField()
    status = serializers.CharField()
