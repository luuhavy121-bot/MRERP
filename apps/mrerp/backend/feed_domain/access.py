from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

from people_domain.access import get_actor_employee

from .capabilities import MODERATE, VIEW_FEED
from .models import Post


def audience_filter(actor, prefix=""):
    key = lambda field: f"{prefix}{field}"
    query = Q(**{key("company_scope"): True}) | Q(**{key("audience_employees"): actor})
    if actor.team_id:
        query |= Q(**{key("audience_teams"): actor.team_id})
    return query


def visible_posts(user):
    actor = get_actor_employee(user)
    if not user.has_perm(VIEW_FEED):
        raise PermissionDenied("Bạn không có capability đọc Bảng tin.")
    current_visible = audience_filter(actor) | Q(author=actor)
    original_visible = Q(shared_from__isnull=True) | audience_filter(actor, "shared_from__")
    return Post.objects.filter(current_visible, original_visible, deleted_at__isnull=True).select_related("author", "shared_from", "shared_from__author").prefetch_related(
        "audience_employees", "audience_teams", "attachments", "reactions", "comments__author", "comments__reactions"
    ).distinct()


def can_moderate(user) -> bool:
    return user.has_perm(MODERATE)
