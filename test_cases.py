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
        "expected_range": (35, 48),
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
        "expected_range": (50, 65),
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
        "expected_range": (82, 92),
        "expected_model": "平衡型",
        "expected_modules": {"energy_rescue": (15, 20), "structure_core": (15, 20), "shen_sha_bonus": (6, 10)}
    },
    {
        "description": "測試案例11：現代案例 - 合理範圍",
        "bazi_data1": {"year": 2000, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "medium"},
        "bazi_data2": {"year": 2001, "month": 1, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "medium"},
        "expected_range": (55, 75),
        "expected_model": "平衡型",
        "expected_modules": {"structure_core": (5, 15), "pressure_penalty": (-5, 0)}
    },
    {
        "description": "測試案例12：高分但為供求型",
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
        "description": "測試案例14：經緯度差異 + 能量救應（香港 vs 北京）",
        "bazi_data1": {"year": 2005, "month": 4, "day": 4, "hour": 12, "gender": "男", "hour_confidence": "high", "longitude": 114.17},
        "bazi_data2": {"year": 2006, "month": 5, "day": 5, "hour": 12, "gender": "女", "hour_confidence": "high", "longitude": 116.4},
        "expected_range": (60, 72),
        "expected_model": "供求型",
        "expected_modules": {"energy_rescue": (12, 18), "pressure_penalty": (-8, -3)}
    },
    {
        "description": "測試案例15：極端刑沖 + 無化解（多柱刑害）",
        "bazi_data1": {"year": 1990, "month": 3, "day": 3, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1990, "month": 9, "day": 3, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (25, 40),
        "expected_model": "混合型",
        "expected_modules": {"pressure_penalty": (-30, -25), "structure_core": (0, 5)}
    },
    {
        "description": "測試案例16：時辰模糊 + 格局特殊（估算時辰）",
        "bazi_data1": {"year": 1990, "month": 6, "day": 16, "hour": 12, "gender": "男", "hour_confidence": "estimated"},
        "bazi_data2": {"year": 1991, "month": 7, "day": 17, "hour": 12, "gender": "女", "hour_confidence": "estimated"},
        "expected_range": (55, 68),
        "expected_model": "混合型",
        "expected_modules": {"structure_core": (5, 10), "energy_rescue": (8, 12)}
    },
    {
        "description": "測試案例17：中等配對（一般緣分）",
        "bazi_data1": {"year": 1995, "month": 5, "day": 15, "hour": 14, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1996, "month": 8, "day": 20, "hour": 16, "gender": "女", "hour_confidence": "high"},
        "expected_range": (50, 65),
        "expected_model": "混合型",
        "expected_modules": {"energy_rescue": (5, 10), "pressure_penalty": (-10, -5)}
    },
    {
        "description": "測試案例18：良好配對（有發展潛力）",
        "bazi_data1": {"year": 1988, "month": 12, "day": 25, "hour": 8, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1989, "month": 6, "day": 18, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (65, 78),
        "expected_model": "平衡型",
        "expected_modules": {"structure_core": (10, 15), "shen_sha_bonus": (5, 10)}
    },
    {
        "description": "測試案例19：低分警告（需要謹慎）",
        "bazi_data1": {"year": 1990, "month": 2, "day": 14, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 1990, "month": 8, "day": 14, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (40, 55),
        "expected_model": "混合型",
        "expected_modules": {"pressure_penalty": (-20, -15), "personality_risk": (-10, -5)}
    },
    {
        "description": "測試案例20：邊緣合格（剛好及格）",
        "bazi_data1": {"year": 2000, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "high"},
        "bazi_data2": {"year": 2000, "month": 7, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "high"},
        "expected_range": (55, 70),
        "expected_model": "混合型",
        "expected_modules": {"energy_rescue": (8, 12), "pressure_penalty": (-15, -10)}
    }
]
# ========1.2 測試案例列表結束 ========#