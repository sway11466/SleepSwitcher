# backlog.md — SleepSwitcher タスク管理

## フェーズ 1：MVP（基本機能）

### セットアップ
- [ ] ディレクトリ構成を作成（`config/`, `core/`, `ui/`, `data/`）
- [ ] `requirements.txt` 作成
- [ ] 各モジュールの `__init__.py` 作成

### config/settings.py
- [ ] デフォルト設定値の定義
- [ ] `data/config.json` の読み込み
- [ ] `data/config.json` への書き込み

### core/power_control.py
- [ ] `disable_sleep()` — powercfg でスリープ無効化
- [ ] `enable_sleep(minutes)` — powercfg でスリープ有効化
- [ ] `get_current_timeout()` — 現在の設定値取得

### core/state_manager.py
- [ ] `force_disable()` — 手動スリープ無効化
- [ ] `force_enable()` — 手動スリープ有効化
- [ ] `get_status()` — UI 表示用の状態取得

### ui/tray_app.py
- [ ] システムトレイアイコン表示
- [ ] トレイメニュー（有効化・無効化・時間設定・終了）
- [ ] スリープ時間設定ダイアログ
- [ ] 状態に応じたアイコン切り替え

### main.py
- [ ] アプリ起動エントリーポイント
- [ ] 起動時に設定を読み込み・適用

### 動作確認
- [ ] Windows 11 実機でトレイ表示確認
- [ ] スリープ有効化・無効化の動作確認
- [ ] 設定の保存・読み込み確認
- [ ] アプリ終了後もスリープ設定が維持されることを確認

---

## フェーズ 2：スケジュール機能

### core/schedule.py
- [ ] `should_disable_sleep(config, now)` — 判定ロジック実装
- [ ] 曜日グループ（`mon-fri`, `sat-sun`）のパース
- [ ] 時刻範囲の判定（`off_hours` 内かどうか）
- [ ] `is_holiday()` スタブ追加（フェーズ 3 用）

### core/state_manager.py
- [ ] 1分ごとのポーリングタイマー追加
- [ ] `apply_schedule()` — スケジュール自動適用

### ui/tray_app.py
- [ ] スケジュール設定ダイアログ
  - [ ] スケジュール有効/無効チェックボックス
  - [ ] 曜日グループごとの開始・終了時刻入力
  - [ ] 保存ボタン
- [ ] トレイメニューにスケジュール設定を追加
- [ ] 状態表示にスケジュール情報を追加

### 動作確認
- [ ] 平日 09:00〜18:00 にスリープ OFF が自動適用されることを確認
- [ ] 時間帯をまたいだ切り替えの動作確認
- [ ] スケジュール設定の保存・読み込み確認

---

## フェーズ 3：祝日対応（将来）

- [ ] `data/holidays.json` フォーマット定義
- [ ] `core/schedule.py` の `is_holiday()` 実装
- [ ] 祝日リスト管理 UI
- [ ] 祝日当日のルール適用確認

---

## 配布準備

- [ ] `assets/icon.ico` アイコン作成
- [ ] PyInstaller で exe ビルド確認
- [ ] README.md 作成（インストール手順・使い方）
- [ ] スタートアップ登録の手順確認（オプション）

---

## 凡例

- `[ ]` 未着手
- `[x]` 完了
- `[-]` スキップ・対象外
