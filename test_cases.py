#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試案例文件 - 包含管理員測試案例
最後更新: 2026年2月1日
"""

from typing import Dict, List, Tuple, Any  # 添加類型提示導入

ADMIN_TEST_CASES = [
    {
        "description": "測試案例1：基礎平衡型",
        "bazi_data1": {
            "year": 1990,
            "month": 1,
            "day": 1,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1991,
            "month": 2,
            "day": 2,
            "hour": 13,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (60, 75),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例2：天合地合",
        "bazi_data1": {
            "year": 1990,
            "month": 1,
            "day": 1,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1995,
            "month": 1,
            "day": 1,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (70, 85),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例3：日柱六沖",
        "bazi_data1": {
            "year": 1990,
            "month": 1,
            "day": 1,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1990,
            "month": 7,
            "day": 1,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (40, 60),
        "expected_model": "相欠型"
    },
    {
        "description": "測試案例4：紅鸞天喜組合",
        "bazi_data1": {
            "year": 1985,
            "month": 2,
            "day": 14,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1986,
            "month": 8,
            "day": 15,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (75, 90),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例5：喜用神互補",
        "bazi_data1": {
            "year": 1990,
            "month": 1,
            "day": 1,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1988,
            "month": 5,
            "day": 5,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (70, 85),
        "expected_model": "供求型"
    },
    {
        "description": "測試案例6：強烈沖剋",
        "bazi_data1": {
            "year": 1992,
            "month": 6,
            "day": 6,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1992,
            "month": 12,
            "day": 6,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (30, 50),
        "expected_model": "相欠型"
    },
    {
        "description": "測試案例7：神煞加持",
        "bazi_data1": {
            "year": 1987,
            "month": 3,
            "day": 8,
            "hour": 8,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1988,
            "month": 9,
            "day": 10,
            "hour": 16,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (65, 80),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例8：年齡差距大",
        "bazi_data1": {
            "year": 1975,
            "month": 1,
            "day": 1,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1995,
            "month": 1,
            "day": 1,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (60, 75),
        "expected_model": "供求型"
    },
    {
        "description": "測試案例9：相同八字",
        "bazi_data1": {
            "year": 1990,
            "month": 1,
            "day": 1,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1990,
            "month": 1,
            "day": 1,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (40, 60),
        "expected_model": "混合型"
    },
    {
        "description": "測試案例10：極品組合",
        "bazi_data1": {
            "year": 1988,
            "month": 8,
            "day": 8,
            "hour": 8,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1989,
            "month": 9,
            "day": 9,
            "hour": 9,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (80, 95),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例11：六合解沖",
        "bazi_data1": {
            "year": 1991,
            "month": 3,
            "day": 3,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1992,
            "month": 4,
            "day": 4,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (65, 80),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例12：天乙貴人",
        "bazi_data1": {
            "year": 1986,
            "month": 6,
            "day": 6,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1987,
            "month": 7,
            "day": 7,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (70, 85),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例13：地支三合",
        "bazi_data1": {
            "year": 1985,
            "month": 5,
            "day": 5,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1989,
            "month": 9,
            "day": 9,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (65, 80),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例14：天干五合",
        "bazi_data1": {
            "year": 1990,
            "month": 10,
            "day": 10,
            "hour": 10,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1991,
            "month": 11,
            "day": 11,
            "hour": 11,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (75, 90),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例15：刑沖嚴重",
        "bazi_data1": {
            "year": 1993,
            "month": 3,
            "day": 3,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1993,
            "month": 9,
            "day": 3,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (30, 50),
        "expected_model": "相欠型"
    },
    {
        "description": "測試案例16：化解組合",
        "bazi_data1": {
            "year": 1984,
            "month": 4,
            "day": 4,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1985,
            "month": 5,
            "day": 5,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (70, 85),
        "expected_model": "供求型"
    },
    {
        "description": "測試案例17：能量救應",
        "bazi_data1": {
            "year": 1992,
            "month": 2,
            "day": 2,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1994,
            "month": 4,
            "day": 4,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (65, 80),
        "expected_model": "供求型"
    },
    {
        "description": "測試案例18：大運良好",
        "bazi_data1": {
            "year": 1988,
            "month": 8,
            "day": 18,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1989,
            "month": 9,
            "day": 19,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (75, 90),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例19：格局特殊",
        "bazi_data1": {
            "year": 1996,
            "month": 6,
            "day": 16,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 1997,
            "month": 7,
            "day": 17,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (60, 75),
        "expected_model": "混合型"
    },
    {
        "description": "測試案例20：綜合測試",
        "bazi_data1": {
            "year": 1999,
            "month": 9,
            "day": 19,
            "hour": 12,
            "gender": "男",
            "hour_confidence": "high"
        },
        "bazi_data2": {
            "year": 2000,
            "month": 10,
            "day": 20,
            "hour": 12,
            "gender": "女",
            "hour_confidence": "high"
        },
        "expected_range": (65, 80),
        "expected_model": "平衡型"
    }
]

def get_all_test_descriptions() -> List[str]:
    """獲取所有測試案例的描述"""
    return [f"{i+1}. {test['description']}" for i, test in enumerate(ADMIN_TEST_CASES)]

def format_test_case(test_case: Dict, index: int) -> str:
    """格式化顯示測試案例"""
    if index >= len(ADMIN_TEST_CASES):
        return "測試案例索引超出範圍"
    
    tc = test_case
    b1 = tc['bazi_data1']
    b2 = tc['bazi_data2']
    
    return f"""
測試案例 {index+1}: {tc['description']}

八字A:
  年份: {b1['year']}
  月份: {b1['month']}
  日期: {b1['day']}
  時辰: {b1['hour']}
  性別: {b1['gender']}
  信心度: {b1['hour_confidence']}

八字B:
  年份: {b2['year']}
  月份: {b2['month']}
  日期: {b2['day']}
  時辰: {b2['hour']}
  性別: {b2['gender']}
  信心度: {b2['hour_confidence']}

預期結果:
  分數範圍: {tc['expected_range'][0]} - {tc['expected_range'][1]}分
  關係模型: {tc.get('expected_model', '未指定')}
"""

def get_test_case_by_id(test_id: int) -> Dict:
    """根據ID獲取測試案例"""
    if 1 <= test_id <= len(ADMIN_TEST_CASES):
        return ADMIN_TEST_CASES[test_id - 1]
    else:
        return {
            "error": f"測試案例ID {test_id} 超出範圍 (1-{len(ADMIN_TEST_CASES)})"
        }

# ========== 文件信息開始 ==========
"""
文件: test_cases.py
功能: 測試案例文件，包含管理員測試案例

引用文件: typing (Python標準庫)
被引用文件: admin_service.py

包含:
- ADMIN_TEST_CASES: 20組測試案例
- get_all_test_descriptions(): 獲取所有測試描述
- format_test_case(): 格式化顯示測試案例
- get_test_case_by_id(): 根據ID獲取測試案例

測試案例格式:
{
    "description": "描述",
    "bazi_data1": {八字1數據},
    "bazi_data2": {八字2數據},
    "expected_range": (最低分, 最高分),
    "expected_model": "預期關係模型"
}
"""
# ========== 文件信息結束 ==========

# ========== 目錄開始 ==========
"""
1. 導入語句 - 導入必要的類型提示
2. 測試案例列表 - ADMIN_TEST_CASES
3. 函數 - get_all_test_descriptions()
4. 函數 - format_test_case()
5. 函數 - get_test_case_by_id()
"""
# ========== 目錄結束 ==========

# ========== 修正紀錄開始 ==========
"""
版本 1.0 (2026-02-01)
創建文件: 添加20組管理員測試案例

主要功能:
1. 提供完整的20組測試案例，覆蓋各種配對情況
2. 測試案例包含：
   - 基礎平衡型
   - 天合地合
   - 日柱六沖
   - 紅鸞天喜組合
   - 喜用神互補
   - 強烈沖剋
   - 神煞加持
   - 年齡差距大
   - 相同八字
   - 極品組合
   - 六合解沖
   - 天乙貴人
   - 地支三合
   - 天干五合
   - 刑沖嚴重
   - 化解組合
   - 能量救應
   - 大運良好
   - 格局特殊
   - 綜合測試

3. 提供輔助函數：
   - get_all_test_descriptions(): 獲取所有測試描述
   - format_test_case(): 格式化顯示測試案例
   - get_test_case_by_id(): 根據ID獲取測試案例

版本 1.1 (2026-02-01) - 緊急修復
修復問題:
1. 添加缺失的導入語句: from typing import Dict, List, Tuple, Any
2. 修復函數類型提示: 添加返回類型提示
3. 修正get_test_case_by_id()函數的錯誤處理
4. 確保所有函數都有完整的文檔字符串

影響:
- 解決NameError: name 'Dict' is not defined錯誤
- 使admin_service.py可以正常導入test_cases.py
- 提供更完善的測試案例管理功能

用途:
- 供admin_service.py使用
- 管理員可以運行所有測試案例
- 確保系統計算正確性
"""
# ========== 修正紀錄結束 ==========