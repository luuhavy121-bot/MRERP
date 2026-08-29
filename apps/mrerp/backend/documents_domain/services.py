from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from config.file_storage import delete_stored_file, save_upload
from people_domain.models import Employee, Team, TeamLeadership
from people_domain.services import audit

from .access import can_manage_document
from .capabilities import MANAGE_ALL_DOCUMENTS
from .models import Document, DocumentFile, DocumentVersion


DOCUMENT_MAX_FILE_SIZE = 25 * 1024 * 1024
DOCUMENT_MAX_FILES = 10


def _validate_audience(*, actor_user, scope, teams, employees):
    actor = actor_user.employee_profile
    manage_all = actor_user.has_perm(MANAGE_ALL_DOCUMENTS)
    if scope in {Document.Scope.COMPANY, Document.Scope.HR_CONFIDENTIAL}:
        if not manage_all:
            raise PermissionDenied("Chỉ HR/CEO được phát hành tài liệu phạm vi này.")
        if teams or employees:
            raise ValidationError({"audience": "Phạm vi company/HR confidential không kết hợp audience khác."})
        return
    if scope == Document.Scope.TEAMS:
        if not teams:
            raise ValidationError({"team_uuids": "Chọn ít nhất một Team."})
        if not manage_all:
            led = set(TeamLeadership.objects.filter(leader=actor).values_list("team_id", flat=True))
            if any(team.pk not in led for team in teams):
                raise PermissionDenied("Leader chỉ được phát hành cho Team mình lãnh đạo.")
        if employees:
            raise ValidationError({"employee_uuids": "Audience Team không kết hợp Employee."})
        return
    if scope == Document.Scope.EMPLOYEES:
        if not employees:
            raise ValidationError({"employee_uuids": "Chọn ít nhất một nhân sự."})
        if not manage_all:
            led = set(TeamLeadership.objects.filter(leader=actor).values_list("team_id", flat=True))
            if any(employee.team_id not in led for employee in employees):
                raise PermissionDenied("Leader chỉ được phát hành cho nhân sự trong Team mình lãnh đạo.")
        if teams:
            raise ValidationError({"team_uuids": "Audience Employee không kết hợp Team."})
        return
    raise ValidationError({"scope": "Phạm vi tài liệu không hợp lệ."})


def _create_version(*, actor_user, document, uploaded_files, note):
    if not uploaded_files:
        raise ValidationError({"attachments": "Chọn ít nhất một file."})
    if len(uploaded_files) > DOCUMENT_MAX_FILES:
        raise ValidationError({"attachments": "Mỗi version có tối đa 10 file."})
    number = (document.versions.order_by("-number").values_list("number", flat=True).first() or 0) + 1
    version = DocumentVersion.objects.create(document=document, number=number, note=note.strip(), uploaded_by=actor_user)
    try:
        for uploaded_file in uploaded_files:
            metadata = save_upload(uploaded_file, "documents", max_file_size=DOCUMENT_MAX_FILE_SIZE)
            DocumentFile.objects.create(version=version, **metadata)
    except Exception:
        for file in version.files.all():
            delete_stored_file(file.storage_key)
        raise
    return version


def create_document(*, actor_user, title, description, category, scope, teams, employees, uploaded_files, note=""):
    _validate_audience(actor_user=actor_user, scope=scope, teams=teams, employees=employees)
    with transaction.atomic():
        document = Document.objects.create(
            title=title,
            description=description,
            category=category,
            owner=actor_user.employee_profile,
            scope=scope,
        )
        document.audience_teams.set(teams)
        document.audience_employees.set(employees)
        version = _create_version(actor_user=actor_user, document=document, uploaded_files=uploaded_files, note=note)
        audit(
            actor=actor_user,
            action="documents.document.created",
            target=document,
            changes={"scope": scope, "version": version.number, "file_count": version.files.count()},
        )
        return document


def add_document_version(*, actor_user, document, uploaded_files, note=""):
    if document.archived_at:
        raise ValidationError({"document": "Tài liệu đã được lưu trữ."})
    if not can_manage_document(actor_user, document):
        raise PermissionDenied("Bạn không có quyền thêm phiên bản cho tài liệu này.")
    with transaction.atomic():
        locked = Document.objects.select_for_update().get(pk=document.pk)
        version = _create_version(actor_user=actor_user, document=locked, uploaded_files=uploaded_files, note=note)
        locked.save(update_fields=["updated_at"])
        audit(
            actor=actor_user,
            action="documents.version.created",
            target=locked,
            changes={"version": version.number, "file_count": version.files.count()},
        )
        return version


def archive_document(*, actor_user, document):
    if not can_manage_document(actor_user, document):
        raise PermissionDenied("Bạn không có quyền lưu trữ tài liệu này.")
    if document.archived_at:
        return document
    document.archived_at = timezone.now()
    document.archived_by = actor_user
    document.save(update_fields=["archived_at", "archived_by", "updated_at"])
    audit(actor=actor_user, action="documents.document.archived", target=document, changes={"retention_days": 30})
    return document


def restore_document(*, actor_user, document):
    if not can_manage_document(actor_user, document):
        raise PermissionDenied("Bạn không có quyền khôi phục tài liệu này.")
    if not document.archived_at:
        return document
    document.archived_at = None
    document.archived_by = None
    document.save(update_fields=["archived_at", "archived_by", "updated_at"])
    audit(actor=actor_user, action="documents.document.restored", target=document)
    return document


def purge_expired_documents():
    cutoff = timezone.now() - timedelta(days=30)
    documents = list(Document.objects.filter(archived_at__lt=cutoff).prefetch_related("versions__files"))
    for document in documents:
        for version in document.versions.all():
            for file in version.files.all():
                delete_stored_file(file.storage_key)
        document.delete()
    return len(documents)
