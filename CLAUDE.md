# CLAUDE.md — SleepSwitcher 開発ガイド

## プロジェクト概要

Windows 11 のスリープ・休止状態を自動制御するシステムトレイ常駐アプリ。
Python + tkinter で実装し、PyInstaller で exe 配布。

## Claude の行動規則

- コマンド実行・ファイル生成・git 操作は、ユーザーの明示的な指示があるまで実行しない
- 提案は「〇〇してよいですか？」と確認するにとどめる

## 開発方針

- ミニマル実装：要件外の機能追加・過剰な抽象化をしない
- フェーズ単位で動くものを作る（フェーズ 1 → 2 → 3 の順）
- コメントは「なぜ」が非自明な箇所のみ記述する
- エラーハンドリングはシステム境界（OS コマンド実行）のみ

## 技術スタック

→ [doc/architecture.md](doc/architecture.md) の「技術選定の理由」を参照

## よく使うコマンド

```bash
# 依存ライブラリのインストール
pip install -r requirements.txt

# アプリ起動
python main.py

# exe ビルド（assets を埋め込み）
pyinstaller --onefile --windowed --icon=assets/icon.ico --name SleepSwitcher --add-data "assets/pc_sleeping.jpg;assets" --add-data "assets/pc_awake.jpg;assets" --add-data "assets/icon.ico;assets" --collect-data holiday_jp main.py

# インストーラービルド
"%LOCALAPPDATA%\Programs\Inno Setup 6\iscc.exe" installer/installer.iss
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

→ [doc/architecture.md](doc/architecture.md) の「ディレクトリ構成」を参照

## 制約・注意事項

- Windows 11 専用（powercfg は Windows コマンド）
- 管理者権限なしで動作すること（powercfg /change は一般ユーザーで実行可能）
- ローカル専用アプリ：ネットワーク機能は実装しない
- PyInstaller でビルドする際は `--add-data` で assets を埋め込むこと
- holiday-jp-pip の祝日 CSV を含めるため `--collect-data holiday_jp` も必須
