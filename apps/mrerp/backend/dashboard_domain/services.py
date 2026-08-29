from datetime import timedelta

from django.db import IntegrityError
from django.utils import timezone

from people_domain.models import Employee

from .models import Notification


def notify(*, recipient: Employee, kind: str, title: str, body: str, target_type: str, target_uuid=None, deduplication_key=None):
    if kind in {"feed", "recognition"}:
        from preferences_domain.models import NotificationPreference

        preference = NotificationPreference.objects.filter(employee=recipient).first()
        if preference is not None and not preference.social_notifications_enabled:
            return None
    try:
        return Notification.objects.create(
            recipient=recipient,
            kind=kind,
            title=title,
            body=body[:500],
            target_type=target_type,
            target_uuid=target_uuid,
            deduplication_key=deduplication_key,
        )
    except IntegrityError:
        return None


def notify_many(*, recipients, kind: str, title: str, body: str, target_type: str, target_uuid=None, key_prefix=None):
    for recipient in recipients:
        notify(
            recipient=recipient,
            kind=kind,
            title=title,
            body=body,
            target_type=target_type,
            target_uuid=target_uuid,
            deduplication_key=f"{key_prefix}:{recipient.pk}" if key_prefix else None,
        )


def retention_cutoff():
    return timezone.now() - timedelta(days=30)
