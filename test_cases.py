# ========1.1 導入模組開始 ========#
from typing import Dict, List, Tuple, Any
# ========1.1 導入模組結束 ========#

# ========1.2 測試案例列表開始 ========#
ADMIN_TEST_CASES = [
    {
        "description": "測試案例1：基礎平衡型",
        "bazi_data1": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1991, "month": 2, "day": 2, "hour": 13, "gender": "女", "hour_confidence": "high"},
        "expected_range": (60, 75),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例2：天合地合",
        "bazi_data1": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1995, "month": 1, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (70, 85),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例3：日柱六沖",
        "bazi_data1": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1990, "month": 7, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (40, 60),
        "expected_model": "相欠型"
    },
    {
        "description": "測試案例4：紅鸞天喜組合",
        "bazi_data1": {"year": 1985, "month": 2, "day": 14, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1986, "month": 8, "day": 15, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (75, 90),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例5：喜用神互補",
        "bazi_data1": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1988, "month": 5, "day": 5, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (70, 85),
        "expected_model": "供求型"
    },
    {
        "description": "測試案例6：強烈沖剋",
        "bazi_data1": {"year": 1992, "month": 6, "day": 6, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1992, "month": 12, "day": 6, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (30, 50),
        "expected_model": "相欠型"
    },
    {
        "description": "測試案例7：神煞加持",
        "bazi_data1": {"year": 1987, "month": 3, "day": 8, "hour": 8, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1988, "month": 9, "day": 10, "hour": 16, "gender": "女", "hour_confidence": "high"},
        "expected_range": (65, 80),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例8：年齡差距大",
        "bazi_data1": {"year": 1975, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1995, "month": 1, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (60, 75),
        "expected_model": "供求型"
    },
    {
        "description": "測試案例9：相同八字",
        "bazi_data1": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (40, 60),
        "expected_model": "混合型"
    },
    {
        "description": "測試案例10：極品組合",
        "bazi_data1": {"year": 1988, "month": 8, "day": 8, "hour": 8, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1989, "month": 9, "day": 9, "hour": 9, "gender": "女", "hour_confidence": "high"},
        "expected_range": (80, 95),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例11：六合解沖",
        "bazi_data1": {"year": 1991, "month": 3, "day": 3, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1992, "month": 4, "day": 4, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (65, 80),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例12：天乙貴人",
        "bazi_data1": {"year": 1986, "month": 6, "day": 6, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1987, "month": 7, "day": 7, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (70, 85),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例13：地支三合",
        "bazi_data1": {"year": 1985, "month": 5, "day": 5, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1989, "month": 9, "day": 9, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (65, 80),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例14：天干五合",
        "bazi_data1": {"year": 1990, "month": 10, "day": 10, "hour": 10, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1991, "month": 11, "day": 11, "hour": 11, "gender": "女", "hour_confidence": "high"},
        "expected_range": (75, 90),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例15：刑沖嚴重",
        "bazi_data1": {"year": 1993, "month": 3, "day": 3, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1993, "month": 9, "day": 3, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (30, 50),
        "expected_model": "相欠型"
    },
    {
        "description": "測試案例16：化解組合",
        "bazi_data1": {"year": 1984, "month": 4, "day": 4, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1985, "month": 5, "day": 5, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (70, 85),
        "expected_model": "供求型"
    },
    {
        "description": "測試案例17：能量救應",
        "bazi_data1": {"year": 1992, "month": 2, "day": 2, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1994, "month": 4, "day": 4, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (65, 80),
        "expected_model": "供求型"
    },
    {
        "description": "測試案例18：大運良好",
        "bazi_data1": {"year": 1988, "month": 8, "day": 18, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1989, "month": 9, "day": 19, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (75, 90),
        "expected_model": "平衡型"
    },
    {
        "description": "測試案例19：格局特殊",
        "bazi_data1": {"year": 1996, "month": 6, "day": 16, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1997, "month": 7, "day": 17, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (60, 75),
        "expected_model": "混合型"
    },
    {
        "description": "測試案例20：綜合測試",
        "bazi_data1": {"year": 1999, "month": 9, "day": 19, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 2000, "month": 10, "day": 20, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (65, 80),
        "expected_model": "平衡型"
    }
]
# ========1.2 測試案例列表結束 ========#

# ========文件信息開始 ========#
"""
文件: test_cases.py
功能: 測試案例文件，包含20組管理員測試案例

引用文件: typing (Python標準庫)
被引用文件: admin_service.py

主要功能:
- ADMIN_TEST_CASES: 20組完整測試案例
- 測試案例格式統一，方便管理員測試使用
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
1.1 導入模組開始
1.2 測試案例列表開始
"""
# ========目錄結束 ========#

# ========修正紀錄開始 ========#
"""
修正內容：
1. 添加缺失的導入語句: from typing import Dict, List, Tuple, Any
2. 移除輔助函數：get_all_test_descriptions(), format_test_case(), get_test_case_by_id()
   （這些函數已移至 admin_service.py）
3. 簡化文件結構，只保留測試案例列表
4. 總行數減少約50行

導致問題：admin_service.py 無法調用輔助函數
如何修復：將輔助函數移至 admin_service.py，保持功能完整
後果：減少文件依賴，test_cases.py 更專注於數據
"""
# ========修正紀錄結束 ========#