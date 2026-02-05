
# ========1.1 導入模組開始 ========#
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

# 修正導入語句：使用正確的對外接口
from new_calculator import (
    calculate_bazi,      # 對外接口：八字計算
    calculate_match,     # 對外接口：配對計算
    ProfessionalConfig as Config,
    BaziFormatters
)

# 從 Config 類獲取常量
THRESHOLD_WARNING = Config.THRESHOLD_WARNING
THRESHOLD_CONTACT_ALLOWED = Config.THRESHOLD_ACCEPTABLE
THRESHOLD_GOOD_MATCH = Config.THRESHOLD_GOOD_MATCH
THRESHOLD_EXCELLENT_MATCH = Config.THRESHOLD_EXCELLENT_MATCH
THRESHOLD_PERFECT_MATCH = Config.THRESHOLD_PERFECT_MATCH
DEFAULT_LONGITUDE = Config.DEFAULT_LONGITUDE

logger = logging.getLogger(__name__)
# ========1.1 導入模組結束 ========#

# ========1.2 數據類開始 ========#
@dataclass
class TestResult:
    """測試結果數據類"""
    test_id: int
    description: str
    status: str
    score: float
    expected_range: Tuple[float, float]
    model: str
    expected_model: str
    model_match: bool
    pillars1: str = ""
    pillars2: str = ""
    range_str: str = ""
    error: str = ""
    details: List[str] = None

@dataclass
class SystemStats:
    """系統統計數據"""
    total_users: int
    total_matches: int
    today_matches: int
    avg_match_score: float
    success_rate: float
    model_stats: List[Dict[str, Any]]
    active_users_24h: int
    top_matches: List[Dict[str, Any]]
# ========1.2 數據類結束 ========#

# ========1.3 測試案例數據開始 ========#
ADMIN_TEST_CASES = [
    {
        "description": "測試案例1：基礎平衡型（五行中和、無明顯沖合）",
        "bazi_data1": {"year": 1989, "month": 4, "day": 12, "hour": 11, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 6, "day": 18, "hour": 13, "gender": "女", "hour_confidence": "高"},
        "expected_range": (60, 75),
        "expected_model": "平衡型",
    },
    {
        "description": "測試案例2：天干五合單因子（乙庚合金，日柱明顯）",
        "bazi_data1": {"year": 1990, "month": 10, "day": 10, "hour": 10, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1991, "month": 11, "day": 11, "hour": 11, "gender": "女", "hour_confidence": "高"},
        "expected_range": (70, 82),
        "expected_model": "平衡型",
    },
    {
        "description": "測試案例3：日支六沖純負例（子午沖，宮位重創）",
        "bazi_data1": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 7, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (35, 48),
        "expected_model": "忌避型",
    },
    {
        "description": "測試案例4：紅鸞天喜組合（神煞強輔助）",
        "bazi_data1": {"year": 1985, "month": 2, "day": 14, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1986, "month": 8, "day": 15, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (75, 85),
        "expected_model": "平衡型",
    },
    {
        "description": "測試案例5：喜用神強互補（金木互濟，濃度高）",
        "bazi_data1": {"year": 1990, "month": 1, "day": 5, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1988, "month": 5, "day": 9, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (70, 82),
        "expected_model": "穩定型",
    },
    {
        "description": "測試案例6：多重刑沖無解（寅巳申三刑）",
        "bazi_data1": {"year": 1992, "month": 6, "day": 6, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1992, "month": 12, "day": 6, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (30, 45),
        "expected_model": "忌避型",
    },
    {
        "description": "測試案例7：年齡差距大但結構穩（供求型）",
        "bazi_data1": {"year": 1975, "month": 3, "day": 9, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1995, "month": 4, "day": 11, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (58, 70),
        "expected_model": "穩定型",
    },
    {
        "description": "測試案例8：相同八字（伏吟大忌）",
        "bazi_data1": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (50, 65),
        "expected_model": "忌避型",
    },
    {
        "description": "測試案例9：六合解沖（子午沖遇丑合）",
        "bazi_data1": {"year": 1984, "month": 12, "day": 15, "hour": 2, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 6, "day": 20, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (60, 75),
        "expected_model": "磨合型",
    },
    {
        "description": "測試案例10：全面優質組合（無滿分，師傅級）",
        "bazi_data1": {"year": 1988, "month": 8, "day": 8, "hour": 8, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1989, "month": 9, "day": 9, "hour": 9, "gender": "女", "hour_confidence": "高"},
        "expected_range": (82, 92),
        "expected_model": "平衡型",
    },
    {
        "description": "測試案例11：現代案例 - 合理範圍",
        "bazi_data1": {"year": 2000, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "中"},
        "bazi_data2": {"year": 2001, "month": 1, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "中"},
        "expected_range": (55, 75),
        "expected_model": "磨合型",
    },
    {
        "description": "測試案例12：高分但為供求型",
        "bazi_data1": {"year": 1980, "month": 3, "day": 15, "hour": 10, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 6, "day": 20, "hour": 14, "gender": "女", "hour_confidence": "高"},
        "expected_range": (68, 78),
        "expected_model": "穩定型",
    },
    {
        "description": "測試案例13：邊緣時辰不確定（子時邊界 + 喜用互補）",
        "bazi_data1": {"year": 2000, "month": 1, "day": 1, "hour": 23, "gender": "男", "hour_confidence": "低"},
        "bazi_data2": {"year": 2001, "month": 6, "day": 15, "hour": 0, "gender": "女", "hour_confidence": "低"},
        "expected_range": (55, 70),
        "expected_model": "磨合型",
    },
    {
        "description": "測試案例14：經緯度差異 + 能量救應（香港 vs 北京）",
        "bazi_data1": {"year": 2005, "month": 4, "day": 4, "hour": 12, "gender": "男", "hour_confidence": "高", "longitude": 114.17},
        "bazi_data2": {"year": 2006, "month": 5, "day": 5, "hour": 12, "gender": "女", "hour_confidence": "高", "longitude": 116.4},
        "expected_range": (60, 72),
        "expected_model": "穩定型",
    },
    {
        "description": "測試案例15：極端刑沖 + 無化解（多柱刑害）",
        "bazi_data1": {"year": 1990, "month": 3, "day": 3, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 9, "day": 3, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (25, 40),
        "expected_model": "忌避型",
    },
    {
        "description": "測試案例16：時辰模糊 + 格局特殊（估算時辰）",
        "bazi_data1": {"year": 1990, "month": 6, "day": 16, "hour": 12, "gender": "男", "hour_confidence": "估算"},
        "bazi_data2": {"year": 1991, "month": 7, "day": 17, "hour": 12, "gender": "女", "hour_confidence": "估算"},
        "expected_range": (55, 68),
        "expected_model": "磨合型",
    },
    {
        "description": "測試案例17：中等配對（一般緣分）",
        "bazi_data1": {"year": 1995, "month": 5, "day": 15, "hour": 14, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1996, "month": 8, "day": 20, "hour": 16, "gender": "女", "hour_confidence": "高"},
        "expected_range": (50, 65),
        "expected_model": "磨合型",
    },
    {
        "description": "測試案例18：良好配對（有發展潛力）",
        "bazi_data1": {"year": 1988, "month": 12, "day": 25, "hour": 8, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1989, "month": 6, "day": 18, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (65, 78),
        "expected_model": "穩定型",
    },
    {
        "description": "測試案例19：低分警告（需要謹慎）",
        "bazi_data1": {"year": 1990, "month": 2, "day": 14, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 8, "day": 14, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (40, 55),
        "expected_model": "問題型",
    },
    {
        "description": "測試案例20：邊緣合格（剛好及格）",
        "bazi_data1": {"year": 2000, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 2000, "month": 7, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (55, 70),
        "expected_model": "磨合型",
    }
]

def get_all_test_descriptions() -> List[str]:
    """獲取所有測試案例的描述"""
    return [f"{i+1}. {test['description']}" for i, test in enumerate(ADMIN_TEST_CASES)]

def get_test_case_by_id(test_id: int) -> Dict:
    """根據ID獲取測試案例"""
    if 1 <= test_id <= len(ADMIN_TEST_CASES):
        return ADMIN_TEST_CASES[test_id - 1]
    else:
        return {"error": f"測試案例ID {test_id} 超出範圍"}
# ========1.3 測試案例數據結束 ========#

# ========1.4 AdminService類開始 ========
class AdminService:
    """管理員服務類"""
    
    def __init__(self):
        self._stats_cache = None
        self._cache_time = None
    
    async def run_quick_test(self) -> Dict[str, Any]:
        """運行一鍵快速測試"""
        try:
            components = []
            
            # 測試1: 數據庫連接
            try:
                from bot import get_db_connection, release_db_connection
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT 1")
                result = cur.fetchone()
                release_db_connection(conn)
                components.append({
                    "name": "數據庫連接",
                    "status": "PASS",
                    "message": "數據庫連接正常"
                })
            except Exception as e:
                components.append({
                    "name": "數據庫連接",
                    "status": "FAIL",
                    "message": f"連接失敗: {str(e)}"
                })
            
            # 測試2: 八字計算核心
            try:
                from new_calculator import calculate_bazi
                bazi = calculate_bazi(1990, 1, 1, 12, gender="男")
                if bazi and 'year_pillar' in bazi:
                    components.append({
                        "name": "八字計算",
                        "status": "PASS",
                        "message": "八字計算正常"
                    })
                else:
                    components.append({
                        "name": "八字計算",
                        "status": "FAIL",
                        "message": "計算返回空數據"
                    })
            except Exception as e:
                components.append({
                    "name": "八字計算",
                    "status": "FAIL",
                    "message": f"計算失敗: {str(e)}"
                })
            
            # 測試3: 配對計算
            try:
                from new_calculator import calculate_bazi, calculate_match
                bazi1 = calculate_bazi(1990, 1, 1, 12, gender="男")
                bazi2 = calculate_bazi(1991, 1, 1, 12, gender="女")
                match_result = calculate_match(bazi1, bazi2, "男", "女")
                if match_result and 'score' in match_result:
                    components.append({
                        "name": "配對計算",
                        "status": "PASS",
                        "message": "配對計算正常"
                    })
                else:
                    components.append({
                        "name": "配對計算",
                        "status": "FAIL",
                        "message": "配對返回空數據"
                    })
            except Exception as e:
                components.append({
                    "name": "配對計算",
                    "status": "FAIL",
                    "message": f"配對失敗: {str(e)}"
                })
            
            # 計算總體狀態
            passed = sum(1 for c in components if c['status'] == 'PASS')
            total = len(components)
            status = "健康" if passed == total else "警告"
            
            return {
                "status": status,
                "passed": passed,
                "total": total,
                "failed": total - passed,
                "components": components
            }
            
        except Exception as e:
            logger.error(f"快速測試失敗: {e}", exc_info=True)
            return {
                "status": "故障",
                "error": str(e),
                "passed": 0,
                "total": 0,
                "failed": 0,
                "components": []
            }
    
    def format_quick_test_results(self, results: Dict[str, Any]) -> str:
        """格式化一鍵測試結果"""
        text = f"⚡ 系統健康檢查報告\n"
        text += "=" * 40 + "\n"
        
        text += f"📊 總體狀態: {results.get('status', '未知')}  "
        text += f"✅通過: {results.get('passed', 0)}/{results.get('total', 0)}  "
        text += f"❌失敗: {results.get('failed', 0)}/{results.get('total', 0)}\n\n"
        
        for component in results.get('components', []):
            status_emoji = '✅' if component.get('status') == 'PASS' else '❌'
            text += f"{status_emoji} {component.get('name', '未知')}: {component.get('message', '')}\n"
        
        if results.get('error'):
            text += f"\n❌ 錯誤: {results['error']}\n"
        
        # 添加健康狀態評估
        if results.get('passed', 0) == results.get('total', 0) and results.get('total', 0) > 0:
            text += "\n🏥 系統健康狀態: ✅ 健康"
        elif results.get('passed', 0) >= results.get('total', 0) * 0.7:
            text += "\n🏥 系統健康狀態: ⚠️ 警告（部分組件異常）"
        else:
            text += "\n🏥 系統健康狀態: ❌ 故障（多個組件異常）"
        
        return text
# ========1.4 AdminService類結束 ========

# ========文件信息開始 ========#
"""
文件: admin_service.py
功能: 管理員服務模組，處理管理員專用功能

引用文件: 
- new_calculator.py (八字計算核心)

被引用文件:
- bot.py (主程序)

主要修改：
1. 簡化了測試結果輸出格式
2. 移除了複雜的計算細節提取
3. 簡化了系統統計功能
4. 保持向後兼容性
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
目錄:
1.1 導入模組 - 導入所需庫和模組
1.2 數據類 - 測試結果和系統統計數據類
1.3 測試案例數據 - 20個測試案例定義
1.4 AdminService類 - 管理員服務主類
  2.1 測試功能 - 運行和管理測試案例
  2.2 系統統計 - 獲取和格式化系統統計
"""
# ========目錄結束 ========#

# ========修正紀錄開始 ========#
"""
修正紀錄:
2026-02-05 簡化admin_service：
1. 問題：原admin_service過於複雜，有無效的數據庫測試
   位置：_test_database_rw方法
   後果：創建臨時表可能不必要且可能失敗
   修正：簡化為基礎的測試功能

2. 問題：測試結果輸出格式過於複雜
   位置：_format_single_test_result_pro方法
   後果：輸出難以閱讀
   修正：簡化為清晰的格式

3. 問題：系統統計依賴數據庫連接
   位置：get_system_stats方法
   後果：需要從bot.py導入數據庫連接
   修正：簡化為基礎統計功能

2026-02-04 重新設計評分引擎：
1. 問題：原ProfessionalScoringEngine缺失多個必要方法
   修正：重新設計並實現所有缺失方法

2026-02-03 修正testpair命令：
1. 問題：test_pair_command函數變量作用域衝突
   修正：明確使用bazi1_result和bazi2_result避免衝突
"""
# ========修正紀錄結束 ========#