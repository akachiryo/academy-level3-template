#!/usr/bin/env python3
"""
GitHub API操作の共通モジュール
"""

import os
import requests
import time
import random
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any


class GitHubAPI:
    """GitHub API操作クラス"""
    
    def __init__(self, token: str = None, repository: str = None):
        self.token = token or os.environ.get('TEAM_SETUP_TOKEN')
        self.repository = repository or os.environ.get('GITHUB_REPOSITORY')
        
        if not self.token or not self.repository:
            raise ValueError("TEAM_SETUP_TOKEN and GITHUB_REPOSITORY are required")
        
        self.owner, self.repo_name = self.repository.split('/')
        
        # API設定
        self.api_base = 'https://api.github.com'
        self.graphql_url = 'https://api.github.com/graphql'
        
        self.rest_headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        self.graphql_headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # スレッドローカルセッション
        self.thread_local = threading.local()
    
    def get_session(self) -> requests.Session:
        """スレッドローカルセッションを取得"""
        if not hasattr(self.thread_local, "session"):
            self.thread_local.session = requests.Session()
            self.thread_local.session.headers.update(self.rest_headers)
        return self.thread_local.session
    
    def check_rate_limit_headers(self, response: requests.Response) -> Dict[str, Optional[int]]:
        """レート制限ヘッダーをチェックし、情報を表示"""
        headers = response.headers
        remaining = headers.get('x-ratelimit-remaining')
        limit = headers.get('x-ratelimit-limit') 
        reset_timestamp = headers.get('x-ratelimit-reset')
        
        if remaining and limit:
            remaining_pct = (int(remaining) / int(limit)) * 100
            if remaining_pct < 20:  # 20%以下の場合警告
                if reset_timestamp:
                    reset_time = datetime.fromtimestamp(int(reset_timestamp))
                    print(f"  ⚠️ Rate limit warning: {remaining}/{limit} remaining ({remaining_pct:.1f}%), resets at {reset_time.strftime('%H:%M:%S')}")
                else:
                    print(f"  ⚠️ Rate limit warning: {remaining}/{limit} remaining ({remaining_pct:.1f}%)")
            elif int(remaining) % 100 == 0:  # 100の倍数で情報表示
                print(f"  📊 Rate limit status: {remaining}/{limit} remaining ({remaining_pct:.1f}%)")
        
        return {
            'remaining': int(remaining) if remaining else None,
            'limit': int(limit) if limit else None,
            'reset': int(reset_timestamp) if reset_timestamp else None
        }
    
    def check_initial_rate_limit(self) -> Optional[int]:
        """初期レート制限状態をチェック"""
        try:
            response = requests.get(f"{self.api_base}/rate_limit", headers=self.rest_headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                core = data.get('resources', {}).get('core', {})
                remaining = core.get('remaining', 0)
                limit = core.get('limit', 0)
                reset_timestamp = core.get('reset', 0)
                
                if reset_timestamp:
                    reset_time = datetime.fromtimestamp(reset_timestamp)
                    print(f"📊 Initial rate limit: {remaining}/{limit} requests remaining")
                    print(f"🔄 Rate limit resets at: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    if remaining < 100:
                        print(f"⚠️ Warning: Low rate limit remaining ({remaining}). Consider waiting until reset.")
                return remaining
        except Exception as e:
            print(f"⚠️ Could not check rate limit: {str(e)}")
        return None
    
    def create_issue(self, issue_data: Dict[str, Any], 
                    index: int, total: int, issue_type: str,
                    max_retries: int = 15, 
                    request_delay: float = 1.0,
                    retry_delay: float = 120.0,
                    secondary_limit_delay: float = 300.0) -> Optional[Dict[str, Any]]:
        """単一のIssueを作成（リトライ機能付き）"""
        session = self.get_session()
        
        # レート制限回避のためのディレイ
        if index > 0:
            time.sleep(request_delay)
        
        for attempt in range(max_retries):
            try:
                response = session.post(
                    f"{self.api_base}/repos/{self.repository}/issues",
                    json=issue_data,
                    timeout=30
                )
                
                if response.status_code == 201:
                    issue = response.json()
                    # レート制限ヘッダーをチェック
                    self.check_rate_limit_headers(response)
                    
                    if attempt > 0:
                        print(f"  ✅ {issue_type} ({index + 1}/{total}) [retry {attempt}]: {issue_data['title'][:50]}...")
                    else:
                        print(f"  ✅ {issue_type} ({index + 1}/{total}): {issue_data['title'][:50]}...")
                    return issue
                
                elif response.status_code == 403:
                    # GitHub推奨: セカンダリレート制限の可能性
                    retry_after = response.headers.get('retry-after')
                    if retry_after:
                        wait_time = int(retry_after)
                        print(f"  ⏳ Rate limit (retry-after: {wait_time}s) ({index + 1}/{total}) [attempt {attempt + 1}]")
                    else:
                        # 指数バックオフ with jitter
                        base_delay = retry_delay if attempt == 0 else secondary_limit_delay
                        jitter = random.uniform(0.8, 1.2)
                        wait_time = int(base_delay * (2 ** (attempt // 2)) * jitter)
                        print(f"  ⏳ Rate limit hit ({index + 1}/{total}) [attempt {attempt + 1}], waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                    
                elif response.status_code >= 500:
                    print(f"  🔄 Server error ({response.status_code}) ({index + 1}/{total}) [attempt {attempt + 1}]...")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                
                else:
                    print(f"  ❌ {issue_type} failed ({index + 1}/{total}): {response.status_code} - {response.text[:100]}")
                    break
                    
            except Exception as e:
                print(f"  ❌ {issue_type} exception ({index + 1}/{total}) [attempt {attempt + 1}]: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
        
        return None
    
    def add_issue_to_project(self, project_id: str, issue: Dict[str, Any]) -> Optional[str]:
        """IssueをProjectに追加し、アイテムIDを返す"""
        query = """
        mutation($projectId: ID!, $contentId: ID!) {
            addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
                item { id }
            }
        }
        """
        
        variables = {
            'projectId': project_id,
            'contentId': issue['node_id']
        }
        
        payload = {'query': query, 'variables': variables}
        
        try:
            response = requests.post(
                self.graphql_url, 
                json=payload, 
                headers=self.graphql_headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' not in data and 'data' in data:
                    return data['data']['addProjectV2ItemById']['item']['id']
            return None
        except:
            return None
    
    def graphql_request(self, query: str, variables: Dict = None, timeout: int = 30) -> Dict:
        """GraphQL APIリクエスト実行"""
        payload = {'query': query}
        if variables:
            payload['variables'] = variables
        
        try:
            response = requests.post(
                self.graphql_url, 
                json=payload, 
                headers=self.graphql_headers,
                timeout=timeout
            )
            
            if response.status_code != 200:
                print(f"❌ GraphQL Error: {response.status_code} - {response.text}")
                return {}
            
            data = response.json()
            if 'errors' in data:
                print(f"❌ GraphQL Errors: {data['errors']}")
                return {}
            
            return data.get('data', {})
            
        except Exception as e:
            print(f"❌ GraphQL Request Exception: {str(e)}")
            return {}
    
    # Repository and Project Management Methods
    
    def get_repository_info(self) -> Optional[Dict]:
        """リポジトリ情報と既存プロジェクトを取得"""
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
            'owner': self.owner,
            'name': self.repo_name
        }
        
        result = self.graphql_request(query, variables)
        if result and 'repository' in result:
            return {
                'repository_id': result['repository']['id'],
                'owner_id': result['repository']['owner']['id'],
                'existing_projects': result['repository']['projectsV2']['nodes']
            }
        return None
    
    def create_project_v2(self, title: str, description: str = "") -> Optional[str]:
        """ProjectsV2を作成"""
        repo_info = self.get_repository_info()
        if not repo_info:
            return None
        
        query = """
        mutation($ownerId: ID!, $title: String!, $repositoryId: ID!) {
            createProjectV2(input: {
                ownerId: $ownerId,
                title: $title,
                repositoryId: $repositoryId
            }) {
                projectV2 {
                    id
                    title
                    url
                }
            }
        }
        """
        
        variables = {
            'ownerId': repo_info['owner_id'],
            'title': title,
            'repositoryId': repo_info['repository_id']
        }
        
        result = self.graphql_request(query, variables)
        if result and 'createProjectV2' in result:
            return result['createProjectV2']['projectV2']['id']
        return None
    
    # Discussion Management Methods
    
    def get_discussion_categories(self) -> List[Dict]:
        """Discussionカテゴリーを取得"""
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                discussionCategories(first: 20) {
                    nodes {
                        id
                        name
                        description
                        emoji
                        emojiHTML
                    }
                }
            }
        }
        """
        
        variables = {
            'owner': self.owner,
            'name': self.repo_name
        }
        
        result = self.graphql_request(query, variables)
        if result and 'repository' in result:
            return result['repository']['discussionCategories']['nodes']
        return []
    
    # Note: createDiscussionCategory mutation does not exist in GitHub GraphQL API
    # Discussion categories must be created manually through the GitHub web interface
    
    def create_discussion(self, title: str, body: str, category_id: str) -> Optional[str]:
        """Discussionを作成"""
        repo_info = self.get_repository_info()
        if not repo_info:
            return None
        
        query = """
        mutation($repositoryId: ID!, $title: String!, $body: String!, $categoryId: ID!) {
            createDiscussion(input: {
                repositoryId: $repositoryId,
                title: $title,
                body: $body,
                categoryId: $categoryId
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
            'repositoryId': repo_info['repository_id'],
            'title': title,
            'body': body,
            'categoryId': category_id
        }
        
        result = self.graphql_request(query, variables)
        if result and 'createDiscussion' in result:
            return result['createDiscussion']['discussion']['id']
        return None
    
    # Note: deleteDiscussionCategory mutation does not exist in GitHub GraphQL API
    # Discussion categories must be managed manually through the GitHub web interface