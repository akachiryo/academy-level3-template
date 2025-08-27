#!/usr/bin/env python3
"""
GitHub Discussions設定スクリプト v5.0 (Refactored)
デフォルトカテゴリーを削除し、議事録カテゴリーとテンプレートを作成
共通ライブラリを使用してリファクタリング済み
"""

import sys
import requests
import time
from typing import Dict, List, Optional

# 共通ライブラリをインポート
sys.path.append('scripts')
from common.github_api import GitHubAPI

def check_discussions_enabled(github_api: GitHubAPI) -> bool:
    """リポジトリでDiscussionsが有効化されているかチェック"""
    url = f"https://api.github.com/repos/{github_api.repository}"
    
    response = requests.get(url, headers=github_api.rest_headers)
    if response.status_code == 200:
        repo_data = response.json()
        discussions_enabled = repo_data.get('has_discussions', False)
        print(f"🔍 Discussions enabled: {discussions_enabled}")
        return discussions_enabled
    else:
        print(f"⚠️ Could not check discussions status: {response.status_code}")
        return False

def enable_discussions(github_api: GitHubAPI) -> bool:
    """リポジトリでDiscussionsを有効化"""
    url = f"https://api.github.com/repos/{github_api.repository}"
    
    data = {'has_discussions': True}
    response = requests.patch(url, json=data, headers=github_api.rest_headers)
    
    if response.status_code == 200:
        print("✅ Discussions enabled successfully")
        return True
    else:
        print(f"❌ Failed to enable discussions: {response.status_code} - {response.text}")
        return False

def get_repository_info(github_api: GitHubAPI) -> Optional[Dict]:
    """リポジトリ情報とDiscussionカテゴリーを取得"""
    # まずDiscussionsが有効かチェック
    if not check_discussions_enabled(github_api):
        print("📝 Discussions not enabled, attempting to enable...")
        if not enable_discussions(github_api):
            print("⚠️ Could not enable discussions automatically")
            print("💡 Please enable discussions manually:")
            print(f"   1. Go to https://github.com/{github_api.repository}/settings")
            print("   2. Scroll down to 'Features' section")
            print("   3. Check 'Discussions' checkbox")
            return None
        else:
            # 有効化後少し待機
            print("⏳ Waiting for discussions to be fully enabled...")
            time.sleep(5)
    
    # リポジトリ情報とDiscussionカテゴリーを取得
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            id
            hasDiscussionsEnabled
            discussionCategories(first: 20) {
                nodes {
                    id
                    name
                    slug
                    description
                    isAnswerable
                }
            }
        }
    }
    """
    
    variables = {
        'owner': github_api.owner,
        'name': github_api.repo_name
    }
    
    result = github_api.graphql_request(query, variables)
    if result and 'repository' in result:
        repo = result['repository']
        print(f"📊 Repository discussions enabled: {repo.get('hasDiscussionsEnabled', 'Unknown')}")
        print(f"📊 Found {len(repo.get('discussionCategories', {}).get('nodes', []))} discussion categories")
        return repo
    return None

def get_existing_discussions(github_api: GitHubAPI, repository_id: str) -> List[Dict]:
    """既存のDiscussionsを取得"""
    query = """
    query($repositoryId: ID!) {
        node(id: $repositoryId) {
            ... on Repository {
                discussions(first: 100) {
                    nodes {
                        id
                        title
                        body
                        category {
                            id
                            name
                        }
                        createdAt
                        updatedAt
                    }
                }
            }
        }
    }
    """
    
    variables = {'repositoryId': repository_id}
    
    result = github_api.graphql_request(query, variables)
    if result and 'node' in result and result['node']:
        discussions = result['node'].get('discussions', {}).get('nodes', [])
        print(f"📄 Found {len(discussions)} existing discussions")
        return discussions
    return []

def create_category_via_web_api(github_api: GitHubAPI, repository_id: str, name: str, description: str) -> Optional[str]:
    """WebAPI経由でDiscussionカテゴリーを作成（GraphQLで制限がある場合）"""
    # GraphQLのcreateDiscussionCategoryを使用
    category_id = github_api.create_discussion_category(name, description, "📋")
    if category_id:
        print(f"✅ Created discussion category: {name}")
        return category_id
    else:
        print(f"❌ Failed to create discussion category: {name}")
        return None

def create_discussion(github_api: GitHubAPI, repository_id: str, category_id: str, title: str, body: str) -> bool:
    """Discussionを作成"""
    discussion_id = github_api.create_discussion(title, body, category_id)
    if discussion_id:
        print(f"✅ Created discussion: {title}")
        return True
    else:
        print(f"❌ Failed to create discussion: {title}")
        return False

def main():
    """メイン処理"""
    print("=" * 60)
    print("💬 GITHUB DISCUSSIONS SETUP v5.0 (Refactored)")
    print("=" * 60)
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script: setup_discussions.py v5.0 (Refactored)")
    print("=" * 60)
    
    try:
        # GitHub APIクラスの初期化
        github_api = GitHubAPI()
        print(f"📦 Repository: {github_api.repository}")
        
        # リポジトリ情報とDiscussionカテゴリー取得
        repo_info = get_repository_info(github_api)
        if not repo_info:
            return 1
        
        repository_id = repo_info['id']
        categories = repo_info.get('discussionCategories', {}).get('nodes', [])
        
        # 既存カテゴリーをチェック
        category_names = [cat['name'] for cat in categories]
        print(f"\n📋 Existing categories: {', '.join(category_names) if category_names else 'None'}")
        
        # 議事録カテゴリーが存在するかチェック
        meeting_category_id = None
        for category in categories:
            if category['name'] == '議事録':
                meeting_category_id = category['id']
                print(f"ℹ️ Found existing '議事録' category")
                break
        
        # 議事録カテゴリーが存在しない場合は作成
        if not meeting_category_id:
            print("📝 Creating '議事録' discussion category...")
            meeting_category_id = create_category_via_web_api(
                github_api,
                repository_id,
                "議事録",
                "チーム開発の議事録を管理するカテゴリーです"
            )
            
            if not meeting_category_id:
                print("❌ Failed to create meeting category")
                return 1
        
        # 既存のDiscussionsをチェック
        existing_discussions = get_existing_discussions(github_api, repository_id)
        discussion_titles = [d['title'] for d in existing_discussions]
        
        # キックオフ議事録の作成
        kickoff_title = "キックオフ議事録"
        if kickoff_title not in discussion_titles:
            print(f"\n📝 Creating '{kickoff_title}' discussion...")
            
            kickoff_body = """# キックオフ議事録

## 開催情報
- **日時**: 2024年XX月XX日 XX:XX-XX:XX
- **参加者**: 
  - [ ] メンバー1
  - [ ] メンバー2
  - [ ] メンバー3
  - [ ] メンバー4

## アジェンダ
1. **プロジェクト概要説明** (10分)
   - イマココSNSの機能要件
   - 技術スタック確認

2. **チーム体制の確認** (10分)
   - 役割分担の決定
   - コミュニケーション方法

3. **開発環境セットアップ** (15分)
   - 各自の環境構築状況確認
   - 問題があれば解決策検討

4. **スケジュール確認** (10分)
   - マイルストーンの確認
   - 今後の開発スケジュール

## 決定事項
- [ ] 役割分担の決定
- [ ] 使用する技術の最終確認
- [ ] コーディング規約の確認
- [ ] 開発フローの確認

## 次回までのアクション
- [ ] 各自の開発環境セットアップ完了
- [ ] 担当機能の詳細設計書作成
- [ ] 次回ミーティング日程調整

## その他・質問事項
(自由に記載してください)

---
**次回ミーティング予定**: 未定
**議事録作成者**: 
"""
            
            success = create_discussion(github_api, repository_id, meeting_category_id, kickoff_title, kickoff_body)
            if not success:
                print("❌ Failed to create kickoff discussion")
        else:
            print(f"ℹ️ Discussion '{kickoff_title}' already exists")
        
        print(f"\n✨ Discussions setup completed!")
        print(f"🔗 Access your discussions:")
        print(f"  https://github.com/{github_api.repository}/discussions")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")
        return 1

if __name__ == '__main__':
    exit(main())