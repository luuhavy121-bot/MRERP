from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from people_domain.models import Employee, Team

from .models import Application, Candidate, HiringRequest, JobOpening
from .services import anonymize_expired_candidates


class RecruitmentApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", password="Local-Demo-1234!")
        cls.alpha = Team.objects.get(code="ALPHA")
        cls.beta = Team.objects.get(code="BETA")

    def setUp(self):
        self.client = APIClient()

    def login(self, username):
        self.assertTrue(self.client.login(username=username, password="Local-Demo-1234!"))

    def test_leader_request_requires_hr_approval_and_is_team_scoped(self):
        self.login("leader.demo")
        response = self.client.post("/api/v1/recruitment/requests/", {
            "team_uuid": str(self.alpha.pk), "title": "Content Creator", "headcount": 2, "justification": "Mở rộng Team",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], HiringRequest.Status.PENDING)
        denied = self.client.post("/api/v1/recruitment/requests/", {
            "team_uuid": str(self.beta.pk), "title": "Sale", "headcount": 1, "justification": "Ngoài scope",
        }, format="json")
        self.assertEqual(denied.status_code, 403)

        self.client.logout()
        self.login("hr.demo")
        reviewed = self.client.post(
            f"/api/v1/recruitment/requests/{response.data['uuid']}/review/",
            {"decision": "approved", "note": "Đã duyệt"},
            format="json",
        )
        self.assertEqual(reviewed.status_code, 200)
        self.assertIsNotNone(reviewed.data["opening_uuid"])

    def _create_application(self):
        self.login("hr.demo")
        request = self.client.post("/api/v1/recruitment/requests/", {
            "team_uuid": str(self.alpha.pk), "title": "Designer", "headcount": 1, "justification": "Cần tuyển",
        }, format="json")
        self.assertEqual(request.status_code, 201)
        application = self.client.post("/api/v1/recruitment/applications/", {
            "opening_uuid": request.data["opening_uuid"], "full_name": "Nguyễn Ứng Viên",
            "email": "candidate@example.test", "phone": "0900000000", "source": "Referral",
        }, format="json")
        self.assertEqual(application.status_code, 201)
        return application

    def test_hr_pipeline_and_conversion_are_idempotently_guarded(self):
        application = self._create_application()
        uuid = application.data["uuid"]
        for stage in ["screening", "interview", "offer", "hired"]:
            response = self.client.post(f"/api/v1/recruitment/applications/{uuid}/transition/", {"stage": stage, "note": stage}, format="json")
            self.assertEqual(response.status_code, 200)
        converted = self.client.post(f"/api/v1/recruitment/applications/{uuid}/convert-to-employee/", {
            "employee_code": "NEW-P3-01", "create_account": False, "username": "",
        }, format="json")
        self.assertEqual(converted.status_code, 201)
        self.assertEqual(converted.data["employee"]["employment_status"], Employee.EmploymentStatus.PROBATION)
        self.assertEqual(str(converted.data["employee"]["team"]), str(self.alpha.pk))
        repeated = self.client.post(f"/api/v1/recruitment/applications/{uuid}/convert-to-employee/", {
            "employee_code": "NEW-P3-02", "create_account": False, "username": "",
        }, format="json")
        self.assertEqual(repeated.status_code, 400)

    def test_leader_projection_redacts_candidate_contact_and_staff_is_denied(self):
        application = self._create_application()
        self.client.logout()
        self.login("leader.demo")
        response = self.client.get("/api/v1/recruitment/applications/")
        self.assertEqual(response.status_code, 200)
        row = next(item for item in response.data["results"] if item["uuid"] == application.data["uuid"])
        self.assertNotIn("candidate_email", row)
        self.assertNotIn("candidate_phone", row)
        self.assertNotIn("attachments", row)
        self.client.logout()
        self.login("staff.demo")
        self.assertEqual(self.client.get("/api/v1/recruitment/applications/").status_code, 403)

    def test_rejected_candidate_is_anonymized_after_six_months(self):
        candidate = Candidate.objects.create(full_name="Cần xóa", email="pii@example.test", phone="123")
        request = HiringRequest.objects.create(team=self.alpha, title="Test", justification="Test", requester=Employee.objects.get(employee_code="HRA01"), status=HiringRequest.Status.APPROVED)
        opening = JobOpening.objects.create(hiring_request=request, team=self.alpha, title="Test")
        application = Application.objects.create(
            candidate=candidate,
            opening=opening,
            created_by=Employee.objects.get(employee_code="HRA01").identity_user,
            stage=Application.Stage.REJECTED,
            retention_until=timezone.now() - timedelta(seconds=1),
        )
        self.assertEqual(anonymize_expired_candidates(), 1)
        candidate.refresh_from_db()
        self.assertEqual(candidate.email, "")
        self.assertIsNotNone(candidate.anonymized_at)

    def test_recruitment_options_only_offer_teams_in_actor_scope(self):
        self.login("leader.demo")
        response = self.client.get("/api/v1/recruitment/options/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([team["code"] for team in response.data["teams"]], ["ALPHA"])
