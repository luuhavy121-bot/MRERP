from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from people_domain.models import Employee

from .models import StarLedgerEntry, TeamStarAllowance
from django.utils import timezone


class RewardsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", password="Local-Demo-1234!")
        cls.staff = Employee.objects.get(employee_code="STF01")
        cls.other = Employee.objects.get(employee_code="OTH01")
        cls.leader = Employee.objects.get(employee_code="LDR01")
        TeamStarAllowance.objects.create(team=cls.staff.team, month=timezone.localdate().replace(day=1), limit=100)

    def setUp(self):
        self.client = APIClient()

    def login(self, username):
        self.assertTrue(self.client.login(username=username, password="Local-Demo-1234!"))

    def test_leader_recognition_is_team_scoped_and_does_not_add_stars(self):
        self.login("leader.demo")
        response = self.client.post("/api/v1/rewards/recognitions/", {
            "recipient_uuids": [str(self.staff.pk)], "category": "Hợp tác", "message": "Hỗ trợ Team rất tốt",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(StarLedgerEntry.objects.count(), 0)
        outside = self.client.post("/api/v1/rewards/recognitions/", {
            "recipient_uuids": [str(self.other.pk)], "category": "Hợp tác", "message": "Ngoài Team",
        }, format="json")
        self.assertEqual(outside.status_code, 403)
        self_grant = self.client.post("/api/v1/rewards/recognitions/", {
            "recipient_uuids": [str(self.leader.pk)], "category": "Tự ghi", "message": "Không hợp lệ",
        }, format="json")
        self.assertEqual(self_grant.status_code, 403)

    def test_star_ledger_balance_leaderboard_and_negative_guard(self):
        self.login("leader.demo")
        granted = self.client.post("/api/v1/rewards/stars/grant/", {
            "employee_uuid": str(self.staff.pk), "amount": 12, "reason": "Hoàn thành mục tiêu",
        }, format="json")
        self.assertEqual(granted.status_code, 201)
        denied = self.client.post("/api/v1/rewards/stars/grant/", {
            "employee_uuid": str(self.other.pk), "amount": 1, "reason": "Ngoài scope",
        }, format="json")
        self.assertEqual(denied.status_code, 403)
        negative = self.client.post("/api/v1/rewards/stars/grant/", {
            "employee_uuid": str(self.staff.pk), "amount": -13, "reason": "Điều chỉnh",
        }, format="json")
        self.assertEqual(negative.status_code, 403)

        self.client.logout()
        self.login("staff.demo")
        balance = self.client.get("/api/v1/rewards/stars/me/")
        self.assertEqual(balance.status_code, 200)
        self.assertEqual(balance.data["balance"], 12)
        leaderboard = self.client.get("/api/v1/rewards/leaderboard/?period=month")
        self.assertEqual(leaderboard.status_code, 200)
        self.assertEqual(leaderboard.data[0]["stars"], 12)
        self.assertNotIn("ledger", leaderboard.data[0])
        self.assertEqual(self.client.post("/api/v1/rewards/stars/grant/", {
            "employee_uuid": str(self.other.pk), "amount": 1, "reason": "Không quyền",
        }, format="json").status_code, 403)

    def test_star_grant_idempotency_prevents_duplicate_credit(self):
        self.login("leader.demo")
        payload = {
            "employee_uuid": str(self.staff.pk), "amount": 5, "reason": "Idempotent grant",
            "idempotency_key": "reward-test-once",
        }
        first = self.client.post("/api/v1/rewards/stars/grant/", payload, format="json")
        second = self.client.post("/api/v1/rewards/stars/grant/", payload, format="json")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(first.data["uuid"], second.data["uuid"])
        self.assertEqual(StarLedgerEntry.objects.filter(idempotency_key="reward-test-once").count(), 1)
        changed = self.client.post(
            "/api/v1/rewards/stars/grant/",
            {**payload, "amount": 6},
            format="json",
        )
        self.assertEqual(changed.status_code, 400)
