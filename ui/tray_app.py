import os
import threading
import tkinter as tk
from tkinter import messagebox

import pystray
from PIL import Image, ImageDraw, ImageFont, ImageTk

from core.state_manager import StateManager

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')

# グリッド定数
CELL_W   = 14
CELL_H   = 22
LABEL_W  = 30
HEADER_H = 20
SLOTS    = 48  # 30分 × 48 = 24時間
COLOR_OFF = '#4CAF50'
COLOR_ON  = '#DCDCDC'

DAYS_JP  = ['月', '火', '水', '木', '金', '土', '日']
DAY_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


def _time_to_slot(time_str: str) -> int:
    h, m = map(int, time_str.split(':'))
    return h * 2 + m // 30


def _slot_to_time(slot: int) -> str:
    return f'{slot // 2:02d}:{(slot % 2) * 30:02d}'


def _periods_to_grid(periods: list) -> list:
    # デフォルトは全て True（グリーン = スリープ ON）
    # スリープ OFF にする時間帯だけ False（グレー）にする
    row = [True] * SLOTS
    for p in periods:
        start = _time_to_slot(p['from'])
        end   = min(_time_to_slot(p['to']), SLOTS)
        for i in range(start, end):
            row[i] = False
    return row


def _grid_to_periods(grid_row: list) -> list:
    # False（グレー = スリープ OFF）の連続区間を periods として返す
    periods = []
    in_period = False
    start = 0
    for i, active in enumerate(grid_row + [True]):
        if not active and not in_period:
            start = i
            in_period = True
        elif active and in_period:
            periods.append({'from': _slot_to_time(start), 'to': _slot_to_time(i)})
            in_period = False
    return periods


def _replace_bg_color(img: Image.Image,
                      src: tuple, dst: tuple, tolerance: int = 10) -> Image.Image:
    """src に近い色のピクセルを dst に置換する"""
    img = img.convert('RGB')
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            if (abs(r - src[0]) <= tolerance and
                    abs(g - src[1]) <= tolerance and
                    abs(b - src[2]) <= tolerance):
                pixels[x, y] = dst
    return img


def _create_icon_image(sleep_enabled: bool) -> Image.Image:
    size  = 64
    img   = Image.new('RGB', (size, size), color=(30, 30, 30))
    draw  = ImageDraw.Draw(img)
    color = (76, 175, 80) if sleep_enabled else (180, 180, 180)
    draw.ellipse([8, 8, size - 8, size - 8], fill=color)
    try:
        font = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', int(size * 0.55))
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), 'Z', font=font)
    x = (size - (bbox[2] - bbox[0])) // 2 - bbox[0]
    y = (size - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((x, y), 'Z', font=font, fill=(80, 80, 80))
    return img


class TrayApp:
    def __init__(self, manager: StateManager):
        self._manager = manager
        self._icon    = None

    def run(self) -> None:
        self._icon = pystray.Icon(
            name  = 'SleepSwitcher',
            icon  = _create_icon_image(self._manager.get_status()['sleep_enabled']),
            title = self._make_tooltip(),
            menu  = self._make_menu(),
        )
        self._icon.run()

    # --- tray actions ---

    def _on_enable_sleep(self):
        self._manager.force_enable()
        self._refresh()

    def _on_disable_sleep(self):
        self._manager.force_disable()
        self._refresh()

    def _on_open_settings(self):
        threading.Thread(target=self._show_settings_dialog, daemon=True).start()

    def _on_exit(self):
        self._manager.stop()
        self._icon.stop()

    # --- settings dialog ---

    def _show_settings_dialog(self):
        status = self._manager.get_status()
        config = self._manager.config

        root = tk.Tk()
        root.title('SleepSwitcher — 設定')
        root.resizable(False, False)

        # ── 使い方・注意事項 ──
        info_frame = tk.LabelFrame(root, text='使い方・注意事項', padx=8, pady=6)
        info_frame.pack(fill='x', padx=12, pady=(12, 6))
        info_text = (
            '■ 使い方\n'
            '・スリープ設定の有効／無効を設定画面やタスクトレイから切り替えられます\n'
            '・特定の曜日・時間帯だけ無効化したい場合はスケジュールを設定できます\n'
            '・スリープを無効化したい時間帯（30分単位）を選択するとグリーンになります\n'
            '\n'
            '■ アプリの動作\n'
            '・スリープ設定は Windows の設定と同期しています\n'
            '・無効となっている状態では Windows 上の設定は 0（無効）になります\n'
            '・有効になったタイミングで、このアプリで指定した値に戻ります\n'
            '\n'
            '■ 注意事項\n'
            '・アプリを終了するとスケジュール制御が止まるためタスクトレイに常駐させてください\n'
            '・スリープ状態に入ってしまった場合は、手動で復帰させる必要があります'
        )
        tk.Label(info_frame, text=info_text, anchor='w', justify='left').pack(fill='x')

        # ── スリープ設定 ──
        sleep_frame = tk.LabelFrame(root, text='スリープ設定', padx=8, pady=6)
        sleep_frame.pack(fill='x', padx=12, pady=(0, 6))

        # 有効/無効トグル ＋ Windows 設定リンク
        sleep_enabled_var = tk.BooleanVar(value=status['sleep_enabled'])
        toggle_row = tk.Frame(sleep_frame)
        toggle_row.grid(row=0, column=0, columnspan=8, sticky='ew', pady=(0, 4))
        toggle_row.columnconfigure(1, weight=1)

        radios = tk.Frame(toggle_row)
        radios.grid(row=0, column=0, sticky='w')
        tk.Radiobutton(radios, text='有効', variable=sleep_enabled_var, value=True).pack(side='left')
        tk.Radiobutton(radios, text='無効', variable=sleep_enabled_var, value=False).pack(side='left')

        def open_win_settings():
            import subprocess
            subprocess.Popen(['start', 'ms-settings:powersleep'], shell=True)

        link = tk.Label(toggle_row, text='Windows の電源設定を開く ›', fg='#0078D4', cursor='hand2')
        link.grid(row=0, column=2, sticky='e')
        link.bind('<Button-1>', lambda e: open_win_settings())
        # スケジュール制御中の注記
        note_row = 1
        if status['schedule_active']:
            tk.Label(sleep_frame, text='※ スケジュールにより自動制御中', fg='gray').grid(
                row=note_row, column=0, columnspan=8, sticky='w'
            )
            note_row += 1

        # タイムアウト入力（スリープ／休止状態を横並び）
        # 各行: [（左）key, label] [（右）key, label]
        field_rows = [
            [('standby_ac',   'スリープ：電源'),   ('hibernate_ac', '休止状態：電源')],
            [('standby_dc',   'スリープ：バッテリー'), ('hibernate_dc', '休止状態：バッテリー')],
        ]
        timeout_vars    = {}
        timeout_widgets = []
        for i, row_fields in enumerate(field_rows):
            row = note_row + i
            for col_offset, (key, label) in enumerate(row_fields):
                base_col = col_offset * 4
                tk.Label(sleep_frame, text=label, anchor='w').grid(
                    row=row, column=base_col, sticky='w', padx=(0 if col_offset == 0 else 12, 0), pady=3
                )
                var = tk.IntVar(value=config['timeouts'][key])
                timeout_vars[key] = var
                sb = tk.Spinbox(sleep_frame, from_=0, to=480, textvariable=var, width=6)
                sb.grid(row=row, column=base_col + 1, padx=4)
                timeout_widgets.append(sb)
                tk.Label(sleep_frame, text='分').grid(row=row, column=base_col + 2, sticky='w')

        tk.Label(sleep_frame, text='※ 0 = 無効', fg='gray').grid(
            row=note_row + len(field_rows), column=0, columnspan=8, sticky='w'
        )

        def update_spinbox_state(*_):
            s = 'normal' if sleep_enabled_var.get() else 'disabled'
            for w in timeout_widgets:
                w.configure(state=s)
        sleep_enabled_var.trace_add('write', update_spinbox_state)
        update_spinbox_state()

        # スリープ状態画像（右端）
        _status_imgs = []  # GC 防止用
        try:
            _img_h = 150
            for fname in ('pc_sleeping.jpg', 'pc_awake.jpg'):
                raw = Image.open(os.path.join(_ASSETS_DIR, fname))
                raw = _replace_bg_color(raw, src=(233, 233, 233), dst=(240, 240, 240))
                w, h = raw.size
                _img_w = int(_img_h * w / h)
                raw = raw.resize((_img_w, _img_h), Image.LANCZOS)
                _status_imgs.append(ImageTk.PhotoImage(raw))
            img_sleeping, img_awake = _status_imgs

            init_img = img_sleeping if status['sleep_enabled'] else img_awake
            status_img_label = tk.Label(sleep_frame, image=init_img)
            status_img_label.grid(row=0, column=8, rowspan=6, padx=(16, 4))

            def update_status_image(*_):
                status_img_label.configure(
                    image=img_sleeping if sleep_enabled_var.get() else img_awake
                )
            sleep_enabled_var.trace_add('write', update_status_image)
        except Exception:
            pass  # 画像ファイルがない場合はスキップ

        # ── スケジュール ──
        sched_frame = tk.LabelFrame(root, text='スケジュール', padx=8, pady=6)
        sched_frame.pack(fill='x', padx=12, pady=(0, 6))

        # グリッドの初期状態を config から作成
        grid_state = [
            _periods_to_grid(config['schedule']['days'].get(dk, []))
            for dk in DAY_KEYS
        ]

        canvas_w = LABEL_W + CELL_W * SLOTS
        canvas_h = HEADER_H + CELL_H * len(DAYS_JP)
        # 凡例
        legend_frame = tk.Frame(sched_frame)
        legend_frame.pack(anchor='w', pady=(0, 4))
        for color, label in [(COLOR_OFF, 'スリープ ON'), (COLOR_ON, 'スリープ OFF')]:
            tk.Label(legend_frame, bg=color, width=2).pack(side='left', padx=(0, 2))
            tk.Label(legend_frame, text=label).pack(side='left', padx=(0, 12))

        canvas = tk.Canvas(sched_frame, width=canvas_w, height=canvas_h,
                           bg='white', cursor='crosshair')
        canvas.pack()

        # 時間ラベル（全時間）
        for h in range(0, 24):
            x = LABEL_W + h * 2 * CELL_W
            canvas.create_text(x + CELL_W // 2, HEADER_H // 2, text=str(h), font=('', 7))

        # セル描画
        cell_ids = [[None] * SLOTS for _ in range(len(DAYS_JP))]
        for row, day in enumerate(DAYS_JP):
            y = HEADER_H + row * CELL_H
            canvas.create_text(LABEL_W // 2, y + CELL_H // 2, text=day, font=('', 9))
            for col in range(SLOTS):
                x = LABEL_W + col * CELL_W
                color = COLOR_OFF if grid_state[row][col] else COLOR_ON
                cid = canvas.create_rectangle(
                    x, y, x + CELL_W, y + CELL_H,
                    fill=color, outline='white', width=1,
                )
                cell_ids[row][col] = cid

        # マウス操作（クリック＋ドラッグで塗り）
        drag_value = [None]

        def get_cell(event):
            col = (event.x - LABEL_W) // CELL_W
            row = (event.y - HEADER_H) // CELL_H
            if 0 <= row < len(DAYS_JP) and 0 <= col < SLOTS:
                return row, col
            return None, None

        def paint(row, col, value):
            grid_state[row][col] = value
            canvas.itemconfig(cell_ids[row][col], fill=COLOR_OFF if value else COLOR_ON)

        def on_press(event):
            row, col = get_cell(event)
            if row is not None:
                new_val = not grid_state[row][col]
                drag_value[0] = new_val
                paint(row, col, new_val)

        def on_drag(event):
            if drag_value[0] is None:
                return
            row, col = get_cell(event)
            if row is not None and grid_state[row][col] != drag_value[0]:
                paint(row, col, drag_value[0])

        def on_release(event):
            drag_value[0] = None

        canvas.bind('<ButtonPress-1>',  on_press)
        canvas.bind('<B1-Motion>',      on_drag)
        canvas.bind('<ButtonRelease-1>', on_release)

        # ── ボタン ──
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill='x', padx=12, pady=(4, 12))

        def on_apply():
            # タイムアウト値を保存・適用
            new_timeouts = {k: v.get() for k, v in timeout_vars.items()}
            self._manager.update_timeouts(new_timeouts)

            # 有効/無効トグルを適用
            if sleep_enabled_var.get():
                self._manager.force_enable()
            else:
                self._manager.force_disable()

            # スケジュールを保存・即時評価
            new_days = {dk: _grid_to_periods(grid_state[i]) for i, dk in enumerate(DAY_KEYS)}
            new_schedule = dict(self._manager.config['schedule'])
            new_schedule['days'] = new_days
            self._manager.update_schedule(new_schedule)

            self._refresh()
            # スケジュール適用後の実際の状態をUIに反映（画像も trace 経由で更新される）
            sleep_enabled_var.set(self._manager.get_status()['sleep_enabled'])
            messagebox.showinfo('完了', '設定を保存しました。', parent=root)

        tk.Button(btn_frame, text='キャンセル',     width=12, command=root.destroy).pack(side='left')
        tk.Button(btn_frame, text='適用して閉じる', width=14, command=lambda: [on_apply(), root.destroy()]).pack(side='right')
        tk.Button(btn_frame, text='適用',           width=10, command=on_apply).pack(side='right', padx=6)

        root.mainloop()

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
            self._icon.icon  = _create_icon_image(self._manager.get_status()['sleep_enabled'])
            self._icon.title = self._make_tooltip()
            self._icon.menu  = self._make_menu()
