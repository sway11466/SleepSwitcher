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
│   ├── holidays.py         # 祝日判定（holiday-jp-pip ラッパー）
│   └── state_manager.py    # アプリ状態管理・スケジュール自動適用
├── ui/
│   ├── __init__.py
│   └── tray_app.py         # システムトレイ UI
└── data/
    └── config.json         # ユーザー設定（永続化）
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
- 管理対象：タイムアウト値（4値）とスケジュールルール（曜日＋祝日ごとの from-to 配列）
- デフォルト設定値の定義
- 旧形式の設定をロード時にマイグレーションする

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

- 現在時刻・曜日・祝日からスリープ OFF にすべきか判定
- 当日が祝日なら `days.holiday` を、平日なら曜日ごとの配列を走査
- 祝日判定は `core/holidays.py` に委譲

```python
def should_disable_sleep(schedule: dict, now: datetime) -> bool
```

### `core/holidays.py`

- holiday-jp-pip をラップし、祝日 CSV をメモリにキャッシュする
- CSV を以下の優先順で探索する：
    1. `%APPDATA%\SleepSwitcher\syukujitsu.csv`（ユーザによる上書き用）
    2. frozen 時：exe と同じフォルダの `syukujitsu.csv`／開発時：リポジトリの `assets/syukujitsu.csv`
- 解決したパスと `mtime` をキャッシュキーにし、変更があれば `HolidayJP` を再生成
- 範囲外の年（2028 年以降）でも例外を出さないよう `unsupported_date_behavior='ignore'` で初期化

```python
def is_holiday(d: date) -> bool
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

### 祝日対応

- 祝日判定は外部ライブラリ [holiday-jp-pip](https://github.com/sway11466/holiday-jp-pip) に委譲（v0.3.0+ の `csv_path` 機能を利用）
- 祝日 CSV は `assets/syukujitsu.csv` をリポジトリに同梱し、配布時は exe と同じ場所に配置する
- ユーザは `%APPDATA%\SleepSwitcher\syukujitsu.csv` に置くことで上書き可能（探索順は `core/holidays.py` 参照）
- `should_disable_sleep` は祝日に該当する日は `days.holiday` のみを参照し、曜日設定は無視する

## 技術選定の理由

| 技術 | 理由 |
|------|------|
| pystray + tkinter | トレイ常駐は pystray、ダイアログは tkinter（標準ライブラリ）で構成 |
| JSON 設定ファイル | 外部ライブラリ不要、人間が読める |
| powercfg | Windows 標準コマンド、管理者権限不要 |
| PyInstaller | 単一 exe にまとめられ配布が容易 |
| holiday-jp-pip | 内閣府データに基づく日本の祝日判定。`csv_path` で外部 CSV を指定できユーザによる差し替えが可能 |
