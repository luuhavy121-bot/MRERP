from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from people_domain.models import Employee, Team

from .models import Goal, Recurrence, Task
from .services import generate_due_occurrences


@override_settings(MEDIA_ROOT="test-media-task")
class TaskApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", password="Test-only-1234!")

    def login_as(self, username):
        user = get_user_model().objects.get(username=username)
        self.client.force_authenticate(user)
        return user

    def task_payload(self, assignee_username="staff.demo", **overrides):
        assignee = get_user_model().objects.get(username=assignee_username).employee_profile
        payload = {"title": "Chốt báo cáo tuần", "description": "Đối chiếu số liệu", "assignee_uuid": str(assignee.pk), "due_at": (timezone.now() + timedelta(days=2)).isoformat(), "goal_uuid": None}
        payload.update(overrides)
        return payload

    def test_staff_self_assign_only_and_team_scope_does_not_leak(self):
        self.login_as("staff.demo")
        created = self.client.post("/api/v1/tasks/tasks/", self.task_payload(), format="json")
        self.assertEqual(created.status_code, 201)
        denied = self.client.post("/api/v1/tasks/tasks/", self.task_payload("other.demo"), format="json")
        self.assertEqual(denied.status_code, 403)
        self.login_as("other.demo")
        self.assertEqual(self.client.get("/api/v1/tasks/tasks/").data["count"], 0)

    def test_leader_assigns_submits_accepts_and_goal_reaches_100(self):
        leader = self.login_as("leader.demo")
        today = timezone.localdate()
        team = leader.employee_profile.team
        goal_response = self.client.post("/api/v1/tasks/goals/", {"title": "Vận hành tuần", "description": "", "scope": "team", "team_uuid": str(team.pk), "period": "week", "starts_on": str(today), "ends_on": str(today + timedelta(days=7))}, format="json")
        self.assertEqual(goal_response.status_code, 201)
        task_response = self.client.post("/api/v1/tasks/tasks/", self.task_payload(goal_uuid=goal_response.data["uuid"]), format="json")
        self.assertEqual(task_response.status_code, 201)
        task_id = task_response.data["uuid"]
        self.login_as("staff.demo")
        self.assertEqual(self.client.patch(f"/api/v1/tasks/tasks/{task_id}/", {"progress": 80}, format="json").status_code, 200)
        self.assertEqual(self.client.post(f"/api/v1/tasks/tasks/{task_id}/transition/", {"action": "submit", "note": ""}, format="json").status_code, 200)
        self.login_as("leader.demo")
        accepted = self.client.post(f"/api/v1/tasks/tasks/{task_id}/transition/", {"action": "accept", "note": "Đạt"}, format="json")
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.data["progress"], 100)
        goal = self.client.get(f"/api/v1/tasks/goals/{goal_response.data['uuid']}/")
        self.assertEqual(goal.data["progress"], 100)

    def test_self_task_cannot_be_self_accepted(self):
        self.login_as("leader.demo")
        task = self.client.post("/api/v1/tasks/tasks/", self.task_payload("leader.demo"), format="json").data
        self.client.post(f"/api/v1/tasks/tasks/{task['uuid']}/transition/", {"action": "submit", "note": ""}, format="json")
        denied = self.client.post(f"/api/v1/tasks/tasks/{task['uuid']}/transition/", {"action": "accept", "note": ""}, format="json")
        self.assertEqual(denied.status_code, 403)

    def test_ceo_cannot_create_self_task(self):
        self.login_as("ceo.demo")
        self.assertEqual(self.client.post("/api/v1/tasks/tasks/", self.task_payload("ceo.demo"), format="json").status_code, 400)

    def test_monthly_recurrence_backfills_idempotently_and_clamps_month_end(self):
        leader = self.login_as("leader.demo")
        assignee = get_user_model().objects.get(username="staff.demo").employee_profile
        start = timezone.make_aware(timezone.datetime(2026, 1, 31, 9, 0))
        series = Recurrence.objects.create(title="Đối soát tháng", creator=leader.employee_profile, assignee=assignee, team=assignee.team, frequency="monthly", interval=1, start_at=start, next_occurrence_at=start, anchor_day=31, deadline_offset_minutes=60)
        generated = generate_due_occurrences(series, timezone.make_aware(timezone.datetime(2026, 3, 1, 0, 0)))
        self.assertEqual(generated, 2)
        self.assertEqual(list(series.occurrences.order_by("scheduled_for").values_list("scheduled_for__day", flat=True)), [31, 28])
        self.assertEqual(generate_due_occurrences(series, timezone.make_aware(timezone.datetime(2026, 3, 1, 0, 0))), 0)

    def test_paused_recurrence_does_not_generate(self):
        leader = self.login_as("leader.demo")
        assignee = get_user_model().objects.get(username="staff.demo").employee_profile
        now = timezone.now() - timedelta(days=2)
        series = Recurrence.objects.create(title="Daily", creator=leader.employee_profile, assignee=assignee, team=assignee.team, frequency="daily", interval=1, start_at=now, next_occurrence_at=now, deadline_offset_minutes=60, status=Recurrence.Status.PAUSED)
        self.assertEqual(generate_due_occurrences(series), 0)
        self.assertEqual(Task.objects.filter(recurrence=series).count(), 0)

    def test_leader_cannot_assign_outside_led_team_or_change_assignee_progress(self):
        self.login_as("leader.demo")
        self.assertEqual(
            self.client.post("/api/v1/tasks/tasks/", self.task_payload("other.demo"), format="json").status_code,
            403,
        )
        task = self.client.post("/api/v1/tasks/tasks/", self.task_payload(), format="json").data
        self.assertEqual(
            self.client.patch(f"/api/v1/tasks/tasks/{task['uuid']}/", {"progress": 50}, format="json").status_code,
            403,
        )

    def test_goal_and_recurrence_require_task_capability(self):
        user = self.login_as("staff.demo")
        user.groups.clear()
        self.assertEqual(self.client.get("/api/v1/tasks/goals/").status_code, 403)
        self.assertEqual(self.client.get("/api/v1/tasks/recurrences/").status_code, 403)

    def test_task_attachment_is_protected_outside_task_scope(self):
        self.login_as("leader.demo")
        task = self.client.post("/api/v1/tasks/tasks/", self.task_payload(), format="json").data
        upload = SimpleUploadedFile("brief.txt", b"internal brief", content_type="text/plain")
        response = self.client.post(
            f"/api/v1/tasks/tasks/{task['uuid']}/attachments/",
            {"kind": "brief", "attachments": upload},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        download_url = response.data[0]["download_url"]
        self.login_as("other.demo")
        self.assertEqual(self.client.get(download_url).status_code, 404)
