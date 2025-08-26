#!/usr/bin/env python3
"""
WikiページをGitHub Discussionsに移行するスクリプト
private無料版ではWikiが使えないため、Discussionsで代替する
"""

import os
import csv
import time
import requests
from typing import Dict, List, Optional

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')

if not TEAM_SETUP_TOKEN or not GITHUB_REPOSITORY:
    raise ValueError("TEAM_SETUP_TOKEN and GITHUB_REPOSITORY environment variables are required")

REPO_OWNER, REPO_NAME = GITHUB_REPOSITORY.split('/')

# GitHub GraphQL API設定
GRAPHQL_URL = 'https://api.github.com/graphql'
HEADERS = {
    'Authorization': f'Bearer {TEAM_SETUP_TOKEN}',
    'Content-Type': 'application/json'
}

def graphql_request(query: str, variables: Dict = None) -> Dict:
    """GraphQL APIリクエスト実行"""
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    
    response = requests.post(GRAPHQL_URL, json=payload, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ GraphQL Error: {response.status_code} - {response.text}")
        return {}
    
    data = response.json()
    if 'errors' in data:
        print(f"❌ GraphQL Errors: {data['errors']}")
        return {}
    
    return data.get('data', {})

def get_general_category_id(repository_id: str) -> Optional[str]:
    """GeneralカテゴリーのIDを取得"""
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            discussionCategories(first: 20) {
                nodes {
                    id
                    name
                    slug
                }
            }
        }
    }
    """
    
    variables = {
        'owner': REPO_OWNER,
        'name': REPO_NAME
    }
    
    result = graphql_request(query, variables)
    if result and 'repository' in result:
        categories = result['repository']['discussionCategories']['nodes']
        for category in categories:
            if category['name'].lower() == 'general' or category['slug'] == 'general':
                print(f"✅ Found General category: {category['id']}")
                return category['id']
    
    print("❌ General category not found")
    return None

def create_discussion(repository_id: str, category_id: str, title: str, body: str) -> bool:
    """Discussionを作成"""
    query = """
    mutation($repositoryId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
        createDiscussion(input: {
            repositoryId: $repositoryId,
            categoryId: $categoryId,
            title: $title,
            body: $body
        }) {
            discussion {
                id
                title
                url
            }
        }
    }
    """
    
    variables = {
        'repositoryId': repository_id,
        'categoryId': category_id,
        'title': title,
        'body': body
    }
    
    result = graphql_request(query, variables)
    if result and 'createDiscussion' in result:
        discussion = result['createDiscussion']['discussion']
        print(f"  ✅ Created discussion: {discussion['title']}")
        print(f"  🔗 URL: {discussion['url']}")
        return True
    else:
        print(f"  ❌ Failed to create discussion: {title}")
        return False

def generate_table_design_content() -> str:
    """CSVファイルからテーブル設計書の内容を生成"""
    csv_path = 'data/imakoko_sns_tables.csv'
    
    if not os.path.exists(csv_path):
        return """# テーブル設計書

テーブル設計ファイルが見つかりません。

データベース設計の詳細については、プロジェクトメンバーにお問い合わせください。

*最終更新: {}*""".format(time.strftime('%Y-%m-%d %H:%M:%S'))
    
    content = """# テーブル設計書

イマココSNSのデータベース設計書です。

*最終更新: {}*

""".format(time.strftime('%Y-%m-%d %H:%M:%S'))
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # テーブルごとにグループ化
        tables = {}
        for row in rows:
            table_name = row['table_name']
            if table_name not in tables:
                tables[table_name] = {
                    'role': row['table_role'],
                    'columns': []
                }
            
            # 空のカラムは除外
            if row['logical_name'] and row['physical_name']:
                tables[table_name]['columns'].append(row)
        
        # 各テーブルの情報を出力
        for table_name, table_info in tables.items():
            content += f"## {table_name}\n\n"
            
            if table_info['role']:
                content += f"**役割**: {table_info['role']}\n\n"
            
            content += "| # | 論理名 | 物理名 | データ型 | 長さ | NOT NULL | PK | FK | 備考 |\n"
            content += "|---|--------|--------|----------|------|----------|----|----|------|\n"
            
            for col in table_info['columns']:
                num = col['column_no']
                logical = col['logical_name']
                physical = col['physical_name']
                dtype = col['data_type']
                length = col['length']
                not_null = "✓" if col['not_null'] == 'YES' else ""
                pk = "✓" if col['primary_key'] == 'YES' else ""
                fk = "✓" if col['foreign_key'] == 'YES' else ""
                note = col['note']
                
                content += f"| {num} | {logical} | {physical} | {dtype} | {length} | {not_null} | {pk} | {fk} | {note} |\n"
            
            content += "\n"
            
    except Exception as e:
        content += f"\nエラー: テーブル設計の読み込みに失敗しました - {str(e)}\n"
    
    return content

def read_wiki_file(filename: str) -> str:
    """Wikiファイルを読み込み"""
    file_path = f"wiki/{filename}"
    
    if not os.path.exists(file_path):
        return f"# {filename}\n\nファイルが見つかりません。"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"# {filename}\n\nファイルの読み込みエラー: {str(e)}"

def get_existing_discussions(repository_id: str) -> List[Dict]:
    """既存のディスカッションを取得"""
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            discussions(first: 100) {
                nodes {
                    id
                    title
                    category {
                        name
                    }
                }
            }
        }
    }
    """
    
    variables = {
        'owner': REPO_OWNER,
        'name': REPO_NAME
    }
    
    result = graphql_request(query, variables)
    if result and 'repository' in result:
        return result['repository']['discussions']['nodes']
    return []

def create_wiki_discussions(repository_id: str, category_id: str) -> int:
    """WikiページをDiscussionsとして作成"""
    discussions_to_create = [
        {
            'title': '📋 テーブル設計書',
            'content': generate_table_design_content()
        },
        {
            'title': '📖 チーム開発ルール',
            'content': read_wiki_file('ルール.md')
        },
        {
            'title': '🚀 キックオフ情報',
            'content': read_wiki_file('キックオフ.md')
        },
        {
            'title': '📝 プロジェクト概要',
            'content': read_wiki_file('Home.md').replace('# イマココSNS Wiki', '# プロジェクト概要\n\nイマココSNS開発プロジェクトの概要情報です。')
        }
    ]
    
    # 既存のディスカッションをチェック
    existing_discussions = get_existing_discussions(repository_id)
    existing_titles = [d['title'] for d in existing_discussions]
    
    created_count = 0
    
    for discussion in discussions_to_create:
        title = discussion['title']
        content = discussion['content']
        
        # 既に存在するかチェック
        if any(title in existing_title for existing_title in existing_titles):
            print(f"  ℹ️ Discussion already exists: {title}")
            continue
        
        if create_discussion(repository_id, category_id, title, content):
            created_count += 1
        
        # Rate limit対策
        time.sleep(2)
    
    return created_count

def get_repository_info() -> Optional[Dict]:
    """リポジトリ情報を取得"""
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            id
            hasDiscussionsEnabled
        }
    }
    """
    
    variables = {
        'owner': REPO_OWNER,
        'name': REPO_NAME
    }
    
    result = graphql_request(query, variables)
    if result and 'repository' in result:
        return result['repository']
    return None

def main():
    """メイン処理"""
    print("=" * 60)
    print("📚 WIKI TO DISCUSSIONS MIGRATION v1.0")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script: create_wiki_discussions.py v1.0")
    print("=" * 60)
    
    # リポジトリ情報取得
    repo_info = get_repository_info()
    if not repo_info:
        print("❌ Failed to get repository information")
        return 1
    
    repository_id = repo_info['id']
    
    if not repo_info.get('hasDiscussionsEnabled', False):
        print("⚠️ Discussions not enabled for this repository")
        print("💡 Please enable discussions first in repository settings")
        return 1
    
    # Generalカテゴリーを取得
    category_id = get_general_category_id(repository_id)
    if not category_id:
        print("❌ Could not find General category")
        return 1
    
    # WikiページをDiscussionsに移行
    print(f"\n📚 Creating Wiki content as discussions...")
    created_count = create_wiki_discussions(repository_id, category_id)
    
    print(f"\n✨ Wiki to Discussions migration completed!")
    print(f"📊 Created {created_count} new discussions")
    print(f"📌 All discussions created in 'General' category")
    
    print(f"\n🔗 Access your discussions:")
    print(f"  https://github.com/{GITHUB_REPOSITORY}/discussions")
    
    return 0

if __name__ == '__main__':
    exit(main())