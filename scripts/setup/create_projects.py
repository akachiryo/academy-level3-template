#!/usr/bin/env python3
"""
GitHub Projects作成スクリプト
3つの独立したプロジェクトを作成する
共通ライブラリを使用してリファクタリング済み
"""

import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 共通ライブラリをインポート
sys.path.append('scripts')
from common.github_api import GitHubAPI


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

def get_existing_fields(github_api: GitHubAPI, project_id: str) -> Dict[str, str]:
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
    result = github_api.graphql_request(query, variables)
    
    fields = {}
    if result and 'node' in result:
        field_nodes = result['node'].get('fields', {}).get('nodes', [])
        for field in field_nodes:
            if field and 'name' in field:
                fields[field['name']] = field['id']
    
    return fields

def create_custom_field(github_api: GitHubAPI, project_id: str, field_name: str, options: List[str]) -> Optional[str]:
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
    
    result = github_api.graphql_request(query, variables)
    if result and 'createProjectV2Field' in result:
        field = result['createProjectV2Field']['projectV2Field']
        print(f"✅ Created custom field: {field['name']}")
        for option in field.get('options', []):
            print(f"  • {option['name']} (ID: {option['id']})")
        return field['id']
    else:
        print(f"❌ Failed to create custom field: {field_name}")
        return None

def setup_project_fields(github_api: GitHubAPI, project_id: str, project_title: str) -> Dict[str, str]:
    """プロジェクトにカスタムフィールドを設定"""
    created_fields = {}
    
    # 既存フィールドをチェック
    existing_fields = get_existing_fields(github_api, project_id)
    print(f"\n📝 Setting up fields for: {project_title}")
    print(f"  • Found {len(existing_fields)} existing fields")
    
    # Sprint選択肢を生成
    sprint_options = generate_sprint_options()
    
    if "タスク" in project_title:
        # タスクプロジェクト: 計画pt、実績pt、Sprint
        point_options = ["1", "2", "3", "5", "8", "13"]
        
        # 計画ptフィールド
        if "計画pt" not in existing_fields:
            field_id = create_custom_field(github_api, project_id, "計画pt", point_options)
            if field_id:
                created_fields["計画pt"] = field_id
        else:
            print(f"  ℹ️ Field already exists: 計画pt")
        
        # 実績ptフィールド
        if "実績pt" not in existing_fields:
            field_id = create_custom_field(github_api, project_id, "実績pt", point_options)
            if field_id:
                created_fields["実績pt"] = field_id
        else:
            print(f"  ℹ️ Field already exists: 実績pt")
        
        # Sprintフィールド
        if "Sprint" not in existing_fields:
            field_id = create_custom_field(github_api, project_id, "Sprint", sprint_options)
            if field_id:
                created_fields["Sprint"] = field_id
        else:
            print(f"  ℹ️ Field already exists: Sprint")
    
    # KPTプロジェクトには追加フィールドなし
    
    return created_fields

def create_project(github_api: GitHubAPI, title: str) -> Optional[str]:
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
    
    # リポジトリ情報を取得
    repo_info = github_api.get_repository_info()
    if not repo_info:
        return None
        
    variables = {
        'ownerId': repo_info['owner_id'],
        'repositoryId': repo_info['repository_id'],
        'title': title
    }
    
    result = github_api.graphql_request(query, variables)
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
    print("📊 GITHUB PROJECTS CREATION")
    print("=" * 60)
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script: create_projects.py")
    print("=" * 60)
    
    try:
        # GitHub APIクラスの初期化
        github_api = GitHubAPI()
        print(f"📦 Repository: {github_api.repository}")
        
        # リポジトリ情報取得
        repo_info = github_api.get_repository_info()
        if not repo_info:
            print("❌ Failed to get repository information")
            return 1
        
        # 既存プロジェクトをチェック
        existing_projects = repo_info.get('existing_projects', [])
        existing_titles = {p['title']: p for p in existing_projects}
        
        print(f"\n🔍 Found {len(existing_projects)} existing projects")
        for project in existing_projects:
            print(f"  • {project['title']} (#{project['number']})")
        
        # プロジェクトタイプを環境変数から取得
        project_type = os.environ.get('PROJECT_TYPE', 'imakoko')
        print(f"\n📦 Project Type: {project_type}")
        
        # プロジェクトタイプに応じてプロジェクト名を設定
        if project_type == 'real_estate':
            projects = [
                "不動産検索サイト（タスク）",
                "不動産検索サイト（KPT）"
            ]
        else:  # imakoko or default
            projects = [
                "イマココSNS（タスク）",
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
                setup_project_fields(github_api, existing_project['id'], project_title)
            else:
                project_id = create_project(github_api, project_title)
                if project_id:
                    created_projects[project_title] = project_id
                    # プロジェクトにカスタムフィールドを設定
                    setup_project_fields(github_api, project_id, project_title)
            
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
        print(f"  https://github.com/{github_api.repository}/projects")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")
        return 1

if __name__ == '__main__':
    exit(main())