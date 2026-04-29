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

- `data/config.json` の読み書き（スケジュールルールのみ）
- デフォルト設定値の定義
- スリープ時間は管理しない（Windows の設定値が Single Source of Truth）

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

```python
def should_disable_sleep(config: dict, now: datetime) -> bool
def is_holiday(config: dict, date: date) -> bool  # フェーズ 3 用スタブ
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

### Windows 設定値の Single Source of Truth

スリープ時間は config.json に持たず、Windows の設定値をそのまま使う。
起動時に `powercfg /query` で読み込み、「有効化」時はその値を復元する。

### スリープ無効化・有効化の実装方針

- 無効化：standby/hibernate の AC/DC 計4値をすべて 0 に書き込む
- 有効化：起動時に読み込んだ元の値を書き戻す

### スケジュール適用方式：定期ポーリング（1分ごと）

時刻切り替わり時だけ検知する方式（B案）より実装がシンプルで確実。
アプリ性質上 CPU 負荷は問題にならない。

### 手動操作とスケジュールの競合

手動操作は即時反映し、次の1分ポーリング時にスケジュールが再評価・上書きする。
「手動ロック」機能は初版では実装しない（YAGNI）。

### 祝日対応の拡張ポイント

`schedule.py` の `is_holiday()` をスタブとして定義しておき、
フェーズ 3 で実装を差し込む。`config.json` の `holidays` 配列は初版から構造を確保。

## 技術選定の理由

| 技術 | 理由 |
|------|------|
| PySimpleGUI | Python でのトレイアプリ実装が最もシンプル |
| JSON 設定ファイル | 外部ライブラリ不要、人間が読める |
| powercfg | Windows 標準コマンド、管理者権限不要 |
| PyInstaller | 単一 exe にまとめられ配布が容易 |
