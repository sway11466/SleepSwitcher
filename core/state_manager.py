from core import power_control
from config import settings

_DEFAULT_TIMEOUTS = {
    'standby_ac':   15,
    'standby_dc':   10,
    'hibernate_ac': 180,
    'hibernate_dc': 180,
}


class StateManager:
    def __init__(self):
        self._config = settings.load()
        self._windows_timeouts = power_control.read_all_timeouts()

        # 起動時に全値が 0 の場合（すでに無効化済み）はデフォルト値を復元候補とする
        if all(v == 0 for v in self._windows_timeouts.values()):
            self._restore_timeouts = _DEFAULT_TIMEOUTS.copy()
            self._sleep_enabled = False
        else:
            self._restore_timeouts = self._windows_timeouts.copy()
            self._sleep_enabled = True

    @property
    def config(self) -> dict:
        return self._config

    def force_disable(self) -> None:
        # 現在の値を退避してから無効化
        current = power_control.read_all_timeouts()
        if any(v > 0 for v in current.values()):
            self._restore_timeouts = current
        power_control.disable_all()
        self._sleep_enabled = False

    def force_enable(self) -> None:
        power_control.write_all_timeouts(self._restore_timeouts)
        self._sleep_enabled = True

    def get_status(self) -> dict:
        return {
            'sleep_enabled': self._sleep_enabled,
            'restore_timeouts': self._restore_timeouts,
        }
