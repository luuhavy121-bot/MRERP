import hashlib
from collections import defaultdict
from datetime import date
from decimal import Decimal
from xml.etree.ElementTree import ParseError

from defusedxml.common import DefusedXmlException

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from people_domain.access import get_actor_employee
from people_domain.models import AuditEvent, Employee
from .attendance_parser import MAX_BYTES, METRICS, parse_workbook
from .models import AttendanceEmployeeMapping, AttendanceImport, AttendanceRecord
from .services import month_bounds

IMPORT = "leave_domain.import_attendance"
OWN = "leave_domain.view_own_actual_attendance"
TEAM = "leave_domain.view_team_actual_attendance"
COMPANY = "leave_domain.view_company_attendance"


class ImportConflict(APIException):
    status_code = 409
    default_detail = "Dữ liệu đã thay đổi. Hãy tải file để xem trước lại."
    default_code = "attendance_conflict"


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class CommitSerializer(serializers.Serializer):
    mappings = serializers.DictField(child=serializers.UUIDField())
    replace_existing = serializers.BooleanField(default=False)


class AttendanceResultSerializer(serializers.Serializer):
    month = serializers.CharField()
    employees = serializers.ListField(child=serializers.DictField())


class AttendanceImportResultSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    filename = serializers.CharField()
    month = serializers.CharField()
    created_at = serializers.DateTimeField()
    committed_at = serializers.DateTimeField(allow_null=True)
    row_count = serializers.IntegerField()
    replaced_count = serializers.IntegerField()
    imported_by = serializers.CharField()
    source = serializers.JSONField(required=False)
    mappings = serializers.DictField(required=False)
    employee_options = serializers.ListField(child=serializers.DictField(), required=False)
    existing_days = serializers.DictField(required=False)


def require_import(user):
    get_actor_employee(user)
    if not user.has_perm(IMPORT):
        raise PermissionDenied("Bạn không có quyền nhập bảng chấm công.")


def stamp(records):
    return {f"{r.employee_id}/{r.date.isoformat()}": r.version for r in records}


def import_summary(batch):
    return {"uuid": str(batch.pk), "filename": batch.filename, "month": batch.month.strftime("%Y-%m"),
            "created_at": batch.created_at, "committed_at": batch.committed_at,
            "row_count": batch.source["row_count"], "replaced_count": batch.replaced_count,
            "imported_by": batch.imported_by.get_username()}


def preview_payload(batch):
    result = import_summary(batch)
    result.update(source=batch.source, mappings=batch.mappings,
                  employee_options=[{"uuid": str(e.pk), "code": e.employee_code, "name": e.display_name,
                                     "team": e.team.name if e.team else "Chưa vào Team"}
                                    for e in Employee.objects.select_related("team").order_by("employee_code")])
    existing = defaultdict(list)
    for key in batch.baseline:
        employee, day = key.split("/")
        existing[employee].append(day)
    result["existing_days"] = dict(existing)
    return result


@transaction.atomic
def commit_batch(user, batch_uuid, mappings, replace_existing):
    require_import(user)
    batch = get_object_or_404(AttendanceImport.objects.select_for_update(), pk=batch_uuid, imported_by=user)
    if batch.committed_at:
        return batch  # retry is idempotent
    if batch.source["errors"]:
        raise ValidationError("File còn lỗi. Hãy sửa file nguồn rồi tải lại.")
    mappings = {k: str(v) for k, v in mappings.items()}
    codes = {e["code"] for e in batch.source["employees"]}
    if set(mappings) != codes or len(set(mappings.values())) != len(codes):
        raise ValidationError("Ghép mỗi mã với một nhân sự khác nhau, không bỏ sót mã.")
    # Lock Employee in stable order: serializes first inserts as well as replacement.
    employees = list(Employee.objects.select_for_update().filter(pk__in=mappings.values()).order_by("pk"))
    if len(employees) != len(codes):
        raise ValidationError("Nhân sự được chọn không tồn tại.")
    saved = AttendanceEmployeeMapping.objects.filter(Q(source_code__in=codes) | Q(employee_id__in=mappings.values()))
    for link in saved:
        if mappings.get(link.source_code) != str(link.employee_id):
            raise ImportConflict("Mã đã được ghép với nhân sự khác. Không thể đổi liên kết khi nhập.")
    start, end = month_bounds(batch.month.strftime("%Y-%m"))
    records = list(AttendanceRecord.objects.filter(employee_id__in=mappings.values(), date__range=(start, end)))
    current = stamp(records)
    expected = {k: v for k, v in batch.baseline.items() if k.split("/")[0] in mappings.values()}
    if current != expected:
        raise ImportConflict()
    by_key = {(str(r.employee_id), r.date.isoformat()): r for r in records}
    replacements = sum((mappings[e["code"]], row["date"]) in by_key
                       for e in batch.source["employees"] for row in e["rows"])
    if replacements and not replace_existing:
        raise ImportConflict("Có ngày đã nhập. Chọn xác nhận thay thế trước khi lưu.")
    for item in batch.source["employees"]:
        employee_id = mappings[item["code"]]
        AttendanceEmployeeMapping.objects.get_or_create(source_code=item["code"], defaults={"employee_id": employee_id})
        for row in item["rows"]:
            previous = by_key.get((employee_id, row["date"]))
            if previous:
                previous.data, previous.batch, previous.version = row, batch, previous.version + 1
                previous.save(update_fields=["data", "batch", "version", "updated_at"])
            else:
                AttendanceRecord.objects.create(employee_id=employee_id, date=row["date"], data=row, batch=batch)
    batch.mappings = mappings
    batch.committed_at = timezone.now()
    batch.replaced_count = replacements
    batch.save(update_fields=["mappings", "committed_at", "replaced_count", "updated_at"])
    AuditEvent.objects.create(actor=user, action="attendance.import.committed", target_type="AttendanceImport",
                              target_uuid=str(batch.pk), changes={"rows": batch.source["row_count"], "replaced": replacements})
    return batch


class ActualAttendanceViewSet(viewsets.ViewSet):
    @extend_schema(parameters=[OpenApiParameter("month", OpenApiTypes.STR, required=True)], responses=AttendanceResultSerializer)
    def list(self, request):
        actor = get_actor_employee(request.user)
        scope = Q(pk__in=[])
        if request.user.has_perm(COMPANY):
            scope = Q()
        else:
            if request.user.has_perm(OWN):
                scope |= Q(employee=actor)
            if request.user.has_perm(TEAM):
                scope |= Q(employee__team__leaderships__leader=actor)
            if not (request.user.has_perm(OWN) or request.user.has_perm(TEAM)):
                raise PermissionDenied("Bạn không có quyền xem bảng chấm công.")
        month = request.query_params.get("month", "")
        start, end = month_bounds(month)
        # A batch source can contain the whole company/month. Do not repeat that
        # JSON for every day in this read model; only its timestamp is needed.
        records = (AttendanceRecord.objects.filter(scope, date__range=(start, end))
                   .select_related("employee__team", "batch")
                   .defer("batch__source", "batch__baseline", "batch__mappings").distinct())
        grouped = {}
        for record in records:
            e = record.employee
            key = str(e.pk)
            if key not in grouped:
                grouped[key] = {"uuid": key, "code": e.employee_code, "name": e.display_name,
                                "team": e.team.name if e.team else "Chưa vào Team", "days": []}
            # Deliberate allow-list: source employee names/codes, importer and other employees never leak.
            grouped[key]["days"].append({**{k: record.data.get(k) for k in (*METRICS, "punches")},
                                         "date": record.date.isoformat(), "imported_at": record.batch.committed_at})
        for item in grouped.values():
            item["totals"] = {key: str(sum((Decimal(d[key]) for d in item["days"] if d[key] is not None), Decimal(0)))
                              if any(d[key] is not None for d in item["days"]) else None for key in METRICS}
            item["incomplete"] = any(d["workdays"] is None or d["hours"] is None for d in item["days"])
        return Response({"month": month, "employees": list(grouped.values())})


class AttendanceImportViewSet(viewsets.ViewSet):
    @extend_schema(responses=AttendanceImportResultSerializer(many=True))
    def list(self, request):
        require_import(request.user)
        batches = AttendanceImport.objects.filter(committed_at__isnull=False).select_related("imported_by")[:100]
        return Response([import_summary(b) for b in batches])

    @extend_schema(request=UploadSerializer, responses={201: AttendanceImportResultSerializer})
    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def preview(self, request):
        require_import(request.user)
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upload = serializer.validated_data["file"]
        if not upload.name.lower().endswith(".xlsx") or upload.size > MAX_BYTES:
            raise ValidationError("Chỉ nhận .xlsx tối đa 10 MB.")
        content = upload.read(MAX_BYTES + 1)
        try:
            parsed = parse_workbook(content)
        except (ParseError, DefusedXmlException, ValueError, TypeError, KeyError) as exc:
            raise ValidationError("File Excel hỏng hoặc cấu trúc không được hỗ trợ.") from exc
        start, end = month_bounds(parsed["month"])
        baseline = stamp(AttendanceRecord.objects.filter(date__range=(start, end)))
        mappings = {m.source_code: str(m.employee_id) for m in AttendanceEmployeeMapping.objects.filter(source_code__in=[e["code"] for e in parsed["employees"]])}
        batch = AttendanceImport.objects.create(filename=upload.name[:255], sha256=hashlib.sha256(content).hexdigest(),
                                               month=date.fromisoformat(parsed["month"] + "-01"), source=parsed,
                                               baseline=baseline, mappings=mappings, imported_by=request.user)
        return Response(preview_payload(batch), status=201)

    @extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.UUID, location=OpenApiParameter.PATH)], request=CommitSerializer, responses=AttendanceImportResultSerializer)
    @action(detail=True, methods=["post"])
    def commit(self, request, pk=None):
        require_import(request.user)
        serializer = CommitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            batch = commit_batch(request.user, pk, **serializer.validated_data)
        except IntegrityError as exc:
            raise ImportConflict() from exc
        return Response(import_summary(batch))
