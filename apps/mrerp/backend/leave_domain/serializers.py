from rest_framework import serializers

from .access import can_edit_request, can_review_request
from .models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    requester_code = serializers.CharField(source="requester.employee_code", read_only=True)
    requester_name = serializers.CharField(source="requester.display_name", read_only=True)
    team_name = serializers.CharField(source="requester_team.name", read_only=True, allow_null=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    reviewer_name = serializers.CharField(source="reviewer.employee_profile.display_name", read_only=True, allow_null=True)
    can_review = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    def get_can_review(self, leave_request) -> bool:
        request = self.context.get("request")
        return bool(request and can_review_request(request.user, leave_request) and leave_request.status == LeaveRequest.Status.PENDING)

    def get_can_edit(self, leave_request) -> bool:
        request = self.context.get("request")
        return bool(request and can_edit_request(request.user, leave_request))

    class Meta:
        model = LeaveRequest
        fields = [
            "uuid",
            "requester_code",
            "requester_name",
            "team_name",
            "start_date",
            "end_date",
            "reason",
            "status",
            "status_label",
            "reviewer_name",
            "review_note",
            "reviewed_at",
            "version",
            "can_review",
            "can_edit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class LeaveRequestCreateSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    reason = serializers.CharField(min_length=1, max_length=2000, trim_whitespace=True)

    def validate(self, attrs):
        if attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError({"end_date": "Ngày kết thúc phải từ ngày bắt đầu trở đi."})
        return attrs


class LeaveRequestUpdateSerializer(LeaveRequestCreateSerializer):
    expected_version = serializers.IntegerField(min_value=1)


class LeaveReviewSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=[LeaveRequest.Status.APPROVED, LeaveRequest.Status.REJECTED])
    note = serializers.CharField(required=False, allow_blank=True, max_length=2000, trim_whitespace=True)


class AttendanceRowSerializer(serializers.Serializer):
    employee_uuid = serializers.UUIDField()
    employee_code = serializers.CharField()
    display_name = serializers.CharField()
    team_name = serializers.CharField(allow_null=True)
    month = serializers.CharField()
    scheduled_workdays = serializers.IntegerField()
    public_holiday_days = serializers.IntegerField()
    approved_leave_days = serializers.IntegerField()
    adjustment_days = serializers.IntegerField()
    adjustment_reason = serializers.CharField(allow_blank=True)
    projected_workdays = serializers.IntegerField()


class AttendanceAdjustmentSerializer(serializers.Serializer):
    employee_uuid = serializers.UUIDField()
    month = serializers.RegexField(r"^\d{4}-\d{2}$")
    days = serializers.IntegerField(min_value=-31, max_value=31)
    reason = serializers.CharField(min_length=1, max_length=500, trim_whitespace=True)
