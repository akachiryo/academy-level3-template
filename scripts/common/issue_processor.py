#!/usr/bin/env python3
"""
Issue処理の共通モジュール
"""

import re
from typing import Dict, List, Tuple, Any

from .config import IssueTypeConfig


class IssueProcessor:
    """Issue処理クラス"""
    
    def __init__(self, issue_type_config: IssueTypeConfig):
        self.issue_type_config = issue_type_config
    
    def prepare_issue_data(self, issues: List[Dict], issue_type: str) -> List[Tuple[Dict, str]]:
        """Issue作成用のデータを準備（番号付きタイトル）"""
        issue_requests = []
        config = self.issue_type_config.get_issue_type(issue_type)
        
        if not config:
            print(f"⚠️ Unknown issue type: {issue_type}")
            return []
        
        title_prefix = config.get('title_prefix', '')
        default_labels = config.get('labels', [])
        numbered_title = config.get('numbered_title', True)
        
        for index, row in enumerate(issues, 1):
            title = row.get('title', '').strip()
            body = row.get('body', '').strip()
            
            if not title:
                continue
            
            # タイトルに番号を追加（設定に応じて）
            if numbered_title and title_prefix:
                # タイトル接頭辞で始まる場合は、番号を置き換え
                if title.startswith(title_prefix):
                    match = re.match(rf'{title_prefix}[\d\s:.]*(.+)', title)
                    if match:
                        clean_title = match.group(1).strip()
                    else:
                        clean_title = title
                    numbered_title_text = f"{title_prefix}{index:03d}: {clean_title}"
                else:
                    numbered_title_text = f"{title_prefix}{index:03d}: {title}"
            else:
                # 番号付けしない場合（KPT等）はそのまま使用
                numbered_title_text = title
            
            # CSVからラベルを取得（"task,Required"のような形式に対応）
            labels_str = row.get('labels', '').strip()
            if labels_str.startswith('"') and labels_str.endswith('"'):
                labels_str = labels_str[1:-1]  # クォートを除去
            existing_labels = [label.strip() for label in labels_str.split(',') if label.strip()]
            
            # デフォルトラベルがない場合は追加
            all_labels = list(set(existing_labels + default_labels))
            
            issue_data = {
                'title': numbered_title_text,
                'body': body,
                'labels': all_labels
            }
            
            issue_requests.append((issue_data, issue_type))
        
        return issue_requests
    
    def classify_created_issues(self, created_issues: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """作成されたIssueをタイプ別に分類"""
        task_created = []
        test_created = []
        kpt_created = []
        
        for issue in created_issues:
            issue_labels = [label['name'] for label in issue.get('labels', [])]
            if 'task' in issue_labels:
                task_created.append(issue)
            elif 'kpt' in issue_labels:
                kpt_created.append(issue)
            else:  # デフォルトはtest
                test_created.append(issue)
        
        return task_created, test_created, kpt_created
    
    def prepare_all_issue_data(self, task_data: List[Dict], 
                              test_data: List[Dict], 
                              kpt_data: List[Dict]) -> List[Tuple[Dict, str]]:
        """全Issue種別のデータを準備"""
        all_requests = []
        
        # 各Issue種別のデータを準備
        task_requests = self.prepare_issue_data(task_data, 'task')
        test_requests = self.prepare_issue_data(test_data, 'test')
        kpt_requests = self.prepare_issue_data(kpt_data, 'kpt')
        
        all_requests = task_requests + test_requests + kpt_requests
        print(f"📋 Prepared requests: {len(all_requests)} issues total")
        print(f"  • Task: {len(task_requests)} issues")
        print(f"  • Test: {len(test_requests)} issues")
        print(f"  • KPT: {len(kpt_requests)} issues")
        
        return all_requests