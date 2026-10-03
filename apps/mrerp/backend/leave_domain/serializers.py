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
            "start_period", "end_period",
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
    start_period = serializers.ChoiceField(choices=["am", "pm"], default="am")
    end_period = serializers.ChoiceField(choices=["am", "pm"], default="pm")
    reason = serializers.CharField(min_length=1, max_length=2000, trim_whitespace=True)

    def validate(self, attrs):
        if attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError({"end_date": "Ngày kết thúc phải từ ngày bắt đầu trở đi."})
        if (attrs["end_date"] - attrs["start_date"]).days > 365:
            raise serializers.ValidationError({"end_date": "Mỗi đơn tối đa 366 ngày."})
        if attrs["end_date"] == attrs["start_date"] and attrs["start_period"] == "pm" and attrs["end_period"] == "am":
            raise serializers.ValidationError({"end_period": "Buổi kết thúc phải sau hoặc cùng buổi bắt đầu."})
        return attrs


class LeaveRequestUpdateSerializer(LeaveRequestCreateSerializer):
    expected_version = serializers.IntegerField(min_value=1)


class LeaveReviewSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=[LeaveRequest.Status.APPROVED, LeaveRequest.Status.REJECTED])
    note = serializers.CharField(required=False, allow_blank=True, max_length=2000, trim_whitespace=True)

    def validate(self, data):
        if data["decision"] == LeaveRequest.Status.REJECTED and not data.get("note", "").strip():
            raise serializers.ValidationError({"note": "Nhập lý do từ chối đơn nghỉ."})
        return data


class LeaveCalendarSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    name = serializers.CharField()
    employee_code = serializers.CharField()
    team_name = serializers.CharField(allow_null=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    start_period = serializers.CharField()
    end_period = serializers.CharField()


class AttendanceRowSerializer(serializers.Serializer):
    employee_uuid = serializers.UUIDField()
    employee_code = serializers.CharField()
    display_name = serializers.CharField()
    team_name = serializers.CharField(allow_null=True)
    month = serializers.CharField()
    scheduled_workdays = serializers.FloatField()
    public_holiday_days = serializers.FloatField()
    approved_leave_days = serializers.FloatField()
    adjustment_days = serializers.IntegerField()
    adjustment_reason = serializers.CharField(allow_blank=True)
    projected_workdays = serializers.FloatField()


class AttendanceAdjustmentSerializer(serializers.Serializer):
    employee_uuid = serializers.UUIDField()
    month = serializers.RegexField(r"^\d{4}-\d{2}$")
    days = serializers.IntegerField(min_value=-31, max_value=31)
    reason = serializers.CharField(min_length=1, max_length=500, trim_whitespace=True)
