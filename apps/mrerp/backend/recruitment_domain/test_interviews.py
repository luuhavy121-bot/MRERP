from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APITestCase
from people_domain.models import Employee, Team
from .models import Candidate, HiringRequest, JobOpening, Application
from .services import anonymize_expired_candidates


class InterviewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", password="Test-Only-1234!", verbosity=0)
        team=Team.objects.get(code="ALPHA")
        hiring=HiringRequest.objects.create(team=team,requester=Employee.objects.get(employee_code="LDR01"),title="Test Ads")
        opening=JobOpening.objects.create(team=team,hiring_request=hiring,title="Test Ads")
        cls.application=Application.objects.create(opening=opening,candidate=Candidate.objects.create(full_name="Test Candidate"))

    def login(self,name):
        self.user=get_user_model().objects.get(username=name);self.client.force_authenticate(self.user)

    def payload(self,version=1):
        return {"version":version,"interview_at":"2026-10-05T09:00:00+07:00","interviewer_name":"Leader Test","recruiter_note":"Private note"}

    def test_save_conflict_and_redacted_audit(self):
        self.login("leader.demo")
        url=f"/api/v1/recruitment/applications/{self.application.pk}/interview/"
        r=self.client.post(url,self.payload(),format="json")
        self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data["version"],2)
        self.assertEqual(r.data["recruiter_note"],"Private note")
        self.assertEqual(self.client.post(url,self.payload(),format="json").status_code,409)
        from people_domain.models import AuditEvent
        self.assertNotIn("Private note",str(AuditEvent.objects.latest("created_at").changes))

    def test_outside_scope_missing_capability_locked_ended_and_terminal(self):
        url=f"/api/v1/recruitment/applications/{self.application.pk}/interview/"
        for name,status in (("other.demo",403),("staff.demo",403)):
            self.login(name);self.assertEqual(self.client.post(url,self.payload(),format="json").status_code,status)
        self.login("leader.demo")
        self.user.is_active=False;self.user.save()
        self.assertEqual(self.client.post(url,self.payload(),format="json").status_code,403)
        self.user.is_active=True;self.user.save()
        employee=self.user.employee_profile;employee.employment_status="ended";employee.save()
        self.assertEqual(self.client.post(url,self.payload(),format="json").status_code,403)
        self.login("hr.demo")
        self.application.stage="rejected";self.application.save()
        self.assertEqual(self.client.post(url,self.payload(),format="json").status_code,400)

    def test_validation_retention_and_nonmanager_projection(self):
        self.login("leader.demo")
        url=f"/api/v1/recruitment/applications/{self.application.pk}/interview/"
        data=self.payload();data["interviewer_name"]=""
        self.assertEqual(self.client.post(url,data,format="json").status_code,400)
        self.client.post(url,self.payload(),format="json")
        permission=Permission.objects.get(codename="manage_candidates")
        for group in self.user.groups.all():group.permissions.remove(permission)
        self.login("leader.demo")
        r=self.client.get(f"/api/v1/recruitment/applications/{self.application.pk}/")
        self.assertEqual(r.status_code,200)
        for field in ("interview_at","interviewer_name","recruiter_note","candidate_email"):
            self.assertNotIn(field,r.data)
        app=Application.objects.get(pk=self.application.pk);app.stage="rejected";app.retention_until=timezone.now()-timedelta(days=1);app.save()
        anonymize_expired_candidates();app.refresh_from_db()
        self.assertEqual(app.recruiter_note,"");self.assertIsNone(app.interview_at)

    def test_notifications_require_capability_and_team_or_company_scope(self):
        from dashboard_domain.models import Notification
        from .interviews import notify_recruitment_owners
        outsider = get_user_model().objects.get(username="other.demo")
        outsider.user_permissions.add(Permission.objects.get(codename="approve_hiring_request"))
        notify_recruitment_owners(self.application.opening.team_id, "Scope test", self.application.pk, approval=True)
        recipients = Notification.objects.filter(title="Scope test").values_list("recipient__identity_user__username", flat=True)
        self.assertNotIn("other.demo", recipients)
        self.assertIn("hr.demo", recipients)
