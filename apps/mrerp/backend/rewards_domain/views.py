from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from people_domain.access import get_actor_employee
from people_domain.models import Employee, TeamLeadership
from people_domain.serializers import ApiErrorSerializer
from people_domain.views import require_capability

from .capabilities import (
    GRANT_STARS_COMPANY,
    GRANT_STARS_SCOPED,
    RECOGNIZE_COMPANY,
    RECOGNIZE_SCOPED,
    VIEW_REWARDS,
)
from .models import Recognition
from .serializers import (
    BalanceSerializer,
    LeaderboardRowSerializer,
    RecognitionCreateSerializer,
    RecognitionSerializer,
    RewardAudienceMemberSerializer,
    StarEntryCreateSerializer,
    StarEntrySerializer,
)
from .services import create_recognition, create_star_entry, leaderboard, star_balance


class RecognitionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = RecognitionSerializer
    queryset = Recognition.objects.none()

    def get_queryset(self):
        get_actor_employee(self.request.user)
        require_capability(self.request.user, VIEW_REWARDS)
        return Recognition.objects.filter(moderated_at__isnull=True).select_related("sender").prefetch_related("recipients")

    @extend_schema(request=RecognitionCreateSerializer, responses={201: RecognitionSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def create(self, request):
        get_actor_employee(request.user)
        require_capability(request.user, RECOGNIZE_SCOPED)
        serializer = RecognitionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipient_uuids = serializer.validated_data.pop("recipient_uuids")
        recipients = list(Employee.objects.filter(pk__in=recipient_uuids))
        if len(recipients) != len(set(recipient_uuids)):
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"recipient_uuids": "Có người nhận không tồn tại."})
        recognition = create_recognition(actor_user=request.user, recipients=recipients, **serializer.validated_data)
        return Response(RecognitionSerializer(recognition).data, status=status.HTTP_201_CREATED)


class RewardAudienceView(APIView):
    @extend_schema(responses={200: RewardAudienceMemberSerializer(many=True), 403: ApiErrorSerializer})
    def get(self, request):
        actor = get_actor_employee(request.user)
        require_capability(request.user, VIEW_REWARDS)
        if request.user.has_perm(RECOGNIZE_COMPANY) or request.user.has_perm(GRANT_STARS_COMPANY):
            employees = Employee.objects.filter(employment_status__in=[Employee.EmploymentStatus.PROBATION, Employee.EmploymentStatus.OFFICIAL])
        else:
            team_ids = TeamLeadership.objects.filter(leader=actor).values_list("team_id", flat=True)
            employees = Employee.objects.filter(team_id__in=team_ids, employment_status__in=[Employee.EmploymentStatus.PROBATION, Employee.EmploymentStatus.OFFICIAL])
        employees = employees.exclude(pk=actor.pk).select_related("team")
        return Response([
            {"uuid": str(employee.pk), "employee_code": employee.employee_code, "display_name": employee.display_name, "team_name": employee.team.name if employee.team else None}
            for employee in employees
        ])


class StarGrantView(APIView):
    @extend_schema(request=StarEntryCreateSerializer, responses={201: StarEntrySerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def post(self, request):
        get_actor_employee(request.user)
        require_capability(request.user, GRANT_STARS_SCOPED)
        serializer = StarEntryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = get_object_or_404(Employee, pk=serializer.validated_data.pop("employee_uuid"))
        entry = create_star_entry(actor_user=request.user, employee=employee, **serializer.validated_data)
        return Response(StarEntrySerializer(entry).data, status=status.HTTP_201_CREATED)


class MyStarBalanceView(APIView):
    @extend_schema(responses={200: BalanceSerializer, 403: ApiErrorSerializer})
    def get(self, request):
        actor = get_actor_employee(request.user)
        require_capability(request.user, VIEW_REWARDS)
        ledger = actor.star_ledger.select_related("actor__employee_profile")[:100]
        return Response({"balance": star_balance(actor), "ledger": StarEntrySerializer(ledger, many=True).data})


class LeaderboardView(APIView):
    @extend_schema(
        parameters=[OpenApiParameter("period", str, enum=["month", "quarter", "year"], default="month")],
        responses={200: LeaderboardRowSerializer(many=True), 400: ApiErrorSerializer, 403: ApiErrorSerializer},
    )
    def get(self, request):
        get_actor_employee(request.user)
        require_capability(request.user, VIEW_REWARDS)
        return Response(leaderboard(request.query_params.get("period", "month")))
