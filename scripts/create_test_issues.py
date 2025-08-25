#!/usr/bin/env python3
"""
テストIssue作成スクリプト（順序保持・並列実行最適化版）
"""

import os
import requests
import csv
import time
import math
import random
from typing import Dict, List, Optional

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')

# Rate Limit設定（GitHub公式80req/min制限準拠）
REQUEST_DELAY = 0.9      # 0.9秒間隔（67req/min、安全マージンあり）
BATCH_SIZE = 15          # 15件ずつ処理
BATCH_PAUSE = 20.0       # 20秒休憩（Rate制限リセット待ち）
MAX_RETRIES = 3          # 短いリトライ

if not TEAM_SETUP_TOKEN or not GITHUB_REPOSITORY:
    raise ValueError("TEAM_SETUP_TOKEN and GITHUB_REPOSITORY environment variables are required")

# GitHub API設定
API_BASE = 'https://api.github.com'
HEADERS = {
    'Authorization': f'token {TEAM_SETUP_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

def load_test_data() -> List[Dict]:
    """テストCSVデータを読み込み（全件）"""
    print("📊 Loading test data...")
    
    test_issues = []
    csv_path = 'data/tests_for_issues.csv'
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            test_issues = [row for row in reader if row.get('title', '').strip()]
    
    print(f"📋 Loaded: {len(test_issues)} test issues (all issues)")
    return test_issues

def create_single_issue(issue_data: Dict, index: int, total: int) -> Optional[Dict]:
    """単一のテストIssueを作成（順序保持）"""
    session = requests.Session()
    session.headers.update(HEADERS)
    
    if index > 0:
        time.sleep(REQUEST_DELAY)
    
    for attempt in range(MAX_RETRIES):
        try:
            response = session.post(
                f"{API_BASE}/repos/{GITHUB_REPOSITORY}/issues",
                json=issue_data,
                timeout=30
            )
            
            if response.status_code == 201:
                issue = response.json()
                print(f"  ✅ Test ({index + 1}/{total}): {issue_data['title'][:50]}...")
                return issue
            
            elif response.status_code == 403:
                remaining = int(response.headers.get('x-ratelimit-remaining', 0))
                retry_after = response.headers.get('retry-after')
                
                if remaining > 3000:
                    # Secondary Rate Limit（80req/min制限）の可能性
                    if attempt == 1:
                        wait_time = 90   # 初回は1.5分待機
                    else:
                        wait_time = 180  # 2回目以降は3分待機
                    print(f"  ⏳ Content creation rate limit (80/min) hit (remaining: {remaining}), waiting {wait_time}s...")
                else:
                    # Primary Rate Limit
                    if retry_after:
                        wait_time = int(retry_after) + 30
                    else:
                        wait_time = 300  # 5分待機
                    print(f"  ⏳ Primary rate limit hit (remaining: {remaining}), waiting {wait_time}s...")
                
                time.sleep(wait_time)
                continue
                
            else:
                print(f"  ❌ Test failed ({index + 1}/{total}): {response.status_code}")
                break
                
        except Exception as e:
            print(f"  ❌ Exception ({index + 1}/{total}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(30 * (attempt + 1))
                continue
    
    return None

def prepare_test_data(tests: List[Dict]) -> List[Dict]:
    """テストIssue作成用データを準備"""
    test_requests = []
    
    for index, row in enumerate(tests, 1):
        title = row.get('title', '').strip()
        body = row.get('body', '').strip()
        
        if not title:
            continue
        
        # タイトル番号の整理
        if title.startswith('テスト'):
            import re
            match = re.match(r'テスト[\d\s:.]*(.+)', title)
            if match:
                clean_title = match.group(1).strip()
            else:
                clean_title = title
            numbered_title = f"テスト{index:03d}: {clean_title}"
        else:
            numbered_title = f"テスト{index:03d}: {title}"
        
        # ラベル処理
        labels_str = row.get('labels', '').strip()
        if labels_str.startswith('"') and labels_str.endswith('"'):
            labels_str = labels_str[1:-1]
        labels = [label.strip() for label in labels_str.split(',') if label.strip()]
        
        if 'test' not in labels:
            labels.append('test')
        
        issue_data = {
            'title': numbered_title,
            'body': body,
            'labels': labels
        }
        
        test_requests.append(issue_data)
    
    return test_requests

def smart_batch_pause(batch_num: int, batch_size: int, start_time: float):
    """バッチ処理開始からの経過時間を考慮した休憩"""
    elapsed = time.time() - start_time
    requests_sent = batch_num * batch_size
    
    # 1分間の送信レートをチェック（80req/min制限対策）
    if requests_sent > 60 and elapsed < 60:
        # 1分以内に60件超過の場合、追加待機
        extra_wait = 65 - elapsed
        print(f"  ⏳ Rate limit safety wait: {extra_wait:.1f}s (sent {requests_sent} requests in {elapsed:.1f}s)")
        time.sleep(extra_wait)
    
    print(f"  ⏳ Batch pause ({BATCH_PAUSE}s) - allowing rate limits to recover...")
    time.sleep(BATCH_PAUSE)

def create_test_issues_batch(issues_data: List[Dict], batch_num: int, total_batches: int, start_time: float, total_created: int, total_issues: int) -> List[Dict]:
    """テストIssuesをバッチ作成（順序保持）"""
    created_issues = []
    
    print(f"🚀 Processing test batch {batch_num}/{total_batches} ({len(issues_data)} issues)")
    
    # 順序保持のため順次実行
    for i, issue_data in enumerate(issues_data):
        issue = create_single_issue(issue_data, i, len(issues_data))
        if issue:
            created_issues.append(issue)
        
        # 進捗表示（タイムアウト防止）
        current_total = total_created + len(created_issues)
        if (i + 1) % 10 == 0 or i == len(issues_data) - 1:  # 10件ごとに変更
            elapsed = time.time() - start_time
            rate = current_total / elapsed if elapsed > 0 else 0
            remaining_issues = total_issues - current_total
            eta = remaining_issues / rate if rate > 0 else 0
            print(f"  📊 Progress: {current_total}/{total_issues} ({current_total*100/total_issues:.1f}%) - ETA: {eta/60:.1f} min")
    
    print(f"📊 Test batch {batch_num} result: {len(created_issues)}/{len(issues_data)} issues created")
    return created_issues

def main():
    """メイン処理"""
    print("=" * 60)
    print("🧪 TEST ISSUE CREATOR (Sequential Order Preserved)")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"⚙️ Settings: delay={REQUEST_DELAY}s, batch_size={BATCH_SIZE}")
    print(f"🔄 Order preservation: Sequential execution within batches")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # プロジェクトステータスチェック
        if os.path.exists('project_status.txt'):
            with open('project_status.txt', 'r') as f:
                status = f.read().strip()
            if status == 'ALL_SKIPPED':
                print("\n✅ All projects already exist. Skipping test issue creation.")
                print("💡 Projects were reused from previous setup.")
                # 空の結果ファイルを作成（後続処理のため）
                with open('test_issues_result.txt', 'w', encoding='utf-8') as f:
                    f.write("Test Issues: SKIPPED (projects already exist)\n")
                return 0
        
        # データ読み込み
        test_data = load_test_data()
        
        if not test_data:
            print("⚠️ No test issues found")
            return 0
        
        # データ準備
        test_requests = prepare_test_data(test_data)
        total_batches = math.ceil(len(test_requests) / BATCH_SIZE)
        
        print(f"📋 Processing {len(test_requests)} test issues in {total_batches} batches")
        print(f"⚙️ GitHub API compliant: {REQUEST_DELAY}s delay ({60/REQUEST_DELAY:.0f} req/min), {BATCH_SIZE} batch size, {BATCH_PAUSE}s pause")
        print(f"💡 Target: Complete all {len(test_requests)} issues within 10 minutes")
        
        # 完了予想時刻（GitHub公式制限準拠）
        base_time = len(test_requests) * REQUEST_DELAY
        pause_time = (total_batches - 1) * BATCH_PAUSE
        buffer_time = 60   # Rate limit対応の予備時間（短縮）
        estimated_time = (base_time + pause_time + buffer_time) / 60
        print(f"⏱️ Estimated completion: {estimated_time:.1f} minutes (GitHub 80 req/min compliant)")
        print(f"🎯 Target: Under 10 minutes for {len(test_requests)} issues")
        
        # バッチ処理
        all_created = []
        
        for batch_num in range(total_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(test_requests))
            batch_requests = test_requests[start_idx:end_idx]
            
            batch_created = create_test_issues_batch(
                batch_requests, 
                batch_num + 1, 
                total_batches, 
                start_time,
                len(all_created),
                len(test_requests)
            )
            all_created.extend(batch_created)
            
            # バッチ間休憩（Rate limit回復のため）
            if batch_num < total_batches - 1:
                smart_batch_pause(batch_num + 1, BATCH_SIZE, start_time)
        
        # 結果保存
        with open('test_issues_result.txt', 'w', encoding='utf-8') as f:
            f.write(f"Test Issues Created: {len(all_created)}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Execution time: {time.time() - start_time:.1f}s\n")
            
            for issue in all_created:
                f.write(f"{issue['number']}: {issue['title']}\n")
        
        print(f"\n✅ Test issues completed: {len(all_created)}/{len(test_requests)}")
        print(f"⏱️ Execution time: {(time.time() - start_time)/60:.1f} minutes")
        
        return 0
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())