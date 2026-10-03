from io import StringIO
import json

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from .models import Employee, Team, TeamLeadership


class LocalReadinessTests(TestCase):
    def test_inventory_distinguishes_available_and_inactive_leaders_without_pii(self):
        team = Team.objects.create(code="LOCAL", name="Private team name")
        user = get_user_model().objects.create_user("private.user", password="Test-Only-1234!")
        leader = Employee.objects.create(employee_code="PRIVATE", display_name="Private employee name", team=team, identity_user=user)
        TeamLeadership.objects.create(team=team, leader=leader)
        output = StringIO()
        call_command("local_readiness", stdout=output)
        report = json.loads(output.getvalue())
        self.assertEqual(report["active_teams_without_available_leader"], 0)
        self.assertFalse(report["production_ready"])
        self.assertNotIn("private.user", output.getvalue())
        self.assertNotIn("Private employee name", output.getvalue())
        user.is_active = False
        user.save(update_fields=["is_active"])
        output = StringIO()
        call_command("local_readiness", stdout=output)
        self.assertEqual(json.loads(output.getvalue())["active_teams_without_available_leader"], 1)

    @override_settings(APP_ENV="production")
    def test_local_inventory_cannot_run_in_production(self):
        with self.assertRaises(CommandError):
            call_command("local_readiness")
