from rest_framework import serializers

from .account_services import can_reset_password
from .models import AuditEvent, Department, Employee, EmploymentTransition, Team, TeamLeadership, TeamMembershipHistory


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["uuid", "code", "name", "is_active", "created_at", "updated_at"]
        read_only_fields = ["uuid", "created_at", "updated_at"]


class TeamSerializer(serializers.ModelSerializer):
    leader_count = serializers.IntegerField(source="leaderships.count", read_only=True)

    class Meta:
        model = Team
        fields = ["uuid", "code", "name", "is_active", "leader_count", "created_at", "updated_at"]
        read_only_fields = ["uuid", "is_active", "created_at", "updated_at", "leader_count"]


class EmployeeBasicSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = Employee
        fields = ["uuid", "employee_code", "display_name", "job_title", "team", "team_name"]


class EmployeeLeaderSerializer(EmployeeBasicSerializer):
    employment_status_label = serializers.CharField(source="get_employment_status_display", read_only=True)
    can_promote = serializers.SerializerMethodField()
    has_account = serializers.SerializerMethodField()
    account_active = serializers.SerializerMethodField()
    can_reset_password = serializers.SerializerMethodField()
    can_manage_account = serializers.SerializerMethodField()
    can_change_employment = serializers.SerializerMethodField()
    can_provision_account = serializers.SerializerMethodField()

    def get_can_promote(self, employee) -> bool:
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or not request.user.has_perm("people_domain.promote_employee"):
            return False
        actor_employee = getattr(request.user, "employee_profile", None)
        return bool(
            actor_employee
            and (
                request.user.has_perm("people_domain.promote_any_employee")
                or (
                    employee.team_id
                    and TeamLeadership.objects.filter(team_id=employee.team_id, leader=actor_employee).exists()
                )
            )
            and employee.employment_status == Employee.EmploymentStatus.PROBATION
        )

    def get_can_reset_password(self, employee) -> bool:
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and can_reset_password(request.user, employee))

    def get_can_manage_account(self, employee) -> bool:
        request = self.context.get("request")
        return bool(request and request.user.has_perm("people_domain.manage_employee_account") and request.user.employee_profile.pk != employee.pk)

    def get_can_change_employment(self, employee) -> bool:
        request = self.context.get("request")
        return bool(request and request.user.has_perm("people_domain.change_employment_status") and request.user.employee_profile.pk != employee.pk)

    def get_can_provision_account(self, employee) -> bool:
        request = self.context.get("request")
        return bool(request and request.user.has_perm("people_domain.provision_employee_account") and not employee.identity_user_id)

    def _can_see_account_state(self, employee) -> bool:
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and (
                request.user.has_perm("people_domain.view_hr_detail")
                or request.user.employee_profile.pk == employee.pk
                or can_reset_password(request.user, employee)
            )
        )

    def get_has_account(self, employee) -> bool | None:
        return bool(employee.identity_user_id) if self._can_see_account_state(employee) else None

    def get_account_active(self, employee) -> bool | None:
        return bool(employee.identity_user_id and employee.identity_user.is_active) if self._can_see_account_state(employee) else None

    class Meta(EmployeeBasicSerializer.Meta):
        fields = EmployeeBasicSerializer.Meta.fields + ["employment_status", "employment_status_label", "rank", "can_promote", "has_account", "account_active", "can_reset_password", "can_manage_account", "can_change_employment", "can_provision_account"]


class EmployeeHRSerializer(EmployeeLeaderSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, employee) -> str | None:
        return employee.identity_user.username if employee.identity_user_id else None

    class Meta(EmployeeLeaderSerializer.Meta):
        fields = EmployeeLeaderSerializer.Meta.fields + ["username", "national_id", "date_of_birth", "address", "version", "created_at", "updated_at"]


class EmployeeSelfSerializer(EmployeeLeaderSerializer):
    username = serializers.SerializerMethodField()
    must_change_password = serializers.SerializerMethodField()

    def get_username(self, employee) -> str | None:
        return employee.identity_user.username if employee.identity_user_id else None

    def get_must_change_password(self, employee) -> bool:
        state = getattr(employee, "account_state", None)
        return bool(state and state.must_change_password)

    class Meta(EmployeeLeaderSerializer.Meta):
        fields = EmployeeLeaderSerializer.Meta.fields + ["username", "date_of_birth", "address", "version", "created_at", "updated_at", "must_change_password"]


class EmployeeCreateSerializer(serializers.Serializer):
    employee_code = serializers.CharField(max_length=64)
    create_account = serializers.BooleanField(default=True)
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)

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
        else:
            attrs["username"] = ""
        return attrs


class EmployeeCreateResponseSerializer(EmployeeHRSerializer):
    temporary_password = serializers.CharField(required=False)

    class Meta(EmployeeHRSerializer.Meta):
        fields = EmployeeHRSerializer.Meta.fields + ["temporary_password"]


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    expected_version = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = Employee
        fields = ["display_name", "national_id", "date_of_birth", "address", "job_title", "expected_version"]

    def validate_national_id(self, value):
        return value or None


class EmployeeSelfUpdateSerializer(serializers.ModelSerializer):
    expected_version = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = Employee
        fields = ["display_name", "date_of_birth", "address", "expected_version"]


class AccountProvisionSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)


class TemporaryPasswordSerializer(serializers.Serializer):
    temporary_password = serializers.CharField()


class AccountCommandResponseSerializer(serializers.Serializer):
    employee = EmployeeHRSerializer()
    temporary_password = serializers.CharField(required=False)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)


class EmploymentCommandSerializer(serializers.Serializer):
    command = serializers.ChoiceField(choices=["pause", "terminate", "reactivate"])
    note = serializers.CharField(min_length=1, max_length=2000)


class EmploymentHistorySerializer(serializers.ModelSerializer):
    from_label = serializers.CharField(source="get_from_status_display", read_only=True)
    to_label = serializers.CharField(source="get_to_status_display", read_only=True)
    actor_name = serializers.CharField(source="actor.employee_profile.display_name", read_only=True)

    class Meta:
        model = EmploymentTransition
        fields = ["uuid", "from_status", "from_label", "to_status", "to_label", "note", "actor_name", "effective_at"]


class MembershipHistorySerializer(serializers.ModelSerializer):
    from_team_name = serializers.CharField(source="from_team.name", read_only=True, allow_null=True)
    to_team_name = serializers.CharField(source="to_team.name", read_only=True, allow_null=True)
    actor_name = serializers.CharField(source="actor.employee_profile.display_name", read_only=True)

    class Meta:
        model = TeamMembershipHistory
        fields = ["uuid", "from_team", "from_team_name", "to_team", "to_team_name", "actor_name", "effective_at"]


class EmployeeHistorySerializer(serializers.Serializer):
    employment = EmploymentHistorySerializer(many=True)
    membership = MembershipHistorySerializer(many=True)


class AccessUpdateSerializer(serializers.Serializer):
    employee_uuid = serializers.UUIDField()
    bundle = serializers.ChoiceField(choices=["staff", "leader", "hr", "ceo"])


class AccessAccountSerializer(serializers.Serializer):
    employee_uuid = serializers.UUIDField()
    employee_code = serializers.CharField()
    display_name = serializers.CharField()
    team_name = serializers.CharField(allow_null=True)
    username = serializers.CharField(allow_null=True)
    account_active = serializers.BooleanField()
    groups = serializers.ListField(child=serializers.CharField())
    capabilities = serializers.ListField(child=serializers.CharField())


class AuditEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()

    def get_actor_name(self, event) -> str | None:
        if not event.actor_id:
            return None
        employee = getattr(event.actor, "employee_profile", None)
        return (employee.display_name or employee.employee_code) if employee else event.actor.username

    class Meta:
        model = AuditEvent
        fields = ["uuid", "actor_name", "action", "target_type", "target_uuid", "changes", "correlation_id", "created_at"]


class ImportResultSerializer(serializers.Serializer):
    created = serializers.IntegerField()


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


class ApiErrorSerializer(serializers.Serializer):
    code = serializers.CharField()
    detail = serializers.CharField()
    correlation_id = serializers.UUIDField()
    errors = serializers.DictField(required=False)
