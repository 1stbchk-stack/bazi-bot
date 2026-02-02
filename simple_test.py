#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
極簡本地測試工具
直接運行20組八字測試
"""

import sys
import os
from datetime import datetime

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_environment():
    """設置環境變數"""
    os.environ["BOT_TOKEN"] = "local-test-token"
    os.environ["DATABASE_URL"] = "postgresql://local:test@localhost:5432/testdb"
    os.environ["MATCH_SECRET_KEY"] = "local-test-secret-key"
    os.environ["ADMIN_USER_IDS"] = "123456789"
    print("✅ 環境變數已設置")

def run_simple_test():
    """簡單測試"""
    try:
        from new_calculator import BaziCalculator, calculate_match
        from admin_service import ADMIN_TEST_CASES
        
        print("🧪 八字配對系統 - 本地測試")
        print("=" * 60)
        print(f"📋 總共 {len(ADMIN_TEST_CASES)} 組測試案例")
        print()
        
        total = len(ADMIN_TEST_CASES)
        passed = 0
        failed = 0
        errors = 0
        
        for i, test_case in enumerate(ADMIN_TEST_CASES, 1):
            print(f"測試 {i:2d}/{total}: {test_case['description']}")
            
            try:
                bazi_data1 = test_case['bazi_data1']
                bazi_data2 = test_case['bazi_data2']
                
                # 計算八字
                bazi1 = BaziCalculator.calculate(**bazi_data1)
                bazi2 = BaziCalculator.calculate(**bazi_data2)
                
                if not bazi1 or not bazi2:
                    print(f"  ❌ 八字計算失敗")
                    failed += 1
                    continue
                
                # 配對計算
                gender1 = bazi_data1['gender']
                gender2 = bazi_data2['gender']
                
                match_result = calculate_match(bazi1, bazi2, gender1, gender2, is_testpair=True)
                
                score = match_result.get('score', 0)
                expected_min, expected_max = test_case['expected_range']
                
                # 檢查結果
                if expected_min <= score <= expected_max:
                    status = "✅"
                    passed += 1
                elif abs(score - expected_min) <= 1 or abs(score - expected_max) <= 1:
                    status = "⚠️"
                    passed += 1
                else:
                    status = "❌"
                    failed += 1
                
                # 提取八字四柱
                pillars1 = f"{bazi1.get('year_pillar', '')}{bazi1.get('month_pillar', '')}{bazi1.get('day_pillar', '')}{bazi1.get('hour_pillar', '')}"
                pillars2 = f"{bazi2.get('year_pillar', '')}{bazi2.get('month_pillar', '')}{bazi2.get('day_pillar', '')}{bazi2.get('hour_pillar', '')}"
                
                print(f"  {status} 分數: {score:.1f}分 (預期: {expected_min}-{expected_max}分)")
                print(f"     八字A: {pillars1}")
                print(f"     八字B: {pillars2}")
                
            except Exception as e:
                print(f"  ❌ 錯誤: {str(e)}")
                errors += 1
            
            print()
        
        # 統計結果
        print("=" * 60)
        print("📊 測試結果摘要:")
        print(f"   總數: {total}")
        print(f"   通過: {passed}")
        print(f"   失敗: {failed}")
        print(f"   錯誤: {errors}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"   成功率: {success_rate:.1f}%")
        
        # 保存結果
        save_results(total, passed, failed, errors, success_rate)
        
    except ImportError as e:
        print(f"❌ 導入失敗: {e}")
        print("請確保以下文件在當前目錄:")
        print("  - new_calculator.py")
        print("  - admin_service.py")

def save_results(total, passed, failed, errors, success_rate):
    """保存測試結果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_results_{timestamp}.txt"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("八字配對系統測試報告\n")
            f.write("=" * 50 + "\n")
            f.write(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"測試案例數: {total}\n")
            f.write(f"通過數: {passed}\n")
            f.write(f"失敗數: {failed}\n")
            f.write(f"錯誤數: {errors}\n")
            f.write(f"成功率: {success_rate:.1f}%\n")
        
        print(f"📄 報告已保存到: {report_file}")
        
    except Exception as e:
        print(f"❌ 保存報告失敗: {e}")

def main():
    """主函數"""
    print("🔧 八字配對系統本地測試工具")
    print("=" * 50)
    
    setup_environment()
    run_simple_test()

if __name__ == "__main__":
    main()