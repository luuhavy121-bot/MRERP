import logging

from celery import shared_task
from django.utils import timezone

from .models import Recurrence
from .services import generate_due_occurrences


logger = logging.getLogger("mrerp.task_worker")


@shared_task(name="task_domain.process_recurrences")
def process_recurrences():
    total = 0
    failed = 0
    series_ids = list(
        Recurrence.objects.filter(
            status=Recurrence.Status.ACTIVE,
            next_occurrence_at__lte=timezone.now(),
        ).values_list("pk", flat=True)
    )
    for series_id in series_ids:
        try:
            total += generate_due_occurrences(Recurrence.objects.get(pk=series_id))
        except Exception:
            failed += 1
            logger.exception("Recurring task generation failed", extra={"recurrence_uuid": str(series_id)})
    return {"generated": total, "failed_series": failed}
