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
            name="Recognition",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("category", models.CharField(max_length=80)),
                ("message", models.TextField()),
                ("moderated_at", models.DateTimeField(blank=True, null=True)),
                ("moderated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="moderated_recognitions", to=settings.AUTH_USER_MODEL)),
                ("recipients", models.ManyToManyField(related_name="received_recognitions", to="people_domain.employee")),
                ("sender", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sent_recognitions", to="people_domain.employee")),
            ],
            options={"ordering": ["-created_at"], "permissions": [("view_rewards", "Can view recognition and leaderboards"), ("recognize_scoped", "Can recognize employees in led teams"), ("recognize_company", "Can recognize employees across company"), ("moderate_recognition", "Can moderate recognition")]},
        ),
        migrations.CreateModel(
            name="StarLedgerEntry",
            fields=[
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("amount", models.IntegerField()),
                ("entry_type", models.CharField(choices=[("grant", "Cấp sao"), ("adjustment", "Điều chỉnh")], max_length=16)),
                ("reason", models.CharField(max_length=500)),
                ("idempotency_key", models.CharField(blank=True, max_length=120, null=True, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="star_ledger_entries", to=settings.AUTH_USER_MODEL)),
                ("employee", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="star_ledger", to="people_domain.employee")),
            ],
            options={"ordering": ["-created_at"], "permissions": [("grant_stars_scoped", "Can grant stars in led teams"), ("grant_stars_company", "Can grant stars across company")]},
        ),
        migrations.AddConstraint(model_name="starledgerentry", constraint=models.CheckConstraint(condition=models.Q(("amount", 0), _negated=True), name="star_ledger_amount_nonzero")),
    ]
