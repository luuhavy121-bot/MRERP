from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient


class PreferenceApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", password="Local-Demo-1234!")

    def setUp(self):
        self.client = APIClient()

    def test_employee_can_read_and_update_own_preferences(self):
        self.client.login(username="staff.demo", password="Local-Demo-1234!")
        response = self.client.get("/api/v1/settings/me/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["social_notifications_enabled"])
        response = self.client.patch(
            "/api/v1/settings/me/",
            {"social_notifications_enabled": False},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["social_notifications_enabled"])
        self.assertIn("account", response.data["mandatory_notifications"])

    def test_locked_account_is_denied(self):
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.get(username="staff.demo")
        user.is_active = False
        user.save(update_fields=["is_active"])
        self.client.force_authenticate(user=user)
        self.assertEqual(self.client.get("/api/v1/settings/me/").status_code, 403)
