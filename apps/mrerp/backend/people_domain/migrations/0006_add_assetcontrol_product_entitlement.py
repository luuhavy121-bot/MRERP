from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("people_domain", "0005_alter_employee_options_and_more")]

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
                    ("change_own_profile", "Can change allowed fields on own profile"),
                    ("change_own_password", "Can change own account password"),
                    ("provision_employee_account", "Can provision an account for an employee"),
                    ("manage_employee_account", "Can lock and unlock employee accounts"),
                    ("reset_employee_password", "Can reset employee account passwords"),
                    ("change_employment_status", "Can pause, terminate and reactivate employment"),
                    ("import_export_employee", "Can import and export employees"),
                    ("view_people_admin_panel", "Can view People access administration"),
                    ("manage_people_access", "Can manage People access bundles"),
                    ("access_assetcontrol", "Can access the ASSETCONTROL product"),
                ],
            },
        ),
    ]
