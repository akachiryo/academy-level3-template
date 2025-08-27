# イマココSNS開発プロジェクト

このプロジェクトは、アカデミー生を対象としたイマココSNSチーム開発用リポジトリです。

## 🚀 チーム開発環境自動セットアップ

### 1. GitHub Personal Access Tokenの作成

1. **Personal Access Tokenの作成**
   - 画面右上の自身のアイコン → サイドバー → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic) をクリック
   - Noteに任意の名前(academy-token等)を入力
   - Expirationは「Cusom」を選択し、１年後の日付を入力
   - 下記にチェックをつける:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `project` (Full control of projects)
     - ✅ `write:discussion` (Read and write team discussions)
   - 「Generate token」ボタンをクリック
   - tokenが生成され画面に表示されるため、メモする

2. **Repository Secretへの登録**
   - cloneしたリポジトリ → 「Settings」タブ → Secrets and variables → Actions
   - 「New repository secret」ボタンクリック
   - Name: `TEAM_SETUP_TOKEN`を入力
   - Secret: メモしたトークンを貼り付け
   - 「Add secret」ボタン押下

### 2. 自動セットアップの実行
[![🚀 Team Setup](https://img.shields.io/badge/🚀_Team_Setup_v5.0-Click_to_Start-success?style=for-the-badge&logo=github)](../../actions/workflows/team-setup.yml)

1. 上記の「🚀 Team Setup」ボタンをクリック
2. `Run workflow` ボタンをクリックして実行
3. [Actions](../../actions) タブで進行状況を確認
4. 全セットアップが完了するまで待つ

**v5.0の新機能**: プロジェクト情報（テーブル設計書、開発ルールなど）がDiscussionsとして作成されます。

### 3. 手動セットアップ
1. イマココSNS（KPT）のstatusをKPT用に変更する
- 変更前：Todo, In Progress, Done
- 変更後：Keep, Problem, Try, Done

## 🛠️ 開発環境

### 技術スタック

- **フレームワーク**: Spring Boot 3.2.0
- **データベース**: H2 Database (インメモリ)
- **ビルドツール**: Maven
- **コンテナ**: Docker

### 実行方法

```bash
# Docker Compose で起動
docker-compose up --build

# または Maven で起動
mvn spring-boot:run
```

アクセス: http://localhost:8080

## 🔧 トラブルシューティング

### 古いエラーが出る場合（v5.0移行後）
もし以下のエラーメッセージが表示される場合:
- `⚠️ Limiting to first 50 test issues to avoid rate limits`
- `⚠️ Limiting to first 30 issues for project addition`
- Wiki関連のエラー

**これは古いコードが実行されている証拠です。**

### 解決手順
```bash
# 1. 環境をクリーンアップ
python scripts/cleanup_force_refresh.py

# 2. 環境を確認
python scripts/verify_environment.py

# 3. ワークフローを手動実行
# GitHub Actions タブで「🚀 Team Development Setup v5.0 (DISCUSSIONS MIGRATION)」を実行
```

## 📋 プロジェクト情報

v5.0より、プロジェクト情報はDiscussionsで管理されます：
- **テーブル設計書**: データベース設計の詳細
- **チーム開発ルール**: 開発・レビュールールとガイドライン
- **キックオフ情報**: プロジェクト開始情報
- **プロジェクト概要**: 全体概要と参考資料

[Discussions](../../discussions) タブでアクセスできます。

## 📝 参考資料

- [チーム開発説明資料](https://docs.google.com/presentation/d/1XO9Ru_5e85g63vwidmGGKmOZdUMKjqPG/edit?slide=id.p1#slide=id.p1)
- [Figma デザイン](https://www.figma.com/file/l8Zzw1wPJBitm0bQMNXTdB/イマココSNS)
