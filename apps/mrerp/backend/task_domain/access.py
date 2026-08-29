from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

from people_domain.access import get_actor_employee
from people_domain.models import TeamLeadership

from .capabilities import VIEW_COMPANY_TASKS, VIEW_TASK, VIEW_TEAM_TASKS
from .models import Goal, Recurrence, Task


def led_team_ids(actor):
    return TeamLeadership.objects.filter(leader=actor).values_list("team_id", flat=True)


def visible_tasks(user):
    actor = get_actor_employee(user)
    if not user.has_perm(VIEW_TASK):
        raise PermissionDenied("Bạn không có capability đọc Công việc.")
    if user.has_perm(VIEW_COMPANY_TASKS):
        return Task.objects.all()
    scope = Q(creator=actor) | Q(assignee=actor)
    if user.has_perm(VIEW_TEAM_TASKS):
        scope |= Q(team_id__in=led_team_ids(actor))
    return Task.objects.filter(scope).distinct()


def visible_goals(user):
    actor = get_actor_employee(user)
    if not user.has_perm(VIEW_TASK):
        raise PermissionDenied("Bạn không có capability đọc mục tiêu công việc.")
    scope = Q(scope=Goal.Scope.COMPANY)
    if actor.team_id:
        scope |= Q(scope=Goal.Scope.TEAM, team_id=actor.team_id)
    if user.has_perm(VIEW_COMPANY_TASKS):
        return Goal.objects.all()
    if user.has_perm(VIEW_TEAM_TASKS):
        scope |= Q(team_id__in=led_team_ids(actor))
    return Goal.objects.filter(scope).distinct()


def visible_recurrences(user):
    actor = get_actor_employee(user)
    if not user.has_perm(VIEW_TASK):
        raise PermissionDenied("Bạn không có capability đọc lịch công việc.")
    if user.has_perm(VIEW_COMPANY_TASKS):
        return Recurrence.objects.all()
    scope = Q(creator=actor) | Q(assignee=actor)
    if user.has_perm(VIEW_TEAM_TASKS):
        scope |= Q(team_id__in=led_team_ids(actor))
    return Recurrence.objects.filter(scope).distinct()


def manages_team(user, team_id) -> bool:
    actor = get_actor_employee(user)
    return bool(user.has_perm(VIEW_COMPANY_TASKS) or TeamLeadership.objects.filter(leader=actor, team_id=team_id).exists())
