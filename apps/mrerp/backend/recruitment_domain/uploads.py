"""CV-only validation, isolated from other attachment policies."""
import uuid
import zipfile
from pathlib import Path
from django.conf import settings
from rest_framework.exceptions import ValidationError


def save_cv(upload):
    suffix = Path(upload.name).suffix.lower()
    mime = {".pdf": "application/pdf", ".doc": "application/msword", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if suffix not in mime or upload.size <= 0 or upload.size > 10 * 1024 * 1024:
        raise ValidationError({"cv": "CV phải là PDF, DOC hoặc DOCX, lớn hơn 0 byte và tối đa 10 MB."})
    if upload.content_type not in {mime[suffix], "application/octet-stream"}:
        raise ValidationError({"cv": "Loại nội dung CV không hợp lệ."})
    prefix = upload.read(8)
    upload.seek(0)
    valid = (suffix == ".pdf" and prefix.startswith(b"%PDF-")) or (suffix == ".doc" and prefix == bytes.fromhex("d0cf11e0a1b11ae1"))
    if suffix == ".docx":
        try:
            with zipfile.ZipFile(upload) as archive:
                valid = "word/document.xml" in archive.namelist() and "[Content_Types].xml" in archive.namelist()
        except (zipfile.BadZipFile, OSError):
            valid = False
        finally:
            upload.seek(0)
    if not valid:
        raise ValidationError({"cv": "Nội dung CV không khớp định dạng file."})
    key = f"recruitment/{uuid.uuid4().hex}{suffix}"
    target = Path(settings.MEDIA_ROOT) / key
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("xb") as out:
            for chunk in upload.chunks():
                out.write(chunk)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    name = upload.name.replace(chr(92), "/").split("/")[-1][:240]
    return {"original_name": name, "storage_key": key, "content_type": mime[suffix], "size": upload.size}
