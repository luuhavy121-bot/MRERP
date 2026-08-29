import json

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.file_storage import protected_file_response
from people_domain.access import get_actor_employee
from people_domain.models import Employee, Team, TeamLeadership
from people_domain.serializers import ApiErrorSerializer
from people_domain.views import require_capability

from .access import visible_documents
from .capabilities import MANAGE_ALL_DOCUMENTS, UPLOAD_DOCUMENTS, VIEW_DOCUMENTS
from .models import Document, DocumentFile
from .serializers import (
    DocumentAudienceOptionsSerializer,
    DocumentCreateSerializer,
    DocumentMultipartCreateSerializer,
    DocumentSerializer,
    DocumentVersionCreateSerializer,
    DocumentVersionMultipartSerializer,
    DocumentVersionSerializer,
)
from .services import add_document_version, archive_document, create_document, restore_document


def _json_list(value, field_name):
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValidationError({field_name: "Danh sách UUID không hợp lệ."}) from exc
    if not isinstance(parsed, list):
        raise ValidationError({field_name: "Danh sách UUID không hợp lệ."})
    return parsed


class DocumentAudienceOptionsView(APIView):
    """Scope audience choices so the UI cannot suggest invalid targets."""

    @extend_schema(responses={200: DocumentAudienceOptionsSerializer, 403: ApiErrorSerializer})
    def get(self, request):
        actor = get_actor_employee(request.user)
        require_capability(request.user, UPLOAD_DOCUMENTS)
        if request.user.has_perm(MANAGE_ALL_DOCUMENTS):
            teams = Team.objects.filter(is_active=True)
            employees = Employee.objects.filter(
                employment_status__in=[Employee.EmploymentStatus.PROBATION, Employee.EmploymentStatus.OFFICIAL]
            )
        else:
            led_team_ids = TeamLeadership.objects.filter(leader=actor).values_list("team_id", flat=True)
            teams = Team.objects.filter(is_active=True, pk__in=led_team_ids)
            employees = Employee.objects.filter(
                team_id__in=led_team_ids,
                employment_status__in=[Employee.EmploymentStatus.PROBATION, Employee.EmploymentStatus.OFFICIAL],
            )
        return Response({
            "teams": [{"uuid": str(team.pk), "code": team.code, "name": team.name} for team in teams.order_by("name")],
            "employees": [
                {
                    "uuid": str(employee.pk),
                    "employee_code": employee.employee_code,
                    "display_name": employee.display_name,
                    "team_name": employee.team.name if employee.team else None,
                }
                for employee in employees.select_related("team").order_by("display_name", "employee_code")
            ],
        })


class DocumentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Document.objects.none()
    serializer_class = DocumentSerializer

    def get_queryset(self):
        require_capability(self.request.user, VIEW_DOCUMENTS)
        include_archived = self.request.query_params.get("include_archived") == "true"
        return visible_documents(self.request.user, include_archived=include_archived)

    @extend_schema(request=DocumentMultipartCreateSerializer, responses={201: DocumentSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def create(self, request):
        get_actor_employee(request.user)
        require_capability(request.user, UPLOAD_DOCUMENTS)
        data = {
            "title": request.data.get("title", ""),
            "description": request.data.get("description", ""),
            "category": request.data.get("category", ""),
            "scope": request.data.get("scope", ""),
            "team_uuids": _json_list(request.data.get("team_uuids"), "team_uuids"),
            "employee_uuids": _json_list(request.data.get("employee_uuids"), "employee_uuids"),
            "note": request.data.get("note", ""),
        }
        serializer = DocumentCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        requested_team_uuids = values.pop("team_uuids")
        requested_employee_uuids = values.pop("employee_uuids")
        teams = list(Team.objects.filter(pk__in=requested_team_uuids, is_active=True))
        employees = list(Employee.objects.filter(pk__in=requested_employee_uuids))
        if len(teams) != len(set(requested_team_uuids)):
            raise ValidationError({"team_uuids": "Có Team không tồn tại hoặc đã ngừng hoạt động."})
        if len(employees) != len(set(requested_employee_uuids)):
            raise ValidationError({"employee_uuids": "Có nhân sự không tồn tại."})
        document = create_document(
            actor_user=request.user,
            teams=teams,
            employees=employees,
            uploaded_files=request.FILES.getlist("attachments"),
            **values,
        )
        return Response(DocumentSerializer(document, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=DocumentVersionMultipartSerializer, responses={201: DocumentVersionSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"])
    def versions(self, request, pk=None):
        document = self.get_object()
        serializer = DocumentVersionCreateSerializer(data={"note": request.data.get("note", "")})
        serializer.is_valid(raise_exception=True)
        version = add_document_version(
            actor_user=request.user,
            document=document,
            uploaded_files=request.FILES.getlist("attachments"),
            **serializer.validated_data,
        )
        return Response(DocumentVersionSerializer(version).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses={200: DocumentSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        document = self.get_object()
        return Response(DocumentSerializer(archive_document(actor_user=request.user, document=document), context={"request": request}).data)

    @extend_schema(request=None, responses={200: DocumentSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        require_capability(request.user, VIEW_DOCUMENTS)
        document = get_object_or_404(visible_documents(request.user, include_archived=True), pk=pk)
        return Response(DocumentSerializer(restore_document(actor_user=request.user, document=document), context={"request": request}).data)


class DocumentFileDownloadView(APIView):
    @extend_schema(responses={(200, "application/octet-stream"): bytes, 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    def get(self, request, file_uuid):
        get_actor_employee(request.user)
        require_capability(request.user, VIEW_DOCUMENTS)
        file = get_object_or_404(DocumentFile.objects.select_related("version__document"), pk=file_uuid)
        if not visible_documents(request.user).filter(pk=file.version.document_id).exists():
            raise PermissionDenied("Bạn không có quyền tải tài liệu này.")
        return protected_file_response(file.storage_key, file.original_name, file.content_type)
