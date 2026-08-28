import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("people_domain", "0003_add_company_promotion_capability"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="department",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="teams",
                to="people_domain.department",
            ),
        ),
    ]
