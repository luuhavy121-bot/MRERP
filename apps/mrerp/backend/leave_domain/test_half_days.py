from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase
from .models import LeaveRequest
from dashboard_domain.models import Notification


class HalfDayTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", password="Test-Only-1234!", verbosity=0)

    def login(self, name):
        self.user = get_user_model().objects.get(username=name)
        self.client.force_authenticate(self.user)

    def submit(self, start="2026-10-03", end="2026-10-03", a="am", b="am"):
        return self.client.post("/api/v1/leave/requests/", {"start_date": start, "end_date": end, "start_period": a, "end_period": b, "reason": "Private medical reason"}, format="json")

    def test_two_distinct_halves_allowed_same_half_blocked_and_saturday_projection(self):
        self.login("staff.demo")
        first = self.submit()
        self.assertEqual(first.status_code, 201)
        self.assertEqual(self.submit().status_code, 400)
        second = self.submit(a="pm", b="pm")
        self.assertEqual(second.status_code, 201)
        self.login("leader.demo")
        url = f"/api/v1/leave/requests/{first.data['uuid']}/review/"
        self.assertEqual(self.client.post(url, {"decision": "approved"}, format="json").status_code, 200)
        self.login("hr.demo")
        rows = self.client.get("/api/v1/leave/attendance/?month=2026-10").data
        row = next(r for r in rows if r["employee_code"] == "STF01")
        self.assertEqual(row["scheduled_workdays"], 27)
        self.assertEqual(row["approved_leave_days"], 0.5)
        self.assertEqual(row["projected_workdays"], 26.5)

    def test_cross_month_periods_and_invalid_order(self):
        self.login("staff.demo")
        self.assertEqual(self.submit(a="pm", b="am").status_code, 400)
        response = self.submit("2026-09-30", "2026-10-01", "pm", "am")
        self.assertEqual(response.status_code, 201)
        self.login("leader.demo")
        self.client.post(f"/api/v1/leave/requests/{response.data['uuid']}/review/", {"decision": "approved"}, format="json")
        self.login("hr.demo")
        for month in ("2026-09", "2026-10"):
            rows = self.client.get(f"/api/v1/leave/attendance/?month={month}").data
            self.assertEqual(next(r for r in rows if r["employee_code"] == "STF01")["approved_leave_days"], 0.5)

    def test_legacy_defaults_and_calendar_acl_redaction_account_gate(self):
        self.login("staff.demo")
        first = self.client.post("/api/v1/leave/requests/", {"start_date": "2026-10-05", "end_date": "2026-10-05", "reason": "Private"}, format="json")
        self.assertEqual((first.data["start_period"], first.data["end_period"]), ("am", "pm"))
        self.login("leader.demo")
        self.assertEqual(self.client.get("/api/v1/leave/requests/calendar/?month=2026-10").data, [])
        self.client.post(f"/api/v1/leave/requests/{first.data['uuid']}/review/", {"decision": "approved"}, format="json")
        rows = self.client.get("/api/v1/leave/requests/calendar/?month=2026-10").data
        self.assertEqual(len(rows), 1)
        self.assertNotIn("reason", rows[0]); self.assertNotIn("review_note", rows[0])
        self.login("other.demo")
        self.assertEqual(self.client.get("/api/v1/leave/requests/calendar/?month=2026-10").data, [])
        self.login("staff.demo")
        self.user.is_active=False; self.user.save()
        self.assertEqual(self.client.get("/api/v1/leave/requests/calendar/?month=2026-10").status_code,403)
        self.user.is_active=True;self.user.save()
        employee=self.user.employee_profile;employee.employment_status="ended";employee.save()
        self.assertEqual(self.client.get("/api/v1/leave/requests/calendar/?month=2026-10").status_code,403)

    def test_period_edit_cannot_overlap_and_missing_capability_denied(self):
        self.login("staff.demo")
        first=self.submit(); second=self.submit(a="pm",b="pm")
        response=self.client.patch(f"/api/v1/leave/requests/{second.data['uuid']}/", {"start_date":"2026-10-03","end_date":"2026-10-03","start_period":"am","end_period":"pm","reason":"Both","expected_version":1},format="json")
        self.assertEqual(response.status_code,400)
        permission=Permission.objects.get(codename="view_own_leave_request")
        for group in self.user.groups.all():group.permissions.remove(permission)
        self.login("staff.demo")
        self.assertEqual(self.client.get("/api/v1/leave/requests/calendar/?month=2026-10").status_code,403)
        notifications=Notification.objects.filter(kind="leave",title="Đơn xin nghỉ cần duyệt")
        self.assertEqual(notifications.count(),2)
        self.assertFalse(any("Private" in n.body for n in notifications))
