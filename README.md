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

## ビルド

### exe ビルド

```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico --name SleepSwitcher main.py
```

### インストーラービルド

事前に [Inno Setup 6](https://jrsoftware.org/isdl.php) をインストールしておく。

- wingetでインストールした場合
```bash
"%LOCALAPPDATA%\Programs\Inno Setup 6\iscc.exe" installer/installer.iss
```

- 公式インストーラーでインストールした場合
```bash
"C:\Program Files (x86)\Inno Setup 6\iscc.exe" installer/installer.iss
```

ビルド成果物は `dist/` に出力される：
- `dist/SleepSwitcher.exe` — 単体 exe
- `dist/SleepSwitcher_Setup.exe` — インストーラー

## ディレクトリ構成

詳細は [doc/architecture.md](doc/architecture.md) を参照。

## ドキュメント

- [doc/spec.md](doc/spec.md) — 機能仕様
- [doc/architecture.md](doc/architecture.md) — アーキテクチャ
- [doc/backlog.md](doc/backlog.md) — タスク管理
