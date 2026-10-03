from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from people_domain.access import get_actor_employee
from task_domain.access import visible_tasks
from .access import visible_reviews, eligible_employees
from .models import PerformanceReview
from .serializers import ReviewSerializer, CreateReviewSerializer, UpdateReviewSerializer, CommandSerializer, ContextQuerySerializer, ReviewEmployeeSerializer, TaskContextSerializer
from .services import create_review, change_review
from .serializers import KPISourceSerializer

class ReviewViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ReviewSerializer
    queryset = PerformanceReview.objects.none()

    @extend_schema(parameters=[ContextQuerySerializer], responses=KPISourceSerializer)
    @action(detail=False, methods=["get"], url_path="kpi-source")
    def kpi_source(self, request):
        from .serializers import ContextQuerySerializer
        serializer = ContextQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        employee = serializer.validated_data["employee_uuid"]
        if not eligible_employees(request.user).filter(pk=employee).exists():
            raise PermissionDenied("Chỉ sao chép KPI của nhân sự trong Team phụ trách.")
        month = serializer.validated_data["month"]
        previous_month = (month.replace(day=1) - __import__("datetime").timedelta(days=1)).replace(day=1)
        previous = visible_reviews(request.user).filter(employee_id=employee, month=previous_month).first()
        return Response({"month": str(previous_month)[:7], "kpis": [{"title": k.title, "description": k.description, "weight": str(k.weight), "completion": None, "comment": ""} for k in previous.kpis.all()] if previous else []})
    def get_queryset(self):
        qs = visible_reviews(self.request.user)
        month = self.request.query_params.get("month")
        if month:
            from .serializers import MonthField
            qs = qs.filter(month=MonthField().run_validation(month))
        employee = self.request.query_params.get("employee_uuid")
        if employee:
            from rest_framework import serializers
            qs = qs.filter(employee_id=serializers.UUIDField().run_validation(employee))
        return qs
    @extend_schema(request=CreateReviewSerializer, responses={201: ReviewSerializer})
    def create(self, request):
        s = CreateReviewSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(self.get_serializer(create_review(request.user, **s.validated_data)).data, status=201)
    @extend_schema(request=UpdateReviewSerializer, responses=ReviewSerializer)
    def partial_update(self, request, pk=None):
        s = UpdateReviewSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(self.get_serializer(change_review(request.user, self.get_object(), s.validated_data)).data)
    def command(self, request, name):
        s = CommandSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(self.get_serializer(change_review(request.user, self.get_object(), s.validated_data, name)).data)
    @extend_schema(request=CommandSerializer, responses=ReviewSerializer)
    @action(detail=True, methods=["post"])
    def finalize(self, request, pk=None):
        return self.command(request, "finalize")
    @extend_schema(request=CommandSerializer, responses=ReviewSerializer)
    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        return self.command(request, "acknowledge")
    @extend_schema(request=CommandSerializer, responses=ReviewSerializer)
    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        return self.command(request, "reopen")

class ReviewOptionsView(APIView):
    @extend_schema(responses=ReviewEmployeeSerializer(many=True))
    def get(self, request):
        return Response([{ "uuid": str(e.pk), "display_name": e.display_name, "employee_code": e.employee_code, "team_name": e.team.name } for e in eligible_employees(request.user)])

class ReviewContextView(APIView):
    @extend_schema(parameters=[ContextQuerySerializer], responses=TaskContextSerializer(many=True))
    def get(self, request):
        get_actor_employee(request.user)
        s = ContextQuerySerializer(data=request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        employee_id = data["employee_uuid"]
        if not eligible_employees(request.user).filter(pk=employee_id).exists():
            raise PermissionDenied("Chỉ xem tham khảo Task của nhân sự được đánh giá.")
        month = data["month"]
        tasks = visible_tasks(request.user).filter(assignee_id=employee_id, due_at__year=month.year, due_at__month=month.month).order_by("due_at")
        return Response(TaskContextSerializer(tasks, many=True).data)
