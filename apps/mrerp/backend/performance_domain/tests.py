from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from rest_framework.test import APIClient
from people_domain.models import Employee
from .models import PerformanceReview

class PerformanceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", password="Local-Demo-1234!")
    def setUp(self):
        self.client = APIClient()
        self.staff = Employee.objects.get(identity_user__username="staff.demo")
        self.other = Employee.objects.get(identity_user__username="other.demo")
        self.login("leader.demo")
    def login(self, name):
        self.client.force_authenticate(get_user_model().objects.get(username=name))
    def create(self, employee=None):
        return self.client.post("/api/v1/performance/reviews/", {"employee_uuid": str((employee or self.staff).pk), "month": "2026-10"}, format="json")
    def prepare(self):
        r = self.create()
        self.assertEqual(r.status_code, 201, r.data)
        url = f"/api/v1/performance/reviews/{r.data['uuid']}/"
        r = self.client.patch(url, {"version": 1, "leader_comment": "Hoàn thành tốt", "kpis": [
            {"title": "Chất lượng", "weight": "33.33", "completion": "90.12"},
            {"title": "Sản lượng", "weight": "66.67", "completion": "80.55"},
        ]}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        return url
    def test_complete_review_reopen_preserves_snapshot_and_feedback(self):
        url=self.prepare()
        r=self.client.post(url+"finalize/", {"version":2}, format="json")
        self.assertEqual(r.status_code,200,r.data)
        self.assertEqual(r.data["total_score"],"83.74")
        self.assertEqual(len(r.data["revisions"]),1)
        self.assertEqual(self.client.patch(url,{"version":3,"leader_comment":"sửa"},format="json").status_code,400)
        self.login("staff.demo")
        r=self.client.post(url+"acknowledge/",{"version":3,"employee_feedback":"Đã đọc"},format="json")
        self.assertEqual(r.status_code,200,r.data)
        self.assertEqual(r.data["status"],"acknowledged")
        self.login("hr.demo")
        self.assertEqual(self.client.post(url+"reopen/",{"version":4},format="json").status_code,400)
        r=self.client.post(url+"reopen/",{"version":4,"reason":"Cần sửa chỉ tiêu"},format="json")
        self.assertEqual(r.status_code,200,r.data)
        self.assertEqual(r.data["revisions"][-1]["snapshot"]["employee_feedback"],"Đã đọc")
        self.assertEqual(r.data["status"],"draft")
        self.login("staff.demo")
        self.assertEqual(self.client.get(url).status_code,404)
        self.login("leader.demo")
        r=self.client.post(url+"finalize/",{"version":5},format="json")
        self.assertEqual(r.status_code,200,r.data)
        self.assertEqual(len(r.data["revisions"]),3)
    def test_scope_capability_and_draft_redaction(self):
        self.assertEqual(self.create(self.other).status_code,403)
        own=Employee.objects.get(identity_user__username="leader.demo")
        self.assertEqual(self.create(own).status_code,403)
        url=self.prepare()
        for name in ["staff.demo","other.demo"]:
            self.login(name)
            self.assertEqual(self.client.get(url).status_code,404)
            self.assertEqual(self.client.get("/api/v1/performance/reviews/").data["count"],0)
            self.assertEqual(self.create().status_code,403)
        for name in ["hr.demo","ceo.demo"]:
            self.login(name)
            self.assertEqual(self.client.get(url).status_code,200)
            self.assertEqual(self.client.patch(url,{"version":2,"leader_comment":"x"},format="json").status_code,403)
            self.assertEqual(self.create(self.other).status_code,403)
    def test_missing_capability_invalid_account_and_employment(self):
        url=self.prepare()
        user=get_user_model().objects.get(username="leader.demo")
        user.groups.clear()
        self.client.force_authenticate(get_user_model().objects.get(pk=user.pk))
        self.assertEqual(self.client.get(url).status_code,403)
        for name,field,value in [("hr.demo","is_active",False),("ceo.demo","employment_status","terminated")]:
            user=get_user_model().objects.get(username=name)
            target=user if field=="is_active" else user.employee_profile
            setattr(target,field,value);target.save()
            self.client.force_authenticate(get_user_model().objects.get(pk=user.pk))
            self.assertEqual(self.client.get(url).status_code,403)
    def test_invalid_kpis_unique_and_stale_version(self):
        r=self.create();url=f"/api/v1/performance/reviews/{r.data['uuid']}/"
        self.assertEqual(self.create().status_code,409)
        self.assertEqual(self.client.post(url+"finalize/",{"version":1},format="json").status_code,400)
        for kpis in [[{"title":"x","weight":101,"completion":10}],[{"title":"x","weight":100,"completion":-1}]]:
            self.assertEqual(self.client.patch(url,{"version":1,"kpis":kpis},format="json").status_code,400)
        payload={"version":1,"leader_comment":"note","kpis":[{"title":"x","weight":90,"completion":50}]}
        self.assertEqual(self.client.patch(url,payload,format="json").status_code,200)
        self.assertEqual(self.client.patch(url,payload,format="json").status_code,409)
        self.assertEqual(self.client.post(url+"finalize/",{"version":2},format="json").status_code,400)
        self.staff.employment_status="terminated";self.staff.save()
        self.assertEqual(self.client.patch(url,{"version":2},format="json").status_code,403)
    def test_month_validation_and_task_context_scope(self):
        self.assertEqual(self.client.get("/api/v1/performance/reviews/?month=2026-99").status_code,400)
        self.assertEqual(self.client.get(f"/api/v1/performance/context/?employee_uuid={self.other.pk}&month=2026-10").status_code,403)
        self.assertEqual(self.client.get(f"/api/v1/performance/context/?employee_uuid={self.staff.pk}&month=2026-10").status_code,200)


from unittest import skipUnless
from django.db import connection, connections
from django.test import TransactionTestCase
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

@skipUnless(connection.vendor == "postgresql", "Row-lock concurrency requires PostgreSQL")
class PerformanceConcurrencyTests(TransactionTestCase):
    def test_two_writers_with_same_version_only_one_succeeds(self):
        call_command("seed_demo", password="Local-Demo-1234!")
        leader=Employee.objects.get(identity_user__username="leader.demo")
        staff=Employee.objects.get(identity_user__username="staff.demo")
        review=PerformanceReview.objects.create(employee=staff, team=staff.team, leader=leader, month="2026-10-01")
        barrier=Barrier(2)
        def write(note):
            try:
                client=APIClient()
                client.force_authenticate(get_user_model().objects.get(username="leader.demo"))
                barrier.wait(timeout=10)
                return client.patch(f"/api/v1/performance/reviews/{review.pk}/", {"version":1,"leader_comment":note}, format="json").status_code
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(write,["A","B"]))
        self.assertEqual(sorted(results),[200,409])
        review.refresh_from_db()
        self.assertEqual(review.version,2)
