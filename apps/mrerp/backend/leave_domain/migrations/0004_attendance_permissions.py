from django.db import migrations


def forwards(apps, schema_editor):
    ct, _ = apps.get_model("contenttypes", "ContentType").objects.get_or_create(app_label="leave_domain", model="attendancerecord")
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    for code, groups in {
        "import_attendance": ["People HR"],
        "view_own_actual_attendance": ["People Staff", "People Leader", "People HR", "People CEO"],
        "view_team_actual_attendance": ["People Leader"],
    }.items():
        permission, _ = Permission.objects.get_or_create(content_type=ct, codename=code, defaults={"name": code})
        for group in Group.objects.filter(name__in=groups):
            group.permissions.add(permission)


class Migration(migrations.Migration):
    dependencies = [("leave_domain", "0003_attendanceemployeemapping_attendanceimport_and_more")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
