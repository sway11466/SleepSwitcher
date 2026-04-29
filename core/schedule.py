from datetime import datetime, date

_WEEKDAY_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


def should_disable_sleep(schedule: dict, now: datetime) -> bool:
    day_key = _WEEKDAY_KEYS[now.weekday()]
    periods = schedule.get('days', {}).get(day_key, [])
    current = now.strftime('%H:%M')
    return any(p['from'] <= current < p['to'] for p in periods)


def is_holiday(schedule: dict, d: date) -> bool:
    return False  # フェーズ 3 で実装
