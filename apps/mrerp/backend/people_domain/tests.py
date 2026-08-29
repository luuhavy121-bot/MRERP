from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from .models import AuditEvent, Employee, EmployeeAccountState, Team, TeamLeadership, TeamMembershipHistory
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
        self.assertEqual([item["code"] for item in teams.data["results"]], ["ALPHA"])
        self.assertEqual(self.client.get("/api/v1/people/departments/").status_code, status.HTTP_404_NOT_FOUND)

    def test_leader_creates_flat_team_without_department(self):
        self.client.force_login(self.leader)
        response = self.client.post(
            "/api/v1/people/teams/",
            {"code": "CREATIVE", "name": "Creative"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        team = Team.objects.get(code="CREATIVE")
        self.assertIsNone(team.department_id)
        self.assertNotIn("department", response.data)
        event = AuditEvent.objects.get(action="people.team.created", target_uuid=str(team.pk))
        self.assertEqual(event.changes, {"code": "CREATIVE", "name": "Creative"})

    def test_leader_updates_team_and_change_is_audited(self):
        team = Team.objects.get(code="BETA")
        self.client.force_login(self.leader)
        response = self.client.patch(
            f"/api/v1/people/teams/{team.pk}/",
            {"code": "BETA-OPS", "name": "Beta Operations", "is_active": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        team.refresh_from_db()
        self.assertEqual(team.code, "BETA-OPS")
        self.assertTrue(team.is_active)
        self.assertTrue(AuditEvent.objects.filter(action="people.team.updated", target_uuid=str(team.pk)).exists())

    def test_team_archive_requires_no_members_or_leaders_and_is_audited(self):
        alpha = Team.objects.get(code="ALPHA")
        self.client.force_login(self.leader)
        blocked = self.client.post(f"/api/v1/people/teams/{alpha.pk}/archive/", {}, format="json")
        self.assertEqual(blocked.status_code, status.HTTP_400_BAD_REQUEST)

        empty = Team.objects.create(code="EMPTY", name="Empty")
        response = self.client.post(f"/api/v1/people/teams/{empty.pk}/archive/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        empty.refresh_from_db()
        self.assertFalse(empty.is_active)
        self.assertTrue(AuditEvent.objects.filter(action="people.team.archived", target_uuid=str(empty.pk)).exists())

    def test_hr_creates_active_probation_account_and_employee(self):
        self.client.force_login(self.hr)
        response = self.client.post(
            "/api/v1/people/employees/",
            {"employee_code": "ABC13", "username": "new.employee", "employment_status": "official"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee = Employee.objects.get(employee_code="ABC13")
        self.assertEqual(employee.employment_status, Employee.EmploymentStatus.PROBATION)
        self.assertTrue(employee.identity_user.is_active)
        self.assertTrue(employee.identity_user.check_password(response.data["temporary_password"]))
        self.assertTrue(employee.account_state.must_change_password)
        event = AuditEvent.objects.get(action="people.employee.created", target_uuid=str(employee.pk))
        self.assertNotIn("password", str(event.changes).lower())

    def test_non_hr_cannot_create_employee(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            "/api/v1/people/employees/",
            {"employee_code": "ABC14", "username": "denied.employee"},
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
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("employee_code", response.data["errors"])
        self.assertIn("X-Correlation-ID", response)
        self.assertEqual(response.data["correlation_id"], response["X-Correlation-ID"])

    def test_employee_is_rolled_back_when_account_provisioning_fails(self):
        with patch("people_domain.services.provision_account", side_effect=IntegrityError("forced")):
            with self.assertRaises(IntegrityError):
                create_probation_employee(
                    actor=self.hr,
                    employee_code="ERR01",
                    username="orphan.account",
                )
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
        event = AuditEvent.objects.get(action="people.employee.promoted", target_uuid=str(target.pk))
        self.assertEqual(event.changes["from"], Employee.EmploymentStatus.PROBATION)
        self.assertEqual(event.changes["to"], Employee.EmploymentStatus.OFFICIAL)
        self.assertNotIn("Đạt yêu cầu thử việc", str(event.changes))

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "permission_denied")

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

    def test_unsupported_employment_status_fails_closed(self):
        Employee.objects.filter(pk=self.staff.employee_profile.pk).update(employment_status="legacy")
        user = get_user_model().objects.get(pk=self.staff.pk)
        with self.assertLogs("mrerp.security", level="WARNING"):
            response = self.list_employees(user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "permission_denied")
        self.assertIn("correlation_id", response.data)

    def test_unauthenticated_people_request_has_safe_error_envelope(self):
        response = self.client.get("/api/v1/people/employees/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "not_authenticated")
        self.assertEqual(response.data["correlation_id"], response["X-Correlation-ID"])
        self.assertNotIn("errors", response.data)

    def test_staff_search_and_team_filter_do_not_leak_outside_scope(self):
        self.client.force_login(self.staff)
        search = self.client.get("/api/v1/people/employees/?search=OTH01")
        self.assertEqual(search.status_code, status.HTTP_200_OK)
        self.assertEqual(search.data["count"], 0)
        beta = Team.objects.get(code="BETA")
        filtered = self.client.get(f"/api/v1/people/employees/?team={beta.pk}")
        self.assertEqual(filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(filtered.data["count"], 0)

    def test_directory_pagination_uses_scoped_count(self):
        alpha = Team.objects.get(code="ALPHA")
        Employee.objects.bulk_create([
            Employee(employee_code=f"PAGE-{index:02d}", display_name=f"Page {index}", team=alpha)
            for index in range(25)
        ])
        self.client.force_login(self.staff)
        first = self.client.get("/api/v1/people/employees/?page=1")
        second = self.client.get("/api/v1/people/employees/?page=2")
        self.assertEqual(first.data["count"], 28)
        self.assertEqual(len(first.data["results"]), 20)
        self.assertEqual(len(second.data["results"]), 8)
        self.assertIsNotNone(first.data["next"])

    def test_leader_detail_never_contains_hr_fields(self):
        self.client.force_login(self.leader)
        response = self.client.get(f"/api/v1/people/employees/{self.staff.employee_profile.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ("national_id", "date_of_birth", "address", "username"):
            self.assertNotIn(field, response.data)

    def test_staff_cannot_manage_team_or_membership(self):
        alpha = Team.objects.get(code="ALPHA")
        self.client.force_login(self.staff)
        create_team = self.client.post("/api/v1/people/teams/", {"code": "NOPE", "name": "Nope"}, format="json")
        move = self.client.put(
            f"/api/v1/people/employees/{self.other.employee_profile.pk}/membership/",
            {"team_uuid": str(alpha.pk)},
            format="json",
        )
        self.assertEqual(create_team.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(move.status_code, status.HTTP_403_FORBIDDEN)

    def test_leader_cannot_change_own_membership(self):
        beta = Team.objects.get(code="BETA")
        self.client.force_login(self.leader)
        response = self.client.put(
            f"/api/v1/people/employees/{self.leader.employee_profile.pk}/membership/",
            {"team_uuid": str(beta.pk)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_leader_cannot_add_or_remove_own_leadership(self):
        alpha = Team.objects.get(code="ALPHA")
        beta = Team.objects.get(code="BETA")
        self.client.force_login(self.leader)
        add = self.client.post(
            f"/api/v1/people/teams/{beta.pk}/leaders/",
            {"employee_uuid": str(self.leader.employee_profile.pk)},
            format="json",
        )
        remove = self.client.delete(
            f"/api/v1/people/teams/{alpha.pk}/leaders/{self.leader.employee_profile.pk}/"
        )
        self.assertEqual(add.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(remove.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(TeamLeadership.objects.filter(team=alpha, leader=self.leader.employee_profile).exists())

    def test_employee_update_audit_minimizes_sensitive_values(self):
        employee = self.staff.employee_profile
        self.client.force_login(self.hr)
        response = self.client.patch(
            f"/api/v1/people/employees/{employee.pk}/",
            {
                "display_name": "Tên đã cập nhật",
                "national_id": "009999999999",
                "address": "Địa chỉ không được ghi audit",
                "expected_version": employee.version,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event = AuditEvent.objects.get(action="people.employee.updated", target_uuid=str(employee.pk))
        self.assertEqual(event.changes["display_name"], {"from": "Staff Alpha", "to": "Tên đã cập nhật"})
        self.assertEqual(event.changes["national_id"], {"changed": True})
        self.assertEqual(event.changes["address"], {"changed": True})
        self.assertNotIn("009999999999", str(event.changes))
        self.assertNotIn("Địa chỉ không được ghi audit", str(event.changes))

    def test_membership_and_leadership_removal_are_audited(self):
        alpha = Team.objects.get(code="ALPHA")
        target = self.other.employee_profile
        self.client.force_login(self.leader)
        moved = self.client.put(
            f"/api/v1/people/employees/{target.pk}/membership/",
            {"team_uuid": str(alpha.pk)},
            format="json",
        )
        self.assertEqual(moved.status_code, status.HTTP_200_OK)
        membership_event = AuditEvent.objects.get(action="people.membership.changed", target_uuid=str(target.pk))
        self.assertEqual(membership_event.changes["to_team"], str(alpha.pk))

        self.client.force_login(self.ceo)
        removed = self.client.delete(
            f"/api/v1/people/teams/{alpha.pk}/leaders/{self.leader.employee_profile.pk}/"
        )
        self.assertEqual(removed.status_code, status.HTTP_204_NO_CONTENT)
        leadership_event = AuditEvent.objects.get(action="people.leadership.removed", target_uuid=str(alpha.pk))
        self.assertEqual(leadership_event.changes["leader"], str(self.leader.employee_profile.pk))

    def test_me_endpoint_uses_session_actor(self):
        self.client.force_login(self.staff)
        response = self.client.get(f"/api/v1/people/employees/me/?employee_uuid={self.other.employee_profile.pk}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(self.staff.employee_profile.pk))
        self.assertNotIn("national_id", response.data)

    def test_self_profile_updates_only_allowed_fields(self):
        employee = self.staff.employee_profile
        self.client.force_login(self.staff)
        response = self.client.patch(
            "/api/v1/people/employees/me/",
            {"display_name": "Tên tự cập nhật", "date_of_birth": "1998-04-03", "address": "Địa chỉ cá nhân", "expected_version": employee.version},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["display_name"], "Tên tự cập nhật")
        self.assertNotIn("national_id", response.data)
        self.assertTrue(AuditEvent.objects.filter(action="people.employee.updated", target_uuid=str(employee.pk)).exists())

    def test_staff_changes_own_password_and_clears_temporary_flag(self):
        EmployeeAccountState.objects.create(employee=self.staff.employee_profile, must_change_password=True)
        self.client.force_login(self.staff)
        response = self.client.post(
            "/api/v1/people/employees/me/change-password/",
            {"current_password": "Test-Only-1234!", "new_password": "Changed-Only-9876!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.check_password("Changed-Only-9876!"))
        self.assertFalse(self.staff.employee_profile.account_state.must_change_password)

    def test_hr_provisions_account_and_password_is_returned_once_only(self):
        employee = Employee.objects.get(employee_code="TRY-ALPHA-01")
        self.client.force_login(self.hr)
        response = self.client.post(
            f"/api/v1/people/employees/{employee.pk}/account/provision/",
            {"username": "try.alpha"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        password = response.data["temporary_password"]
        employee.refresh_from_db()
        self.assertTrue(employee.identity_user.check_password(password))
        event = AuditEvent.objects.get(action="people.account.provisioned", target_uuid=str(employee.pk))
        self.assertNotIn(password, str(event.changes))
        detail = self.client.get(f"/api/v1/people/employees/{employee.pk}/")
        self.assertNotIn("temporary_password", detail.data)

    def test_leader_resets_password_only_inside_managed_team(self):
        self.client.force_login(self.leader)
        allowed = self.client.post(
            f"/api/v1/people/employees/{self.staff.employee_profile.pk}/account/reset-password/",
            {},
            format="json",
        )
        denied = self.client.post(
            f"/api/v1/people/employees/{self.other.employee_profile.pk}/account/reset-password/",
            {},
            format="json",
        )
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.check_password(allowed.data["temporary_password"]))

    def test_hr_locks_and_unlocks_account_but_staff_cannot(self):
        url = f"/api/v1/people/employees/{self.staff.employee_profile.pk}/account"
        self.client.force_login(self.hr)
        self.assertEqual(self.client.post(f"{url}/lock/", {}, format="json").status_code, status.HTTP_200_OK)
        self.staff.refresh_from_db()
        self.assertFalse(self.staff.is_active)
        self.assertEqual(self.client.post(f"{url}/unlock/", {}, format="json").status_code, status.HTTP_200_OK)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(f"{url}/lock/", {}, format="json").status_code, status.HTTP_403_FORBIDDEN)

    def test_termination_revokes_and_reactivation_restores_access_bundle(self):
        employee = self.staff.employee_profile
        initial_groups = set(self.staff.groups.values_list("name", flat=True))
        self.client.force_login(self.hr)
        terminate = self.client.post(
            f"/api/v1/people/employees/{employee.pk}/employment/",
            {"command": "terminate", "note": "Kết thúc hợp đồng kiểm thử"},
            format="json",
        )
        self.assertEqual(terminate.status_code, status.HTTP_200_OK)
        self.staff.refresh_from_db()
        employee.refresh_from_db()
        self.assertEqual(employee.employment_status, Employee.EmploymentStatus.TERMINATED)
        self.assertFalse(self.staff.is_active)
        self.assertFalse(self.staff.groups.exists())

        reactivate = self.client.post(
            f"/api/v1/people/employees/{employee.pk}/employment/",
            {"command": "reactivate", "note": "Quay lại làm việc"},
            format="json",
        )
        self.assertEqual(reactivate.status_code, status.HTTP_200_OK)
        self.staff.refresh_from_db()
        employee.refresh_from_db()
        self.assertEqual(employee.employment_status, Employee.EmploymentStatus.OFFICIAL)
        self.assertTrue(self.staff.is_active)
        self.assertEqual(set(self.staff.groups.values_list("name", flat=True)), initial_groups)

    def test_membership_change_creates_effective_history(self):
        target = self.other.employee_profile
        alpha = Team.objects.get(code="ALPHA")
        self.client.force_login(self.leader)
        response = self.client.put(
            f"/api/v1/people/employees/{target.pk}/membership/",
            {"team_uuid": str(alpha.pk)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        history = TeamMembershipHistory.objects.get(employee=target)
        self.assertEqual(history.to_team, alpha)
        self.assertEqual(history.from_team.code, "BETA")

    def test_only_ceo_manages_access_bundle_and_cannot_change_self(self):
        self.client.force_login(self.hr)
        self.assertEqual(self.client.get("/api/v1/people/access/").status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_login(self.ceo)
        listing = self.client.get("/api/v1/people/access/")
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        update = self.client.put(
            "/api/v1/people/access/bundle/",
            {"employee_uuid": str(self.other.employee_profile.pk), "bundle": "hr"},
            format="json",
        )
        self.assertEqual(update.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(list(self.other.groups.values_list("name", flat=True)), ["People HR"])
        self_update = self.client.put(
            "/api/v1/people/access/bundle/",
            {"employee_uuid": str(self.ceo.employee_profile.pk), "bundle": "staff"},
            format="json",
        )
        self.assertEqual(self_update.status_code, status.HTTP_403_FORBIDDEN)

    def test_hr_audit_projection_excludes_access_changes(self):
        self.client.force_login(self.ceo)
        self.client.put(
            "/api/v1/people/access/bundle/",
            {"employee_uuid": str(self.other.employee_profile.pk), "bundle": "hr"},
            format="json",
        )
        self.client.force_login(self.hr)
        hr_audit = self.client.get("/api/v1/people/audit/")
        self.assertEqual(hr_audit.status_code, status.HTTP_200_OK)
        self.assertNotIn("people.access.bundle_changed", [item["action"] for item in hr_audit.data["results"]])
        self.client.force_login(self.ceo)
        ceo_audit = self.client.get("/api/v1/people/audit/")
        self.assertIn("people.access.bundle_changed", [item["action"] for item in ceo_audit.data["results"]])

    def test_csv_import_export_never_contains_password(self):
        self.client.force_login(self.hr)
        exported = self.client.get("/api/v1/people/employees/export-csv/")
        self.assertEqual(exported.status_code, status.HTTP_200_OK)
        content = exported.content.decode("utf-8-sig")
        self.assertIn("employee_code", content)
        self.assertNotIn("password", content.lower())
        uploaded = SimpleUploadedFile(
            "employees.csv",
            b"employee_code,display_name,job_title,team_code\nCSV01,Nhan su CSV,QA,ALPHA\n",
            content_type="text/csv",
        )
        imported = self.client.post("/api/v1/people/employees/import-csv/", {"file": uploaded}, format="multipart")
        self.assertEqual(imported.status_code, status.HTTP_200_OK)
        employee = Employee.objects.get(employee_code="CSV01")
        self.assertIsNone(employee.identity_user_id)
        self.assertEqual(employee.employment_status, Employee.EmploymentStatus.PROBATION)
