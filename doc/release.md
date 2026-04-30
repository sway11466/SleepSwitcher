# release.md — リリース手順・バージョン管理

## バージョン番号の考え方

セマンティックバージョニング（`Major.Minor.Patch`）を採用。

| バージョン | 上げるタイミング |
|------------|------------------|
| Major      | 互換性のない大きな変更（UI の刷新など） |
| Minor      | 機能追加（スケジュール機能追加など） |
| Patch      | バグ修正・細かい改善 |

例: `1.0.0` → バグ修正 → `1.0.1` → 機能追加 → `1.1.0`

---

## バージョン番号を変更する場所

リリース時に以下を手動で揃える。

- `installer/installer.iss` の `#define AppVersion`

---

## リリース手順

### 1. バージョン番号を更新

`installer/installer.iss` の `AppVersion` を新しいバージョンに変更してコミット。

```
git add installer/installer.iss
git commit -m "bump version to x.x.x"
```

### 2. ビルド

[README.md のビルド手順](../README.md#ビルド) を参照。

### 3. Git タグを打つ

```bash
git tag v1.0.0
git push origin v1.0.0
```

### 4. GitHub Releases に公開

1. GitHub のリポジトリページ →「Releases」→「Draft a new release」
2. タグ（`v1.0.0`）を選択
3. タイトル例：`SleepSwitcher v1.0.0`
4. 以下のファイルを添付：
   - `dist/SleepSwitcher.exe`
   - `dist/SleepSwitcher_Setup.exe`
5. 「Publish release」

---

## 注意事項

- `dist/` は `.gitignore` に含めてリポジトリには含めない
- ビルド前に動作確認を行うこと
