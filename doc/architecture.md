# architecture.md — SleepSwitcher アーキテクチャ設計

## ディレクトリ構成

```
SleepSwitcher/
├── main.py                 # エントリーポイント
├── requirements.txt
├── config/
│   ├── __init__.py
│   └── settings.py         # 設定の読み書き・デフォルト値
├── core/
│   ├── __init__.py
│   ├── power_control.py    # powercfg コマンド実行
│   ├── schedule.py         # スケジュール判定ロジック
│   └── state_manager.py    # アプリ状態管理・スケジュール自動適用
├── ui/
│   ├── __init__.py
│   └── tray_app.py         # システムトレイ UI
└── data/
    ├── config.json         # ユーザー設定（永続化）
    └── holidays.json       # 祝日リスト（フェーズ 3 用、初版は空）
```

## モジュール依存関係

```
main.py
  └─ ui/tray_app.py
       ├─ core/state_manager.py
       │    ├─ core/power_control.py
       │    ├─ core/schedule.py
       │    └─ config/settings.py
       └─ config/settings.py
```

依存は上位から下位への一方向。`core/` と `config/` は `ui/` を参照しない。

## 各モジュールの責務

### `main.py`

- アプリ起動エントリーポイント
- `tray_app.py` を初期化して実行

### `config/settings.py`

- `data/config.json` の読み書き
- 管理対象：タイムアウト値（4値）とスケジュールルール（曜日ごとの from-to 配列）
- デフォルト設定値の定義

```python
def load() -> dict
def save(config: dict) -> None
def default() -> dict
```

### `core/power_control.py`

- `powercfg` コマンドを subprocess で実行
- OS との唯一の接点（副作用を1箇所に集約）
- 管理対象：standby-timeout と hibernate-timeout の AC/DC 計4値

```python
def read_all_timeouts() -> dict       # 4値を Windows から読み込む
def write_all_timeouts(values: dict) -> None  # 4値を Windows に書き込む
def disable_all() -> None             # 4値をすべて 0 に設定
```

### `core/schedule.py`

- 現在時刻・曜日からスリープ OFF にすべきか判定
- 純粋関数（副作用なし）
- 曜日ごとの from-to 配列を走査して現在時刻が含まれるか判定

```python
def should_disable_sleep(schedule: dict, now: datetime) -> bool
def is_holiday(schedule: dict, date: date) -> bool  # フェーズ 3 用スタブ
```

### `core/state_manager.py`

- 起動時に Windows の現在値を読み込みメモリに保持
- 現在のスリープ状態（有効/無効）を管理
- 1分ごとのスケジュール自動適用タイマーを管理（フェーズ2）
- 手動操作とスケジュール適用の調整

```python
class StateManager:
    def apply_schedule(self) -> None   # スケジュールに従って自動適用
    def force_disable(self) -> None    # 手動: スリープ無効化（4値を 0 に）
    def force_enable(self) -> None     # 手動: スリープ有効化（読み込んだ値に戻す）
    def get_status(self) -> dict       # UI 表示用の現在状態
```

### `ui/tray_app.py`

- PySimpleGUI でシステムトレイ UI を構築
- ユーザー操作を `StateManager` に委譲
- 設定変更ダイアログの表示

## 設計上の判断

### タイムアウト値の管理方針

- `config.json` の `timeouts` が唯一の真実（Single Source of Truth）
- 起動時：`config.json` から読み込み Windows に書き込む
- 設定変更時：`config.json` に保存してから Windows に書き込む
- 無効化時：Windows を 0 に設定するが `config.json` の値は保持する

### スリープ無効化・有効化の実装方針

- 無効化：standby/hibernate の AC/DC 計4値をすべて 0 に書き込む
- 有効化：`config.json` の `timeouts` 値を Windows に書き込む

### スケジュール適用方式：定期ポーリング（1分ごと）

時刻切り替わり時だけ検知する方式（B案）より実装がシンプルで確実。
アプリ性質上 CPU 負荷は問題にならない。

### 手動操作とスケジュールの優先度

優先度の概念を持たず、後勝ちで上書きする。
スケジュール変更保存時は `apply_schedule(now)` を即時実行し、現在時刻で評価・適用する。

### 祝日対応の拡張ポイント

`schedule.py` の `is_holiday()` をスタブとして定義しておき、
フェーズ 3 で実装を差し込む。`config.json` の `holidays` 配列は初版から構造を確保。

## 技術選定の理由

| 技術 | 理由 |
|------|------|
| pystray + tkinter | トレイ常駐は pystray、ダイアログは tkinter（標準ライブラリ）で構成 |
| JSON 設定ファイル | 外部ライブラリ不要、人間が読める |
| powercfg | Windows 標準コマンド、管理者権限不要 |
| PyInstaller | 単一 exe にまとめられ配布が容易 |
