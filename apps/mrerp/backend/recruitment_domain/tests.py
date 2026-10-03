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
        self.assertEqual(response.data["status"], HiringRequest.Status.DRAFT)
        self.submit_request(response.data["uuid"])
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

    def submit_request(self, uuid):
        response = self.client.patch(f"/api/v1/recruitment/requests/{uuid}/", {
            "location": "Hà Nội", "employment_type": "Full time", "description": "Mô tả", "requirements": "Yêu cầu", "benefits": "Quyền lợi", "deadline": str(timezone.localdate() + timedelta(days=30))
        }, format="json")
        self.assertEqual(response.status_code, 200)
        response = self.client.post(f"/api/v1/recruitment/requests/{uuid}/submit/", {}, format="json")
        self.assertEqual(response.status_code, 200)

    def _create_application(self):
        self.login("hr.demo")
        request = self.client.post("/api/v1/recruitment/requests/", {
            "team_uuid": str(self.alpha.pk), "title": "Designer", "headcount": 1, "justification": "Cần tuyển",
        }, format="json")
        self.assertEqual(request.status_code, 201)
        self.submit_request(request.data["uuid"])
        request = self.client.post(f"/api/v1/recruitment/requests/{request.data['uuid']}/review/", {"decision": "approved"}, format="json")
        application = self.client.post("/api/v1/recruitment/applications/", {
            "opening_uuid": request.data["opening_uuid"], "full_name": "Nguyễn Ứng Viên",
            "email": "candidate@example.test", "phone": "0900000000", "source": "Referral",
        }, format="json")
        self.assertEqual(application.status_code, 201)
        return application

    def test_hr_pipeline_and_conversion_are_idempotently_guarded(self):
        application = self._create_application()
        uuid = application.data["uuid"]
        for stage in ["screening", "interview", "hired"]:
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

    def test_leader_can_view_team_contact_and_staff_is_denied(self):
        application = self._create_application()
        self.client.logout()
        self.login("leader.demo")
        response = self.client.get("/api/v1/recruitment/applications/")
        self.assertEqual(response.status_code, 200)
        row = next(item for item in response.data["results"] if item["uuid"] == application.data["uuid"])
        self.assertIn("candidate_email", row)
        self.assertIn("candidate_phone", row)
        self.assertIn("attachments", row)
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


class PublicRecruitmentTests(RecruitmentApiTests):
    def setUp(self):
        super().setUp()
        import tempfile
        from django.test import override_settings
        from django.core.cache import cache
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        override = override_settings(MEDIA_ROOT=self.media.name)
        override.enable(); self.addCleanup(override.disable)
        cache.clear()

    def public_payload(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        return {"full_name":"Ứng viên public", "email":"public@example.test", "introduction":"Giới thiệu", "consent":"true", "cv":SimpleUploadedFile("cv.pdf",b"%PDF-1.4 test",content_type="application/pdf")}

    def opening(self):
        application=self._create_application()
        return Application.objects.get(pk=application.data["uuid"]).opening

    def test_public_submission_and_projection(self):
        opening=self.opening();self.client.logout()
        url=f"/api/v1/public/recruitment/openings/{opening.slug}/"
        r=self.client.get(url)
        self.assertEqual(r.status_code,200,r.data)
        for field in ["justification","requester","hiring_request","uuid"]:
            self.assertNotIn(field,r.data)
        r=self.client.post(url+"applications/",self.public_payload(),format="multipart")
        self.assertEqual(r.status_code,201,r.data)
        self.assertNotIn("uuid",r.data)
        application=Application.objects.get(candidate__email="public@example.test")
        self.assertIsNone(application.created_by_id)
        self.assertIsNotNone(application.consent_at)
        self.assertEqual(application.attachments.count(),1)
        download=f"/api/v1/recruitment/attachments/{application.attachments.get().pk}/download/"
        self.assertEqual(self.client.get(download).status_code,403)
        self.login("leader.demo")
        response=self.client.get(download);self.assertEqual(response.status_code,200);self.assertTrue(b"%PDF" in b"".join(response.streaming_content))
        self.assertEqual(self.client.post(f"/api/v1/recruitment/applications/{application.pk}/convert-to-employee/",{"employee_code":"x"},format="json").status_code,403)

    def test_invalid_cv_consent_contact_throttle(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        opening=self.opening();self.client.logout();url=f"/api/v1/public/recruitment/openings/{opening.slug}/applications/"
        p=self.public_payload();p["consent"]="false";self.assertEqual(self.client.post(url,p,format="multipart").status_code,400)
        p=self.public_payload();p["email"]="";self.assertEqual(self.client.post(url,p,format="multipart").status_code,400)
        p=self.public_payload();p["cv"]=SimpleUploadedFile("bad.pdf",b"<script>x</script>",content_type="application/pdf");self.assertEqual(self.client.post(url,p,format="multipart").status_code,400)
        p=self.public_payload();p["cv"]=SimpleUploadedFile("large.pdf",b"%PDF-"+b"0"*(10*1024*1024),content_type="application/pdf");self.assertEqual(self.client.post(url,p,format="multipart").status_code,400)
        p=self.public_payload();p["cv"]=SimpleUploadedFile("a.txt",b"text",content_type="text/plain");self.assertEqual(self.client.post(url,p,format="multipart").status_code,400)
        self.assertEqual(self.client.post(url,self.public_payload(),format="multipart").status_code,429)

    def test_legacy_expired_closed_and_cross_team(self):
        opening=self.opening()
        opening.published_at=None;opening.save()
        public=f"/api/v1/public/recruitment/openings/{opening.slug}/"
        self.assertEqual(self.client.get(public).status_code,404)
        opening.published_at=timezone.now();opening.save()
        hr=opening.hiring_request;hr.deadline=timezone.localdate()-timedelta(days=1);hr.save()
        self.assertEqual(self.client.get(public).status_code,404)
        hr.deadline=timezone.localdate()+timedelta(days=1);hr.save()
        opening.team=self.beta;opening.save()
        self.client.logout();self.login("leader.demo")
        application=opening.applications.first()
        self.assertEqual(self.client.get(f"/api/v1/recruitment/applications/{application.pk}/").status_code,404)
        self.assertEqual(self.client.post("/api/v1/recruitment/applications/",{"opening_uuid":str(opening.pk),"full_name":"x"},format="json").status_code,403)
        self.assertEqual(self.client.post(f"/api/v1/recruitment/openings/{opening.pk}/close/",{},format="json").status_code,403)
        self.client.logout();self.login("hr.demo")
        self.assertEqual(self.client.post(f"/api/v1/recruitment/openings/{opening.pk}/close/",{},format="json").status_code,200)
        self.assertEqual(self.client.get(public).status_code,404)

    def test_recruitment_account_gate_and_missing_capability(self):
        from django.contrib.auth import get_user_model
        opening=self.opening()
        user=get_user_model().objects.get(username="leader.demo")
        user.groups.clear();self.client.force_authenticate(user)
        self.assertEqual(self.client.get("/api/v1/recruitment/applications/").status_code,403)
        user=get_user_model().objects.get(username="hr.demo");user.is_active=False;user.save();self.client.force_authenticate(user)
        self.assertEqual(self.client.get("/api/v1/recruitment/applications/").status_code,403)
        user=get_user_model().objects.get(username="ceo.demo");employee=user.employee_profile;employee.employment_status="terminated";employee.save();self.client.force_authenticate(user)
        self.assertEqual(self.client.get("/api/v1/recruitment/applications/").status_code,403)
