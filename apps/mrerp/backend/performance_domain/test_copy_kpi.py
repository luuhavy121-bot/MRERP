from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from people_domain.models import Employee
from .models import PerformanceReview, PerformanceKPI


class CopyKPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo",password="Test-Only-1234!",verbosity=0)
        cls.staff=Employee.objects.get(employee_code="STF01")
        cls.leader=Employee.objects.get(employee_code="LDR01")
        review=PerformanceReview.objects.create(employee=cls.staff,team=cls.staff.team,leader=cls.leader,month="2026-09-01",leader_comment="Old comment")
        PerformanceKPI.objects.create(review=review,title="Ads",description="Target",weight=100,completion=90,comment="Private assessment")

    def login(self,name):
        self.user=get_user_model().objects.get(username=name);self.client.force_authenticate(self.user)

    def test_copy_only_structure_and_history_scope(self):
        self.login("leader.demo")
        url=f"/api/v1/performance/reviews/kpi-source/?employee_uuid={self.staff.pk}&month=2026-10"
        r=self.client.get(url)
        self.assertEqual(r.status_code,200,r.data)
        self.assertEqual(r.data["kpis"][0],{"title":"Ads","description":"Target","weight":"100.00","completion":None,"comment":""})
        self.assertEqual(PerformanceReview.objects.count(),1)
        self.login("other.demo");self.assertEqual(self.client.get(url).status_code,403)
        self.login("staff.demo");self.assertEqual(self.client.get(url).status_code,403)
        self.assertEqual(self.client.get(f"/api/v1/performance/reviews/?employee_uuid={self.staff.pk}").data["count"],0)
        self.login("leader.demo");self.user.is_active=False;self.user.save()
        self.assertEqual(self.client.get(url).status_code,403)

    def test_empty_previous_month(self):
        self.login("leader.demo")
        r=self.client.get(f"/api/v1/performance/reviews/kpi-source/?employee_uuid={self.staff.pk}&month=2026-11")
        self.assertEqual(r.status_code,200);self.assertEqual(r.data["kpis"],[])
