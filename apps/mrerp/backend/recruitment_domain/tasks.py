from celery import shared_task

from .services import anonymize_expired_candidates


@shared_task(name="recruitment_domain.anonymize_expired_candidates")
def anonymize_expired_candidates_task():
    return anonymize_expired_candidates()
