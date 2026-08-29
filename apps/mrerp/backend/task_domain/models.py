import uuid

from django.db import models
from django.db.models import Q

from people_domain.models import Employee, Team, TimeStampedModel


class Goal(TimeStampedModel):
    class Scope(models.TextChoices):
        TEAM = "team", "Team"
        COMPANY = "company", "Công ty"

    class Period(models.TextChoices):
        DAY = "day", "Ngày"
        WEEK = "week", "Tuần"
        MONTH = "month", "Tháng"
        QUARTER = "quarter", "Quý"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    scope = models.CharField(max_length=12, choices=Scope.choices)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="goals", null=True, blank=True)
    period = models.CharField(max_length=12, choices=Period.choices)
    starts_on = models.DateField()
    ends_on = models.DateField()
    created_by = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="created_goals")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-starts_on", "title"]
        constraints = [
            models.CheckConstraint(condition=Q(ends_on__gte=models.F("starts_on")), name="goal_end_on_or_after_start"),
        ]
        permissions = [
            ("manage_goals", "Can manage goals for led teams"),
            ("manage_company_goals", "Can manage company and all team goals"),
        ]


class Recurrence(TimeStampedModel):
    class Frequency(models.TextChoices):
        DAILY = "daily", "Hằng ngày"
        WEEKLY = "weekly", "Hằng tuần"
        MONTHLY = "monthly", "Hằng tháng"

    class Status(models.TextChoices):
        ACTIVE = "active", "Đang chạy"
        PAUSED = "paused", "Tạm dừng"
        STOPPED = "stopped", "Đã dừng"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="created_recurrences")
    assignee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="assigned_recurrences")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="recurrences")
    goal = models.ForeignKey(Goal, on_delete=models.PROTECT, related_name="recurrences", null=True, blank=True)
    frequency = models.CharField(max_length=12, choices=Frequency.choices)
    interval = models.PositiveSmallIntegerField(default=1)
    start_at = models.DateTimeField()
    next_occurrence_at = models.DateTimeField()
    anchor_day = models.PositiveSmallIntegerField(null=True, blank=True)
    deadline_offset_minutes = models.PositiveIntegerField(default=1440)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["-created_at"]
        permissions = [("manage_recurrences", "Can manage recurring task series")]


class Task(TimeStampedModel):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "Đang thực hiện"
        PENDING_REVIEW = "pending_review", "Chờ xác nhận"
        COMPLETED = "completed", "Đã hoàn thành"
        REWORK = "rework", "Yêu cầu làm lại"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="created_tasks")
    assignee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="assigned_tasks")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="tasks")
    goal = models.ForeignKey(Goal, on_delete=models.PROTECT, related_name="tasks", null=True, blank=True)
    due_at = models.DateTimeField()
    progress = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    review_note = models.TextField(blank=True)
    accepted_by = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="accepted_tasks", null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    recurrence = models.ForeignKey(Recurrence, on_delete=models.PROTECT, related_name="occurrences", null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["status", "due_at"]
        constraints = [
            models.CheckConstraint(condition=Q(progress__gte=0, progress__lte=100), name="task_progress_0_100"),
            models.UniqueConstraint(fields=["recurrence", "scheduled_for"], condition=Q(recurrence__isnull=False), name="unique_recurrence_occurrence"),
        ]
        permissions = [
            ("update_task_progress", "Can update assigned task progress"),
            ("accept_task", "Can accept or request rework"),
            ("view_team_tasks", "Can view tasks in led teams"),
            ("view_company_tasks", "Can view company tasks"),
        ]


class TaskAttachment(TimeStampedModel):
    class Kind(models.TextChoices):
        BRIEF = "brief", "Yêu cầu"
        EVIDENCE = "evidence", "Kết quả"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    uploaded_by = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="task_attachments")
    kind = models.CharField(max_length=12, choices=Kind.choices)
    original_name = models.CharField(max_length=240)
    storage_key = models.CharField(max_length=300, unique=True)
    content_type = models.CharField(max_length=160)
    size = models.PositiveBigIntegerField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]


GOAL_SCOPE_CHOICES = Goal.Scope.choices
TASK_ATTACHMENT_KIND_CHOICES = TaskAttachment.Kind.choices
