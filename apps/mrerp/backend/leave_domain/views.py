from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from people_domain.access import get_actor_employee
from people_domain.serializers import ApiErrorSerializer
from people_domain.views import require_capability

from .access import visible_leave_queryset
from .capabilities import ADJUST_COMPANY_ATTENDANCE, SUBMIT_LEAVE, VIEW_COMPANY_ATTENDANCE, VIEW_OWN_LEAVE
from .models import LeaveRequest
from .serializers import (
    AttendanceAdjustmentSerializer,
    AttendanceRowSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestSerializer,
    LeaveRequestUpdateSerializer,
    LeaveReviewSerializer,
    LeaveCalendarSerializer,
)
from .services import adjust_attendance, attendance_projection, create_leave_request, review_leave_request, update_leave_request


class LeaveRequestViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = LeaveRequest.objects.none()
    serializer_class = LeaveRequestSerializer

    @extend_schema(parameters=[OpenApiParameter("month", OpenApiTypes.STR, required=True)], responses=LeaveCalendarSerializer(many=True))
    @action(detail=False, methods=["get"])
    def calendar(self, request):
        from .services import month_bounds
        start, end = month_bounds(request.query_params.get("month", ""))
        rows = self.get_queryset().filter(status="approved", start_date__lte=end, end_date__gte=start)
        # A dedicated projection deliberately excludes leave reasons and review notes.
        return Response([{"uuid": str(item.pk), "name": item.requester.display_name,
            "employee_code": item.requester.employee_code, "team_name": item.requester_team.name if item.requester_team else None,
            "start_date": item.start_date, "end_date": item.end_date,
            "start_period": item.start_period, "end_period": item.end_period} for item in rows])

    def get_queryset(self):
        require_capability(self.request.user, VIEW_OWN_LEAVE)
        return visible_leave_queryset(self.request.user)

    @extend_schema(request=LeaveRequestCreateSerializer, responses={201: LeaveRequestSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def create(self, request):
        require_capability(request.user, SUBMIT_LEAVE)
        serializer = LeaveRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_request = create_leave_request(actor=request.user, **serializer.validated_data)
        return Response(LeaveRequestSerializer(leave_request, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=LeaveRequestUpdateSerializer, responses={200: LeaveRequestSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    def partial_update(self, request, pk=None):
        leave_request = self.get_object()
        serializer = LeaveRequestUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = update_leave_request(actor=request.user, leave_request=leave_request, **serializer.validated_data)
        return Response(LeaveRequestSerializer(updated, context={"request": request}).data)

    @extend_schema(request=LeaveReviewSerializer, responses={200: LeaveRequestSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        leave_request = self.get_object()
        serializer = LeaveReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = review_leave_request(actor=request.user, leave_request=leave_request, **serializer.validated_data)
        return Response(LeaveRequestSerializer(updated, context={"request": request}).data)


class AttendanceViewSet(viewsets.ViewSet):
    @extend_schema(
        parameters=[OpenApiParameter("month", OpenApiTypes.STR, required=True, description="Tháng định dạng YYYY-MM.")],
        responses={200: AttendanceRowSerializer(many=True), 400: ApiErrorSerializer, 403: ApiErrorSerializer},
    )
    def list(self, request):
        get_actor_employee(request.user)
        if not request.user.has_perm(VIEW_COMPANY_ATTENDANCE):
            raise PermissionDenied("Bạn không có capability xem bảng công toàn công ty.")
        rows = attendance_projection(request.query_params.get("month", ""))
        return Response(AttendanceRowSerializer(rows, many=True).data)

    @extend_schema(request=AttendanceAdjustmentSerializer, responses={200: AttendanceRowSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=False, methods=["post"], url_path="adjust")
    def adjust(self, request):
        get_actor_employee(request.user)
        if not request.user.has_perm(ADJUST_COMPANY_ATTENDANCE):
            raise PermissionDenied("Bạn không có capability điều chỉnh bảng công.")
        serializer = AttendanceAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        row = adjust_attendance(actor=request.user, **serializer.validated_data)
        return Response(AttendanceRowSerializer(row).data)
