import uuid

from django.conf import settings
from django.db import models

from people_domain.models import Employee, Team, TimeStampedModel


class Document(TimeStampedModel):
    class Scope(models.TextChoices):
        COMPANY = "company", "Toàn công ty"
        TEAMS = "teams", "Team"
        EMPLOYEES = "employees", "Nhân sự cụ thể"
        HR_CONFIDENTIAL = "hr_confidential", "HR confidential"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=80, blank=True)
    owner = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="owned_documents")
    scope = models.CharField(max_length=24, choices=Scope.choices)
    audience_teams = models.ManyToManyField(Team, related_name="documents", blank=True)
    audience_employees = models.ManyToManyField(Employee, related_name="direct_documents", blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="archived_documents",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-updated_at"]
        permissions = [
            ("view_documents", "Can view documents in own audience"),
            ("view_company_documents", "Can view documents across company"),
            ("upload_documents", "Can upload documents"),
            ("view_hr_confidential_documents", "Can view HR confidential documents"),
            ("manage_all_documents", "Can manage all documents"),
        ]


class DocumentVersion(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions")
    number = models.PositiveIntegerField()
    note = models.CharField(max_length=500, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        ordering = ["-number"]
        constraints = [
            models.UniqueConstraint(fields=["document", "number"], name="unique_document_version_number"),
        ]


class DocumentFile(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE, related_name="files")
    original_name = models.CharField(max_length=240)
    storage_key = models.CharField(max_length=300, unique=True)
    content_type = models.CharField(max_length=160)
    size = models.PositiveBigIntegerField()

    class Meta:
        ordering = ["created_at"]


DOCUMENT_SCOPE_CHOICES = Document.Scope.choices
