#!/usr/bin/env python3
"""
GitHub Issues 全自動作成スクリプト v5.0 (REFACTORED)
すべてのIssueを1つのスクリプトで動的に処理
共通ライブラリを使用してリファクタリング済み
"""

import time
import sys
from typing import Dict, List

# 共通ライブラリをインポート
sys.path.append('scripts')
from common.github_api import GitHubAPI
from common.csv_loader import CSVLoader
from common.batch_processor import BatchProcessor
from common.config import Config, IssueTypeConfig
from common.issue_processor import IssueProcessor











def main():
    """メイン処理"""
    print("=" * 70)
    print("🧠 SMART ALL-IN-ONE ISSUE CREATOR v5.0 (Refactored)")
    print("=" * 70)
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script: create_all_issues_smart.py v5.0 (Refactored)")
    print("=" * 70)
    
    start_time = time.time()
    
    try:
        # 設定の初期化
        config = Config()
        issue_type_config = IssueTypeConfig('scripts/config/issue_types.json')
        
        # 設定を表示
        config.display_settings()
        
        # GitHub APIクラスの初期化
        github_api = GitHubAPI(config.token, config.repository)
        
        # 初期レート制限チェック
        github_api.check_initial_rate_limit()
        
        # CSV読み込み
        csv_loader = CSVLoader()
        task_data, kpt_data = csv_loader.load_all_csv_data()
        total_issues = len(task_data) + len(kpt_data)
        
        if total_issues == 0:
            print("⚠️ No issues found in CSV files")
            return 1
        
        # Issue処理クラスの初期化
        issue_processor = IssueProcessor(issue_type_config)
        
        # バッチ処理クラスの初期化
        batch_processor = BatchProcessor(
            github_api,
            config.get_batch_size(),
            config.get_batch_pause(),
            config.get_request_delay()
        )
        
        print(f"\n📊 Processing plan:")
        print(f"  • Total issues: {total_issues}")
        print(f"  • Batch size: {config.get_batch_size()}")
        print(f"  • Total batches: {batch_processor.calculate_batches(total_issues)}")
        
        # 完了予想時刻を表示
        batch_processor.estimate_completion_time(total_issues)
        
        # プロジェクトIDを読み込み
        project_ids = config.load_project_ids()
        
        # Issue作成用データ準備
        all_requests = issue_processor.prepare_all_issue_data(task_data, kpt_data)
        
        # バッチ処理実行
        all_created_issues, all_failed_issues = batch_processor.process_all_batches(all_requests, start_time)
        
        # 失敗したもののリトライ
        retry_created = []
        if all_failed_issues:
            retry_created = batch_processor.retry_failed_issues(all_failed_issues)
            all_created_issues.extend(retry_created)
        
        # 作成されたIssueを種別ごとに分類
        task_created, kpt_created = issue_processor.classify_created_issues(all_created_issues)
        
        # プロジェクトリンク
        task_linked, kpt_linked = batch_processor.link_issues_to_projects(
            task_created, kpt_created, project_ids
        )
        
        # 結果サマリー
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n" + "=" * 60)
        print("🎉 SMART PROCESSING COMPLETED!")
        print("=" * 60)
        print(f"📊 Results:")
        print(f"  • Task issues created: {len(task_created)}")
        print(f"  • KPT issues created: {len(kpt_created)}")
        print(f"  • Total issues created: {len(all_created_issues)}")
        if retry_created:
            print(f"  • Retry issues created: {len(retry_created)}")
        print(f"  • Task issues linked: {task_linked}")
        print(f"  • KPT issues linked: {kpt_linked}")
        final_failed = len(all_failed_issues) - len(retry_created)
        if final_failed > 0:
            print(f"  • Final failed issues: {final_failed}")
        print(f"  • Success rate: {(len(all_created_issues)/total_issues*100):.1f}%")
        print(f"⏱️ Performance:")
        print(f"  • Execution time: {execution_time:.1f} seconds")
        if all_created_issues:
            print(f"  • Average per issue: {(execution_time/len(all_created_issues)):.2f}s")
        
        # 結果保存
        with open('smart_issue_creation_result.txt', 'w', encoding='utf-8') as f:
            f.write(f"Smart Issue Creation Results (v5.0 Refactored)\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Task issues: {len(task_created)}\n")
            f.write(f"KPT issues: {len(kpt_created)}\n")
            f.write(f"Total: {len(all_created_issues)}\n")
            if retry_created:
                f.write(f"Retry issues: {len(retry_created)}\n")
            if final_failed > 0:
                f.write(f"Final failed issues: {final_failed}\n")
            f.write(f"Execution time: {execution_time:.1f}s\n")
            f.write(f"Success rate: {(len(all_created_issues)/total_issues*100):.1f}%\n")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    import sys
    
    # コマンドライン引数処理
    if len(sys.argv) > 1:
        issue_type = sys.argv[1].lower()
        if issue_type in ['task', 'test', 'kpt', 'link']:
            print(f"🎯 Running in {issue_type.upper()} mode")
            # TODO: ここで特定のIssue種別のみ処理するロジックを実装
            # 現在は全種別を処理
    
    exit(main())
