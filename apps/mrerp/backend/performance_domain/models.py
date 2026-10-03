import uuid
from django.conf import settings
from django.db import models
from people_domain.models import TimeStampedModel


class PerformanceReview(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Bản nháp"
        FINALIZED = "finalized", "Đã chốt"
        ACKNOWLEDGED = "acknowledged", "Đã xác nhận"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey("people_domain.Employee", on_delete=models.PROTECT, related_name="performance_reviews")
    team = models.ForeignKey("people_domain.Team", on_delete=models.PROTECT)
    leader = models.ForeignKey("people_domain.Employee", on_delete=models.PROTECT, related_name="authored_reviews")
    month = models.DateField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    leader_comment = models.TextField(blank=True)
    employee_feedback = models.TextField(blank=True)
    finalized_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    class Meta:
        ordering = ["-month", "employee__employee_code"]
        constraints = [models.UniqueConstraint(fields=["employee", "month"], name="unique_employee_review_month")]
        permissions = [("manage_team_reviews", "Create and score reviews in led teams"), ("view_company_reviews", "Read company performance reviews"), ("reopen_reviews", "Reopen finalized reviews"), ("view_own_reviews", "Read and acknowledge own finalized reviews")]


class PerformanceKPI(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(PerformanceReview, on_delete=models.CASCADE, related_name="kpis")
    position = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    completion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    comment = models.TextField(blank=True)
    class Meta:
        ordering = ["position", "uuid"]
        constraints = [models.CheckConstraint(condition=models.Q(weight__gte=0, weight__lte=100), name="kpi_weight_range"), models.CheckConstraint(condition=models.Q(completion__isnull=True) | models.Q(completion__gte=0, completion__lte=100), name="kpi_completion_range")]


class PerformanceReviewRevision(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(PerformanceReview, on_delete=models.PROTECT, related_name="revisions")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    event = models.CharField(max_length=20)
    reason = models.CharField(max_length=1000, blank=True)
    snapshot = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["created_at"]
