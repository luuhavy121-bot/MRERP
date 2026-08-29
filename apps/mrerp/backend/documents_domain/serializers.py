from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Document, DocumentFile, DocumentVersion


class DocumentFileSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_download_url(self, file):
        return f"/api/v1/documents/files/{file.pk}/download/"

    class Meta:
        model = DocumentFile
        fields = ["uuid", "original_name", "content_type", "size", "download_url", "created_at"]
        read_only_fields = fields


class DocumentVersionSerializer(serializers.ModelSerializer):
    files = DocumentFileSerializer(many=True, read_only=True)
    uploaded_by_name = serializers.CharField(source="uploaded_by.employee_profile.display_name", read_only=True)

    class Meta:
        model = DocumentVersion
        fields = ["uuid", "number", "note", "uploaded_by_name", "files", "created_at"]
        read_only_fields = fields


class DocumentSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.display_name", read_only=True)
    scope_label = serializers.CharField(source="get_scope_display", read_only=True)
    audience_team_names = serializers.SlugRelatedField(source="audience_teams", slug_field="name", many=True, read_only=True)
    audience_employee_names = serializers.SlugRelatedField(source="audience_employees", slug_field="display_name", many=True, read_only=True)
    versions = DocumentVersionSerializer(many=True, read_only=True)
    can_manage = serializers.SerializerMethodField()
    is_archived = serializers.SerializerMethodField()

    @extend_schema_field(serializers.BooleanField())
    def get_can_manage(self, document):
        request = self.context.get("request")
        if not request:
            return False
        from .access import can_manage_document
        return can_manage_document(request.user, document)

    @extend_schema_field(serializers.BooleanField())
    def get_is_archived(self, document):
        return document.archived_at is not None

    class Meta:
        model = Document
        fields = [
            "uuid", "title", "description", "category", "owner", "owner_name", "scope",
            "scope_label", "audience_teams", "audience_team_names", "audience_employees",
            "audience_employee_names", "versions", "can_manage", "is_archived", "archived_at",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class DocumentCreateSerializer(serializers.Serializer):
    title = serializers.CharField(min_length=1, max_length=180, trim_whitespace=True)
    description = serializers.CharField(required=False, allow_blank=True, max_length=5000, trim_whitespace=True)
    category = serializers.CharField(required=False, allow_blank=True, max_length=80, trim_whitespace=True)
    scope = serializers.ChoiceField(choices=Document.Scope.choices)
    team_uuids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)
    employee_uuids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)
    note = serializers.CharField(required=False, allow_blank=True, max_length=500, trim_whitespace=True)


class DocumentVersionCreateSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, max_length=500, trim_whitespace=True)


class DocumentMultipartCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=180)
    description = serializers.CharField(required=False, allow_blank=True, max_length=5000)
    category = serializers.CharField(required=False, allow_blank=True, max_length=80)
    scope = serializers.ChoiceField(choices=Document.Scope.choices)
    team_uuids = serializers.CharField(required=False, help_text="JSON array UUID; dùng [] khi không áp dụng.")
    employee_uuids = serializers.CharField(required=False, help_text="JSON array UUID; dùng [] khi không áp dụng.")
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)
    attachments = serializers.ListField(child=serializers.FileField(), min_length=1, max_length=10)


class DocumentVersionMultipartSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)
    attachments = serializers.ListField(child=serializers.FileField(), min_length=1, max_length=10)


class DocumentAudienceTeamSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()


class DocumentAudienceEmployeeSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    employee_code = serializers.CharField()
    display_name = serializers.CharField()
    team_name = serializers.CharField(allow_null=True)


class DocumentAudienceOptionsSerializer(serializers.Serializer):
    teams = DocumentAudienceTeamSerializer(many=True)
    employees = DocumentAudienceEmployeeSerializer(many=True)
