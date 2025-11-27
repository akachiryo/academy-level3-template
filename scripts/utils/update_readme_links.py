#!/usr/bin/env python3
"""
README内のリンクを動的に更新するスクリプト
共通ライブラリを使用してリファクタリング済み
"""

import sys
import os
import re
from typing import Dict, List, Optional

# 共通ライブラリをインポート
sys.path.append('scripts')
from common.github_api import GitHubAPI

def get_project_urls(github_api: GitHubAPI) -> Dict[str, str]:
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
        'owner': github_api.owner,
        'name': github_api.repo_name
    }
    
    result = github_api.graphql_request(query, variables)
    project_urls = {}
    
    if result and 'repository' in result:
        projects = result['repository']['projectsV2']['nodes']
        for project in projects:
            if 'タスク' in project['title'] or 'task' in project['title'].lower():
                project_urls['task'] = project['url']
            elif 'KPT' in project['title']:
                project_urls['kpt'] = project['url']
    
    return project_urls

def get_issue_urls(github_api: GitHubAPI) -> Dict[str, str]:
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
        'owner': github_api.owner,
        'name': github_api.repo_name
    }
    
    result = github_api.graphql_request(query, variables)
    issue_urls = {}
    
    if result and 'repository' in result:
        issues = result['repository']['issues']['nodes']
        for issue in issues:
            if 'KPT説明' in issue['title'] or 'KPTキックオフ' in issue['title']:
                issue_urls['kpt_kickoff'] = issue['url']
            elif 'タスク000' in issue['title'] or '見積もりについて' in issue['title']:
                issue_urls['task000'] = issue['url']
    
    return issue_urls

def update_readme(github_api: GitHubAPI):
    """READMEファイルを更新"""
    readme_path = 'README.md'
    
    # URLを取得
    print("📊 Getting project URLs...")
    project_urls = get_project_urls(github_api)
    
    print("📋 Getting issue URLs...")
    issue_urls = get_issue_urls(github_api)
    
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
        for key, url in {**project_urls, **issue_urls}.items():
            f.write(f"{key}: {url}\n")

def main():
    """メイン処理"""
    print("=" * 60)
    print("🔗 README LINKS UPDATE")
    print("=" * 60)
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script: update_readme_links.py")
    print("=" * 60)
    
    try:
        # GitHub APIクラスの初期化
        github_api = GitHubAPI()
        print(f"📦 Repository: {github_api.repository}")
        
        # READMEを更新
        update_readme(github_api)
        print("\n✅ README links update complete!")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import time
    exit(main())