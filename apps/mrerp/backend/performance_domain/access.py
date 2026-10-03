from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from people_domain.access import get_actor_employee
from people_domain.models import Employee, TeamLeadership
from .models import PerformanceReview

MANAGE = "performance_domain.manage_team_reviews"
COMPANY = "performance_domain.view_company_reviews"
REOPEN = "performance_domain.reopen_reviews"
OWN = "performance_domain.view_own_reviews"


def teams(user):
    return TeamLeadership.objects.filter(leader=get_actor_employee(user), team__is_active=True).values_list("team_id", flat=True)


def can_manage(user, review):
    actor = get_actor_employee(user)
    return user.has_perm(MANAGE) and review.employee_id != actor.pk and review.team_id == review.employee.team_id and review.team_id in teams(user) and review.employee.employment_status in {"probation", "official"}


def visible_reviews(user):
    actor = get_actor_employee(user)
    qs = PerformanceReview.objects.select_related("employee", "team", "leader").prefetch_related("kpis", "revisions")
    if user.has_perm(COMPANY):
        return qs
    scope = Q(pk__in=[])
    if user.has_perm(OWN):
        scope |= Q(employee=actor, status__in=["finalized", "acknowledged"])
    if user.has_perm(MANAGE):
        scope |= Q(team_id__in=teams(user), employee__team_id__in=teams(user)) & ~Q(employee=actor)
    if not user.has_perm(OWN) and not user.has_perm(MANAGE):
        raise PermissionDenied("Bạn không có quyền xem đánh giá.")
    return qs.filter(scope)


def eligible_employees(user):
    actor = get_actor_employee(user)
    if not user.has_perm(MANAGE):
        return Employee.objects.none()
    return Employee.objects.filter(team_id__in=teams(user), employment_status__in=["probation", "official"]).exclude(pk=actor.pk).select_related("team")
