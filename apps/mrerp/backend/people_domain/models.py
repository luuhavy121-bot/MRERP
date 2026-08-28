import uuid as uuid_lib

from django.conf import settings
from django.db import models
from django.db.models.functions import Lower


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Department(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    code = models.CharField(max_length=24, unique=True)
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Team(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="teams")
    code = models.CharField(max_length=24, unique=True)
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(TimeStampedModel):
    class EmploymentStatus(models.TextChoices):
        PROBATION = "probation", "Thử việc"
        OFFICIAL = "official", "Chính thức"

    class Rank(models.TextChoices):
        STAFF = "staff", "Staff"
        CAPTAIN = "captain", "Captain"
        LEADER = "leader", "Leader"
        MANAGER = "manager", "Manager"
        CEO = "ceo", "CEO"

    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    employee_code = models.CharField(max_length=64)
    identity_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="employee_profile",
        null=True,
        blank=True,
    )
    display_name = models.CharField(max_length=160, blank=True)
    national_id = models.CharField(max_length=32, unique=True, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
        null=True,
        blank=True,
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="members",
        null=True,
        blank=True,
    )
    rank = models.CharField(max_length=16, choices=Rank.choices, default=Rank.STAFF)
    employment_status = models.CharField(
        max_length=16,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.PROBATION,
    )
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["employee_code"]
        constraints = [
            models.UniqueConstraint(Lower("employee_code"), name="unique_employee_code_case_insensitive"),
        ]
        permissions = [
            ("view_company_directory", "Can view the company directory"),
            ("view_hr_detail", "Can view HR-only employee details"),
            ("promote_employee", "Can promote probation employees"),
            ("promote_any_employee", "Can promote probation employees across the company"),
            ("manage_organization", "Can manage departments and teams"),
            ("manage_membership", "Can manage team membership and leadership"),
            ("view_people_audit", "Can view People audit events"),
        ]

    def __str__(self):
        return self.display_name or self.employee_code


class TeamLeadership(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="leaderships")
    leader = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="led_team_links")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["team", "leader"], name="unique_team_leader"),
        ]


class EmploymentTransition(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="employment_transitions")
    from_status = models.CharField(max_length=16, choices=Employee.EmploymentStatus.choices)
    to_status = models.CharField(max_length=16, choices=Employee.EmploymentStatus.choices)
    note = models.TextField()
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    effective_at = models.DateTimeField()

    class Meta:
        ordering = ["-effective_at"]


class AuditEvent(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    action = models.CharField(max_length=80)
    target_type = models.CharField(max_length=80)
    target_uuid = models.CharField(max_length=64, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    correlation_id = models.UUIDField(default=uuid_lib.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
