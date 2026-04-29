import threading
import tkinter as tk
from tkinter import ttk, messagebox

import pystray
from PIL import Image, ImageDraw

from core.state_manager import StateManager
from core import power_control


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

    def _on_open_settings(self):
        threading.Thread(target=self._show_settings_dialog, daemon=True).start()

    def _show_settings_dialog(self):
        current = power_control.read_all_timeouts()

        root = tk.Tk()
        root.title('SleepSwitcher — 設定')
        root.resizable(False, False)

        fields = [
            ('standby_ac',   'スリープ（電源接続）',   '分'),
            ('standby_dc',   'スリープ（バッテリー）',  '分'),
            ('hibernate_ac', '休止状態（電源接続）',   '分'),
            ('hibernate_dc', '休止状態（バッテリー）',  '分'),
        ]

        vars_ = {}
        for i, (key, label, unit) in enumerate(fields):
            tk.Label(root, text=label, anchor='w').grid(row=i, column=0, padx=12, pady=6, sticky='w')
            var = tk.IntVar(value=current[key])
            vars_[key] = var
            tk.Spinbox(root, from_=0, to=480, textvariable=var, width=6).grid(row=i, column=1, padx=4)
            tk.Label(root, text=unit).grid(row=i, column=2, padx=(0, 12), sticky='w')

        tk.Label(root, text='※ 0 = 無効', fg='gray').grid(
            row=len(fields), column=0, columnspan=3, padx=12, pady=(0, 4), sticky='w'
        )

        def on_apply():
            values = {key: var.get() for key, var in vars_.items()}
            power_control.write_all_timeouts(values)
            self._manager.update_restore_timeouts(values)
            self._refresh()
            messagebox.showinfo('完了', 'Windows の電源設定を更新しました。', parent=root)

        btn_frame = tk.Frame(root)
        btn_frame.grid(row=len(fields) + 1, column=0, columnspan=3, pady=(4, 12))
        tk.Button(btn_frame, text='変更', width=10, command=on_apply).pack(side='left', padx=6)
        tk.Button(btn_frame, text='閉じる', width=10, command=root.destroy).pack(side='left', padx=6)

        root.mainloop()

    def _on_exit(self):
        self._icon.stop()

    # --- helpers ---

    def _make_menu(self) -> pystray.Menu:
        sleep_enabled = self._manager.get_status()['sleep_enabled']
        return pystray.Menu(
            pystray.MenuItem(
                'スリープ有効化',
                lambda: self._on_enable_sleep(),
                checked=lambda item: sleep_enabled,
                radio=True,
            ),
            pystray.MenuItem(
                'スリープ無効化',
                lambda: self._on_disable_sleep(),
                checked=lambda item: not sleep_enabled,
                radio=True,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('設定...', lambda: self._on_open_settings()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('終了', lambda: self._on_exit()),
        )

    def _make_tooltip(self) -> str:
        state = '有効' if self._manager.get_status()['sleep_enabled'] else '無効'
        return f'SleepSwitcher — スリープ{state}'

    def _refresh(self) -> None:
        if self._icon:
            self._icon.icon = _create_icon_image(self._manager.get_status()['sleep_enabled'])
            self._icon.title = self._make_tooltip()
            self._icon.menu = self._make_menu()
