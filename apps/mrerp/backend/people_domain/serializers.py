from rest_framework import serializers

from .models import Department, Employee, Team, TeamLeadership


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["uuid", "code", "name", "is_active", "created_at", "updated_at"]
        read_only_fields = ["uuid", "created_at", "updated_at"]


class TeamSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    leader_count = serializers.IntegerField(source="leaderships.count", read_only=True)

    class Meta:
        model = Team
        fields = ["uuid", "code", "name", "department", "department_name", "is_active", "leader_count", "created_at", "updated_at"]
        read_only_fields = ["uuid", "created_at", "updated_at", "department_name", "leader_count"]


class EmployeeBasicSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = Employee
        fields = ["uuid", "employee_code", "display_name", "job_title", "department", "department_name", "team", "team_name"]


class EmployeeLeaderSerializer(EmployeeBasicSerializer):
    employment_status_label = serializers.CharField(source="get_employment_status_display", read_only=True)

    class Meta(EmployeeBasicSerializer.Meta):
        fields = EmployeeBasicSerializer.Meta.fields + ["employment_status", "employment_status_label", "rank"]


class EmployeeHRSerializer(EmployeeLeaderSerializer):
    username = serializers.CharField(source="identity_user.username", read_only=True)

    class Meta(EmployeeLeaderSerializer.Meta):
        fields = EmployeeLeaderSerializer.Meta.fields + ["username", "national_id", "date_of_birth", "address", "version", "created_at", "updated_at"]


class EmployeeCreateSerializer(serializers.Serializer):
    employee_code = serializers.RegexField(regex=r"^[A-Z]{3}\d+$", max_length=16)
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    expected_version = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = Employee
        fields = ["display_name", "national_id", "date_of_birth", "address", "job_title", "department", "expected_version"]

    def validate_national_id(self, value):
        return value or None


class PromotionSerializer(serializers.Serializer):
    note = serializers.CharField(min_length=1, max_length=1000)


class MembershipSerializer(serializers.Serializer):
    team_uuid = serializers.UUIDField(allow_null=True)


class LeadershipSerializer(serializers.Serializer):
    employee_uuid = serializers.UUIDField()


class TeamLeadershipSerializer(serializers.ModelSerializer):
    leader_name = serializers.CharField(source="leader.display_name", read_only=True)
    leader_code = serializers.CharField(source="leader.employee_code", read_only=True)

    class Meta:
        model = TeamLeadership
        fields = ["uuid", "leader", "leader_name", "leader_code", "created_at"]
