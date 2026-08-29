import csv

from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .access import can_view_hr_detail, get_actor_employee, visible_employee_queryset
from .capabilities import (
    ADD_EMPLOYEE,
    CHANGE_EMPLOYMENT_STATUS,
    CHANGE_EMPLOYEE,
    CHANGE_OWN_PASSWORD,
    CHANGE_OWN_PROFILE,
    IMPORT_EXPORT_EMPLOYEE,
    MANAGE_ACCESS,
    MANAGE_ACCOUNT,
    MANAGE_MEMBERSHIP,
    MANAGE_ORGANIZATION,
    PROMOTE_EMPLOYEE,
    PROVISION_ACCOUNT,
    RESET_PASSWORD,
    VIEW_ADMIN_PANEL,
    VIEW_AUDIT,
    VIEW_COMPANY_DIRECTORY,
    VIEW_EMPLOYEE,
)
from .account_services import change_employment, change_own_password, provision_employee_account, reset_employee_password, set_employee_account_lock
from .admin_services import access_projection, set_access_bundle, visible_audit_queryset
from .csv_services import export_employee_rows, import_employee_csv
from .models import AuditEvent, Employee, Team, TeamLeadership
from .serializers import (
    ApiErrorSerializer,
    AccessAccountSerializer,
    AccessUpdateSerializer,
    AccountCommandResponseSerializer,
    AccountProvisionSerializer,
    AuditEventSerializer,
    ChangePasswordSerializer,
    EmployeeBasicSerializer,
    EmployeeCreateSerializer,
    EmployeeCreateResponseSerializer,
    EmployeeHRSerializer,
    EmployeeHistorySerializer,
    EmployeeLeaderSerializer,
    EmployeeSelfSerializer,
    EmployeeSelfUpdateSerializer,
    EmployeeUpdateSerializer,
    EmploymentCommandSerializer,
    EmploymentHistorySerializer,
    ImportResultSerializer,
    LeadershipSerializer,
    MembershipSerializer,
    PromotionSerializer,
    TeamLeadershipSerializer,
    TeamSerializer,
    MembershipHistorySerializer,
)
from .services import assign_team, audit, create_probation_employee, promote_employee, update_employee_details, update_self_profile


def require_capability(user, capability: str):
    get_actor_employee(user)
    if not user.has_perm(capability):
        raise PermissionDenied("Bạn không có capability phù hợp.")


class EmployeeViewSet(viewsets.GenericViewSet):
    queryset = Employee.objects.none()

    def get_queryset(self):
        require_capability(self.request.user, VIEW_EMPLOYEE)
        queryset = visible_employee_queryset(self.request.user)
        search = self.request.query_params.get("search", "").strip()
        team_uuid = self.request.query_params.get("team")
        if search:
            queryset = queryset.filter(
                Q(employee_code__icontains=search)
                | Q(display_name__icontains=search)
                | Q(job_title__icontains=search)
            )
        if team_uuid:
            queryset = queryset.filter(team_id=team_uuid)
        return queryset

    def get_serializer_class(self):
        if can_view_hr_detail(self.request.user):
            return EmployeeHRSerializer
        if self.request.user.has_perm(VIEW_COMPANY_DIRECTORY):
            return EmployeeLeaderSerializer
        return EmployeeBasicSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, description="Tìm theo mã, tên hiển thị hoặc vị trí."),
            OpenApiParameter("team", OpenApiTypes.UUID, description="Lọc theo Team trong scope của actor."),
        ],
        responses={200: EmployeeBasicSerializer(many=True), 403: ApiErrorSerializer},
    )
    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema(responses={200: EmployeeBasicSerializer, 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    def retrieve(self, request, pk=None):
        employee = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(self.get_serializer(employee).data)

    @extend_schema(
        request=EmployeeCreateSerializer,
        responses={201: EmployeeCreateResponseSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer},
    )
    def create(self, request):
        require_capability(request.user, ADD_EMPLOYEE)
        serializer = EmployeeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee, temporary_password = create_probation_employee(actor=request.user, **serializer.validated_data)
        payload = EmployeeHRSerializer(employee, context={"request": request}).data
        if temporary_password:
            payload["temporary_password"] = temporary_password
        return Response(payload, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=EmployeeUpdateSerializer,
        responses={200: EmployeeHRSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer, 404: ApiErrorSerializer},
    )
    def partial_update(self, request, pk=None):
        require_capability(request.user, CHANGE_EMPLOYEE)
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeUpdateSerializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if "expected_version" not in serializer.validated_data:
            return Response({"expected_version": "Trường này là bắt buộc."}, status=status.HTTP_400_BAD_REQUEST)
        updated = update_employee_details(
            actor=request.user,
            employee=employee,
            validated_data=dict(serializer.validated_data),
        )
        return Response(EmployeeHRSerializer(updated).data)

    @extend_schema(request=EmployeeSelfUpdateSerializer, responses={200: EmployeeSelfSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        employee = get_actor_employee(request.user)
        if request.method == "PATCH":
            require_capability(request.user, CHANGE_OWN_PROFILE)
            serializer = EmployeeSelfUpdateSerializer(employee, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            if "expected_version" not in serializer.validated_data:
                raise ValidationError({"expected_version": "Trường này là bắt buộc."})
            employee = update_self_profile(actor=request.user, validated_data=dict(serializer.validated_data))
        return Response(EmployeeSelfSerializer(employee, context={"request": request}).data)

    @extend_schema(request=ChangePasswordSerializer, responses={204: None, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=False, methods=["post"], url_path="me/change-password")
    def change_password(self, request):
        require_capability(request.user, CHANGE_OWN_PASSWORD)
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_own_password(actor=request.user, **serializer.validated_data)
        update_session_auth_hash(request, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=PromotionSerializer,
        responses={200: EmployeeLeaderSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer, 404: ApiErrorSerializer},
    )
    @action(detail=True, methods=["post"])
    def promote(self, request, pk=None):
        require_capability(request.user, PROMOTE_EMPLOYEE)
        target = get_object_or_404(Employee.objects.select_related("team"), pk=pk)
        serializer = PromotionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = promote_employee(actor=request.user, target=target, **serializer.validated_data)
        return Response(EmployeeLeaderSerializer(updated).data)

    @extend_schema(
        request=MembershipSerializer,
        responses={200: EmployeeLeaderSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer, 404: ApiErrorSerializer},
    )
    @action(detail=True, methods=["put"])
    def membership(self, request, pk=None):
        require_capability(request.user, MANAGE_MEMBERSHIP)
        employee = get_object_or_404(Employee, pk=pk)
        serializer = MembershipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team_uuid = serializer.validated_data["team_uuid"]
        team = get_object_or_404(Team, pk=team_uuid, is_active=True) if team_uuid else None
        updated = assign_team(actor=request.user, employee=employee, team=team)
        return Response(EmployeeLeaderSerializer(updated).data)

    @extend_schema(request=AccountProvisionSerializer, responses={200: AccountCommandResponseSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"], url_path="account/provision")
    def provision_account(self, request, pk=None):
        require_capability(request.user, PROVISION_ACCOUNT)
        employee = get_object_or_404(Employee.objects.select_related("identity_user"), pk=pk)
        serializer = AccountProvisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated, password = provision_employee_account(actor=request.user, employee=employee, **serializer.validated_data)
        return Response({"employee": EmployeeHRSerializer(updated, context={"request": request}).data, "temporary_password": password})

    @extend_schema(request=None, responses={200: AccountCommandResponseSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"], url_path="account/reset-password")
    def reset_password(self, request, pk=None):
        require_capability(request.user, RESET_PASSWORD)
        employee = get_object_or_404(Employee.objects.select_related("identity_user", "team"), pk=pk)
        password = reset_employee_password(actor=request.user, employee=employee)
        return Response({"employee": EmployeeLeaderSerializer(employee, context={"request": request}).data, "temporary_password": password})

    @extend_schema(request=None, responses={200: AccountCommandResponseSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"], url_path="account/lock")
    def lock_account(self, request, pk=None):
        require_capability(request.user, MANAGE_ACCOUNT)
        employee = get_object_or_404(Employee.objects.select_related("identity_user"), pk=pk)
        set_employee_account_lock(actor=request.user, employee=employee, locked=True)
        employee.refresh_from_db()
        return Response({"employee": EmployeeHRSerializer(employee, context={"request": request}).data})

    @extend_schema(request=None, responses={200: AccountCommandResponseSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"], url_path="account/unlock")
    def unlock_account(self, request, pk=None):
        require_capability(request.user, MANAGE_ACCOUNT)
        employee = get_object_or_404(Employee.objects.select_related("identity_user"), pk=pk)
        set_employee_account_lock(actor=request.user, employee=employee, locked=False)
        employee.refresh_from_db()
        return Response({"employee": EmployeeHRSerializer(employee, context={"request": request}).data})

    @extend_schema(request=EmploymentCommandSerializer, responses={200: EmployeeHRSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"], url_path="employment")
    def employment(self, request, pk=None):
        require_capability(request.user, CHANGE_EMPLOYMENT_STATUS)
        employee = get_object_or_404(Employee.objects.select_related("identity_user"), pk=pk)
        serializer = EmploymentCommandSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = change_employment(actor=request.user, employee=employee, **serializer.validated_data)
        return Response(EmployeeHRSerializer(updated, context={"request": request}).data)

    @extend_schema(responses={200: EmployeeHistorySerializer, 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        actor = get_actor_employee(request.user)
        employee = get_object_or_404(Employee.objects.select_related("team"), pk=pk)
        managed = bool(employee.team_id and TeamLeadership.objects.filter(team_id=employee.team_id, leader=actor).exists())
        if employee.pk != actor.pk and not can_view_hr_detail(request.user) and not managed:
            raise PermissionDenied("Bạn không có scope xem lịch sử Employee này.")
        return Response({
            "employment": EmploymentHistorySerializer(employee.employment_transitions.select_related("actor", "actor__employee_profile"), many=True).data,
            "membership": MembershipHistorySerializer(employee.team_membership_history.select_related("from_team", "to_team", "actor", "actor__employee_profile"), many=True).data,
        })

    @extend_schema(request={"multipart/form-data": OpenApiTypes.BINARY}, responses={200: ImportResultSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=False, methods=["post"], url_path="import-csv", parser_classes=[MultiPartParser])
    def import_csv(self, request):
        require_capability(request.user, IMPORT_EXPORT_EMPLOYEE)
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            raise ValidationError({"file": "File CSV là bắt buộc."})
        return Response({"created": import_employee_csv(actor=request.user, uploaded_file=uploaded_file)})

    @extend_schema(responses={(200, "text/csv"): OpenApiTypes.BINARY, 403: ApiErrorSerializer})
    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        require_capability(request.user, IMPORT_EXPORT_EMPLOYEE)
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="mrerp-employees.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerows(export_employee_rows())
        return response


class AccessViewSet(viewsets.ViewSet):
    @extend_schema(responses={200: AccessAccountSerializer(many=True), 403: ApiErrorSerializer})
    def list(self, request):
        require_capability(request.user, VIEW_ADMIN_PANEL)
        return Response(AccessAccountSerializer(access_projection(), many=True).data)

    @extend_schema(request=AccessUpdateSerializer, responses={204: None, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=False, methods=["put"], url_path="bundle")
    def bundle(self, request):
        require_capability(request.user, MANAGE_ACCESS)
        serializer = AccessUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = get_object_or_404(Employee.objects.select_related("identity_user"), pk=serializer.validated_data["employee_uuid"])
        set_access_bundle(actor=request.user, employee=employee, bundle=serializer.validated_data["bundle"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuditViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AuditEventSerializer
    queryset = AuditEvent.objects.none()

    def get_queryset(self):
        get_actor_employee(self.request.user)
        return visible_audit_queryset(self.request.user)


class OrganizationViewSetMixin:
    def _require_read(self):
        require_capability(self.request.user, VIEW_EMPLOYEE)

    def _require_write(self):
        require_capability(self.request.user, MANAGE_ORGANIZATION)

    def list(self, request):
        self._require_read()
        return super().list(request)

    def retrieve(self, request, *args, **kwargs):
        self._require_read()
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self._require_write()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._require_write()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._require_write()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied("Slice đầu tiên không hỗ trợ xóa cứng organization.")

    def perform_create(self, serializer):
        instance = serializer.save()
        audit(
            actor=self.request.user,
            action=f"people.{instance.__class__.__name__.lower()}.created",
            target=instance,
            changes={"code": instance.code, "name": instance.name},
        )

    def perform_update(self, serializer):
        before = {field: getattr(serializer.instance, field) for field in ("code", "name")}
        instance = serializer.save()
        changes = {
            field: {"from": before[field], "to": getattr(instance, field)}
            for field in before
            if before[field] != getattr(instance, field)
        }
        audit(
            actor=self.request.user,
            action=f"people.{instance.__class__.__name__.lower()}.updated",
            target=instance,
            changes=changes,
        )


class TeamViewSet(OrganizationViewSetMixin, viewsets.ModelViewSet):
    queryset = Team.objects.filter(is_active=True).select_related("department").prefetch_related("leaderships")
    serializer_class = TeamSerializer

    def get_queryset(self):
        actor = get_actor_employee(self.request.user)
        if self.request.user.has_perm(VIEW_COMPANY_DIRECTORY) or can_view_hr_detail(self.request.user):
            return self.queryset
        if actor.team_id:
            return self.queryset.filter(pk=actor.team_id)
        return self.queryset.none()

    @action(detail=True, methods=["get", "post"])
    def leaders(self, request, pk=None):
        team = self.get_object()
        if request.method == "GET":
            self._require_read()
            return Response(TeamLeadershipSerializer(team.leaderships.select_related("leader"), many=True).data)
        require_capability(request.user, MANAGE_MEMBERSHIP)
        serializer = LeadershipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leader = get_object_or_404(Employee, pk=serializer.validated_data["employee_uuid"], rank=Employee.Rank.LEADER)
        if leader.pk == get_actor_employee(request.user).pk:
            raise PermissionDenied("Không được tự gán quyền Leader–Team cho chính mình.")
        link, created = TeamLeadership.objects.get_or_create(team=team, leader=leader)
        if created:
            audit(actor=request.user, action="people.leadership.created", target=link, changes={"team": str(team.pk), "leader": str(leader.pk)})
        return Response(TeamLeadershipSerializer(link).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @extend_schema(parameters=[OpenApiParameter("employee_uuid", OpenApiTypes.UUID, OpenApiParameter.PATH)])
    @action(detail=True, methods=["delete"], url_path=r"leaders/(?P<employee_uuid>[^/.]+)")
    def remove_leader(self, request, pk=None, employee_uuid=None):
        require_capability(request.user, MANAGE_MEMBERSHIP)
        team = self.get_object()
        link = get_object_or_404(TeamLeadership, team=team, leader_id=employee_uuid)
        if link.leader_id == get_actor_employee(request.user).pk:
            raise PermissionDenied("Không được tự gỡ quan hệ Leader–Team của chính mình.")
        target_uuid = str(link.pk)
        link.delete()
        audit(
            actor=request.user,
            action="people.leadership.removed",
            target=team,
            changes={"leadership_uuid": target_uuid, "leader": str(employee_uuid)},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        require_capability(request.user, MANAGE_ORGANIZATION)
        team = self.get_object()
        if team.members.exists() or team.leaderships.exists():
            raise ValidationError({"team": "Phải chuyển hết nhân sự và gỡ toàn bộ Leader trước khi archive Team."})
        team.is_active = False
        team.save(update_fields=["is_active", "updated_at"])
        audit(actor=request.user, action="people.team.archived", target=team, changes={"is_active": False})
        return Response(TeamSerializer(team).data)
