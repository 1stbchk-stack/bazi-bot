#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地管理員測試工具
可以在本地運行20組八字測試，無需部署到Railway
"""

import sys
import os
import json
from datetime import datetime

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_environment():
    """設置環境變數"""
    # 設置必需的環境變數
    os.environ["BOT_TOKEN"] = "local-test-token"
    os.environ["DATABASE_URL"] = "postgresql://local:test@localhost:5432/testdb"
    os.environ["MATCH_SECRET_KEY"] = "local-test-secret-key"
    os.environ["ADMIN_USER_IDS"] = "123456789"
    
    print("✅ 環境變數已設置")

def run_admin_tests():
    """運行管理員測試"""
    try:
        # 導入admin_service
        from admin_service import AdminService, ADMIN_TEST_CASES
        
        print("=" * 60)
        print("🧪 開始運行本地管理員測試")
        print("=" * 60)
        print(f"📋 總共 {len(ADMIN_TEST_CASES)} 組測試案例\n")
        
        admin_service = AdminService()
        
        # 運行所有測試
        results = admin_service.run_admin_tests()
        
        # 輸出詳細結果
        print("📊 測試結果摘要:")
        print(f"   總數: {results['total']}")
        print(f"   通過: {results['passed']}")
        print(f"   失敗: {results['failed']}")
        print(f"   錯誤: {results['errors']}")
        print(f"   成功率: {results['success_rate']:.1f}%\n")
        
        # 輸出詳細結果
        print("📋 詳細測試結果:")
        print("-" * 80)
        
        for i, test_result in enumerate(results['details']):
            status_emoji = "✅" if test_result['status'] == 'PASS' else "❌" if test_result['status'] == 'FAIL' else "⚠️"
            
            print(f"{i+1:2d}. {status_emoji} {test_result['description']}")
            print(f"    分數: {test_result['score']:.1f}分 (預期: {test_result['expected_range'][0]}-{test_result['expected_range'][1]}分)")
            print(f"    模型: {test_result['model']} (預期: {test_result['expected_model']})")
            
            if test_result.get('birth1') and test_result.get('birth2'):
                print(f"    A八字: {test_result['birth1']}")
                print(f"    B八字: {test_result['birth2']}")
            
            if test_result.get('score_details'):
                print(f"    分數細項: {test_result['score_details']}")
            
            if test_result.get('details'):
                for detail in test_result['details'][:2]:  # 只顯示前兩條
                    print(f"    {detail}")
            
            if test_result.get('error'):
                print(f"    ❌ 錯誤: {test_result['error']}")
            
            print()
        
        # 輸出統計報告
        print("=" * 80)
        print("📈 統計報告")
        print("=" * 80)
        
        # 分數分佈統計
        scores = [r['score'] for r in results['details'] if r['status'] != 'ERROR']
        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            
            print(f"分數範圍: {min_score:.1f} - {max_score:.1f}分")
            print(f"平均分數: {avg_score:.1f}分")
        
        # 模型分佈
        models = {}
        for r in results['details']:
            if r['model']:
                models[r['model']] = models.get(r['model'], 0) + 1
        
        if models:
            print("\n模型分佈:")
            for model, count in models.items():
                print(f"  {model}: {count}次")
        
        # 生成報告文件
        generate_report(results)
        
        return results
        
    except ImportError as e:
        print(f"❌ 導入失敗: {e}")
        print("請確保以下文件在當前目錄:")
        print("  - admin_service.py")
        print("  - new_calculator.py")
        return None
    except Exception as e:
        print(f"❌ 測試運行失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_report(results):
    """生成測試報告文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"admin_test_report_{timestamp}.txt"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("🧪 八字配對系統管理員測試報告\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"測試案例數: {results['total']}\n")
            f.write(f"通過數: {results['passed']}\n")
            f.write(f"失敗數: {results['failed']}\n")
            f.write(f"錯誤數: {results['errors']}\n")
            f.write(f"成功率: {results['success_rate']:.1f}%\n\n")
            
            f.write("詳細測試結果:\n")
            f.write("-" * 80 + "\n")
            
            for i, test_result in enumerate(results['details']):
                status_emoji = "✅" if test_result['status'] == 'PASS' else "❌" if test_result['status'] == 'FAIL' else "⚠️"
                
                f.write(f"{i+1:2d}. {status_emoji} {test_result['description']}\n")
                f.write(f"    分數: {test_result['score']:.1f}分 (預期: {test_result['expected_range'][0]}-{test_result['expected_range'][1]}分)\n")
                f.write(f"    模型: {test_result['model']} (預期: {test_result['expected_model']})\n")
                
                if test_result.get('score_details'):
                    f.write(f"    分數細項: {test_result['score_details']}\n")
                
                if test_result.get('details'):
                    for detail in test_result['details']:
                        f.write(f"    {detail}\n")
                
                if test_result.get('error'):
                    f.write(f"    ❌ 錯誤: {test_result['error']}\n")
                
                f.write("\n")
            
            # 極簡格式結果
            f.write("\n" + "=" * 80 + "\n")
            f.write("極簡格式結果 (供快速查看):\n")
            f.write("=" * 80 + "\n")
            
            for formatted_result in results.get('formatted_results', []):
                f.write(formatted_result + "\n")
        
        print(f"📄 報告已保存到: {report_file}")
        
    except Exception as e:
        print(f"❌ 生成報告失敗: {e}")

def run_single_test(test_number):
    """運行單個測試案例"""
    try:
        from admin_service import AdminService, ADMIN_TEST_CASES, get_test_case_by_id
        
        if test_number < 1 or test_number > len(ADMIN_TEST_CASES):
            print(f"❌ 測試編號 {test_number} 無效，請輸入 1-{len(ADMIN_TEST_CASES)}")
            return
        
        test_case = get_test_case_by_id(test_number)
        if 'error' in test_case:
            print(f"❌ {test_case['error']}")
            return
        
        print(f"🔍 運行單個測試案例 #{test_number}")
        print(f"描述: {test_case['description']}")
        
        admin_service = AdminService()
        
        # 使用私有方法運行測試
        test_result = admin_service._run_single_test(test_number, test_case)
        
        # 顯示結果
        print("\n📊 測試結果:")
        print(f"  狀態: {test_result.status}")
        print(f"  分數: {test_result.score:.1f}分")
        print(f"  預期範圍: {test_result.expected_range[0]}-{test_result.expected_range[1]}分")
        print(f"  模型: {test_result.model}")
        print(f"  預期模型: {test_result.expected_model}")
        
        if test_result.details:
            print("\n  詳細信息:")
            for detail in test_result.details:
                print(f"    {detail}")
        
        if test_result.score_details:
            print(f"  分數細項: {test_result.score_details}")
        
        # 檢查是否在預期範圍內
        if test_result.expected_range[0] <= test_result.score <= test_result.expected_range[1]:
            print("✅ 分數在預期範圍內")
        else:
            print("❌ 分數超出預期範圍")
        
        if test_result.model == test_result.expected_model:
            print("✅ 模型匹配")
        else:
            print("❌ 模型不匹配")
            
    except Exception as e:
        print(f"❌ 運行單個測試失敗: {e}")
        import traceback
        traceback.print_exc()

def list_tests():
    """列出所有測試案例"""
    try:
        from admin_service import ADMIN_TEST_CASES
        
        print("📋 可用測試案例:")
        print("=" * 80)
        
        for i, test_case in enumerate(ADMIN_TEST_CASES, 1):
            print(f"{i:2d}. {test_case['description']}")
            print(f"    預期分數: {test_case['expected_range'][0]}-{test_case['expected_range'][1]}分")
            print(f"    預期模型: {test_case.get('expected_model', '未指定')}")
            print()
            
    except ImportError as e:
        print(f"❌ 導入失敗: {e}")

def main():
    """主函數"""
    print("🔧 八字配對系統 - 本地管理員測試工具")
    print("=" * 60)
    
    # 檢查參數
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_tests()
            return
        elif command == "single" and len(sys.argv) > 2:
            try:
                test_number = int(sys.argv[2])
                setup_environment()
                run_single_test(test_number)
                return
            except ValueError:
                print("❌ 請輸入有效的測試編號")
                return
        elif command == "help":
            print_help()
            return
    
    # 默認運行所有測試
    setup_environment()
    results = run_admin_tests()
    
    if results:
        if results['success_rate'] >= 80:
            print("🎉 測試完成！系統狀態良好！")
        elif results['success_rate'] >= 60:
            print("⚠️ 測試完成！系統有部分問題需要注意！")
        else:
            print("❌ 測試完成！系統存在較多問題！")

def print_help():
    """顯示幫助信息"""
    print("使用方法:")
    print("  python local_admin_test.py              # 運行所有測試")
    print("  python local_admin_test.py list         # 列出所有測試案例")
    print("  python local_admin_test.py single <編號>  # 運行單個測試案例")
    print("  python local_admin_test.py help         # 顯示此幫助信息")
    print()
    print("示例:")
    print("  python local_admin_test.py")
    print("  python local_admin_test.py list")
    print("  python local_admin_test.py single 5")

if __name__ == "__main__":
    main()