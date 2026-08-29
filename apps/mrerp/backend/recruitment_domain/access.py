from django.db.models import Q

from people_domain.access import get_actor_employee
from people_domain.models import TeamLeadership

from .capabilities import MANAGE_CANDIDATES, VIEW_COMPANY_RECRUITMENT
from .models import Application, HiringRequest


def led_team_ids(actor):
    return TeamLeadership.objects.filter(leader=actor).values_list("team_id", flat=True)


def visible_hiring_requests(user):
    actor = get_actor_employee(user)
    queryset = HiringRequest.objects.select_related("team", "requester", "reviewer").all()
    if user.has_perm(VIEW_COMPANY_RECRUITMENT):
        return queryset
    return queryset.filter(team_id__in=led_team_ids(actor))


def visible_applications(user):
    actor = get_actor_employee(user)
    queryset = Application.objects.select_related(
        "candidate",
        "opening__team",
        "opening__hiring_request",
        "converted_employee",
    ).prefetch_related("transitions", "attachments")
    if user.has_perm(VIEW_COMPANY_RECRUITMENT) or user.has_perm(MANAGE_CANDIDATES):
        return queryset
    return queryset.filter(opening__team_id__in=led_team_ids(actor))


def can_view_candidate_files(user, application):
    get_actor_employee(user)
    return user.has_perm(MANAGE_CANDIDATES) and visible_applications(user).filter(pk=application.pk).exists()
