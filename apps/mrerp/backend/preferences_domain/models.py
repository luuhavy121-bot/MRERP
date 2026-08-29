from django.db import models

from people_domain.models import Employee


class NotificationPreference(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="notification_preference",
    )
    social_notifications_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("manage_own_preferences", "Can manage own notification preferences"),
        ]
