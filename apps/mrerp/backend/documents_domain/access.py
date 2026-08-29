from django.db.models import Q

from people_domain.access import get_actor_employee
from people_domain.models import TeamLeadership

from .capabilities import MANAGE_ALL_DOCUMENTS, VIEW_COMPANY_DOCUMENTS, VIEW_HR_CONFIDENTIAL
from .models import Document


def led_team_ids(actor):
    return TeamLeadership.objects.filter(leader=actor).values_list("team_id", flat=True)


def visible_documents(user, *, include_archived=False):
    actor = get_actor_employee(user)
    queryset = Document.objects.select_related("owner").prefetch_related(
        "audience_teams", "audience_employees", "versions__files"
    )
    if user.has_perm(VIEW_COMPANY_DOCUMENTS):
        return queryset if include_archived else queryset.filter(archived_at__isnull=True)
    scope = Q(scope=Document.Scope.COMPANY) | Q(audience_employees=actor)
    if actor.team_id:
        scope |= Q(audience_teams=actor.team_id)
    if user.has_perm(VIEW_HR_CONFIDENTIAL):
        scope |= Q(scope=Document.Scope.HR_CONFIDENTIAL)
    if user.has_perm(MANAGE_ALL_DOCUMENTS):
        scope |= Q(owner=actor)
    else:
        scope |= Q(owner=actor)
    queryset = queryset.filter(scope).distinct()
    if include_archived:
        if user.has_perm(MANAGE_ALL_DOCUMENTS):
            return queryset
        queryset = queryset.filter(Q(archived_at__isnull=True) | Q(owner=actor))
    else:
        queryset = queryset.filter(archived_at__isnull=True)
    return queryset


def can_manage_document(user, document):
    actor = get_actor_employee(user)
    return user.has_perm(MANAGE_ALL_DOCUMENTS) or document.owner_id == actor.pk
