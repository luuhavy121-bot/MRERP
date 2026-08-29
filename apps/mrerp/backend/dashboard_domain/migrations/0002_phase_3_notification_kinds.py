from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("dashboard_domain", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="kind",
            field=models.CharField(choices=[("feed", "Bảng tin"), ("task", "Công việc"), ("goal", "Mục tiêu"), ("leave", "Nghỉ phép"), ("account", "Tài khoản"), ("recruitment", "Tuyển dụng"), ("document", "Tài liệu"), ("recognition", "Ghi nhận")], max_length=16),
        ),
    ]
