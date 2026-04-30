# SleepSwitcher

Windows 11 のスリープ・休止状態を自動制御するシステムトレイ常駐アプリ。

## 技術スタック

- Python 3.13
- pystray（トレイアイコン）
- tkinter（設定画面 UI）
- Pillow（アイコン画像生成）
- PyInstaller（exe ビルド）

詳細は [doc/architecture.md](doc/architecture.md) を参照。

## セットアップ

```bash
pip install -r requirements.txt
```

## 起動

```bash
python main.py
```

## exe ビルド

```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```

## ディレクトリ構成

詳細は [doc/architecture.md](doc/architecture.md) を参照。

## ドキュメント

- [doc/spec.md](doc/spec.md) — 機能仕様
- [doc/architecture.md](doc/architecture.md) — アーキテクチャ
- [doc/backlog.md](doc/backlog.md) — タスク管理
