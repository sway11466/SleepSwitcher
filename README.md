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
pyinstaller --onefile --windowed --icon=assets/icon.ico --name SleepSwitcher --add-data "assets/pc_sleeping.jpg;assets" --add-data "assets/pc_awake.jpg;assets" --add-data "assets/icon.ico;assets" --collect-data holiday_jp main.py
copy assets\syukujitsu.csv dist\syukujitsu.csv
copy assets\readme.txt dist\readme.txt
```

- `--collect-data holiday_jp` は holiday-jp-pip の import 時に必要なバンドル CSV を埋め込むため必須
- `syukujitsu.csv` は exe と同じフォルダに配置する（ユーザが後から差し替えできるように外出ししている）

### 配布用 zip 作成

GitHub Releases に添付する用の zip。`v1.1.0` の部分は実際のバージョンに置き換える。

```powershell
Compress-Archive -Path dist\SleepSwitcher.exe,dist\syukujitsu.csv,dist\readme.txt -DestinationPath dist\SleepSwitcher_v1.1.0.zip -Force
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
- `dist/syukujitsu.csv` — 祝日 CSV（exe と並べて配置する）
- `dist/readme.txt` — ユーザ向け README
- `dist/SleepSwitcher_v{version}.zip` — exe・CSV・README をまとめた配布用 zip
- `dist/SleepSwitcher_Setup.exe` — インストーラー

## ディレクトリ構成

詳細は [doc/architecture.md](doc/architecture.md) を参照。

## ドキュメント

- [doc/spec.md](doc/spec.md) — 機能仕様
- [doc/architecture.md](doc/architecture.md) — アーキテクチャ
- [doc/backlog.md](doc/backlog.md) — タスク管理
