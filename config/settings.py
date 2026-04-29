import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')


def default() -> dict:
    return {
        'schedule': {
            'enabled': True,
            'rules': [
                {
                    'weekday': 'mon-fri',
                    'description': '平日',
                    'off_hours': {'start': '09:00', 'end': '18:00'},
                },
                {
                    'weekday': 'sat-sun',
                    'description': '休日',
                    'off_hours': None,
                },
            ],
            'holidays': [],
        },
    }


def load() -> dict:
    path = os.path.abspath(_CONFIG_PATH)
    if not os.path.exists(path):
        return default()
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save(config: dict) -> None:
    path = os.path.abspath(_CONFIG_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
