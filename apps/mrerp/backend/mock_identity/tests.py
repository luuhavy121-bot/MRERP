from django.core.management import call_command
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase


class MockIdentityTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", **{"password": "Test-" + "Only-1234!"}, verbosity=0)

    def test_session_bootstraps_csrf_cookie(self):
        response = self.client.get("/api/v1/auth/session/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["authenticated"])
        self.assertIn("csrftoken", response.cookies)

    def test_mock_login_and_logout(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "hr.demo", "password": "Test-Only-1234!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employee_code"], "HRA01")
        self.assertTrue(response.data["mock_identity"])
        self.assertEqual(len(response.data["debug_personas"]), 4)
        session_response = self.client.get("/api/v1/auth/session/")
        self.assertTrue(session_response.data["authenticated"])
        self.assertEqual(session_response.data["username"], "hr.demo")
        logout_response = self.client.post("/api/v1/auth/logout/")
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)

    @override_settings(MOCK_IDENTITY_ENABLED=False)
    def test_login_endpoint_is_closed_when_mock_identity_disabled(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "hr.demo", "password": "Test-Only-1234!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_user_can_switch_to_allowlisted_debug_persona(self):
        self.client.login(username="hr.demo", password="Test-Only-1234!")
        response = self.client.post("/api/v1/auth/debug/switch/", {"username": "leader.demo"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employee_code"], "LDR01")
        session = self.client.get("/api/v1/auth/session/")
        self.assertEqual(session.data["username"], "leader.demo")

    def test_debug_switch_rejects_user_outside_allowlist(self):
        self.client.login(username="hr.demo", password="Test-Only-1234!")
        response = self.client.post("/api/v1/auth/debug/switch/", {"username": "not-allowed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_debug_switch_requires_authenticated_session(self):
        response = self.client.post("/api/v1/auth/debug/switch/", {"username": "leader.demo"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(APP_ENV="production")
    def test_debug_switch_is_closed_outside_debug_mode(self):
        self.client.login(username="hr.demo", password="Test-Only-1234!")
        response = self.client.post("/api/v1/auth/debug/switch/", {"username": "leader.demo"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
