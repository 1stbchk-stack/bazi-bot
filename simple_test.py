#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
極簡本地測試工具 - 直接運行20組八字測試，不生成文件
"""

import sys
import os
import time

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_environment():
    """設置環境變數"""
    os.environ["BOT_TOKEN"] = "local-test-token"
    os.environ["DATABASE_URL"] = "postgresql://local:test@localhost:5432/testdb"
    os.environ["MATCH_SECRET_KEY"] = "local-test-secret-key"
    os.environ["ADMIN_USER_IDS"] = "123456789"

def run_all_tests():
    """運行所有20組測試"""
    try:
        from new_calculator import BaziCalculator, calculate_match
        from admin_service import ADMIN_TEST_CASES
        
        print("🧪 八字配對系統 - 本地測試")
        print("=" * 70)
        print(f"📋 總共 {len(ADMIN_TEST_CASES)} 組測試案例")
        print()
        
        total = len(ADMIN_TEST_CASES)
        passed = 0
        failed = 0
        errors = 0
        
        all_results = []
        
        for i, test_case in enumerate(ADMIN_TEST_CASES, 1):
            print(f"🔍 測試 {i:2d}/{total}: {test_case['description'][:50]}...")
            
            try:
                bazi_data1 = test_case['bazi_data1']
                bazi_data2 = test_case['bazi_data2']
                
                # 計算八字
                bazi1 = BaziCalculator.calculate(**bazi_data1)
                bazi2 = BaziCalculator.calculate(**bazi_data2)
                
                if not bazi1 or not bazi2:
                    result = {"status": "❌", "reason": "八字計算失敗"}
                    failed += 1
                    continue
                
                # 配對計算
                gender1 = bazi_data1['gender']
                gender2 = bazi_data2['gender']
                
                match_result = calculate_match(bazi1, bazi2, gender1, gender2, is_testpair=True)
                
                score = match_result.get('score', 0)
                expected_min, expected_max = test_case['expected_range']
                
                # 提取八字四柱
                pillars1 = f"{bazi1.get('year_pillar', '')}{bazi1.get('month_pillar', '')}{bazi1.get('day_pillar', '')}{bazi1.get('hour_pillar', '')}"
                pillars2 = f"{bazi2.get('year_pillar', '')}{bazi2.get('month_pillar', '')}{bazi2.get('day_pillar', '')}{bazi2.get('hour_pillar', '')}"
                
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
                
                # 提取分數細項
                module_scores = match_result.get('module_scores', {})
                score_details = match_result.get('score_details', {})
                base_score = score_details.get('base_score', 50)
                
                # 計算各模組分數
                energy = module_scores.get('energy_rescue', 0)
                structure = module_scores.get('structure_core', 0)
                shensha = module_scores.get('shen_sha_bonus', 0)
                resolution = module_scores.get('resolution_bonus', 0)
                personality = module_scores.get('personality_risk', 0)
                pressure = module_scores.get('pressure_penalty', 0)
                dayun = module_scores.get('dayun_risk', 0)
                
                positive_bonus = energy + structure + shensha + resolution
                negative_penalty = personality + pressure + dayun
                
                # 構建結果
                result = {
                    "status": status,
                    "score": score,
                    "expected_range": f"{expected_min}-{expected_max}",
                    "pillars1": pillars1,
                    "pillars2": pillars2,
                    "base_score": base_score,
                    "positive_bonus": positive_bonus,
                    "negative_penalty": negative_penalty,
                    "energy": energy,
                    "structure": structure,
                    "shensha": shensha,
                    "resolution": resolution,
                    "personality": personality,
                    "pressure": pressure,
                    "dayun": dayun,
                    "model": match_result.get('relationship_model', '')
                }
                
                all_results.append(result)
                
                # 顯示結果
                print(f"  {status} 分數: {score:.1f}分 (預期: {expected_min}-{expected_max}分)")
                print(f"     八字: {pillars1} ↔ {pillars2}")
                if result['model']:
                    print(f"     模型: {result['model']}")
                
            except Exception as e:
                print(f"  ❌ 錯誤: {str(e)[:50]}")
                errors += 1
            
            print()
        
        return all_results, total, passed, failed, errors
        
    except ImportError as e:
        print(f"❌ 導入失敗: {e}")
        print("請確保以下文件在當前目錄:")
        print("  - new_calculator.py")
        print("  - admin_service.py")
        return None, 0, 0, 0, 0

def show_summary(all_results, total, passed, failed, errors):
    """顯示測試摘要"""
    print("=" * 70)
    print("📊 測試結果摘要")
    print("=" * 70)
    
    print(f"   總數: {total} 組測試案例")
    print(f"   ✅ 通過: {passed}")
    print(f"   ❌ 失敗: {failed}")
    print(f"   ⚠️  錯誤: {errors}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"   📈 成功率: {success_rate:.1f}%")
    print()
    
    # 顯示分數分佈
    if all_results:
        scores = [r['score'] for r in all_results if r['status'] != '❌']
        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            
            print("📈 分數分佈:")
            print(f"   平均分數: {avg_score:.1f}分")
            print(f"   最低分數: {min_score:.1f}分")
            print(f"   最高分數: {max_score:.1f}分")
            print()
    
    # 顯示詳細結果
    print("🔍 詳細結果 (前10個):")
    print("-" * 70)
    
    for i, result in enumerate(all_results[:10], 1):
        status = result['status']
        score = result['score']
        expected = result['expected_range']
        pillars1 = result['pillars1']
        pillars2 = result['pillars2']
        
        print(f"{i:2d}. {status} {score:5.1f}分 ({expected}分)")
        print(f"    {pillars1} ↔ {pillars2}")
        
        # 顯示分數細項
        details = []
        if result['energy'] != 0:
            details.append(f"能量:{result['energy']:+.0f}")
        if result['structure'] != 0:
            details.append(f"結構:{result['structure']:+.0f}")
        if result['shensha'] != 0:
            details.append(f"神煞:{result['shensha']:+.0f}")
        if result['resolution'] != 0:
            details.append(f"化解:{result['resolution']:+.0f}")
        if result['personality'] != 0:
            details.append(f"人格:{result['personality']:+.0f}")
        if result['pressure'] != 0:
            details.append(f"刑沖:{result['pressure']:+.0f}")
        if result['dayun'] != 0:
            details.append(f"大運:{result['dayun']:+.0f}")
        
        if details:
            print(f"    {' '.join(details)}")
        
        print()

def run_single_test(test_number):
    """運行單個測試"""
    try:
        from new_calculator import BaziCalculator, calculate_match
        from admin_service import ADMIN_TEST_CASES, get_test_case_by_id
        
        if test_number < 1 or test_number > len(ADMIN_TEST_CASES):
            print(f"❌ 測試編號 {test_number} 無效，請輸入 1-{len(ADMIN_TEST_CASES)}")
            return
        
        test_case = get_test_case_by_id(test_number)
        if 'error' in test_case:
            print(f"❌ {test_case['error']}")
            return
        
        print(f"🔍 運行測試案例 #{test_number}")
        print(f"描述: {test_case['description']}")
        print()
        
        bazi_data1 = test_case['bazi_data1']
        bazi_data2 = test_case['bazi_data2']
        
        # 顯示測試參數
        print("📝 測試參數:")
        print(f"  A: {bazi_data1['gender']} {bazi_data1['year']}年{bazi_data1['month']}月{bazi_data1['day']}日{bazi_data1['hour']}時")
        print(f"  B: {bazi_data2['gender']} {bazi_data2['year']}年{bazi_data2['month']}月{bazi_data2['day']}日{bazi_data2['hour']}時")
        print()
        
        # 計算八字
        bazi1 = BaziCalculator.calculate(**bazi_data1)
        bazi2 = BaziCalculator.calculate(**bazi_data2)
        
        if not bazi1 or not bazi2:
            print("❌ 八字計算失敗")
            return
        
        # 顯示八字
        print("🔢 八字四柱:")
        print(f"  A: {bazi1.get('year_pillar', '')} {bazi1.get('month_pillar', '')} {bazi1.get('day_pillar', '')} {bazi1.get('hour_pillar', '')}")
        print(f"  B: {bazi2.get('year_pillar', '')} {bazi2.get('month_pillar', '')} {bazi2.get('day_pillar', '')} {bazi2.get('hour_pillar', '')}")
        print()
        
        # 配對計算
        gender1 = bazi_data1['gender']
        gender2 = bazi_data2['gender']
        
        match_result = calculate_match(bazi1, bazi2, gender1, gender2, is_testpair=True)
        
        score = match_result.get('score', 0)
        expected_min, expected_max = test_case['expected_range']
        expected_model = test_case.get('expected_model', '')
        
        # 檢查結果
        if expected_min <= score <= expected_max:
            status = "✅"
        elif abs(score - expected_min) <= 1 or abs(score - expected_max) <= 1:
            status = "⚠️"
        else:
            status = "❌"
        
        # 顯示結果
        print("📊 測試結果:")
        print(f"  {status} 分數: {score:.1f}分")
        print(f"     預期範圍: {expected_min}-{expected_max}分")
        
        # 顯示評級
        rating = match_result.get('rating', '未知')
        print(f"     評級: {rating}")
        
        # 顯示模型
        model = match_result.get('relationship_model', '')
        print(f"     模型: {model} (預期: {expected_model})")
        
        # 顯示分數細項
        print()
        print("🧮 分數細項:")
        
        module_scores = match_result.get('module_scores', {})
        score_details = match_result.get('score_details', {})
        base_score = score_details.get('base_score', 50)
        
        print(f"     基準分: {base_score}分")
        
        # 顯示各模組分數
        modules = [
            ("⚡ 能量救應", "energy_rescue"),
            ("🏛️ 結構核心", "structure_core"),
            ("✨ 神煞加持", "shen_sha_bonus"),
            ("🛡️ 專業化解", "resolution_bonus"),
            ("🎭 人格風險", "personality_risk"),
            ("⚡ 刑沖壓力", "pressure_penalty"),
            ("🔄 大運風險", "dayun_risk"),
        ]
        
        for name, key in modules:
            value = module_scores.get(key, 0)
            if value != 0:
                sign = "+" if value > 0 else ""
                print(f"     {name}: {sign}{value:.1f}分")
        
        # 計算總加分和總扣分
        positive_total = sum(max(0, v) for v in module_scores.values())
        negative_total = sum(min(0, v) for v in module_scores.values())
        
        print(f"     📈 總加分: +{positive_total:.1f}分")
        print(f"     📉 總扣分: {negative_total:.1f}分")
        
        # 檢查是否在預期範圍內
        print()
        if status == "✅":
            print("🎉 測試通過！分數在預期範圍內")
        elif status == "⚠️":
            print("⚠️  測試邊緣通過！分數接近預期範圍")
        else:
            print("❌ 測試失敗！分數超出預期範圍")
            
    except Exception as e:
        print(f"❌ 運行失敗: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print("🔧 八字配對系統 - 本地測試工具")
    print("=" * 50)
    
    # 檢查參數
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            try:
                from admin_service import ADMIN_TEST_CASES
                print("📋 可用測試案例:")
                print("=" * 50)
                
                for i, test_case in enumerate(ADMIN_TEST_CASES, 1):
                    print(f"{i:2d}. {test_case['description']}")
                    print(f"    預期分數: {test_case['expected_range'][0]}-{test_case['expected_range'][1]}分")
                    print()
                    
            except ImportError as e:
                print(f"❌ 導入失敗: {e}")
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
    print("🔄 設置環境變數...")
    setup_environment()
    
    print("⚡ 開始運行所有測試...")
    start_time = time.time()
    
    results, total, passed, failed, errors = run_all_tests()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    if results is not None:
        show_summary(results, total, passed, failed, errors)
        print(f"⏱️  總用時: {elapsed_time:.1f}秒")
        print(f"📊 平均每組: {elapsed_time/total:.2f}秒")

def print_help():
    """顯示幫助信息"""
    print("使用方法:")
    print("  python simple_test.py              # 運行所有測試")
    print("  python simple_test.py list         # 列出所有測試案例")
    print("  python simple_test.py single <編號>  # 運行單個測試案例")
    print("  python simple_test.py help         # 顯示此幫助信息")
    print()
    print("示例:")
    print("  python simple_test.py")
    print("  python simple_test.py list")
    print("  python simple_test.py single 5")

if __name__ == "__main__":
    main()