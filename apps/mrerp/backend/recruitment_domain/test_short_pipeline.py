from importlib import import_module
from types import SimpleNamespace

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from rest_framework.test import APITestCase

from people_domain.models import Employee, Team
from .models import Application, ApplicationTransition, Candidate, HiringRequest, JobOpening
from .public import PublicOpeningSerializer


class ShortPipelineTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo', password='Test-Only-1234!', verbosity=0)
        cls.team = Team.objects.get(code='ALPHA')
        cls.leader = Employee.objects.get(employee_code='LDR01')
        cls.hiring = HiringRequest.objects.create(team=cls.team, requester=cls.leader, title='Test Ads', justification='Internal', utilization_plan='Run campaign A')
        cls.opening = JobOpening.objects.create(team=cls.team, hiring_request=cls.hiring, title='Test Ads')
        cls.application = Application.objects.create(opening=cls.opening, candidate=Candidate.objects.create(full_name='Synthetic candidate'), stage='interview')

    def login(self, name):
        self.client.force_authenticate(get_user_model().objects.get(username=name))

    def test_direct_hire_and_removed_offer_and_skipping_stage(self):
        self.login('leader.demo')
        url = f'/api/v1/recruitment/applications/{self.application.pk}/transition/'
        self.assertEqual(self.client.post(url, {'stage':'offer'}, format='json').status_code, 400)
        self.assertEqual(self.client.post(url, {'stage':'hired'}, format='json').status_code, 200)
        self.assertEqual(self.client.post(f'/api/v1/recruitment/applications/{self.application.pk}/convert-to-employee/', {'employee_code':'SYNTH-01', 'create_account':False, 'username':''}, format='json').status_code, 403)
        self.application.stage = 'new'; self.application.save()
        self.assertEqual(self.client.post(url, {'stage':'hired'}, format='json').status_code, 400)

    def test_plan_is_internal_draft_only_and_scoped(self):
        self.login('leader.demo')
        url = f'/api/v1/recruitment/requests/{self.hiring.pk}/'
        self.assertEqual(self.client.patch(url, {'utilization_plan':'New internal work'}, format='json').status_code, 200)
        self.assertEqual(self.client.get(url).data['utilization_plan'], 'New internal work')
        self.assertEqual(self.client.patch(url, {'utilization_plan':'a'*3001}, format='json').status_code, 400)
        self.hiring.refresh_from_db()
        self.assertNotIn('utilization_plan', PublicOpeningSerializer(self.opening).data)
        self.hiring.status = 'pending'; self.hiring.save()
        self.assertEqual(self.client.patch(url, {'utilization_plan':'Change submitted'}, format='json').status_code, 400)
        for name in ['staff.demo', 'other.demo']:
            self.login(name)
            self.assertIn(self.client.patch(url, {'utilization_plan':'Outside'}, format='json').status_code, [403,404])
        self.login('leader.demo')
        user = get_user_model().objects.get(username='leader.demo'); user.is_active=False; user.save()
        self.login('leader.demo')
        self.assertEqual(self.client.patch(url, {'utilization_plan':'Locked'}, format='json').status_code, 403)
        user.is_active=True; user.save()
        self.leader.employment_status='ended'; self.leader.save()
        self.login('leader.demo')
        self.assertEqual(self.client.patch(url, {'utilization_plan':'Ended'}, format='json').status_code, 403)

    def test_offer_migration_keeps_history_and_interview_data(self):
        user = get_user_model().objects.get(username='leader.demo')
        self.application.stage='offer'; self.application.version=4; self.application.recruiter_note='Keep note'; self.application.save()
        history = ApplicationTransition.objects.create(application=self.application, from_stage='interview', to_stage='offer', actor=user, note='Historical note')
        migration = import_module('recruitment_domain.migrations.0004_hiringrequest_utilization_plan_and_more')
        migration.collapse_offer(apps, SimpleNamespace(connection=connection))
        self.application.refresh_from_db(); history.refresh_from_db()
        self.assertEqual(self.application.stage,'interview')
        self.assertEqual(self.application.version,5)
        self.assertEqual(self.application.recruiter_note,'Keep note')
        self.assertEqual(history.to_stage,'offer')
        self.assertEqual(history.note,'Historical note')
        self.assertEqual(history.get_to_stage_display(),'Đề nghị (trước đây)')
