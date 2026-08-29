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
            name="Candidate",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("full_name", models.CharField(max_length=160)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=32)),
                ("source", models.CharField(blank=True, max_length=120)),
                ("anonymized_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ["full_name"]},
        ),
        migrations.CreateModel(
            name="HiringRequest",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=160)),
                ("headcount", models.PositiveSmallIntegerField(default=1)),
                ("justification", models.TextField()),
                ("status", models.CharField(choices=[("pending", "Chờ duyệt"), ("approved", "Đã duyệt"), ("rejected", "Từ chối"), ("closed", "Đã đóng")], default="pending", max_length=16)),
                ("review_note", models.CharField(blank=True, max_length=500)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("requester", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="hiring_requests", to="people_domain.employee")),
                ("reviewer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="reviewed_hiring_requests", to=settings.AUTH_USER_MODEL)),
                ("team", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="hiring_requests", to="people_domain.team")),
            ],
            options={
                "ordering": ["-created_at"],
                "permissions": [("create_hiring_request", "Can create hiring requests"), ("approve_hiring_request", "Can approve hiring requests"), ("view_scoped_recruitment", "Can view recruitment in led teams"), ("view_company_recruitment", "Can view recruitment across company")],
            },
        ),
        migrations.CreateModel(
            name="JobOpening",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=160)),
                ("status", models.CharField(choices=[("open", "Đang tuyển"), ("closed", "Đã đóng")], default="open", max_length=16)),
                ("hiring_request", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="opening", to="recruitment_domain.hiringrequest")),
                ("team", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="job_openings", to="people_domain.team")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Application",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("stage", models.CharField(choices=[("new", "Mới"), ("screening", "Sàng lọc"), ("interview", "Phỏng vấn"), ("offer", "Đề nghị"), ("hired", "Đã tuyển"), ("rejected", "Từ chối")], default="new", max_length=16)),
                ("retention_until", models.DateTimeField(blank=True, null=True)),
                ("version", models.PositiveIntegerField(default=1)),
                ("candidate", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="applications", to="recruitment_domain.candidate")),
                ("converted_employee", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="source_application", to="people_domain.employee")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_applications", to=settings.AUTH_USER_MODEL)),
                ("opening", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="applications", to="recruitment_domain.jobopening")),
            ],
            options={"ordering": ["-created_at"], "permissions": [("manage_candidates", "Can manage candidates and application pipeline"), ("convert_candidate", "Can convert hired applications into employees")]},
        ),
        migrations.AddConstraint(model_name="application", constraint=models.UniqueConstraint(fields=("candidate", "opening"), name="unique_candidate_opening")),
        migrations.CreateModel(
            name="ApplicationTransition",
            fields=[
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("from_stage", models.CharField(choices=[("new", "Mới"), ("screening", "Sàng lọc"), ("interview", "Phỏng vấn"), ("offer", "Đề nghị"), ("hired", "Đã tuyển"), ("rejected", "Từ chối")], max_length=16)),
                ("to_stage", models.CharField(choices=[("new", "Mới"), ("screening", "Sàng lọc"), ("interview", "Phỏng vấn"), ("offer", "Đề nghị"), ("hired", "Đã tuyển"), ("rejected", "Từ chối")], max_length=16)),
                ("note", models.CharField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transitions", to="recruitment_domain.application")),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.CreateModel(
            name="CandidateAttachment",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("original_name", models.CharField(max_length=240)),
                ("storage_key", models.CharField(max_length=300, unique=True)),
                ("content_type", models.CharField(max_length=160)),
                ("size", models.PositiveBigIntegerField()),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="recruitment_domain.application")),
                ("uploaded_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["created_at"]},
        ),
    ]
