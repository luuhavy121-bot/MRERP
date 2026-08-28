from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from people_domain.capabilities import CEO_GROUP, HR_GROUP, LEADER_GROUP, STAFF_GROUP
from people_domain.models import Employee, Team, TeamLeadership


GROUP_PERMISSIONS = {
    HR_GROUP: ["view_employee", "add_employee", "change_employee", "view_hr_detail"],
    LEADER_GROUP: [
        "view_employee",
        "view_company_directory",
        "promote_employee",
        "manage_organization",
        "manage_membership",
        "add_team",
        "change_team",
        "view_team",
    ],
    STAFF_GROUP: ["view_employee"],
    CEO_GROUP: [
        "view_employee",
        "view_company_directory",
        "view_hr_detail",
        "add_employee",
        "change_employee",
        "promote_employee",
        "promote_any_employee",
        "manage_organization",
        "manage_membership",
        "view_people_audit",
        "add_team",
        "change_team",
        "view_team",
    ],
}


class Command(BaseCommand):
    help = "Create deterministic fake People/HR accounts and organization for local development."

    def add_arguments(self, parser):
        parser.add_argument("--password", required=True, help="Local-only password used for all demo accounts.")

    def handle(self, *args, **options):
        password = options["password"]
        groups = {}
        for group_name, codenames in GROUP_PERMISSIONS.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            permissions = Permission.objects.filter(content_type__app_label="people_domain", codename__in=codenames)
            group.permissions.set(permissions)
            groups[group_name] = group

        team_alpha, _ = Team.objects.update_or_create(code="ALPHA", defaults={"name": "Alpha", "department": None})
        team_beta, _ = Team.objects.update_or_create(code="BETA", defaults={"name": "Beta", "department": None})

        user_model = get_user_model()
        demos = [
            ("ceo.demo", "CEO01", Employee.Rank.CEO, groups[CEO_GROUP], None, "CEO Demo"),
            ("hr.demo", "HRA01", Employee.Rank.STAFF, groups[HR_GROUP], None, "HR Demo"),
            ("leader.demo", "LDR01", Employee.Rank.LEADER, groups[LEADER_GROUP], team_alpha, "Leader Alpha"),
            ("staff.demo", "STF01", Employee.Rank.STAFF, groups[STAFF_GROUP], team_alpha, "Staff Alpha"),
            ("other.demo", "OTH01", Employee.Rank.STAFF, groups[STAFF_GROUP], team_beta, "Staff Beta"),
        ]
        employees = {}
        for username, code, rank, group, team, display_name in demos:
            user, _ = user_model.objects.get_or_create(username=username, defaults={"is_active": True})
            user.set_password(password)
            user.is_active = True
            user.save(update_fields=["password", "is_active"])
            user.groups.set([group])
            employee, _ = Employee.objects.update_or_create(
                identity_user=user,
                defaults={
                    "employee_code": code,
                    "display_name": display_name,
                    "rank": rank,
                    "department": None,
                    "team": team,
                    "employment_status": Employee.EmploymentStatus.OFFICIAL,
                },
            )
            employees[username] = employee

        Employee.objects.update_or_create(
            employee_code="TRY-ALPHA-01",
            defaults={
                "identity_user": None,
                "display_name": "Nhân sự thử việc Alpha",
                "rank": Employee.Rank.STAFF,
                "department": None,
                "team": team_alpha,
                "employment_status": Employee.EmploymentStatus.PROBATION,
            },
        )

        TeamLeadership.objects.get_or_create(team=team_alpha, leader=employees["leader.demo"])
        self.stdout.write(self.style.SUCCESS("Created fake local accounts: ceo.demo, hr.demo, leader.demo, staff.demo, other.demo"))
