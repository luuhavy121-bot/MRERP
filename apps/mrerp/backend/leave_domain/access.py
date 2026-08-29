from django.db.models import Q

from people_domain.access import get_actor_employee

from .capabilities import REVIEW_TEAM_LEAVE
from .models import LeaveRequest


def visible_leave_queryset(user):
    actor = get_actor_employee(user)
    queryset = LeaveRequest.objects.select_related("requester", "requester_team", "reviewer")
    scope = Q(requester=actor)
    if user.has_perm(REVIEW_TEAM_LEAVE):
        scope |= Q(requester_team__leaderships__leader=actor)
    return queryset.filter(scope).distinct()


def can_review_request(user, leave_request: LeaveRequest) -> bool:
    actor = get_actor_employee(user)
    return bool(
        user.has_perm(REVIEW_TEAM_LEAVE)
        and leave_request.requester_id != actor.pk
        and leave_request.requester_team_id
        and leave_request.requester_team.leaderships.filter(leader=actor).exists()
    )


def can_edit_request(user, leave_request: LeaveRequest) -> bool:
    actor = get_actor_employee(user)
    return bool(leave_request.requester_id == actor.pk and leave_request.status == LeaveRequest.Status.PENDING)
