from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("people_domain", "0002_optional_identity_and_flexible_employee_code"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="employee",
            options={
                "ordering": ["employee_code"],
                "permissions": [
                    ("view_company_directory", "Can view the company directory"),
                    ("view_hr_detail", "Can view HR-only employee details"),
                    ("promote_employee", "Can promote probation employees"),
                    ("promote_any_employee", "Can promote probation employees across the company"),
                    ("manage_organization", "Can manage departments and teams"),
                    ("manage_membership", "Can manage team membership and leadership"),
                    ("view_people_audit", "Can view People audit events"),
                ],
            },
        ),
    ]
