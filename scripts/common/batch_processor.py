#!/usr/bin/env python3
"""
バッチ処理の共通モジュール
"""

import time
import math
from typing import Dict, List, Tuple, Optional, Any

from .github_api import GitHubAPI


class BatchProcessor:
    """バッチ処理クラス"""
    
    def __init__(self, github_api: GitHubAPI, 
                 batch_size: int = 10,
                 batch_pause: float = 15.0,
                 request_delay: float = 1.0):
        self.github_api = github_api
        self.batch_size = batch_size
        self.batch_pause = batch_pause
        self.request_delay = request_delay
    
    def calculate_batches(self, total_count: int) -> int:
        """必要なバッチ数を計算"""
        return math.ceil(total_count / self.batch_size)
    
    def estimate_completion_time(self, total_issues: int) -> float:
        """完了予想時刻を計算"""
        batches = self.calculate_batches(total_issues)
        
        time_per_issue = self.request_delay
        time_for_issues = total_issues * time_per_issue
        time_for_batch_pauses = (batches - 1) * self.batch_pause
        
        total_seconds = time_for_issues + time_for_batch_pauses
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        
        print(f"⏱️ Estimated completion time: {minutes}m {seconds}s ({batches} batches)")
        return total_seconds
    
    def create_issues_batch(self, issues_data: List[Tuple], 
                           batch_num: int, total_batches: int,
                           start_time: float = None) -> Tuple[List[Dict], List[Tuple]]:
        """1つのバッチでIssueを作成（失敗したものを返す）"""
        created_issues = []
        failed_issues = []
        
        if not issues_data:
            return created_issues, failed_issues
        
        print(f"🚀 Processing batch {batch_num}/{total_batches} ({len(issues_data)} issues)")
        
        # シーケンシャル実行（順番保持のため）
        for i, (issue_data, issue_type) in enumerate(issues_data):
            try:
                issue = self.github_api.create_issue(
                    issue_data, i, len(issues_data), issue_type,
                    request_delay=self.request_delay
                )
                if issue:
                    created_issues.append(issue)
                else:
                    failed_issues.append((issue_data, issue_type))
            except Exception as e:
                print(f"  ❌ Exception: {str(e)}")
                failed_issues.append((issue_data, issue_type))
        
        print(f"📊 Batch {batch_num} result: {len(created_issues)}/{len(issues_data)} issues created, {len(failed_issues)} failed")
        return created_issues, failed_issues
    
    def process_all_batches(self, all_requests: List[Tuple],
                           start_time: float = None) -> Tuple[List[Dict], List[Tuple]]:
        """全バッチを処理"""
        if start_time is None:
            start_time = time.time()
        
        total_batches = self.calculate_batches(len(all_requests))
        all_created_issues = []
        all_failed_issues = []
        
        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(all_requests))
            batch_requests = all_requests[start_idx:end_idx]
            
            print(f"\n🔄 Batch {batch_num + 1}/{total_batches}: Processing issues {start_idx + 1}-{end_idx}")
            
            batch_created, batch_failed = self.create_issues_batch(
                batch_requests, batch_num + 1, total_batches, start_time
            )
            all_created_issues.extend(batch_created)
            all_failed_issues.extend(batch_failed)
            
            # バッチ間の休憩（GitHub推奨パターン）
            if batch_num < total_batches - 1:
                print(f"  ⏳ Batch pause ({self.batch_pause}s)...")
                time.sleep(self.batch_pause)
        
        return all_created_issues, all_failed_issues
    
    def retry_failed_issues(self, failed_issues: List[Tuple], 
                           max_retry_rounds: int = 2) -> List[Dict]:
        """失敗したissueをリトライする"""
        if not failed_issues:
            return []
        
        print(f"\n🔄 Retrying {len(failed_issues)} failed issues...")
        
        retry_created = []
        remaining_failed = failed_issues.copy()
        
        for round_num in range(max_retry_rounds):
            if not remaining_failed:
                break
                
            print(f"  🔁 Retry round {round_num + 1}/{max_retry_rounds}: {len(remaining_failed)} issues")
            
            # リトライ前に長めの休憩
            time.sleep(3.0)
            
            current_round_created, current_round_failed = self.create_issues_batch(
                remaining_failed, round_num + 1, max_retry_rounds
            )
            
            retry_created.extend(current_round_created)
            remaining_failed = current_round_failed
            
            # 次のラウンドまでの休憩
            if remaining_failed and round_num < max_retry_rounds - 1:
                print(f"    ⏳ Waiting before next retry round...")
                time.sleep(5.0)
        
        if remaining_failed:
            print(f"  ⚠️ {len(remaining_failed)} issues could not be created after all retries")
            print("  Failed issues:")
            for issue_data, issue_type in remaining_failed[:5]:  # 最初の5個だけ表示
                print(f"    - {issue_type}: {issue_data['title'][:50]}...")
            if len(remaining_failed) > 5:
                print(f"    ... and {len(remaining_failed) - 5} more")
        
        print(f"  ✅ Retry success: {len(retry_created)} issues created")
        return retry_created
    
    def link_issues_to_projects(self, task_issues: List[Dict], 
                               kpt_issues: List[Dict], 
                               project_ids: Dict[str, str]) -> Tuple[int, int]:
        """IssueをProjectsにリンク"""
        print("\n🔗 Linking issues to projects...")
        
        def link_batch(issues: List[Dict], project_id: str, project_name: str, issue_type: str):
            if not issues or not project_id:
                return 0
            
            print(f"  📌 Linking {len(issues)} {issue_type} issues to {project_name}")
            success_count = 0
            
            for i, issue in enumerate(issues):
                try:
                    item_id = self.github_api.add_issue_to_project(project_id, issue)
                    if item_id:
                        success_count += 1
                    
                    if (i + 1) % 20 == 0:
                        print(f"    ✅ Linked {i + 1}/{len(issues)} to {project_name}")
                except Exception as e:
                    print(f"    ❌ Link exception: {str(e)}")
                time.sleep(0.1)  # プロジェクトリンクも少し間隔を空ける
            
            print(f"  📊 {project_name}: {success_count}/{len(issues)} issues linked")
            return success_count
        
        # プロジェクトにリンク
        task_linked = link_batch(
            task_issues, 
            project_ids.get('イマココSNS（タスク）'), 
            'イマココSNS（タスク）',
            'task'
        )
        
        kpt_linked = link_batch(
            kpt_issues,
            project_ids.get('イマココSNS（KPT）'),
            'イマココSNS（KPT）',
            'kpt'
        )
        
        return task_linked, kpt_linked