#!/usr/bin/env python3
"""
CSV読み込み処理の共通モジュール
"""

import os
import csv
from typing import Dict, List, Tuple


class CSVLoader:
    """CSV読み込みクラス"""
    
    @staticmethod
    def load_issue_data(file_path: str, issue_type: str) -> List[Dict]:
        """特定のIssue種別のCSVデータを読み込み"""
        if not os.path.exists(file_path):
            print(f"⚠️ CSV file not found: {file_path}")
            return []
        
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                issues = [row for row in reader if row.get('title', '').strip()]
        except Exception as e:
            print(f"❌ Error loading {issue_type} CSV: {str(e)}")
            return []
        
        print(f"📋 Loaded: {len(issues)} {issue_type} issues from {file_path}")
        return issues
    
    @staticmethod
    def load_all_csv_data(data_dir: str = 'data') -> Tuple[List[Dict], List[Dict]]:
        """全てのCSVデータを読み込み"""
        print("📊 Loading all CSV data...")
        
        # プロジェクトタイプを環境変数から取得
        project_type = os.environ.get('PROJECT_TYPE', 'imakoko')
        print(f"📦 Project Type: {project_type}")
        
        # プロジェクトタイプに応じてCSVファイルを選択
        if project_type == 'real_estate':
            task_csv = 'tasks_for_real_estate.csv'
            # 不動産検索サイトではKPTを生成しない
            kpt_issues = []
            print("ℹ️ KPT issues are disabled for real_estate project type")
        else:  # imakoko or default
            task_csv = 'tasks_for_issues.csv'
            # CSV ファイルマッピング
            kpt_csv = os.path.join(data_dir, 'kpt_for_issues.csv')
            kpt_issues = CSVLoader.load_issue_data(kpt_csv, 'kpt')
        
        # タスクCSVを読み込み
        task_csv_path = os.path.join(data_dir, task_csv)
        task_issues = CSVLoader.load_issue_data(task_csv_path, 'task')
        
        total = len(task_issues) + len(kpt_issues)
        print(f"📊 Total: {total} issues to create")
        
        return task_issues, kpt_issues
    
    @staticmethod
    def validate_csv_data(issues: List[Dict], issue_type: str) -> List[Dict]:
        """CSVデータの妥当性をチェック"""
        valid_issues = []
        
        for index, issue in enumerate(issues):
            title = issue.get('title', '').strip()
            if not title:
                print(f"  ⚠️ Skipping {issue_type} issue {index + 1}: No title")
                continue
            
            # 必要なフィールドをチェック
            if 'body' not in issue:
                issue['body'] = ''
            if 'labels' not in issue:
                issue['labels'] = ''
            
            valid_issues.append(issue)
        
        if len(valid_issues) != len(issues):
            print(f"  📝 {issue_type}: {len(valid_issues)}/{len(issues)} issues are valid")
        
        return valid_issues