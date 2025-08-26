#!/usr/bin/env python3
"""
GitHub Projects V2作成スクリプト
3つの独立したプロジェクトを作成する
"""

import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')

if not TEAM_SETUP_TOKEN or not GITHUB_REPOSITORY:
    raise ValueError("TEAM_SETUP_TOKEN and GITHUB_REPOSITORY environment variables are required")

REPO_OWNER, REPO_NAME = GITHUB_REPOSITORY.split('/')

# GitHub GraphQL API設定
# API Reference: https://docs.github.com/en/graphql/reference/mutations#createprojectv2
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

def get_repository_info() -> Optional[Dict]:
    """リポジトリ情報と既存プロジェクトを取得"""
    # API Reference: https://docs.github.com/en/graphql/reference/queries#repository
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            id
            owner {
                id
                __typename
            }
            projectsV2(first: 100) {
                nodes {
                    id
                    title
                    number
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
    if result and 'repository' in result:
        return {
            'repository_id': result['repository']['id'],
            'owner_id': result['repository']['owner']['id'],
            'existing_projects': result['repository']['projectsV2']['nodes']
        }
    return None

def generate_sprint_options() -> List[str]:
    """Sprint選択肢を動的生成（3ヶ月分）"""
    start_date = datetime.now()
    options = []
    
    for i in range(13):  # 約3ヶ月分（13週間）
        sprint_start = start_date + timedelta(weeks=i)
        sprint_end = sprint_start + timedelta(days=6)
        
        # 日付フォーマット: 月/日 形式
        sprint_name = f"Sprint {i+1} ({sprint_start.month}/{sprint_start.day}-{sprint_end.month}/{sprint_end.day})"
        options.append(sprint_name)
    
    return options

def get_existing_fields(project_id: str) -> Dict[str, str]:
    """プロジェクトの既存フィールドを取得"""
    query = """
    query($projectId: ID!) {
        node(id: $projectId) {
            ... on ProjectV2 {
                fields(first: 100) {
                    nodes {
                        ... on ProjectV2SingleSelectField {
                            id
                            name
                        }
                    }
                }
            }
        }
    }
    """
    
    variables = {'projectId': project_id}
    result = graphql_request(query, variables)
    
    fields = {}
    if result and 'node' in result:
        field_nodes = result['node'].get('fields', {}).get('nodes', [])
        for field in field_nodes:
            if field and 'name' in field:
                fields[field['name']] = field['id']
    
    return fields

def create_custom_field(project_id: str, field_name: str, options: List[str]) -> Optional[str]:
    """プロジェクトにカスタムフィールドを作成"""
    # API Reference: https://docs.github.com/en/graphql/reference/mutations#createprojectv2field
    query = """
    mutation($projectId: ID!, $name: String!, $dataType: ProjectV2CustomFieldType!, $options: [ProjectV2SingleSelectFieldOptionInput!]) {
        createProjectV2Field(input: {
            projectId: $projectId,
            name: $name,
            dataType: $dataType,
            singleSelectOptions: $options
        }) {
            projectV2Field {
                ... on ProjectV2SingleSelectField {
                    id
                    name
                    options {
                        id
                        name
                    }
                }
            }
        }
    }
    """
    
    # オプションを作成
    field_options = []
    for option in options:
        field_options.append({
            "name": option,
            "color": "GRAY",  # デフォルトカラー
            "description": ""
        })
    
    variables = {
        'projectId': project_id,
        'name': field_name,
        'dataType': 'SINGLE_SELECT',
        'options': field_options
    }
    
    result = graphql_request(query, variables)
    if result and 'createProjectV2Field' in result:
        field = result['createProjectV2Field']['projectV2Field']
        print(f"✅ Created custom field: {field['name']}")
        for option in field.get('options', []):
            print(f"  • {option['name']} (ID: {option['id']})")
        return field['id']
    else:
        print(f"❌ Failed to create custom field: {field_name}")
        return None

def setup_project_fields(project_id: str, project_title: str) -> Dict[str, str]:
    """プロジェクトにカスタムフィールドを設定"""
    created_fields = {}
    
    # 既存フィールドをチェック
    existing_fields = get_existing_fields(project_id)
    print(f"\n📝 Setting up fields for: {project_title}")
    print(f"  • Found {len(existing_fields)} existing fields")
    
    # Sprint選択肢を生成
    sprint_options = generate_sprint_options()
    
    if "タスク" in project_title:
        # タスクプロジェクト: 計画pt、実績pt、Sprint
        point_options = ["1", "2", "3", "5", "8", "13"]
        
        # 計画ptフィールド
        if "計画pt" not in existing_fields:
            field_id = create_custom_field(project_id, "計画pt", point_options)
            if field_id:
                created_fields["計画pt"] = field_id
        else:
            print(f"  ℹ️ Field already exists: 計画pt")
        
        # 実績ptフィールド
        if "実績pt" not in existing_fields:
            field_id = create_custom_field(project_id, "実績pt", point_options)
            if field_id:
                created_fields["実績pt"] = field_id
        else:
            print(f"  ℹ️ Field already exists: 実績pt")
        
        # Sprintフィールド
        if "Sprint" not in existing_fields:
            field_id = create_custom_field(project_id, "Sprint", sprint_options)
            if field_id:
                created_fields["Sprint"] = field_id
        else:
            print(f"  ℹ️ Field already exists: Sprint")
        
    
    elif "テスト" in project_title:
        # テストプロジェクト: Sprintのみ
        if "Sprint" not in existing_fields:
            field_id = create_custom_field(project_id, "Sprint", sprint_options)
            if field_id:
                created_fields["Sprint"] = field_id
        else:
            print(f"  ℹ️ Field already exists: Sprint")
    
    # KPTプロジェクトには追加フィールドなし
    
    return created_fields

def create_project(title: str, repo_info: Dict) -> Optional[str]:
    """プロジェクトを作成"""
    # API Reference: https://docs.github.com/en/graphql/reference/mutations#createprojectv2
    query = """
    mutation($ownerId: ID!, $repositoryId: ID!, $title: String!) {
        createProjectV2(input: {ownerId: $ownerId, repositoryId: $repositoryId, title: $title}) {
            projectV2 {
                id
                number
                title
                url
            }
        }
    }
    """
    
    variables = {
        'ownerId': repo_info['owner_id'],
        'repositoryId': repo_info['repository_id'],
        'title': title
    }
    
    result = graphql_request(query, variables)
    if result and 'createProjectV2' in result:
        project = result['createProjectV2']['projectV2']
        print(f"✅ Created project: {project['title']} (#{project['number']})")
        print(f"🔗 Project URL: {project['url']}")
        return project['id']
    else:
        print(f"❌ Failed to create project: {title}")
        return None

def main():
    """メイン処理"""
    print("=" * 60)
    print("📊 GITHUB PROJECTS CREATION v4.0 (ENHANCED FIELDS)")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script: create_projects.py v4.0")
    print("=" * 60)
    
    # リポジトリ情報取得
    repo_info = get_repository_info()
    if not repo_info:
        print("❌ Failed to get repository information")
        return 1
    
    # 既存プロジェクトをチェック
    existing_projects = repo_info.get('existing_projects', [])
    existing_titles = {p['title']: p for p in existing_projects}
    
    print(f"\n🔍 Found {len(existing_projects)} existing projects")
    for project in existing_projects:
        print(f"  • {project['title']} (#{project['number']})")
    
    # 3つのプロジェクトを作成
    projects = [
        "イマココSNS（タスク）",
        "イマココSNS（テスト）", 
        "イマココSNS（KPT）"
    ]
    
    created_projects = {}
    skipped_projects = {}
    
    for project_title in projects:
        # 既存プロジェクトをチェック
        if project_title in existing_titles:
            existing_project = existing_titles[project_title]
            print(f"\nℹ️ Project already exists: {project_title}")
            print(f"🆔 Using existing project ID: {existing_project['id']}")
            skipped_projects[project_title] = existing_project['id']
            created_projects[project_title] = existing_project['id']
            # 既存プロジェクトにもフィールドを追加/更新
            setup_project_fields(existing_project['id'], project_title)
        else:
            project_id = create_project(project_title, repo_info)
            if project_id:
                created_projects[project_title] = project_id
                # プロジェクトにカスタムフィールドを設定
                setup_project_fields(project_id, project_title)
        
        # Rate limit対策
        time.sleep(2)
    
    # 結果をファイルに保存（他のスクリプトで使用）
    if created_projects:
        project_info = []
        for title, project_id in created_projects.items():
            project_info.append(f"{title}:{project_id}")
        
        with open('project_ids.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(project_info))
    
    # プロジェクトステータスを保存（Issue作成制御用）
    all_skipped = len(skipped_projects) == len(projects)
    with open('project_status.txt', 'w', encoding='utf-8') as f:
        if all_skipped:
            f.write('ALL_SKIPPED')
            print(f"\n📝 Status: ALL_SKIPPED (all projects already exist)")
        else:
            f.write('CREATED')
            print(f"\n📝 Status: CREATED (some projects were created)")
    
    print(f"\n✨ Project setup completed!")
    print(f"📌 Summary:")
    print(f"  • Created {len(created_projects) - len(skipped_projects)} new projects")
    print(f"  • Reused {len(skipped_projects)} existing projects")
    
    if created_projects:
        print(f"\n📊 All projects:")
        for title in created_projects:
            status = " (existing)" if title in skipped_projects else " (new)"
            print(f"  • {title}{status}")
    
    print(f"\n🔗 Access your projects:")
    print(f"  https://github.com/{GITHUB_REPOSITORY}/projects")
    
    return 0

if __name__ == '__main__':
    exit(main())