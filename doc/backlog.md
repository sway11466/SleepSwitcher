# backlog.md — SleepSwitcher タスク管理

## 当日のみの一時的な変更を行う機能

詳細未決。スケジュールに「当日のみ」があるといいのかな？

## 祝日対応

祝日判定は別プロジェクト [holiday-jp-pip](https://github.com/sway11466/holiday-jp-pip) を採用。

- [x] `core/holidays.py` を holiday-jp-pip を使って実装（mtime キャッシュ付き）
- [x] `core/schedule.py` を祝日対応に修正（祝日は `days.holiday` のみ参照）
- [x] `config/settings.py` に `holiday` キー追加と旧設定マイグレーション
- [x] `ui/tray_app.py` のスケジュール表に「祝」行を追加
- [x] PyInstaller ビルドコマンドに `--collect-data holiday_jp` 追加
- [x] 祝日 CSV を外部ファイル化（holiday-jp-pip v0.3.0 の `csv_path` 機能を利用）
- [x] CSV 探索順を実装（AppData → exe 同フォルダ／dev は repo の assets）
- [x] インストーラとビルド手順に CSV 配置を追加
- [ ] 祝日当日のスケジュール適用確認（実機テスト）
- [ ] AppData 上書きと CSV 差し替え再読込の動作確認（実機テスト）

---

## 凡例

- `[ ]` 未着手
- `[x]` 完了
- `[-]` スキップ・対象外
