import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [("people_domain", "0005_alter_employee_options_and_more")]

    operations = [
        migrations.CreateModel(
            name="NotificationPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("social_notifications_enabled", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("employee", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="notification_preference", to="people_domain.employee")),
            ],
            options={"permissions": [("manage_own_preferences", "Can manage own notification preferences")]},
        ),
    ]
