import threading
from datetime import datetime

from core import power_control
from core import schedule as schedule_module
from config import settings


class StateManager:
    def __init__(self):
        self._config = settings.load()
        self._sleep_enabled = True
        self._timer = None
        self._on_state_change = lambda: None

        # 起動時に Windows の現在値とスケジュール判定を照合し、必要なら再適用
        self._apply_schedule_now()

        # 1分ごとのポーリング開始
        self._start_polling()

    def set_state_change_callback(self, callback) -> None:
        self._on_state_change = callback

    @property
    def config(self) -> dict:
        return self._config

    def force_disable(self) -> None:
        power_control.disable_all()
        self._sleep_enabled = False

    def force_enable(self) -> None:
        power_control.write_all_timeouts(self._config['timeouts'])
        self._sleep_enabled = True

    def update_timeouts(self, timeouts: dict) -> None:
        self._config['timeouts'] = timeouts
        settings.save(self._config)
        if self._sleep_enabled:
            power_control.write_all_timeouts(timeouts)

    def update_schedule(self, schedule: dict) -> None:
        self._config['schedule'] = schedule
        settings.save(self._config)
        self._apply_schedule_now()

    def is_schedule_active(self) -> bool:
        return schedule_module.should_disable_sleep(
            self._config['schedule'], datetime.now()
        )

    def get_status(self) -> dict:
        return {
            'sleep_enabled':    self._sleep_enabled,
            'timeouts':         self._config['timeouts'],
            'schedule_active':  self.is_schedule_active(),
        }

    def stop(self) -> None:
        if self._timer:
            self._timer.cancel()

    def _apply_schedule_now(self) -> None:
        # スケジュール判定と Windows 現在値を照合し、矛盾していれば書き込む
        prev = self._sleep_enabled
        should_disable = schedule_module.should_disable_sleep(
            self._config['schedule'], datetime.now()
        )
        actual   = power_control.read_all_timeouts()
        expected = {k: 0 for k in actual} if should_disable else self._config['timeouts']
        if actual != expected:
            if should_disable:
                power_control.disable_all()
            else:
                power_control.write_all_timeouts(self._config['timeouts'])
        self._sleep_enabled = not should_disable
        if self._sleep_enabled != prev:
            self._on_state_change()

    def _start_polling(self) -> None:
        self._timer = threading.Timer(60, self._poll)
        self._timer.daemon = True
        self._timer.start()

    def _poll(self) -> None:
        self._apply_schedule_now()
        self._timer = threading.Timer(60, self._poll)
        self._timer.daemon = True
        self._timer.start()
