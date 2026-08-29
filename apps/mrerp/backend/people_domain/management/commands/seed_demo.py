from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from people_domain.capabilities import CEO_GROUP, HR_GROUP, LEADER_GROUP, STAFF_GROUP
from people_domain.models import Employee, Team, TeamLeadership
from preferences_domain.models import NotificationPreference


GROUP_PERMISSIONS = {
    HR_GROUP: [
        "view_employee", "add_employee", "change_employee", "view_hr_detail",
        "submit_leave_request", "view_own_leave_request", "view_company_attendance", "adjust_company_attendance",
        "change_own_profile", "change_own_password", "provision_employee_account",
        "manage_employee_account", "reset_employee_password", "change_employment_status",
        "import_export_employee", "view_people_audit",
        "view_post", "add_post", "add_comment", "add_postreaction", "share_post",
        "moderate_post", "publish_official_post",
        "view_task", "add_task", "update_task_progress",
        "manage_own_preferences",
        "create_hiring_request", "approve_hiring_request", "view_scoped_recruitment",
        "view_company_recruitment", "manage_candidates", "convert_candidate",
        "view_documents", "upload_documents", "view_hr_confidential_documents", "manage_all_documents",
        "view_rewards", "recognize_scoped", "recognize_company", "grant_stars_scoped",
        "grant_stars_company", "moderate_recognition",
    ],
    LEADER_GROUP: [
        "view_employee",
        "view_company_directory",
        "promote_employee",
        "manage_organization",
        "manage_membership",
        "add_team",
        "change_team",
        "view_team",
        "submit_leave_request",
        "view_own_leave_request",
        "review_team_leave_request",
        "change_own_profile",
        "change_own_password",
        "reset_employee_password",
        "view_post", "add_post", "add_comment", "add_postreaction", "share_post",
        "view_task", "add_task", "update_task_progress", "accept_task", "view_team_tasks",
        "manage_goals", "manage_recurrences",
        "manage_own_preferences",
        "create_hiring_request", "view_scoped_recruitment",
        "view_documents", "upload_documents",
        "view_rewards", "recognize_scoped", "grant_stars_scoped",
        "access_assetcontrol",
    ],
    STAFF_GROUP: [
        "view_employee", "submit_leave_request", "view_own_leave_request",
        "change_own_profile", "change_own_password",
        "view_post", "add_post", "add_comment", "add_postreaction", "share_post",
        "view_task", "add_task", "update_task_progress",
        "manage_own_preferences", "view_documents", "view_rewards",
    ],
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
        "submit_leave_request",
        "view_own_leave_request",
        "view_company_attendance",
        "adjust_company_attendance",
        "change_own_profile",
        "change_own_password",
        "provision_employee_account",
        "manage_employee_account",
        "reset_employee_password",
        "change_employment_status",
        "import_export_employee",
        "view_people_admin_panel",
        "manage_people_access",
        "view_post", "add_post", "add_comment", "add_postreaction", "share_post",
        "moderate_post", "publish_official_post",
        "view_task", "add_task", "update_task_progress", "accept_task", "view_team_tasks",
        "view_company_tasks", "manage_goals", "manage_company_goals", "manage_recurrences",
        "manage_own_preferences",
        "create_hiring_request", "approve_hiring_request", "view_scoped_recruitment",
        "view_company_recruitment", "manage_candidates", "convert_candidate",
        "view_documents", "view_company_documents", "upload_documents", "view_hr_confidential_documents", "manage_all_documents",
        "view_rewards", "recognize_scoped", "recognize_company", "grant_stars_scoped",
        "grant_stars_company", "moderate_recognition",
        "access_assetcontrol",
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
            permissions = Permission.objects.filter(
                codename__in=codenames,
                content_type__app_label__in=[
                    "people_domain", "leave_domain", "feed_domain", "task_domain",
                    "preferences_domain", "recruitment_domain", "documents_domain", "rewards_domain",
                ],
            )
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
            NotificationPreference.objects.update_or_create(
                employee=employee,
                defaults={"social_notifications_enabled": True},
            )

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
