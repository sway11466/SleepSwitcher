# CLAUDE.md — SleepSwitcher 開発ガイド

## プロジェクト概要

Windows 11 のモニタースリープを自動制御するシステムトレイ常駐アプリ。
Python + PySimpleGUI で実装し、PyInstaller で exe 配布。

## 開発方針

- ミニマル実装：要件外の機能追加・過剰な抽象化をしない
- フェーズ単位で動くものを作る（フェーズ 1 → 2 → 3 の順）
- コメントは「なぜ」が非自明な箇所のみ記述する
- エラーハンドリングはシステム境界（OS コマンド実行）のみ

## 技術スタック

- Python 3.x
- PySimpleGUI（システムトレイ UI）
- subprocess（powercfg コマンド実行）
- json（設定ファイル管理）
- PyInstaller（exe 化）

## よく使うコマンド

```bash
# 依存ライブラリのインストール
pip install -r requirements.txt

# アプリ起動
python main.py

# exe ビルド
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```

## Windows コマンド（powercfg）

```bash
# モニタースリープを N 分後に設定（AC 電源）
powercfg /change monitor-timeout-ac {N}

# モニタースリープを無効化（0 = 無効）
powercfg /change monitor-timeout-ac 0

# 現在の電源設定を確認
powercfg /query SCHEME_CURRENT SUB_VIDEO VIDEOIDLE
```

## ディレクトリ構成

```
SleepSwitcher/
├── CLAUDE.md
├── spec.md
├── architecture.md
├── backlog.md
├── main.py
├── requirements.txt
├── config/
│   ├── __init__.py
│   └── settings.py
├── core/
│   ├── __init__.py
│   ├── power_control.py
│   ├── schedule.py
│   └── state_manager.py
├── ui/
│   ├── __init__.py
│   └── tray_app.py
└── data/
    ├── config.json
    └── holidays.json
```

## 制約・注意事項

- Windows 11 専用（powercfg は Windows コマンド）
- 管理者権限なしで動作すること（powercfg /change は一般ユーザーで実行可能）
- ローカル専用アプリ：ネットワーク機能は実装しない
- PySimpleGUI のライセンスに注意（個人利用は無償）
