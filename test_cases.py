# ========1.1 導入模組開始 ========#
from typing import Dict, List, Tuple, Any
# ========1.1 導入模組結束 ========#

# ========1.2 測試案例列表開始 ========#
ADMIN_TEST_CASES = [
    {
        "description": "測試案例1：基礎平衡型（五行中和、無明顯沖合）",
        "bazi_data1": {"year": 1989, "month": 4, "day": 12, "hour": 11, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1990, "month": 6, "day": 18, "hour": 13, "gender": "女", "hour_confidence": "high"},
        "expected_range": (60, 75),
        "expected_model": "平衡型",
        "expected_modules": {"energy_rescue": (8, 12), "structure_core": (10, 14), "pressure_penalty": (-8, -3), "shen_sha_bonus": (2, 6)}
    },
    {
        "description": "測試案例2：天干五合單因子（乙庚合金，日柱明顯）",
        "bazi_data1": {"year": 1990, "month": 10, "day": 10, "hour": 10, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1991, "month": 11, "day": 11, "hour": 11, "gender": "女", "hour_confidence": "high"},
        "expected_range": (70, 82),
        "expected_model": "平衡型",
        "expected_modules": {"structure_core": (15, 20), "pressure_penalty": (-5, 0)}
    },
    {
        "description": "測試案例3：日支六沖純負例（子午沖，宮位重創）",
        "bazi_data1": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1990, "month": 7, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (35, 48),  # ChatGPT建議：日支六沖硬上限45
        "expected_model": "混合型",
        "expected_modules": {"pressure_penalty": (-20, -15), "structure_core": (0, 5)}
    },
    {
        "description": "測試案例4：紅鸞天喜組合（神煞強輔助）",
        "bazi_data1": {"year": 1985, "month": 2, "day": 14, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1986, "month": 8, "day": 15, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (75, 85),
        "expected_model": "平衡型",
        "expected_modules": {"shen_sha_bonus": (8, 12), "energy_rescue": (8, 12)}
    },
    {
        "description": "測試案例5：喜用神強互補（金木互濟，濃度高）",
        "bazi_data1": {"year": 1990, "month": 1, "day": 5, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1988, "month": 5, "day": 9, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (70, 82),
        "expected_model": "供求型",
        "expected_modules": {"energy_rescue": (15, 22), "pressure_penalty": (-5, 0)}
    },
    {
        "description": "測試案例6：多重刑沖無解（寅巳申三刑）",
        "bazi_data1": {"year": 1992, "month": 6, "day": 6, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1992, "month": 12, "day": 6, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (30, 45),
        "expected_model": "混合型",
        "expected_modules": {"pressure_penalty": (-25, -18), "structure_core": (0, 5)}
    },
    {
        "description": "測試案例7：年齡差距大但結構穩（供求型）",
        "bazi_data1": {"year": 1975, "month": 3, "day": 9, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1995, "month": 4, "day": 11, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (58, 70),
        "expected_model": "供求型",
        "expected_modules": {"pressure_penalty": (-10, -5), "structure_core": (8, 12)}
    },
    {
        "description": "測試案例8：相同八字（伏吟大忌）",
        "bazi_data1": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (50, 65),  # ChatGPT建議：相同八字應為55-70
        "expected_model": "混合型",
        "expected_modules": {"structure_core": (-12, -8), "pressure_penalty": (-15, -10)}
    },
    {
        "description": "測試案例9：六合解沖（子午沖遇丑合）",
        "bazi_data1": {"year": 1984, "month": 12, "day": 15, "hour": 2, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1990, "month": 6, "day": 20, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (60, 75),
        "expected_model": "平衡型",
        "expected_modules": {"pressure_penalty": (-12, -6), "structure_core": (10, 15)}
    },
    {
        "description": "測試案例10：全面優質組合（無滿分，師傅級）",
        "bazi_data1": {"year": 1988, "month": 8, "day": 8, "hour": 8, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1989, "month": 9, "day": 9, "hour": 9, "gender": "女", "hour_confidence": "high"},
        "expected_range": (82, 92),  # ChatGPT建議：收窄為82-92
        "expected_model": "平衡型",
        "expected_modules": {"energy_rescue": (15, 20), "structure_core": (15, 20), "shen_sha_bonus": (6, 10)}
    },
    {
        "description": "測試案例11：歷史案例 - 康熙與赫舍里皇后（三合化解 + 上等）",
        "bazi_data1": {"year": 1654, "month": 5, "day": 4, "hour": 12, "gender": "男", "hour_confidence": "medium"},
        "bazi_data2": {"year": 1653, "month": 10, "day": 16, "hour": 12, "gender": "女", "hour_confidence": "medium"},
        "expected_range": (75, 85),
        "expected_model": "平衡型",
        "expected_modules": {"structure_core": (15, 20), "pressure_penalty": (-5, 0)}
    },
    {
        "description": "測試案例12：高分但為供求型（ChatGPT建議新增）",
        "bazi_data1": {"year": 1980, "month": 3, "day": 15, "hour": 10, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1990, "month": 6, "day": 20, "hour": 14, "gender": "女", "hour_confidence": "high"},
        "expected_range": (68, 78),
        "expected_model": "供求型",
        "expected_modules": {"energy_rescue": (12, 18), "structure_core": (8, 12)}
    },
    {
        "description": "測試案例13：邊緣時辰不確定（子時邊界 + 喜用互補）",
        "bazi_data1": {"year": 2000, "month": 1, "day": 1, "hour": 23, "gender": "男", "hour_confidence": "low"},
        "bazi_data2": {"year": 2001, "month": 6, "day": 15, "hour": 0, "gender": "女", "hour_confidence": "low"},
        "expected_range": (55, 70),
        "expected_model": "供求型",
        "expected_modules": {"energy_rescue": (10, 15), "pressure_penalty": (-10, -5)}
    },
    {
        "description": "測試案例14：歷史案例 - 李嘉誠與周凱旋（神煞 + 年齡差距）",
        "bazi_data1": {"year": 1928, "month": 7, "day": 29, "hour": 12, "gender": "男", "hour_confidence": "medium"},
        "bazi_data2": {"year": 1954, "month": 1, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "medium"},
        "expected_range": (60, 75),
        "expected_model": "供求型",
        "expected_modules": {"shen_sha_bonus": (10, 15), "pressure_penalty": (-10, -5)}
    },
    {
        "description": "測試案例15：極端刑沖 + 無化解（多柱刑害）",
        "bazi_data1": {"year": 1900, "month": 3, "day": 3, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1900, "month": 9, "day": 3, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (25, 40),
        "expected_model": "混合型",
        "expected_modules": {"pressure_penalty": (-30, -25), "structure_core": (0, 5)}
    },
    {
        "description": "測試案例16：歷史案例 - 楊玉環與唐玄宗（格局特殊 + 大運良好）",
        "bazi_data1": {"year": 719, "month": 6, "day": 22, "hour": 12, "gender": "女", "hour_confidence": "low"},
        "bazi_data2": {"year": 685, "month": 9, "day": 8, "hour": 12, "gender": "男", "hour_confidence": "low"},
        "expected_range": (65, 80),
        "expected_model": "平衡型",
        "expected_modules": {"structure_core": (12, 18), "dayun_risk": (-5, 0)}
    },
    {
        "description": "測試案例17：經緯度差異 + 能量救應（香港 vs 北京）",
        "bazi_data1": {"year": 2005, "month": 4, "day": 4, "hour": 12, "gender": "男", "hour_confidence": "high", "longitude": 114.17},
        "bazi_data2": {"year": 2006, "month": 5, "day": 5, "hour": 12, "gender": "女", "hour_confidence": "high", "longitude": 116.4},
        "expected_range": (60, 72),
        "expected_model": "供求型",
        "expected_modules": {"energy_rescue": (12, 18), "pressure_penalty": (-8, -3)}
    },
    {
        "description": "測試案例18：歷史案例 - 蘇軾與王朝雲（神煞 + 年齡差距）",
        "bazi_data1": {"year": 1037, "month": 1, "day": 8, "hour": 12, "gender": "男", "hour_confidence": "medium"},
        "bazi_data2": {"year": 1065, "month": 3, "day": 15, "hour": 12, "gender": "女", "hour_confidence": "medium"},
        "expected_range": (65, 78),
        "expected_model": "平衡型",
        "expected_modules": {"shen_sha_bonus": (8, 12), "pressure_penalty": (-10, -5)}
    },
    {
        "description": "測試案例19：時辰模糊 + 格局特殊（估算時辰）",
        "bazi_data1": {"year": 1950, "month": 6, "day": 16, "hour": 12, "gender": "男", "hour_confidence": "estimated"},
        "bazi_data2": {"year": 1951, "month": 7, "day": 17, "hour": 12, "gender": "女", "hour_confidence": "estimated"},
        "expected_range": (55, 68),
        "expected_model": "混合型",
        "expected_modules": {"structure_core": (5, 10), "energy_rescue": (8, 12)}
    },
    {
        "description": "測試案例20：綜合歷史案例 - 武則天與李治（刑沖 + 大運良好）",
        "bazi_data1": {"year": 624, "month": 2, "day": 17, "hour": 12, "gender": "女", "hour_confidence": "low"},
        "bazi_data2": {"year": 628, "month": 7, "day": 23, "hour": 12, "gender": "男", "hour_confidence": "low"},
        "expected_range": (58, 72),
        "expected_model": "供求型",
        "expected_modules": {"pressure_penalty": (-15, -10), "dayun_risk": (-5, 0)}
    }
]
# ========1.2 測試案例列表結束 ========#

# ========文件信息開始 ========#
"""
文件: test_cases.py
功能: 測試案例文件，包含20組管理員測試案例

引用文件: typing (Python標準庫)
被引用文件: admin_service.py

主要修改：
1. 根據ChatGPT建議調整測試案例預期範圍：
   - 案例3：日支六沖上限45分
   - 案例8：相同八字範圍50-65分
   - 案例10：極品組合上限92分
2. 新增案例12：高分但為供求型
3. 調整所有案例的預期範圍以匹配60分基準
4. 簡化關係模型為3種（平衡型、供求型、混合型）

修改記錄：
2026-02-02 本次修正：
1. 根據新的評分系統調整所有預期範圍
2. 新增供求型測試案例
3. 簡化關係模型分類
4. 確保測試案例符合新的數學驗證規則
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
1.1 導入模組開始
1.2 測試案例列表開始
"""
# ========目錄結束 ========#