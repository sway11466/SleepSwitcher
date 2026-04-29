# SleepSwitcher - プロジェクト要件書

## 📋 プロジェクト概要

**アプリ名：** SleepSwitcher

**目的：** Windows 11 のスリープ設定を柔軟に制御し、開発継続とプライベート時間のバランスを取る

**背景：**
- Claude Dispatch で外出先から PC での開発を継続
- 帰宅時に手動でスリープ有効化
- 寝る時間帯には自動的にスリープ

---

## ✅ 確定要件

### 機能要件

| # | 要件 | 詳細 |
|---|------|------|
| **(1)** | スリープ時間設定 | モニタースリープまでの時間を分単位で設定可能 |
| **(2)** | スリープ無効化 | スリープ機能を OFF（常時稼働） |
| **(3)** | スリープ有効化 | スリープ機能を ON（(1) の設定時間後に自動スリープ） |
| **(4)** | スケジュール機能 | **曜日単位で異なるルール適用** |
| **(5)** | 常駐アプリ | システムトレイに常駐、カジュアルに操作 |
| **(6)** | ローカルのみ | 外出先からの制御は不要 |

### スケジュール要件の詳細

**曜日単位設定：**
```
平日（月～金）:
  09:00 ~ 18:00 : スリープ OFF（無視）
  18:00 ~ 09:00 : スリープ ON（(1)の設定時間後）

休日（土日）:
  自由に設定可能（デフォルト：全時間 ON）
```

**祝日対応：**
- 将来的に実装予定
- アーキテクチャ設計時から対応可能な構造にしておく
- 初版では未実装

---

## 🏗️ アーキテクチャ設計

### ディレクトリ構成

```
sleep_control_app/
├── main.py                 # エントリーポイント
├── config/
│   ├── __init__.py
│   └── settings.py         # 設定管理（JSON ベース）
├── core/
│   ├── __init__.py
│   ├── power_control.py    # OS コマンド実行
│   ├── schedule.py         # スケジュール判定ロジック
│   └── state_manager.py    # 現在状態管理
├── ui/
│   ├── __init__.py
│   └── tray_app.py         # システムトレイ UI
├── data/
│   ├── config.json         # ユーザー設定（保存）
│   └── holidays.json       # 祝日リスト（将来用）
├── requirements.txt
└── README.md
```

### 各モジュールの責務

**`config/settings.py`**
- スリープ時間、スケジュール設定を JSON で管理
- 祝日リスト追加時も、同じ JSON 構造で対応可能
- デフォルト設定値の提供

**`core/schedule.py`**
- 現在時刻と曜日から「スリープ OFF 時間帯か？」を判定
- 祝日判定ロジックを後追加可能な設計
- `should_sleep_be_disabled_now(config, current_datetime)` → bool

**`core/power_control.py`**
- `powercfg` コマンド実行（現在状態確認、設定変更）
- Windows OS コマンドの実行管理
- エラーハンドリング

**`core/state_manager.py`**
- 現在のスリープ状態を管理
- スケジュール自動適用と手動操作の競合回避
- 状態変更履歴ログ

**`ui/tray_app.py`**
- システムトレイ UI（PySimpleGUI）
- 設定変更、スケジュール表示、状態確認
- トレイアイコンクリックで操作メニュー表示

---

## 📋 設定ファイル設計（JSON）

### `config.json` の例

```json
{
  "sleep_time_minutes": 15,
  "schedule": {
    "enabled": true,
    "rules": [
      {
        "weekday": "mon-fri",
        "description": "平日",
        "off_hours": {
          "start": "09:00",
          "end": "18:00"
        }
      },
      {
        "weekday": "sat-sun",
        "description": "休日",
        "off_hours": {
          "start": "10:00",
          "end": "22:00"
        }
      }
    ],
    "holidays": []
  }
}
```

**将来の拡張（祝日対応）：**
```json
"holidays": [
  {"date": "2025-01-01", "name": "元日", "sleep_off": false},
  {"date": "2025-01-13", "name": "成人の日", "sleep_off": false}
]
```

---

## 🔄 スケジュール判定ロジック（疑似コード）

```python
def should_sleep_be_disabled_now(config, current_datetime):
    """
    現在時刻で「スリープ OFF にするべき」かを判定
    → True なら スリープ無効化, False なら スリープ有効化
    """
    
    # 1. 祝日判定（将来実装）
    if is_holiday(current_datetime, config['holidays']):
        return config['holidays'][date]['sleep_off']
    
    # 2. 曜日判定
    weekday = current_datetime.strftime('%A')  # 'Monday', 'Tuesday', ...
    current_time = current_datetime.strftime('%H:%M')
    
    for rule in config['schedule']['rules']:
        if matches_weekday(weekday, rule['weekday']):
            off_start = rule['off_hours']['start']
            off_end = rule['off_hours']['end']
            
            if off_start <= current_time < off_end:
                return True  # スリープ OFF
            else:
                return False  # スリープ ON
    
    return False  # デフォルト: スリープ ON
```

---

## 🎮 UI フロー（常駐アプリ）

システムトレイアイコンから以下を操作：

```
【トレイメニュー】
├─ 🟢 スリープ有効化
├─ 🔴 スリープ無効化
├─ ⏱️ スリープ時間設定 → スピンボックスで分数指定
├─ 📅 スケジュール設定 → 曜日・時間帯を編集
├─ 📊 状態確認
│  └─ 現在: スリープ有効（次: 15分後）
│  └─ スケジュール: 有効（今は平日 09:30 → 18:00 OFF）
└─ 🚪 終了
```

---

## ⚡ 実装フェーズ

### フェーズ 1（MVP）：基本機能

**実装内容：**
- (1) スリープ時間設定 ✅
- (2) スリープ無効化 ✅
- (3) スリープ有効化 ✅
- (5) 常駐アプリ ✅
- 設定 JSON 保存・読込

**成果物：**
- 動作する常駐アプリ
- トレイから基本操作可能
- 設定が保存される

### フェーズ 2：スケジュール機能

**実装内容：**
- (4) 曜日単位スケジュール
- スケジュール自動適用
- スケジュール設定 UI

**成果物：**
- 曜日ごとに異なるルール適用
- 時刻切り替わりで自動適用

### フェーズ 3（将来）：祝日対応

**実装内容：**
- 祝日リスト管理
- 祝日判定ロジック
- GUI での祝日カスタマイズ

---

## 🛠️ 技術スタック

**言語：** Python 3.x

**GUI フレームワーク：** PySimpleGUI

**設定管理：** JSON（組み込み json モジュール）

**OS コマンド実行：** subprocess

**配布方法：** PyInstaller で exe 化

---

## 🔧 実装時の留意点

### スケジュール自動適用の方式

**A案：定期チェック（1分ごと）**
- メリット：実装が簡単、確実
- デメリット：CPU 負荷微増

**B案：時刻切り替わり時だけチェック**
- メリット：効率的
- デメリット：実装がやや複雑

→ **初版は A案を採用（シンプル）、必要に応じて B案へ最適化**

### Windows コマンド

**スリープ有効化：**
```bash
powercfg /change monitor-timeout-ac {分}
```

**スリープ無効化：**
```bash
powercfg /change monitor-timeout-ac 0
```

**即座にスリープ：**
```bash
rundll32.exe powrprof.dll,SetSuspendState 0,1,0
```

---

## 📦 依存ライブラリ

```
PySimpleGUI>=4.60.0
```

---

## 🎯 次のステップ

1. **Claude Code で実装開始**
   - フェーズ 1 の MVP 実装
   - テスト（Windows 11 環境で）

2. **フェーズ 2 への移行**
   - スケジュール機能追加
   - UI 改善

3. **配布準備**
   - PyInstaller で exe 化
   - README 作成

---

## 📝 プロジェクトメタ情報

- **開始日：** 2026-04-29
- **言語：** 日本語（ドキュメント）/ English（コード）
- **ライセンス：** 個人用（未定）
- **GitHub：** 未定

---

**このドキュメントは、Claude Code での実装時に参照してください。**
