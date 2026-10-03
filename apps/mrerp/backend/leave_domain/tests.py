from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management import call_command
from rest_framework.test import APITestCase

from people_domain.models import AuditEvent, Employee, TeamLeadership

from .models import LeaveRequest


class LeaveAttendanceApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", password="Test-Only-1234!", verbosity=0)
        users = get_user_model().objects
        cls.staff = users.get(username="staff.demo")
        cls.other = users.get(username="other.demo")
        cls.leader = users.get(username="leader.demo")
        cls.hr = users.get(username="hr.demo")
        cls.ceo = users.get(username="ceo.demo")

    def authenticate(self, user):
        self.client.force_authenticate(user)

    def create_request(self, user=None, start="2026-09-07", end="2026-09-08"):
        self.authenticate(user or self.staff)
        return self.client.post(
            "/api/v1/leave/requests/",
            {"start_date": start, "end_date": end, "reason": "Nghỉ việc cá nhân"},
            format="json",
        )

    def test_staff_can_submit_and_only_sees_own_requests(self):
        response = self.create_request()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], LeaveRequest.Status.PENDING)
        self.assertNotIn("requester", response.data)
        self.create_request(self.other, "2026-09-10", "2026-09-10")

        self.authenticate(self.staff)
        listing = self.client.get("/api/v1/leave/requests/")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.data["count"], 1)
        self.assertEqual(listing.data["results"][0]["requester_code"], "STF01")

    def test_invalid_dates_and_overlap_are_rejected(self):
        invalid = self.create_request(start="2026-09-09", end="2026-09-08")
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(self.create_request().status_code, 201)
        overlap = self.create_request(start="2026-09-08", end="2026-09-09")
        self.assertEqual(overlap.status_code, 400)

    def test_staff_can_edit_only_own_pending_request(self):
        created = self.create_request(start="2026-09-07", end="2026-09-07")
        self.assertTrue(created.data["can_edit"])
        response = self.client.patch(
            f"/api/v1/leave/requests/{created.data['uuid']}/",
            {
                "start_date": "2026-09-08",
                "end_date": "2026-09-09",
                "reason": "Lý do đã cập nhật",
                "expected_version": created.data["version"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["start_date"], "2026-09-08")
        self.assertFalse("Lý do đã cập nhật" in str(AuditEvent.objects.filter(action="leave.request.updated").latest("created_at").changes))

        self.authenticate(self.other)
        self.assertEqual(
            self.client.patch(
                f"/api/v1/leave/requests/{created.data['uuid']}/",
                {"start_date": "2026-09-10", "end_date": "2026-09-10", "reason": "Không hợp lệ", "expected_version": response.data["version"]},
                format="json",
            ).status_code,
            404,
        )

    def test_processed_request_cannot_be_edited(self):
        created = self.create_request()
        self.authenticate(self.leader)
        self.client.post(f"/api/v1/leave/requests/{created.data['uuid']}/review/", {"decision": "approved"}, format="json")
        self.authenticate(self.staff)
        response = self.client.patch(
            f"/api/v1/leave/requests/{created.data['uuid']}/",
            {"start_date": "2026-09-09", "end_date": "2026-09-09", "reason": "Muốn đổi", "expected_version": 2},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_edit_rejects_overlap_and_stale_version(self):
        created = self.create_request(start="2026-09-07", end="2026-09-07")
        self.create_request(start="2026-09-10", end="2026-09-10")
        endpoint = f"/api/v1/leave/requests/{created.data['uuid']}/"
        payload = {
            "start_date": "2026-09-10",
            "end_date": "2026-09-10",
            "reason": "Bị trùng",
            "expected_version": created.data["version"],
        }
        self.assertEqual(self.client.patch(endpoint, payload, format="json").status_code, 400)

        payload.update(start_date="2026-09-08", end_date="2026-09-08", reason="Hợp lệ")
        updated = self.client.patch(endpoint, payload, format="json")
        self.assertEqual(updated.status_code, 200)
        payload.update(start_date="2026-09-09", end_date="2026-09-09", reason="Phiên bản cũ")
        self.assertEqual(self.client.patch(endpoint, payload, format="json").status_code, 400)

    def test_leader_can_review_member_request_and_audit_is_minimal(self):
        created = self.create_request()
        self.authenticate(self.leader)
        listing = self.client.get("/api/v1/leave/requests/")
        self.assertEqual(listing.data["count"], 1)
        self.assertTrue(listing.data["results"][0]["can_review"])
        response = self.client.post(
            f"/api/v1/leave/requests/{created.data['uuid']}/review/",
            {"decision": "approved", "note": "Đã bố trí công việc"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], LeaveRequest.Status.APPROVED)
        event = AuditEvent.objects.filter(action="leave.request.reviewed").latest("created_at")
        self.assertEqual(event.changes["from"], LeaveRequest.Status.PENDING)
        self.assertNotIn("Nghỉ việc cá nhân", str(event.changes))

    def test_leader_outside_team_cannot_see_or_review_request(self):
        created = self.create_request()
        review_permission = Permission.objects.get(codename="review_team_leave_request")
        self.other.user_permissions.add(review_permission)
        TeamLeadership.objects.create(team=self.other.employee_profile.team, leader=self.other.employee_profile)
        self.authenticate(self.other)
        listing = self.client.get("/api/v1/leave/requests/")
        self.assertEqual(listing.data["count"], 0)
        response = self.client.post(
            f"/api/v1/leave/requests/{created.data['uuid']}/review/",
            {"decision": "approved"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_requester_cannot_review_own_request(self):
        created = self.create_request(self.leader)
        self.authenticate(self.leader)
        response = self.client.post(
            f"/api/v1/leave/requests/{created.data['uuid']}/review/",
            {"decision": "approved"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_review_is_single_transition(self):
        created = self.create_request()
        self.authenticate(self.leader)
        url = f"/api/v1/leave/requests/{created.data['uuid']}/review/"
        self.assertEqual(self.client.post(url, {"decision": "rejected"}, format="json").status_code, 400)
        self.assertEqual(self.client.post(url, {"decision": "rejected", "note": "Không thể bố trí"}, format="json").status_code, 200)
        self.assertEqual(self.client.post(url, {"decision": "approved"}, format="json").status_code, 400)

    def test_hr_attendance_projection_reflects_approved_leave(self):
        created = self.create_request()
        self.authenticate(self.leader)
        self.client.post(
            f"/api/v1/leave/requests/{created.data['uuid']}/review/",
            {"decision": "approved"},
            format="json",
        )
        self.authenticate(self.hr)
        response = self.client.get("/api/v1/leave/attendance/?month=2026-09")
        self.assertEqual(response.status_code, 200)
        staff_row = next(row for row in response.data if row["employee_code"] == "STF01")
        self.assertEqual(staff_row["approved_leave_days"], 2)
        self.assertEqual(staff_row["projected_workdays"], staff_row["scheduled_workdays"] - 2)
        self.assertEqual(
            set(staff_row),
            {
                "employee_uuid", "employee_code", "display_name", "team_name", "month", "scheduled_workdays",
                "public_holiday_days", "approved_leave_days", "adjustment_days", "adjustment_reason", "projected_workdays",
            },
        )

    def test_vietnam_holidays_reduce_scheduled_workdays(self):
        self.authenticate(self.hr)
        response = self.client.get("/api/v1/leave/attendance/?month=2026-04")
        self.assertEqual(response.status_code, 200)
        row = next(item for item in response.data if item["employee_code"] == "STF01")
        self.assertEqual(row["public_holiday_days"], 2)
        self.assertEqual(row["scheduled_workdays"], 24)

    def test_hr_can_adjust_attendance_and_staff_cannot(self):
        self.authenticate(self.hr)
        response = self.client.post(
            "/api/v1/leave/attendance/adjust/",
            {"employee_uuid": str(self.staff.employee_profile.pk), "month": "2026-09", "days": -1, "reason": "Điều chỉnh công thực tế"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["adjustment_days"], -1)
        event = AuditEvent.objects.filter(action="attendance.adjusted").latest("created_at")
        self.assertEqual(event.changes["to_days"], -1)
        self.assertNotIn("Điều chỉnh công thực tế", str(event.changes))

        self.authenticate(self.staff)
        denied = self.client.post(
            "/api/v1/leave/attendance/adjust/",
            {"employee_uuid": str(self.staff.employee_profile.pk), "month": "2026-09", "days": 1, "reason": "Tự điều chỉnh"},
            format="json",
        )
        self.assertEqual(denied.status_code, 403)

    def test_hr_monitors_but_does_not_review_team_leave(self):
        created = self.create_request()
        self.authenticate(self.hr)
        self.assertEqual(self.client.get("/api/v1/leave/requests/").data["count"], 0)
        self.assertEqual(
            self.client.post(f"/api/v1/leave/requests/{created.data['uuid']}/review/", {"decision": "approved"}, format="json").status_code,
            404,
        )

    def test_staff_cannot_view_company_attendance(self):
        self.authenticate(self.staff)
        response = self.client.get("/api/v1/leave/attendance/?month=2026-09")
        self.assertEqual(response.status_code, 403)

    def test_invalid_month_is_rejected(self):
        self.authenticate(self.hr)
        response = self.client.get("/api/v1/leave/attendance/?month=09-2026")
        self.assertEqual(response.status_code, 400)

    def test_account_and_employment_gate_fail_closed(self):
        self.staff.is_active = False
        self.staff.save(update_fields=["is_active"])
        self.authenticate(self.staff)
        self.assertEqual(self.client.get("/api/v1/leave/requests/").status_code, 403)

        self.staff.is_active = True
        self.staff.save(update_fields=["is_active"])
        employee = self.staff.employee_profile
        employee.employment_status = "ended"
        employee.save(update_fields=["employment_status"])
        self.assertEqual(self.client.get("/api/v1/leave/requests/").status_code, 403)

    def test_create_audit_does_not_store_reason(self):
        self.assertEqual(self.create_request().status_code, 201)
        event = AuditEvent.objects.filter(action="leave.request.created").latest("created_at")
        self.assertNotIn("reason", event.changes)
        self.assertNotIn("Nghỉ việc cá nhân", str(event.changes))
