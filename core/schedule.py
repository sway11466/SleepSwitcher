from datetime import datetime

from core import holidays

_WEEKDAY_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


def should_disable_sleep(schedule: dict, now: datetime) -> bool:
    days = schedule.get('days', {})
    if holidays.is_holiday(now.date()):
        periods = days.get('holiday', [])
    else:
        periods = days.get(_WEEKDAY_KEYS[now.weekday()], [])
    current = now.strftime('%H:%M')
    return any(p['from'] <= current < p['to'] for p in periods)
