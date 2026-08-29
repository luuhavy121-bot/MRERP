import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("people_domain", "0005_alter_employee_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=180)),
                ("description", models.TextField(blank=True)),
                ("category", models.CharField(blank=True, max_length=80)),
                ("scope", models.CharField(choices=[("company", "Toàn công ty"), ("teams", "Team"), ("employees", "Nhân sự cụ thể"), ("hr_confidential", "HR confidential")], max_length=24)),
                ("archived_at", models.DateTimeField(blank=True, null=True)),
                ("archived_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="archived_documents", to=settings.AUTH_USER_MODEL)),
                ("audience_employees", models.ManyToManyField(blank=True, related_name="direct_documents", to="people_domain.employee")),
                ("audience_teams", models.ManyToManyField(blank=True, related_name="documents", to="people_domain.team")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="owned_documents", to="people_domain.employee")),
            ],
            options={
                "ordering": ["-updated_at"],
                "permissions": [("view_documents", "Can view documents in own audience"), ("upload_documents", "Can upload documents"), ("view_hr_confidential_documents", "Can view HR confidential documents"), ("manage_all_documents", "Can manage all documents")],
            },
        ),
        migrations.CreateModel(
            name="DocumentVersion",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("number", models.PositiveIntegerField()),
                ("note", models.CharField(blank=True, max_length=500)),
                ("document", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="versions", to="documents_domain.document")),
                ("uploaded_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-number"]},
        ),
        migrations.AddConstraint(model_name="documentversion", constraint=models.UniqueConstraint(fields=("document", "number"), name="unique_document_version_number")),
        migrations.CreateModel(
            name="DocumentFile",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("original_name", models.CharField(max_length=240)),
                ("storage_key", models.CharField(max_length=300, unique=True)),
                ("content_type", models.CharField(max_length=160)),
                ("size", models.PositiveBigIntegerField()),
                ("version", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="files", to="documents_domain.documentversion")),
            ],
            options={"ordering": ["created_at"]},
        ),
    ]
