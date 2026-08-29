from celery import shared_task

from .services import purge_expired_documents


@shared_task(name="documents_domain.purge_expired_documents")
def purge_expired_documents_task():
    return purge_expired_documents()
