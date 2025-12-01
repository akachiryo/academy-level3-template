#!/usr/bin/env python3
"""
設定管理の共通モジュール
"""

import os
import json
from typing import Dict, Any, Optional


class Config:
    """設定管理クラス"""
    
    # デフォルト設定
    DEFAULT_SETTINGS = {
        'batch_size': 10,
        'batch_pause': 15.0,
        'request_delay': 1.0,
        'retry_delay': 120.0,
        'max_retries': 15,
        'secondary_limit_delay': 300.0
    }
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file
        self.settings = self.DEFAULT_SETTINGS.copy()
        
        # 環境変数から基本設定を取得
        self.token = os.environ.get('TEAM_SETUP_TOKEN')
        self.repository = os.environ.get('GITHUB_REPOSITORY')
        
        if not self.token or not self.repository:
            raise ValueError("TEAM_SETUP_TOKEN and GITHUB_REPOSITORY environment variables are required")
        
        # 設定ファイルが指定されている場合は読み込み
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_config(self, config_file: str):
        """設定ファイルを読み込み"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_settings = json.load(f)
                self.settings.update(file_settings)
                print(f"📁 Loaded configuration from {config_file}")
        except Exception as e:
            print(f"⚠️ Failed to load config file {config_file}: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        return self.settings.get(key, default)
    
    def get_batch_size(self) -> int:
        """バッチサイズを取得"""
        return self.get('batch_size', 10)
    
    def get_batch_pause(self) -> float:
        """バッチ間の休憩時間を取得"""
        return self.get('batch_pause', 15.0)
    
    def get_request_delay(self) -> float:
        """リクエスト間の遅延時間を取得"""
        return self.get('request_delay', 1.0)
    
    def get_retry_settings(self) -> Dict[str, float]:
        """リトライ設定を取得"""
        return {
            'retry_delay': self.get('retry_delay', 120.0),
            'max_retries': self.get('max_retries', 15),
            'secondary_limit_delay': self.get('secondary_limit_delay', 300.0)
        }
    
    def load_project_ids(self, file_path: str = 'project_ids.txt') -> Dict[str, str]:
        """保存されたプロジェクトIDを読み込み"""
        project_ids = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        title, project_id = line.strip().split(':', 1)
                        project_ids[title] = project_id
            print(f"📂 Loaded {len(project_ids)} project IDs")
        except FileNotFoundError:
            print(f"⚠️ {file_path} not found. Issues will be created but not linked to projects.")
        
        return project_ids
    
    def display_settings(self):
        """現在の設定を表示"""
        print("⚙️ Current Configuration:")
        print(f"  • Repository: {self.repository}")
        print(f"  • Batch Size: {self.get_batch_size()}")
        print(f"  • Batch Pause: {self.get_batch_pause()}s")
        print(f"  • Request Delay: {self.get_request_delay()}s")
        print(f"  • Max Retries: {self.get('max_retries')}")
        print(f"  • Retry Delay: {self.get('retry_delay')}s")


class IssueTypeConfig:
    """Issue種別設定クラス"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file
        self.issue_types = self._load_default_issue_types()
        
        if config_file and os.path.exists(config_file):
            self.load_issue_types(config_file)
            
        # 環境変数に基づいてプロジェクト名を強制的に適用
        self._apply_project_names()
    
    def _apply_project_names(self):
        """環境変数に基づいてプロジェクト名を適用"""
        project_type = os.environ.get('PROJECT_TYPE', 'imakoko')
        
        if project_type == 'real_estate':
            task_project = '不動産検索サイト（タスク）'
            kpt_project = '不動産検索サイト（KPT）'
            task_csv = 'data/tasks_for_real_estate.csv'
        else:
            task_project = 'イマココSNS（タスク）'
            kpt_project = 'イマココSNS（KPT）'
            task_csv = 'data/tasks_for_issues.csv'
            
        if 'task' in self.issue_types:
            self.issue_types['task']['project_name'] = task_project
            self.issue_types['task']['csv_file'] = task_csv
        if 'kpt' in self.issue_types:
            self.issue_types['kpt']['project_name'] = kpt_project

    def _load_default_issue_types(self) -> Dict[str, Dict[str, Any]]:
        """デフォルトのIssue種別設定"""
        project_type = os.environ.get('PROJECT_TYPE', 'imakoko')
        
        if project_type == 'real_estate':
            task_project = '不動産検索サイト（タスク）'
            kpt_project = '不動産検索サイト（KPT）'
        else:
            task_project = 'イマココSNS（タスク）'
            kpt_project = 'イマココSNS（KPT）'
            
        return {
            'task': {
                'csv_file': 'data/tasks_for_issues.csv',
                'title_prefix': 'タスク',
                'labels': ['task'],
                'project_name': task_project
            },
            'kpt': {
                'csv_file': 'data/kpt_for_issues.csv',
                'title_prefix': '',  # KPTは番号付けしない
                'labels': ['kpt'],
                'project_name': kpt_project
            }
        }
    
    def load_issue_types(self, config_file: str):
        """Issue種別設定ファイルを読み込み"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self.issue_types.update(file_config)
                print(f"📁 Loaded issue type configuration from {config_file}")
        except Exception as e:
            print(f"⚠️ Failed to load issue types config {config_file}: {str(e)}")
    
    def get_issue_type(self, issue_type: str) -> Optional[Dict[str, Any]]:
        """Issue種別設定を取得"""
        return self.issue_types.get(issue_type)
    
    def get_all_issue_types(self) -> Dict[str, Dict[str, Any]]:
        """全Issue種別設定を取得"""
        return self.issue_types
    
    def get_csv_file(self, issue_type: str) -> str:
        """CSVファイルパスを取得"""
        config = self.get_issue_type(issue_type)
        return config['csv_file'] if config else ''
    
    def get_title_prefix(self, issue_type: str) -> str:
        """タイトル接頭辞を取得"""
        config = self.get_issue_type(issue_type)
        return config.get('title_prefix', '') if config else ''
    
    def get_labels(self, issue_type: str) -> list:
        """ラベルリストを取得"""
        config = self.get_issue_type(issue_type)
        return config.get('labels', []) if config else []
    
    def get_project_name(self, issue_type: str) -> str:
        """プロジェクト名を取得"""
        config = self.get_issue_type(issue_type)
        return config.get('project_name', '') if config else ''