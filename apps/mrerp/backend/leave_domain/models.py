import uuid as uuid_lib

from django.conf import settings
from django.db import models
from django.db.models import F, Q

from people_domain.models import Employee, Team, TimeStampedModel


class LeaveRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Chờ duyệt"
        APPROVED = "approved", "Đã duyệt"
        REJECTED = "rejected", "Từ chối"

    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    requester = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="leave_requests")
    requester_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="leave_requests",
        null=True,
        blank=True,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    start_period = models.CharField(max_length=2, choices=[("am", "Sáng"), ("pm", "Chiều")], default="am")
    end_period = models.CharField(max_length=2, choices=[("am", "Sáng"), ("pm", "Chiều")], default="pm")
    reason = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reviewed_leave_requests",
        null=True,
        blank=True,
    )
    review_note = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=Q(end_date__gte=F("start_date")), name="leave_end_on_or_after_start"),
            models.CheckConstraint(condition=Q(end_date__gt=F("start_date")) | Q(start_period="am") | Q(end_period="pm"), name="leave_period_order"),
        ]
        permissions = [
            ("submit_leave_request", "Can submit own leave request"),
            ("view_own_leave_request", "Can view own leave requests"),
            ("review_team_leave_request", "Can review leave requests in led teams"),
            ("view_company_attendance", "Can view company attendance projection"),
        ]

    def __str__(self):
        return f"{self.requester.employee_code}: {self.start_date}–{self.end_date}"


class PublicHoliday(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    date = models.DateField(unique=True)
    name = models.CharField(max_length=160)
    source = models.CharField(max_length=240, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.date}: {self.name}"


class AttendanceAdjustment(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="attendance_adjustments")
    month = models.DateField(help_text="Luôn là ngày đầu tháng.")
    days = models.SmallIntegerField(default=0)
    reason = models.CharField(max_length=500)
    adjusted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="attendance_adjustments",
    )

    class Meta:
        ordering = ["-month", "employee__employee_code"]
        constraints = [
            models.UniqueConstraint(fields=["employee", "month"], name="unique_attendance_adjustment_per_month"),
            models.CheckConstraint(condition=Q(days__gte=-31, days__lte=31), name="attendance_adjustment_days_range"),
        ]
        permissions = [
            ("adjust_company_attendance", "Can adjust company attendance projection"),
        ]

    def __str__(self):
        return f"{self.employee.employee_code} {self.month:%Y-%m}: {self.days:+d}"


class AttendanceImport(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    sha256 = models.CharField(max_length=64)
    month = models.DateField()
    source = models.JSONField()
    baseline = models.JSONField(default=dict)
    mappings = models.JSONField(default=dict)
    imported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    committed_at = models.DateTimeField(null=True)
    replaced_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]


class AttendanceEmployeeMapping(TimeStampedModel):
    source_code = models.CharField(max_length=64, unique=True)
    employee = models.OneToOneField(Employee, on_delete=models.PROTECT)


class AttendanceRecord(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    date = models.DateField()
    data = models.JSONField()
    batch = models.ForeignKey(AttendanceImport, on_delete=models.PROTECT)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["employee__employee_code", "date"]
        constraints = [models.UniqueConstraint(fields=["employee", "date"], name="unique_actual_attendance_day")]
        permissions = [
            ("import_attendance", "Can import HR attendance exports"),
            ("view_own_actual_attendance", "Can view own imported attendance"),
            ("view_team_actual_attendance", "Can view imported attendance in led teams"),
        ]
