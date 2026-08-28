from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase

from .models import AuditEvent, Employee, Team
from .services import create_probation_employee


class PeopleApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", **{"password": "Test-" + "Only-1234!"}, verbosity=0)
        user_model = get_user_model()
        cls.hr = user_model.objects.get(username="hr.demo")
        cls.ceo = user_model.objects.get(username="ceo.demo")
        cls.leader = user_model.objects.get(username="leader.demo")
        cls.staff = user_model.objects.get(username="staff.demo")
        cls.other = user_model.objects.get(username="other.demo")

    def list_employees(self, user):
        self.client.force_login(user)
        return self.client.get("/api/v1/people/employees/")

    def test_staff_only_sees_same_team_and_never_hr_fields(self):
        response = self.list_employees(self.staff)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = {item["employee_code"] for item in response.data["results"]}
        self.assertEqual(codes, {"LDR01", "STF01", "TRY-ALPHA-01"})
        self.assertNotIn("national_id", response.data["results"][0])
        self.assertNotIn("employment_status", response.data["results"][0])

    def test_leader_sees_all_teams_without_sensitive_fields(self):
        response = self.list_employees(self.leader)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 6)
        self.assertIn("employment_status", response.data["results"][0])
        self.assertNotIn("national_id", response.data["results"][0])
        probation = next(item for item in response.data["results"] if item["employee_code"] == "TRY-ALPHA-01")
        self.assertTrue(probation["can_promote"])

    def test_staff_cannot_retrieve_employee_outside_team(self):
        self.client.force_login(self.staff)
        response = self.client.get(f"/api/v1/people/employees/{self.other.employee_profile.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_only_sees_own_organization_scope(self):
        self.client.force_login(self.staff)
        teams = self.client.get("/api/v1/people/teams/")
        departments = self.client.get("/api/v1/people/departments/")
        self.assertEqual([item["code"] for item in teams.data["results"]], ["ALPHA"])
        self.assertEqual([item["code"] for item in departments.data["results"]], ["MRE"])

    def test_hr_creates_active_probation_account_and_employee(self):
        self.client.force_login(self.hr)
        response = self.client.post(
            "/api/v1/people/employees/",
            {"employee_code": "ABC13", "username": "new.employee", "password": "Local-Only-5678!", "employment_status": "official"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee = Employee.objects.get(employee_code="ABC13")
        self.assertEqual(employee.employment_status, Employee.EmploymentStatus.PROBATION)
        self.assertTrue(employee.identity_user.is_active)
        self.assertTrue(employee.identity_user.check_password("Local-Only-5678!"))
        event = AuditEvent.objects.get(action="people.employee.created", target_uuid=str(employee.pk))
        self.assertNotIn("password", str(event.changes).lower())

    def test_non_hr_cannot_create_employee(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            "/api/v1/people/employees/",
            {"employee_code": "ABC14", "username": "denied.employee", "password": "Local-Only-5678!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hr_can_create_employee_without_identity_account(self):
        self.client.force_login(self.hr)
        response = self.client.post(
            "/api/v1/people/employees/",
            {"employee_code": "MRE People / 2026-01", "create_account": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee = Employee.objects.get(employee_code="MRE People / 2026-01")
        self.assertIsNone(employee.identity_user)
        self.assertIsNone(response.data["username"])
        event = AuditEvent.objects.get(action="people.employee.created", target_uuid=str(employee.pk))
        self.assertFalse(event.changes["account_created"])

    def test_duplicate_employee_code_is_rejected(self):
        self.client.force_login(self.hr)
        response = self.client.post(
            "/api/v1/people/employees/",
            {"employee_code": "stf01", "create_account": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("employee_code", response.data)

    def test_account_is_cleaned_up_when_employee_creation_fails(self):
        with patch("people_domain.services.Employee.objects.create", side_effect=IntegrityError("forced")):
            with self.assertRaises(IntegrityError):
                create_probation_employee(
                    actor=self.hr,
                    employee_code="ERR01",
                    username="orphan.account",
                    password="Local-Only-5678!",
                )
        self.assertFalse(get_user_model().objects.filter(username="orphan.account").exists())
        self.assertFalse(Employee.objects.filter(employee_code="ERR01").exists())

    def test_hr_updates_sensitive_details_with_version_check(self):
        employee = self.staff.employee_profile
        self.client.force_login(self.hr)
        response = self.client.patch(
            f"/api/v1/people/employees/{employee.pk}/",
            {
                "display_name": "Nhân sự Alpha",
                "national_id": "001234567890",
                "date_of_birth": "1998-05-17",
                "address": "Hà Nội",
                "expected_version": employee.version,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["national_id"], "001234567890")
        employee.refresh_from_db()
        self.assertEqual(employee.version, 2)

    def test_stale_hr_update_is_rejected(self):
        employee = self.staff.employee_profile
        self.client.force_login(self.hr)
        response = self.client.patch(
            f"/api/v1/people/employees/{employee.pk}/",
            {"display_name": "Không ghi đè", "expected_version": 99},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_leader_promotes_probation_employee_in_own_team_with_note(self):
        target = self.staff.employee_profile
        target.employment_status = Employee.EmploymentStatus.PROBATION
        target.save(update_fields=["employment_status"])
        self.client.force_login(self.leader)
        response = self.client.post(
            f"/api/v1/people/employees/{target.pk}/promote/",
            {"note": "Đạt yêu cầu thử việc"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertEqual(target.employment_status, Employee.EmploymentStatus.OFFICIAL)

    def test_leader_cannot_promote_employee_outside_led_team(self):
        target = self.other.employee_profile
        target.employment_status = Employee.EmploymentStatus.PROBATION
        target.save(update_fields=["employment_status"])
        self.client.force_login(self.leader)
        response = self.client.post(
            f"/api/v1/people/employees/{target.pk}/promote/",
            {"note": "Không cùng team"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ceo_has_hr_projection_and_can_promote_across_company(self):
        target = self.other.employee_profile
        target.employment_status = Employee.EmploymentStatus.PROBATION
        target.save(update_fields=["employment_status"])
        self.client.force_login(self.ceo)
        listing = self.client.get("/api/v1/people/employees/")
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        target_payload = next(item for item in listing.data["results"] if item["uuid"] == str(target.pk))
        self.assertIn("national_id", target_payload)
        self.assertTrue(target_payload["can_promote"])
        response = self.client.post(
            f"/api/v1/people/employees/{target.pk}/promote/",
            {"note": "CEO duyệt toàn công ty"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_promotion_requires_note(self):
        target = self.staff.employee_profile
        target.employment_status = Employee.EmploymentStatus.PROBATION
        target.save(update_fields=["employment_status"])
        self.client.force_login(self.leader)
        response = self.client.post(f"/api/v1/people/employees/{target.pk}/promote/", {"note": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_leader_can_move_employee_to_one_team(self):
        target = self.other.employee_profile
        alpha = Team.objects.get(code="ALPHA")
        self.client.force_login(self.leader)
        response = self.client.put(
            f"/api/v1/people/employees/{target.pk}/membership/",
            {"team_uuid": str(alpha.pk)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertEqual(target.team, alpha)

    def test_team_accepts_multiple_leaders_and_audits_relation(self):
        target = self.other.employee_profile
        target.rank = Employee.Rank.LEADER
        target.save(update_fields=["rank"])
        alpha = Team.objects.get(code="ALPHA")
        self.client.force_login(self.leader)
        response = self.client.post(
            f"/api/v1/people/teams/{alpha.pk}/leaders/",
            {"employee_uuid": str(target.pk)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(alpha.leaderships.count(), 2)
        self.assertTrue(AuditEvent.objects.filter(action="people.leadership.created").exists())

    def test_inactive_account_fails_closed(self):
        self.staff.is_active = False
        self.staff.save(update_fields=["is_active"])
        response = self.list_employees(self.staff)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
