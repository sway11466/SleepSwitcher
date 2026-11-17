import threading
from datetime import datetime, timedelta

from core import power_control
from core import update_control
from core import schedule as schedule_module
from config import settings


class StateManager:
    _PRESENCE_SEC = 60                       # この秒数以内に入力があれば在席とみなす
    _PROPOSAL_INTERVAL = timedelta(hours=4)  # 再起動提案を繰り返す間隔

    def __init__(self):
        self._config = settings.load()
        self._sleep_enabled = True
        self._timer = None
        self._on_state_change = lambda: None
        self._on_restart_proposal = lambda: None
        self._next_proposal_at = datetime.min

        # 起動時に Windows の現在値とスケジュール判定を照合し、必要なら再適用
        self._apply_schedule_now()
        # 提案コールバックは未登録のため、ここでは窓の調整だけ行う
        self._guard_update(propose=False)

        # 1分ごとのポーリング開始
        self._start_polling()

    def set_state_change_callback(self, callback) -> None:
        self._on_state_change = callback

    def set_restart_proposal_callback(self, callback) -> None:
        self._on_restart_proposal = callback

    @property
    def config(self) -> dict:
        return self._config

    def set_update_guard(self, enabled: bool) -> None:
        guard = self._config['update_guard']
        if enabled == guard['enabled']:
            return
        if enabled:
            guard['original_hours'] = list(update_control.read_active_hours())
        elif guard['original_hours']:
            update_control.write_active_hours(*guard['original_hours'])
            guard['original_hours'] = None
        guard['enabled'] = enabled
        settings.save(self._config)
        self._guard_update()

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

    def _guard_update(self, propose: bool = True) -> None:
        if not self._config['update_guard']['enabled']:
            return
        now = datetime.now()
        try:
            update_control.keep_active(now)
        except OSError:
            return
        # 在席の判定は直近の入力のみ。提案に応答がなければ何もしない
        if (propose
                and update_control.is_reboot_pending()
                and now >= self._next_proposal_at
                and update_control.seconds_since_last_input() < self._PRESENCE_SEC):
            self._next_proposal_at = now + self._PROPOSAL_INTERVAL
            self._on_restart_proposal()

    def _start_polling(self) -> None:
        self._timer = threading.Timer(60, self._poll)
        self._timer.daemon = True
        self._timer.start()

    def _poll(self) -> None:
        self._apply_schedule_now()
        self._guard_update()
        self._timer = threading.Timer(60, self._poll)
        self._timer.daemon = True
        self._timer.start()
