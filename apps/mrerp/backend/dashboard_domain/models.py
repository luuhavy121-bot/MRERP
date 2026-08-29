import uuid

from django.db import models

from people_domain.models import Employee


class Notification(models.Model):
    class Kind(models.TextChoices):
        FEED = "feed", "Bảng tin"
        TASK = "task", "Công việc"
        GOAL = "goal", "Mục tiêu"
        LEAVE = "leave", "Nghỉ phép"
        ACCOUNT = "account", "Tài khoản"
        RECRUITMENT = "recruitment", "Tuyển dụng"
        DOCUMENT = "document", "Tài liệu"
        RECOGNITION = "recognition", "Ghi nhận"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    title = models.CharField(max_length=180)
    body = models.CharField(max_length=500, blank=True)
    target_type = models.CharField(max_length=40)
    target_uuid = models.UUIDField(null=True, blank=True)
    deduplication_key = models.CharField(max_length=160, unique=True, null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "read_at", "-created_at"])]

    @property
    def is_read(self):
        return self.read_at is not None


NOTIFICATION_KIND_CHOICES = Notification.Kind.choices
