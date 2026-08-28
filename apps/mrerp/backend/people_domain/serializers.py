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
    can_promote = serializers.SerializerMethodField()

    def get_can_promote(self, employee):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or not request.user.has_perm("people_domain.promote_employee"):
            return False
        actor_employee = getattr(request.user, "employee_profile", None)
        return bool(
            actor_employee
            and employee.team_id
            and TeamLeadership.objects.filter(team_id=employee.team_id, leader=actor_employee).exists()
            and employee.employment_status == Employee.EmploymentStatus.PROBATION
        )

    class Meta(EmployeeBasicSerializer.Meta):
        fields = EmployeeBasicSerializer.Meta.fields + ["employment_status", "employment_status_label", "rank", "can_promote"]


class EmployeeHRSerializer(EmployeeLeaderSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, employee):
        return employee.identity_user.username if employee.identity_user_id else None

    class Meta(EmployeeLeaderSerializer.Meta):
        fields = EmployeeLeaderSerializer.Meta.fields + ["username", "national_id", "date_of_birth", "address", "version", "created_at", "updated_at"]


class EmployeeCreateSerializer(serializers.Serializer):
    employee_code = serializers.CharField(max_length=64)
    create_account = serializers.BooleanField(default=True)
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False, required=False, allow_blank=True)

    def validate_employee_code(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Mã nhân sự không được để trống.")
        if Employee.objects.filter(employee_code__iexact=value).exists():
            raise serializers.ValidationError("Mã nhân sự đã tồn tại.")
        return value

    def validate(self, attrs):
        if attrs.get("create_account", True):
            if not attrs.get("username", "").strip():
                raise serializers.ValidationError({"username": "Tài khoản là bắt buộc khi chọn tạo tài khoản."})
            if not attrs.get("password"):
                raise serializers.ValidationError({"password": "Mật khẩu là bắt buộc khi chọn tạo tài khoản."})
        else:
            attrs["username"] = ""
            attrs["password"] = ""
        return attrs


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
