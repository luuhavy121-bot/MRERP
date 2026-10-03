from django.db import migrations


def forwards(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    ct, _ = ContentType.objects.get_or_create(app_label="performance_domain", model="performancereview")
    mapping = {"view_own_reviews": ["People Staff", "People Leader", "People HR", "People CEO"], "manage_team_reviews": ["People Leader"], "view_company_reviews": ["People HR", "People CEO"], "reopen_reviews": ["People HR", "People CEO"]}
    for code, groups in mapping.items():
        permission, _ = Permission.objects.get_or_create(content_type=ct, codename=code, defaults={"name": code})
        for group in Group.objects.filter(name__in=groups):
            group.permissions.add(permission)
    ct, _ = ContentType.objects.get_or_create(app_label="recruitment_domain", model="application")
    permission, _ = Permission.objects.get_or_create(content_type=ct, codename="manage_candidates", defaults={"name": "Can manage candidates and application pipeline"})
    for group in Group.objects.filter(name="People Leader"):
        group.permissions.add(permission)


class Migration(migrations.Migration):
    dependencies = [("performance_domain", "0001_initial"), ("recruitment_domain", "0002_application_consent_at_application_introduction_and_more")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
