import threading
import tkinter as tk

import pystray
from PIL import Image, ImageDraw

from core.state_manager import StateManager


def _create_icon_image(sleep_enabled: bool) -> Image.Image:
    size = 64
    img = Image.new('RGB', (size, size), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    color = (100, 180, 100) if sleep_enabled else (220, 80, 80)
    draw.ellipse([8, 8, size - 8, size - 8], fill=color)
    return img


class TrayApp:
    def __init__(self, manager: StateManager):
        self._manager = manager
        self._icon = None

    def run(self) -> None:
        self._icon = pystray.Icon(
            name='SleepSwitcher',
            icon=_create_icon_image(self._manager.get_status()['sleep_enabled']),
            title=self._make_tooltip(),
            menu=self._make_menu(),
        )
        self._icon.run()

    # --- menu actions ---

    def _on_enable_sleep(self):
        self._manager.force_enable()
        self._refresh()

    def _on_disable_sleep(self):
        self._manager.force_disable()
        self._refresh()

    def _on_exit(self):
        self._icon.stop()

    # --- helpers ---

    def _make_menu(self) -> pystray.Menu:
        status = self._manager.get_status()
        label = '現在: スリープ有効' if status['sleep_enabled'] else '現在: スリープ無効'
        t = status['restore_timeouts']
        timeout_label = (
            f"復元値: スリープ {t['standby_ac']}分(AC)/{t['standby_dc']}分(DC)  "
            f"休止 {t['hibernate_ac']}分(AC)/{t['hibernate_dc']}分(DC)"
        )
        return pystray.Menu(
            pystray.MenuItem(label, None, enabled=False),
            pystray.MenuItem(timeout_label, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('スリープ有効化', lambda: self._on_enable_sleep()),
            pystray.MenuItem('スリープ無効化', lambda: self._on_disable_sleep()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('終了', lambda: self._on_exit()),
        )

    def _make_tooltip(self) -> str:
        status = self._manager.get_status()
        state = '有効' if status['sleep_enabled'] else '無効'
        return f'SleepSwitcher — スリープ{state}'

    def _refresh(self) -> None:
        if self._icon:
            self._icon.icon = _create_icon_image(self._manager.get_status()['sleep_enabled'])
            self._icon.title = self._make_tooltip()
            self._icon.menu = self._make_menu()
