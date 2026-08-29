from django.db.models import Avg, Case, IntegerField, Value, When
from rest_framework import serializers

from .models import Goal, Recurrence, Task, TaskAttachment


class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.display_name", read_only=True)
    download_url = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    def get_download_url(self, attachment) -> str:
        return f"/api/v1/tasks/attachments/{attachment.pk}/download/"

    def get_can_delete(self, attachment) -> bool:
        request = self.context.get("request")
        if not request:
            return False
        actor = request.user.employee_profile
        if attachment.kind == TaskAttachment.Kind.EVIDENCE:
            return attachment.uploaded_by_id == actor.pk and attachment.task.assignee_id == actor.pk
        if attachment.uploaded_by_id == actor.pk:
            return True
        from .access import manages_team
        return manages_team(request.user, attachment.task.team_id)

    class Meta:
        model = TaskAttachment
        fields = ["uuid", "kind", "original_name", "content_type", "size", "uploaded_by_name", "download_url", "can_delete", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source="creator.display_name", read_only=True)
    assignee_name = serializers.CharField(source="assignee.display_name", read_only=True)
    assignee_code = serializers.CharField(source="assignee.employee_code", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    goal_title = serializers.CharField(source="goal.title", read_only=True, allow_null=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    attachments = serializers.SerializerMethodField()
    can_submit = serializers.SerializerMethodField()
    can_review = serializers.SerializerMethodField()

    def get_attachments(self, task) -> list[dict]:
        return TaskAttachmentSerializer(task.attachments.filter(deleted_at__isnull=True), many=True, context=self.context).data

    def get_can_submit(self, task) -> bool:
        request = self.context.get("request")
        return bool(request and task.assignee_id == request.user.employee_profile.pk and task.status in {Task.Status.IN_PROGRESS, Task.Status.REWORK})

    def get_can_review(self, task) -> bool:
        request = self.context.get("request")
        if not request or task.status != Task.Status.PENDING_REVIEW or task.assignee_id == request.user.employee_profile.pk:
            return False
        from .access import manages_team
        return bool(request.user.has_perm("task_domain.accept_task") and manages_team(request.user, task.team_id))

    class Meta:
        model = Task
        fields = ["uuid", "title", "description", "creator", "creator_name", "assignee", "assignee_name", "assignee_code", "team", "team_name", "goal", "goal_title", "due_at", "progress", "status", "status_label", "review_note", "recurrence", "scheduled_for", "version", "attachments", "can_submit", "can_review", "created_at", "updated_at"]


class TaskCreateSerializer(serializers.Serializer):
    title = serializers.CharField(min_length=1, max_length=180)
    description = serializers.CharField(required=False, allow_blank=True, max_length=12000)
    assignee_uuid = serializers.UUIDField()
    due_at = serializers.DateTimeField()
    goal_uuid = serializers.UUIDField(required=False, allow_null=True)


class TaskUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(min_length=1, max_length=180, required=False)
    description = serializers.CharField(max_length=12000, allow_blank=True, required=False)
    due_at = serializers.DateTimeField(required=False)
    progress = serializers.IntegerField(min_value=0, max_value=100, required=False)
    goal_uuid = serializers.UUIDField(required=False, allow_null=True)


class TransitionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["submit", "accept", "rework"])
    note = serializers.CharField(required=False, allow_blank=True, max_length=4000)


class GoalSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source="created_by.display_name", read_only=True)
    progress = serializers.SerializerMethodField()
    task_count = serializers.IntegerField(source="tasks.count", read_only=True)

    def get_progress(self, goal) -> int:
        values = goal.tasks.aggregate(value=Avg(Case(When(status=Task.Status.COMPLETED, then=Value(100)), default="progress", output_field=IntegerField())))
        return round(values["value"] or 0)

    class Meta:
        model = Goal
        fields = ["uuid", "title", "description", "scope", "team", "team_name", "period", "starts_on", "ends_on", "created_by_name", "is_active", "progress", "task_count", "created_at", "updated_at"]


class GoalCreateSerializer(serializers.Serializer):
    title = serializers.CharField(min_length=1, max_length=180)
    description = serializers.CharField(required=False, allow_blank=True, max_length=12000)
    scope = serializers.ChoiceField(choices=Goal.Scope.choices)
    team_uuid = serializers.UUIDField(required=False, allow_null=True)
    period = serializers.ChoiceField(choices=Goal.Period.choices)
    starts_on = serializers.DateField()
    ends_on = serializers.DateField()

    def validate(self, attrs):
        if attrs["ends_on"] < attrs["starts_on"]:
            raise serializers.ValidationError({"ends_on": "Ngày kết thúc phải sau ngày bắt đầu."})
        return attrs


class GoalUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(min_length=1, max_length=180, required=False)
    description = serializers.CharField(allow_blank=True, max_length=12000, required=False)
    period = serializers.ChoiceField(choices=Goal.Period.choices, required=False)
    starts_on = serializers.DateField(required=False)
    ends_on = serializers.DateField(required=False)


class RecurrenceSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source="creator.display_name", read_only=True)
    assignee_name = serializers.CharField(source="assignee.display_name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    frequency_label = serializers.CharField(source="get_frequency_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Recurrence
        fields = ["uuid", "title", "description", "creator_name", "assignee", "assignee_name", "team", "team_name", "goal", "frequency", "frequency_label", "interval", "start_at", "next_occurrence_at", "deadline_offset_minutes", "end_date", "status", "status_label", "created_at"]


class RecurrenceCreateSerializer(serializers.Serializer):
    title = serializers.CharField(min_length=1, max_length=180)
    description = serializers.CharField(required=False, allow_blank=True, max_length=12000)
    assignee_uuid = serializers.UUIDField()
    goal_uuid = serializers.UUIDField(required=False, allow_null=True)
    frequency = serializers.ChoiceField(choices=Recurrence.Frequency.choices)
    interval = serializers.IntegerField(min_value=1, max_value=365)
    start_at = serializers.DateTimeField()
    deadline_offset_minutes = serializers.IntegerField(min_value=1, max_value=525600)
    end_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        end_date = attrs.get("end_date")
        if end_date and end_date < attrs["start_at"].date():
            raise serializers.ValidationError({"end_date": "Ngày dừng không được trước kỳ đầu tiên."})
        return attrs


class AttachmentUploadSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=TaskAttachment.Kind.choices)
