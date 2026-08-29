import uuid

from django.conf import settings
from django.db import models

from people_domain.models import Employee, Team, TimeStampedModel


class HiringRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Chờ duyệt"
        APPROVED = "approved", "Đã duyệt"
        REJECTED = "rejected", "Từ chối"
        CLOSED = "closed", "Đã đóng"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="hiring_requests")
    title = models.CharField(max_length=160)
    headcount = models.PositiveSmallIntegerField(default=1)
    justification = models.TextField()
    requester = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="hiring_requests")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reviewed_hiring_requests",
        null=True,
        blank=True,
    )
    review_note = models.CharField(max_length=500, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("create_hiring_request", "Can create hiring requests"),
            ("approve_hiring_request", "Can approve hiring requests"),
            ("view_scoped_recruitment", "Can view recruitment in led teams"),
            ("view_company_recruitment", "Can view recruitment across company"),
        ]


class JobOpening(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Đang tuyển"
        CLOSED = "closed", "Đã đóng"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hiring_request = models.OneToOneField(
        HiringRequest,
        on_delete=models.PROTECT,
        related_name="opening",
    )
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="job_openings")
    title = models.CharField(max_length=160)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)

    class Meta:
        ordering = ["-created_at"]


class Candidate(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=160)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    source = models.CharField(max_length=120, blank=True)
    anonymized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["full_name"]


class Application(TimeStampedModel):
    class Stage(models.TextChoices):
        NEW = "new", "Mới"
        SCREENING = "screening", "Sàng lọc"
        INTERVIEW = "interview", "Phỏng vấn"
        OFFER = "offer", "Đề nghị"
        HIRED = "hired", "Đã tuyển"
        REJECTED = "rejected", "Từ chối"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.PROTECT, related_name="applications")
    opening = models.ForeignKey(JobOpening, on_delete=models.PROTECT, related_name="applications")
    stage = models.CharField(max_length=16, choices=Stage.choices, default=Stage.NEW)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_applications",
    )
    converted_employee = models.OneToOneField(
        Employee,
        on_delete=models.PROTECT,
        related_name="source_application",
        null=True,
        blank=True,
    )
    retention_until = models.DateTimeField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["candidate", "opening"], name="unique_candidate_opening"),
        ]
        permissions = [
            ("manage_candidates", "Can manage candidates and application pipeline"),
            ("convert_candidate", "Can convert hired applications into employees"),
        ]


class ApplicationTransition(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="transitions")
    from_stage = models.CharField(max_length=16, choices=Application.Stage.choices)
    to_stage = models.CharField(max_length=16, choices=Application.Stage.choices)
    note = models.CharField(max_length=500, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class CandidateAttachment(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="attachments")
    original_name = models.CharField(max_length=240)
    storage_key = models.CharField(max_length=300, unique=True)
    content_type = models.CharField(max_length=160)
    size = models.PositiveBigIntegerField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        ordering = ["created_at"]
