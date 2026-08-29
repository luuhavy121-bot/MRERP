import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q

from people_domain.models import Employee, TimeStampedModel


class Recognition(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="sent_recognitions")
    recipients = models.ManyToManyField(Employee, related_name="received_recognitions")
    category = models.CharField(max_length=80)
    message = models.TextField()
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="moderated_recognitions",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("view_rewards", "Can view recognition and leaderboards"),
            ("recognize_scoped", "Can recognize employees in led teams"),
            ("recognize_company", "Can recognize employees across company"),
            ("moderate_recognition", "Can moderate recognition"),
        ]


class StarLedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        GRANT = "grant", "Cấp sao"
        ADJUSTMENT = "adjustment", "Điều chỉnh"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="star_ledger")
    amount = models.IntegerField()
    entry_type = models.CharField(max_length=16, choices=EntryType.choices)
    reason = models.CharField(max_length=500)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="star_ledger_entries")
    idempotency_key = models.CharField(max_length=120, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.CheckConstraint(condition=~Q(amount=0), name="star_ledger_amount_nonzero")]
        permissions = [
            ("grant_stars_scoped", "Can grant stars in led teams"),
            ("grant_stars_company", "Can grant stars across company"),
        ]
