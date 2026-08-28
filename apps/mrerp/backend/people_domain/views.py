from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .access import can_view_hr_detail, get_actor_employee, visible_employee_queryset
from .capabilities import (
    ADD_EMPLOYEE,
    CHANGE_EMPLOYEE,
    MANAGE_MEMBERSHIP,
    MANAGE_ORGANIZATION,
    PROMOTE_EMPLOYEE,
    VIEW_COMPANY_DIRECTORY,
    VIEW_EMPLOYEE,
)
from .models import Employee, Team, TeamLeadership
from .serializers import (
    EmployeeBasicSerializer,
    EmployeeCreateSerializer,
    EmployeeHRSerializer,
    EmployeeLeaderSerializer,
    EmployeeUpdateSerializer,
    LeadershipSerializer,
    MembershipSerializer,
    PromotionSerializer,
    TeamLeadershipSerializer,
    TeamSerializer,
)
from .services import assign_team, audit, create_probation_employee, promote_employee, update_employee_details


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

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        employee = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(self.get_serializer(employee).data)

    def create(self, request):
        require_capability(request.user, ADD_EMPLOYEE)
        serializer = EmployeeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = create_probation_employee(actor=request.user, **serializer.validated_data)
        return Response(EmployeeHRSerializer(employee).data, status=status.HTTP_201_CREATED)

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

    @action(detail=False, methods=["get"])
    def me(self, request):
        employee = get_actor_employee(request.user)
        serializer_class = EmployeeHRSerializer if can_view_hr_detail(request.user) else EmployeeLeaderSerializer
        return Response(serializer_class(employee).data)

    @action(detail=True, methods=["post"])
    def promote(self, request, pk=None):
        require_capability(request.user, PROMOTE_EMPLOYEE)
        target = get_object_or_404(Employee.objects.select_related("team"), pk=pk)
        serializer = PromotionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = promote_employee(actor=request.user, target=target, **serializer.validated_data)
        return Response(EmployeeLeaderSerializer(updated).data)

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
        audit(actor=self.request.user, action=f"people.{instance.__class__.__name__.lower()}.created", target=instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        audit(actor=self.request.user, action=f"people.{instance.__class__.__name__.lower()}.updated", target=instance)


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
        target_uuid = str(link.pk)
        link.delete()
        audit(actor=request.user, action="people.leadership.removed", target=team, changes={"leadership_uuid": target_uuid})
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
