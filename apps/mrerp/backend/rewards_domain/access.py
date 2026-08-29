from people_domain.access import get_actor_employee
from people_domain.models import TeamLeadership

from .capabilities import GRANT_STARS_COMPANY, RECOGNIZE_COMPANY


def _in_led_team(actor, target):
    return bool(target.team_id and TeamLeadership.objects.filter(team_id=target.team_id, leader=actor).exists())


def can_recognize(user, target):
    actor = get_actor_employee(user)
    return actor.pk != target.pk and (user.has_perm(RECOGNIZE_COMPANY) or _in_led_team(actor, target))


def can_grant_stars(user, target):
    actor = get_actor_employee(user)
    return actor.pk != target.pk and (user.has_perm(GRANT_STARS_COMPANY) or _in_led_team(actor, target))
