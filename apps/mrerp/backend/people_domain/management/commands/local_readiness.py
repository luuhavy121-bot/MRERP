"""Read-only local pilot inventory. Never a production approval or a data export."""
import json
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.models import Exists, OuterRef

from people_domain.models import Employee, Team, TeamLeadership


class Command(BaseCommand):
    help = "Report local pilot prerequisites without changing accounts or printing personal data."

    def handle(self, *args, **options):
        if settings.APP_ENV not in {"development", "test"}:
            raise CommandError("This inventory is restricted to development/test.")
        pending = MigrationExecutor(connection).migration_plan(
            MigrationExecutor(connection).loader.graph.leaf_nodes()
        )
        active = Employee.objects.filter(employment_status__in=["probation", "official"])
        valid_leaders = TeamLeadership.objects.filter(
            team_id=OuterRef("pk"), leader__employment_status__in=["probation", "official"],
            leader__identity_user__is_active=True,
        )
        report = {
            "environment": settings.APP_ENV,
            "mock_identity": settings.MOCK_IDENTITY_ENABLED,
            "debug": settings.DEBUG,
            "database_vendor": connection.vendor,
            "pending_migrations": len(pending),
            "employees": Employee.objects.count(),
            "active_employees": active.count(),
            "active_without_account": active.filter(identity_user__isnull=True).count(),
            "active_without_team": active.exclude(rank="ceo").filter(team__isnull=True).count(),
            "active_teams_without_available_leader": Team.objects.filter(is_active=True).annotate(
                has_available_leader=Exists(valid_leaders)
            ).filter(has_available_leader=False).count(),
            "demo_accounts": get_user_model().objects.filter(username__endswith=".demo").count(),
            "media_directory_exists": settings.MEDIA_ROOT.is_dir(),
            "media_directory_writable": os.access(settings.MEDIA_ROOT, os.W_OK),
            "production_ready": False,
            "production_blockers": [
                "Identity Provider and account lifecycle adapter have not been selected/implemented.",
                "Local Docker uses development web servers and publishes database ports.",
                "VPS capacity, HTTPS, off-host backup and operational policies need review.",
            ],
        }
        self.stdout.write(json.dumps(report, ensure_ascii=False))
