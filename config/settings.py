import json
import os

_CONFIG_PATH = os.path.join(os.environ['APPDATA'], 'SleepSwitcher', 'config.json')


def default() -> dict:
    return {
        'timeouts': {
            'standby_ac':   15,
            'standby_dc':   10,
            'hibernate_ac': 180,
            'hibernate_dc': 180,
        },
        'schedule': {
            'days': {
                'mon':     [],
                'tue':     [],
                'wed':     [],
                'thu':     [],
                'fri':     [],
                'sat':     [],
                'sun':     [],
                'holiday': [],
            },
        },
    }


def load() -> dict:
    path = os.path.abspath(_CONFIG_PATH)
    if not os.path.exists(path):
        return default()
    with open(path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    _migrate(config)
    return config


def save(config: dict) -> None:
    path = os.path.abspath(_CONFIG_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def _migrate(config: dict) -> None:
    schedule = config.setdefault('schedule', {})
    days = schedule.setdefault('days', {})
    days.setdefault('holiday', [])
    schedule.pop('holidays', None)
