from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from config.file_storage import protected_file_response
from people_domain.access import get_actor_employee
from people_domain.models import Employee, Team
from people_domain.serializers import ApiErrorSerializer
from people_domain.views import require_capability

from .access import visible_goals, visible_recurrences, visible_tasks
from .capabilities import CREATE_TASK, MANAGE_RECURRENCES, VIEW_TASK
from .models import Goal, Recurrence, Task, TaskAttachment
from .serializers import AttachmentUploadSerializer, GoalCreateSerializer, GoalSerializer, GoalUpdateSerializer, RecurrenceCreateSerializer, RecurrenceSerializer, TaskAttachmentSerializer, TaskCreateSerializer, TaskSerializer, TaskUpdateSerializer, TransitionSerializer
from .services import add_task_attachment, create_goal, create_task, generate_due_occurrences, soft_delete_task_attachment, transition_task, update_task


class TaskViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Task.objects.none()
    serializer_class = TaskSerializer

    def get_queryset(self):
        # Keep freshly-created work visible on the first page even after the
        # local/demo database has accumulated completed occurrences.
        return visible_tasks(self.request.user).select_related("creator", "assignee", "team", "goal", "recurrence").prefetch_related("attachments").order_by("-created_at")

    @extend_schema(request=TaskCreateSerializer, responses={201: TaskSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def create(self, request):
        require_capability(request.user, CREATE_TASK)
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        assignee = get_object_or_404(Employee, pk=data.pop("assignee_uuid"), employment_status__in=[Employee.EmploymentStatus.PROBATION, Employee.EmploymentStatus.OFFICIAL])
        goal_uuid = data.pop("goal_uuid", None)
        goal = get_object_or_404(visible_goals(request.user), pk=goal_uuid) if goal_uuid else None
        task = create_task(actor=request.user, assignee=assignee, goal=goal, **data)
        return Response(TaskSerializer(task, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=TaskUpdateSerializer, responses={200: TaskSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def partial_update(self, request, pk=None):
        task = self.get_object()
        serializer = TaskUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        if "goal_uuid" in data:
            goal_uuid = data.pop("goal_uuid")
            data["goal"] = get_object_or_404(visible_goals(request.user), pk=goal_uuid) if goal_uuid else None
        updated = update_task(actor=request.user, task=task, validated_data=data)
        return Response(TaskSerializer(updated, context={"request": request}).data)

    @extend_schema(request=TransitionSerializer, responses={200: TaskSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        task = self.get_object()
        serializer = TransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = transition_task(actor=request.user, task=task, **serializer.validated_data)
        return Response(TaskSerializer(updated, context={"request": request}).data)

    @extend_schema(request=AttachmentUploadSerializer, responses={201: TaskAttachmentSerializer(many=True), 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def attachments(self, request, pk=None):
        task = self.get_object()
        serializer = AttachmentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploads = request.FILES.getlist("attachments")
        if not uploads:
            raise ValidationError({"attachments": "Hãy chọn ít nhất một file."})
        created = add_task_attachment(actor=request.user, task=task, uploads=uploads, **serializer.validated_data)
        return Response(TaskAttachmentSerializer(created, many=True).data, status=status.HTTP_201_CREATED)


class GoalViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Goal.objects.none()
    serializer_class = GoalSerializer

    def get_queryset(self):
        get_actor_employee(self.request.user)
        return visible_goals(self.request.user).select_related("team", "created_by").prefetch_related("tasks").order_by("-created_at")

    @extend_schema(request=GoalCreateSerializer, responses={201: GoalSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def create(self, request):
        serializer = GoalCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        team_uuid = data.pop("team_uuid", None)
        team = get_object_or_404(Team, pk=team_uuid, is_active=True) if team_uuid else None
        goal = create_goal(actor=request.user, team=team, **data)
        return Response(GoalSerializer(goal).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=GoalUpdateSerializer, responses={200: GoalSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def partial_update(self, request, pk=None):
        goal = self.get_object()
        if goal.scope == Goal.Scope.COMPANY:
            if not request.user.has_perm("task_domain.manage_company_goals"):
                raise PermissionDenied("Chỉ CEO sửa mục tiêu công ty.")
        elif not request.user.has_perm("task_domain.manage_goals"):
            raise PermissionDenied("Bạn không có capability sửa mục tiêu Team.")
        serializer = GoalUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        allowed = {"title", "description", "period", "starts_on", "ends_on"}
        candidate_start = serializer.validated_data.get("starts_on", goal.starts_on)
        candidate_end = serializer.validated_data.get("ends_on", goal.ends_on)
        if candidate_end < candidate_start:
            raise ValidationError({"ends_on": "Ngày kết thúc phải sau ngày bắt đầu."})
        for field, value in serializer.validated_data.items():
            if field in allowed:
                setattr(goal, field, value)
        goal.save()
        from people_domain.services import audit
        audit(actor=request.user, action="goal.updated", target=goal, changes={"fields": sorted(set(serializer.validated_data) & allowed)})
        from dashboard_domain.models import Notification
        from dashboard_domain.services import notify_many
        recipients = Employee.objects.all() if goal.scope == Goal.Scope.COMPANY else Employee.objects.filter(team=goal.team)
        notify_many(recipients=recipients.exclude(pk=request.user.employee_profile.pk), kind=Notification.Kind.GOAL, title="Mục tiêu đã thay đổi", body=goal.title, target_type="goal", target_uuid=goal.pk, key_prefix=f"goal-updated:{goal.pk}:{goal.updated_at.isoformat()}")
        return Response(GoalSerializer(goal).data)


class RecurrenceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Recurrence.objects.none()
    serializer_class = RecurrenceSerializer

    def get_queryset(self):
        get_actor_employee(self.request.user)
        return visible_recurrences(self.request.user).select_related("creator", "assignee", "team", "goal")

    @extend_schema(request=RecurrenceCreateSerializer, responses={201: RecurrenceSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def create(self, request):
        require_capability(request.user, MANAGE_RECURRENCES)
        serializer = RecurrenceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        assignee = get_object_or_404(Employee, pk=data.pop("assignee_uuid"))
        from .services import validate_assignment, validate_goal_task
        validate_assignment(request.user, assignee)
        if not assignee.team_id:
            raise ValidationError({"assignee_uuid": "Người nhận phải thuộc Team."})
        goal_uuid = data.pop("goal_uuid", None)
        goal = get_object_or_404(visible_goals(request.user), pk=goal_uuid) if goal_uuid else None
        from datetime import timedelta
        validate_goal_task(goal, team_id=assignee.team_id, due_at=data["start_at"] + timedelta(minutes=data["deadline_offset_minutes"]))
        if goal and (not data.get("end_date") or data["end_date"] > goal.ends_on):
            raise ValidationError({"end_date": "Lịch gắn Goal phải có ngày dừng trong timebox của Goal."})
        recurrence = Recurrence.objects.create(creator=request.user.employee_profile, assignee=assignee, team_id=assignee.team_id, goal=goal, next_occurrence_at=data["start_at"], anchor_day=data["start_at"].day if data["frequency"] == Recurrence.Frequency.MONTHLY else None, **data)
        from people_domain.services import audit
        audit(actor=request.user, action="task.recurrence.created", target=recurrence, changes={"frequency": recurrence.frequency, "interval": recurrence.interval, "assignee": str(assignee.pk)})
        generate_due_occurrences(recurrence)
        recurrence.refresh_from_db()
        return Response(RecurrenceSerializer(recurrence).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        return self._set_status(request, self.get_object(), Recurrence.Status.PAUSED)

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        recurrence = self.get_object()
        if recurrence.status == Recurrence.Status.STOPPED:
            raise ValidationError({"status": "Lịch đã dừng không thể chạy lại."})
        return self._set_status(request, recurrence, Recurrence.Status.ACTIVE)

    @action(detail=True, methods=["post"])
    def stop(self, request, pk=None):
        return self._set_status(request, self.get_object(), Recurrence.Status.STOPPED)

    def _set_status(self, request, recurrence, value):
        require_capability(request.user, MANAGE_RECURRENCES)
        if recurrence.creator_id != request.user.employee_profile.pk and not request.user.has_perm("task_domain.view_company_tasks"):
            raise PermissionDenied("Chỉ người tạo hoặc CEO quản lý lịch lặp này.")
        recurrence.status = value
        recurrence.save(update_fields=["status", "updated_at"])
        from people_domain.services import audit
        audit(actor=request.user, action=f"task.recurrence.{value}", target=recurrence, changes={"status": value})
        if value == Recurrence.Status.ACTIVE:
            generate_due_occurrences(recurrence)
        return Response(RecurrenceSerializer(recurrence).data)


class TaskAttachmentDetailView(APIView):
    @extend_schema(request=None, responses={204: None, 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    def delete(self, request, attachment_uuid):
        attachment = TaskAttachment.objects.select_related("task", "uploaded_by").filter(pk=attachment_uuid, task__in=visible_tasks(request.user), deleted_at__isnull=True).first()
        if attachment is None:
            raise Http404
        soft_delete_task_attachment(actor=request.user, attachment=attachment)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskAttachmentDownloadView(APIView):
    @extend_schema(responses={(200, "application/octet-stream"): OpenApiResponse(description="Protected task attachment"), 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    def get(self, request, attachment_uuid):
        attachment = TaskAttachment.objects.select_related("task").filter(pk=attachment_uuid, task__in=visible_tasks(request.user), deleted_at__isnull=True).first()
        if attachment is None:
            raise Http404
        try:
            return protected_file_response(attachment.storage_key, attachment.original_name, attachment.content_type)
        except FileNotFoundError as exc:
            raise Http404 from exc
