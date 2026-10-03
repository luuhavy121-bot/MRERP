"""Half-day intervals; imported attendance is intentionally unaffected."""
from datetime import timedelta
from decimal import Decimal
from django.conf import settings


def interval(start, end, start_period="am", end_period="pm"):
    return start.toordinal() * 2 + (start_period == "pm"), end.toordinal() * 2 + (end_period == "pm")


def overlaps(queryset, start, end, start_period, end_period):
    low, high = interval(start, end, start_period, end_period)
    return any(a <= high and b >= low for a, b in (
        interval(item.start_date, item.end_date, item.start_period, item.end_period) for item in queryset
    ))


def workdays(start, end, holidays, start_period="am", end_period="pm"):
    low, high = interval(start, end, start_period, end_period)
    total = Decimal(0)
    current = start
    while current <= end:
        periods = 2 if current.weekday() in settings.MRERP_WORK_WEEKDAYS else 0
        if current not in holidays:
            for p in range(periods):
                if low <= current.toordinal() * 2 + p <= high:
                    total += Decimal("0.5")
        current += timedelta(days=1)
    return total
