from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("documents_domain", "0001_initial")]

    operations = [
        migrations.AlterModelOptions(
            name="document",
            options={
                "ordering": ["-updated_at"],
                "permissions": [
                    ("view_documents", "Can view documents in own audience"),
                    ("view_company_documents", "Can view documents across company"),
                    ("upload_documents", "Can upload documents"),
                    ("view_hr_confidential_documents", "Can view HR confidential documents"),
                    ("manage_all_documents", "Can manage all documents"),
                ],
            },
        ),
    ]
