import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APITestCase

from people_domain.models import Employee

from .models import Notification
from .tasks import purge_expired_data


class DashboardApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", password="Test-only-1234!")

    def login_as(self, username):
        user = get_user_model().objects.get(username=username)
        self.client.force_authenticate(user)
        return user

    def test_general_and_private_are_separated_and_read_all_is_scoped(self):
        staff = self.login_as("staff.demo")
        self.client.post("/api/v1/feed/posts/", {"content": "Toàn công ty", "company_scope": "true", "employee_uuids": json.dumps([]), "team_uuids": json.dumps([]), "is_official": "false"}, format="multipart")
        Notification.objects.create(recipient=staff.employee_profile, kind="account", title="Riêng Staff", body="", target_type="profile")
        other = get_user_model().objects.get(username="other.demo").employee_profile
        Notification.objects.create(recipient=other, kind="account", title="Riêng Beta", body="", target_type="profile")
        dashboard = self.client.get("/api/v1/dashboard/")
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(len(dashboard.data["general"]["company_posts"]), 1)
        self.assertEqual([item["title"] for item in dashboard.data["private"]["notifications"]], ["Riêng Staff"])
        self.assertEqual(self.client.post("/api/v1/dashboard/notifications/read-all/").status_code, 204)
        self.assertEqual(Notification.objects.get(recipient=other).read_at, None)

    def test_inactive_employment_is_denied(self):
        user = self.login_as("staff.demo")
        user.employee_profile.employment_status = Employee.EmploymentStatus.TERMINATED
        user.employee_profile.save(update_fields=["employment_status"])
        self.assertEqual(self.client.get("/api/v1/dashboard/").status_code, 403)

    def test_notification_retention_removes_only_items_older_than_30_days(self):
        staff = self.login_as("staff.demo").employee_profile
        old = Notification.objects.create(recipient=staff, kind="account", title="Old", body="", target_type="profile")
        recent = Notification.objects.create(recipient=staff, kind="account", title="Recent", body="", target_type="profile")
        Notification.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=31))
        purge_expired_data()
        self.assertFalse(Notification.objects.filter(pk=old.pk).exists())
        self.assertTrue(Notification.objects.filter(pk=recent.pk).exists())
