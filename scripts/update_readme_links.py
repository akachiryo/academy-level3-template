#!/usr/bin/env python3
"""
README内のリンクを動的に更新するスクリプト
"""

import os
import re
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
        print(f"❌ GraphQL Error: {response.status_code}")
        return {}
    
    data = response.json()
    if 'errors' in data:
        print(f"❌ GraphQL Errors: {data['errors']}")
        return {}
    
    return data.get('data', {})

def get_project_urls() -> Dict[str, str]:
    """プロジェクトのURLを取得"""
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            projectsV2(first: 10) {
                nodes {
                    title
                    url
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
    project_urls = {}
    
    if result and 'repository' in result:
        projects = result['repository']['projectsV2']['nodes']
        for project in projects:
            if 'タスク' in project['title'] or 'task' in project['title'].lower():
                project_urls['task'] = project['url']
            elif 'KPT' in project['title']:
                project_urls['kpt'] = project['url']
            elif 'テスト' in project['title'] or 'test' in project['title'].lower():
                project_urls['test'] = project['url']
    
    return project_urls

def get_issue_urls() -> Dict[str, str]:
    """特定のIssueのURLを取得"""
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            issues(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
                nodes {
                    title
                    url
                    number
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
    issue_urls = {}
    
    if result and 'repository' in result:
        issues = result['repository']['issues']['nodes']
        for issue in issues:
            if 'KPT説明' in issue['title'] or 'KPTキックオフ' in issue['title']:
                issue_urls['kpt_kickoff'] = issue['url']
            elif 'タスク000' in issue['title'] or '見積もりについて' in issue['title']:
                issue_urls['task000'] = issue['url']
    
    return issue_urls

def get_discussion_urls() -> Dict[str, str]:
    """DiscussionのURLを取得"""
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            discussions(first: 20) {
                nodes {
                    title
                    url
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
    discussion_urls = {}
    
    if result and 'repository' in result:
        discussions = result['repository']['discussions']['nodes']
        for discussion in discussions:
            if 'プロジェクト概要' in discussion['title']:
                discussion_urls['project_overview'] = discussion['url']
            elif 'チーム開発ルール' in discussion['title'] or 'ルール' in discussion['title']:
                discussion_urls['rules'] = discussion['url']
            elif 'テーブル設計' in discussion['title'] or 'DB設計' in discussion['title']:
                discussion_urls['table_design'] = discussion['url']
    
    return discussion_urls

def update_readme():
    """READMEファイルを更新"""
    readme_path = 'README.md'
    
    # URLを取得
    print("📊 Getting project URLs...")
    project_urls = get_project_urls()
    
    print("📋 Getting issue URLs...")
    issue_urls = get_issue_urls()
    
    print("💬 Getting discussion URLs...")
    discussion_urls = get_discussion_urls()
    
    # READMEを読み込み
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # リンクを更新
    replacements = {
        # KPT関連
        r'\[KPTキックオフ説明Issue\]\(#\)': f"[KPTキックオフ説明Issue]({issue_urls.get('kpt_kickoff', '#')})",
        r'\[KPTプロジェクトボード\]\(#\)': f"[KPTプロジェクトボード]({project_urls.get('kpt', '#')})",
        
        # タスク関連  
        r'\[タスク000: 見積もりIssue\]\(#\)': f"[タスク000: 見積もりIssue]({issue_urls.get('task000', '#')})",
        r'\[タスクプロジェクトボード\]\(#\)': f"[タスクプロジェクトボード]({project_urls.get('task', '#')})",
    }
    
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)
    
    # ファイルを更新
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ README updated with dynamic links")
    
    # 結果を保存
    with open('readme_links_result.txt', 'w', encoding='utf-8') as f:
        f.write(f"Projects: {len(project_urls)} found\n")
        f.write(f"Issues: {len(issue_urls)} found\n")
        f.write(f"Discussions: {len(discussion_urls)} found\n")
        for key, url in {**project_urls, **issue_urls, **discussion_urls}.items():
            f.write(f"{key}: {url}\n")

def main():
    print("=" * 50)
    print("🔗 Updating README Links")
    print("=" * 50)
    
    try:
        update_readme()
        print("✅ README links update complete!")
    except Exception as e:
        print(f"❌ Error updating README: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()