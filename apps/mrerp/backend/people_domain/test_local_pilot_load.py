"""Bounded HTTP concurrency smoke test, not a VPS capacity or SLA certification."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from http.cookiejar import CookieJar
import json
from statistics import median
import threading
import time
from urllib.request import build_opener, HTTPCookieProcessor, Request
from unittest import skipUnless

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.test import LiveServerTestCase
from django.utils import timezone

from people_domain.models import Employee, Team
from task_domain.models import Task


@skipUnless(connection.vendor == "postgresql", "HTTP concurrency evidence requires PostgreSQL")
class LocalPilotConcurrencyTests(LiveServerTestCase):
    def test_ten_distinct_staff_sessions_read_without_cross_scope_or_http_errors(self):
        call_command("seed_demo", password="Test-Only-Pilot-1234!")
        team = Team.objects.get(code="ALPHA")
        creator = Employee.objects.get(identity_user__username="leader.demo")
        staff = get_user_model().objects.get(username="staff.demo")
        usernames = []
        for i in range(10):
            user = get_user_model().objects.create_user(f"load.fixture.{i}", password="Test-Only-Pilot-1234!")
            user.groups.set(staff.groups.all())
            employee = Employee.objects.create(employee_code=f"LOAD-{i}", display_name=f"Fixture {i}", team=team,
                                               identity_user=user, employment_status="official")
            Task.objects.bulk_create([Task(title=f"Load fixture {i}-{j}", creator=creator, assignee=employee,
                team=team, due_at=timezone.now()+timedelta(days=1)) for j in range(50)])
            usernames.append(user.username)
        barrier = threading.Barrier(10)

        def read_session(username):
            opener = build_opener(HTTPCookieProcessor(CookieJar()))
            with opener.open(self.live_server_url+"/api/v1/auth/session/", timeout=30) as response:
                token = json.load(response)["csrf_token"]
            login = Request(self.live_server_url+"/api/v1/auth/login/", method="POST",
                data=json.dumps({"username":username,"password":"Test-Only-Pilot-1234!"}).encode(),
                headers={"Content-Type":"application/json","X-CSRFToken":token,"Origin":self.live_server_url})
            with opener.open(login, timeout=30) as response:
                if not json.load(response)["authenticated"]:
                    raise AssertionError("Fixture session did not authenticate.")
            barrier.wait(timeout=30)
            timings = []
            for _ in range(5):
                for path in ("/api/v1/dashboard/", "/api/v1/tasks/tasks/", "/api/v1/people/employees/"):
                    started = time.perf_counter()
                    with opener.open(self.live_server_url+path, timeout=30) as response:
                        payload = json.load(response)
                        if response.status != 200:
                            raise AssertionError("Authenticated read failed.")
                        if path == "/api/v1/tasks/tasks/" and payload["count"] != 50:
                            raise AssertionError("Staff task scope leaked or omitted assigned fixtures.")
                    timings.append((time.perf_counter()-started)*1000)
            return timings

        with ThreadPoolExecutor(max_workers=10) as pool:
            timings = sorted(n for batch in pool.map(read_session, usernames) for n in batch)
        self.assertEqual(len(timings),150)
        print(json.dumps({"local_http_concurrency":10,"fixture_tasks":500,"authenticated_reads":150,
            "http_errors":0,"p50_ms":round(median(timings),2),"p95_ms":round(timings[int(len(timings)*.95)-1],2),
            "max_ms":round(max(timings),2),"scope":"isolated PostgreSQL test DB + Django LiveServer; not production capacity"}))
