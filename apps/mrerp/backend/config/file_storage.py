"""Small, shared attachment validation and local-media storage service."""

import mimetypes
import os
import uuid
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from rest_framework.exceptions import ValidationError


MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_FILES_PER_PARENT = 5
ALLOWED_EXTENSIONS = {
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".png": {"image/png"},
    ".webp": {"image/webp"},
    ".gif": {"image/gif"},
    ".pdf": {"application/pdf"},
    ".txt": {"text/plain"},
    ".csv": {"text/csv", "application/vnd.ms-excel", "text/plain"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    ".xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    ".pptx": {"application/vnd.openxmlformats-officedocument.presentationml.presentation"},
    ".zip": {"application/zip", "application/x-zip-compressed"},
}
BLOCKED_PREFIXES = (b"<html", b"<!doctype html", b"<script", b"<?xml")


def _safe_name(name: str) -> str:
    value = Path(name).name.strip()
    if not value or value != name or ".." in name or "/" in name or "\\" in name:
        raise ValidationError({"attachments": "Tên file không hợp lệ."})
    return value[:240]


def validate_upload(uploaded_file, *, max_file_size=MAX_FILE_SIZE):
    original_name = _safe_name(uploaded_file.name)
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError({"attachments": f"Loại file {extension or '(không có đuôi)'} không được hỗ trợ."})
    if uploaded_file.size <= 0 or uploaded_file.size > max_file_size:
        limit_mb = max_file_size // (1024 * 1024)
        raise ValidationError({"attachments": f"Mỗi file phải lớn hơn 0 byte và không quá {limit_mb} MB."})
    declared = (uploaded_file.content_type or mimetypes.guess_type(original_name)[0] or "").lower()
    if declared not in ALLOWED_EXTENSIONS[extension]:
        raise ValidationError({"attachments": "MIME của file không khớp loại file được phép."})
    prefix = uploaded_file.read(512).lstrip().lower()
    uploaded_file.seek(0)
    if prefix.startswith(BLOCKED_PREFIXES) or b"<svg" in prefix:
        raise ValidationError({"attachments": "Nội dung HTML, script hoặc SVG không được phép."})
    if extension == ".pdf" and not prefix.startswith(b"%pdf-"):
        raise ValidationError({"attachments": "Nội dung PDF không hợp lệ."})
    if extension == ".png" and not prefix.startswith(b"\x89png\r\n\x1a\n"):
        raise ValidationError({"attachments": "Nội dung PNG không hợp lệ."})
    if extension in {".jpg", ".jpeg"} and not prefix.startswith(b"\xff\xd8\xff"):
        raise ValidationError({"attachments": "Nội dung JPEG không hợp lệ."})
    if extension in {".zip", ".docx", ".xlsx", ".pptx"} and not prefix.startswith(b"pk"):
        raise ValidationError({"attachments": "Nội dung ZIP/Office không hợp lệ."})
    if extension == ".gif" and not prefix.startswith((b"gif87a", b"gif89a")):
        raise ValidationError({"attachments": "Nội dung GIF không hợp lệ."})
    if extension == ".webp" and not (prefix.startswith(b"riff") and prefix[8:12] == b"webp"):
        raise ValidationError({"attachments": "Nội dung WebP không hợp lệ."})
    if extension in {".txt", ".csv"} and b"\x00" in prefix:
        raise ValidationError({"attachments": "File văn bản chứa dữ liệu nhị phân không hợp lệ."})
    return original_name, extension, declared


def save_upload(uploaded_file, namespace: str, *, max_file_size=MAX_FILE_SIZE) -> dict:
    original_name, extension, content_type = validate_upload(uploaded_file, max_file_size=max_file_size)
    relative_path = Path(namespace) / f"{uuid.uuid4().hex}{extension}"
    absolute_path = Path(settings.MEDIA_ROOT) / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    with absolute_path.open("xb") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return {
        "original_name": original_name,
        "storage_key": relative_path.as_posix(),
        "content_type": content_type,
        "size": uploaded_file.size,
    }


def delete_stored_file(storage_key: str):
    media_root = Path(settings.MEDIA_ROOT)
    root = media_root.resolve()
    target = (media_root / storage_key).resolve()
    if root not in target.parents:
        return
    try:
        os.remove(target)
    except FileNotFoundError:
        pass


def protected_file_response(storage_key: str, original_name: str, content_type: str):
    media_root = Path(settings.MEDIA_ROOT)
    root = media_root.resolve()
    target = (media_root / storage_key).resolve()
    if root not in target.parents or not target.is_file():
        raise FileNotFoundError(storage_key)
    response = FileResponse(target.open("rb"), content_type=content_type, as_attachment=True, filename=original_name)
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response
