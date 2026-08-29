from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from config.file_storage import delete_stored_file

from .models import Notification
from .services import notify, retention_cutoff


@shared_task(name="dashboard_domain.emit_deadline_notifications")
def emit_deadline_notifications():
    from task_domain.models import Task

    now = timezone.now()
    soon = now + timedelta(hours=24)
    tasks = Task.objects.filter(due_at__lte=soon, status__in=[Task.Status.IN_PROGRESS, Task.Status.REWORK]).select_related("assignee")
    for task in tasks:
        overdue = task.due_at < now
        notify(
            recipient=task.assignee,
            kind=Notification.Kind.TASK,
            title="Công việc đã quá hạn" if overdue else "Công việc sắp đến hạn",
            body=task.title,
            target_type="task",
            target_uuid=task.pk,
            deduplication_key=f"task-deadline:{task.pk}:{'overdue' if overdue else task.due_at.date()}",
        )


@shared_task(name="dashboard_domain.purge_expired_data")
def purge_expired_data():
    cutoff = retention_cutoff()
    Notification.objects.filter(created_at__lt=cutoff).delete()
    from feed_domain.models import PostAttachment
    from task_domain.models import TaskAttachment

    for model in (PostAttachment, TaskAttachment):
        expired = list(model.objects.filter(deleted_at__lt=cutoff).only("pk", "storage_key"))
        for attachment in expired:
            delete_stored_file(attachment.storage_key)
            attachment.delete()
