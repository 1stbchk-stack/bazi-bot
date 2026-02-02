# ========1.1 導入模組開始 ========#
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from contextlib import closing

import psycopg2

# 修正導入語句
from new_calculator import (
    calculate_bazi_pro,
    calculate_match,
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

# ========1.2 數據庫連接開始 ========#
def get_db_connection():
    """獲取數據庫連接"""
    import os
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL 環境變數未設定")
    
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    
    return psycopg2.connect(DATABASE_URL, sslmode='require')
# ========1.2 數據庫連接結束 ========#

# ========1.3 數據類開始 ========#
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
    birth1: str = ""
    birth2: str = ""
    range_str: str = ""
    error: str = ""
    details: List[str] = None
    score_details: str = ""

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
# ========1.3 數據類結束 ========#

# ========1.4 測試案例數據開始 ========#
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
        "expected_model": "混合型",
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
        "expected_model": "供求型",
    },
    {
        "description": "測試案例6：多重刑沖無解（寅巳申三刑）",
        "bazi_data1": {"year": 1992, "month": 6, "day": 6, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1992, "month": 12, "day": 6, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (30, 45),
        "expected_model": "混合型",
    },
    {
        "description": "測試案例7：年齡差距大但結構穩（供求型）",
        "bazi_data1": {"year": 1975, "month": 3, "day": 9, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1995, "month": 4, "day": 11, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (58, 70),
        "expected_model": "供求型",
    },
    {
        "description": "測試案例8：相同八字（伏吟大忌）",
        "bazi_data1": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 1, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (50, 65),
        "expected_model": "混合型",
    },
    {
        "description": "測試案例9：六合解沖（子午沖遇丑合）",
        "bazi_data1": {"year": 1984, "month": 12, "day": 15, "hour": 2, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 6, "day": 20, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (60, 75),
        "expected_model": "平衡型",
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
        "expected_model": "平衡型",
    },
    {
        "description": "測試案例12：高分但為供求型",
        "bazi_data1": {"year": 1980, "month": 3, "day": 15, "hour": 10, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 6, "day": 20, "hour": 14, "gender": "女", "hour_confidence": "高"},
        "expected_range": (68, 78),
        "expected_model": "供求型",
    },
    {
        "description": "測試案例13：邊緣時辰不確定（子時邊界 + 喜用互補）",
        "bazi_data1": {"year": 2000, "month": 1, "day": 1, "hour": 23, "gender": "男", "hour_confidence": "低"},
        "bazi_data2": {"year": 2001, "month": 6, "day": 15, "hour": 0, "gender": "女", "hour_confidence": "低"},
        "expected_range": (55, 70),
        "expected_model": "供求型",
    },
    {
        "description": "測試案例14：經緯度差異 + 能量救應（香港 vs 北京）",
        "bazi_data1": {"year": 2005, "month": 4, "day": 4, "hour": 12, "gender": "男", "hour_confidence": "高", "longitude": 114.17},
        "bazi_data2": {"year": 2006, "month": 5, "day": 5, "hour": 12, "gender": "女", "hour_confidence": "高", "longitude": 116.4},
        "expected_range": (60, 72),
        "expected_model": "供求型",
    },
    {
        "description": "測試案例15：極端刑沖 + 無化解（多柱刑害）",
        "bazi_data1": {"year": 1990, "month": 3, "day": 3, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 9, "day": 3, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (25, 40),
        "expected_model": "混合型",
    },
    {
        "description": "測試案例16：時辰模糊 + 格局特殊（估算時辰）",
        "bazi_data1": {"year": 1990, "month": 6, "day": 16, "hour": 12, "gender": "男", "hour_confidence": "估算"},
        "bazi_data2": {"year": 1991, "month": 7, "day": 17, "hour": 12, "gender": "女", "hour_confidence": "估算"},
        "expected_range": (55, 68),
        "expected_model": "混合型",
    },
    {
        "description": "測試案例17：中等配對（一般緣分）",
        "bazi_data1": {"year": 1995, "month": 5, "day": 15, "hour": 14, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1996, "month": 8, "day": 20, "hour": 16, "gender": "女", "hour_confidence": "高"},
        "expected_range": (50, 65),
        "expected_model": "混合型",
    },
    {
        "description": "測試案例18：良好配對（有發展潛力）",
        "bazi_data1": {"year": 1988, "month": 12, "day": 25, "hour": 8, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1989, "month": 6, "day": 18, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (65, 78),
        "expected_model": "平衡型",
    },
    {
        "description": "測試案例19：低分警告（需要謹慎）",
        "bazi_data1": {"year": 1990, "month": 2, "day": 14, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 1990, "month": 8, "day": 14, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (40, 55),
        "expected_model": "混合型",
    },
    {
        "description": "測試案例20：邊緣合格（剛好及格）",
        "bazi_data1": {"year": 2000, "month": 1, "day": 1, "hour": 12, "gender": "男", "hour_confidence": "高"},
        "bazi_data2": {"year": 2000, "month": 7, "day": 1, "hour": 12, "gender": "女", "hour_confidence": "高"},
        "expected_range": (55, 70),
        "expected_model": "混合型",
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
# ========1.4 測試案例數據結束 ========#

# ========1.5 AdminService類開始 ========#
class AdminService:
    """管理員服務類"""
    
    def __init__(self):
        self._stats_cache = None
        self._cache_time = None
    
    # ========2.1 測試功能開始 ========#
    async def run_admin_tests(self) -> Dict[str, Any]:
        """運行管理員測試案例 - 採用極簡格式"""
        
        results = {
            'total': len(ADMIN_TEST_CASES),
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'success_rate': 0.0,
            'details': [],
            'formatted_results': []  # 極簡格式結果
        }
        
        for i, test_case in enumerate(ADMIN_TEST_CASES, 1):
            test_result = await self._run_single_test(i, test_case)
            results['details'].append(test_result.__dict__)
            
            # 生成極簡格式結果
            formatted_result = self._format_single_test_result(test_result)
            results['formatted_results'].append(formatted_result)
            
            if test_result.status == 'PASS':
                results['passed'] += 1
            elif test_result.status == 'FAIL':
                results['failed'] += 1
            else:
                results['errors'] += 1
        
        if results['total'] > 0:
            results['success_rate'] = (results['passed'] / results['total']) * 100
        
        return results
    
    async def _run_single_test(self, test_id: int, test_case: Dict) -> TestResult:
        """運行單個測試案例 - 強化分數細項提取"""
        try:
            # 提取出生時間信息用於顯示
            bazi_data1 = test_case['bazi_data1']
            bazi_data2 = test_case['bazi_data2']
            
            # 修復：使用正確的日期格式
            birth1 = f"{bazi_data1['gender']}{bazi_data1['year']}{bazi_data1['month']:02d}{bazi_data1['day']:02d}{bazi_data1['hour']:02d}"
            birth2 = f"{bazi_data2['gender']}{bazi_data2['year']}{bazi_data2['month']:02d}{bazi_data2['day']:02d}{bazi_data2['hour']:02d}"
            
            # 修復：確保範圍字符串正確
            range_min, range_max = test_case['expected_range']
            range_str = f"{range_min}-{range_max}"
            
            # 提取參數
            year1, month1, day1, hour1 = bazi_data1['year'], bazi_data1['month'], bazi_data1['day'], bazi_data1['hour']
            gender1 = bazi_data1['gender']
            hour_confidence1 = bazi_data1.get('hour_confidence', '高')
            longitude1 = bazi_data1.get('longitude', DEFAULT_LONGITUDE)
            
            year2, month2, day2, hour2 = bazi_data2['year'], bazi_data2['month'], bazi_data2['day'], bazi_data2['hour']
            gender2 = bazi_data2['gender']
            hour_confidence2 = bazi_data2.get('hour_confidence', '高')
            longitude2 = bazi_data2.get('longitude', DEFAULT_LONGITUDE)
            
            # 計算八字
            bazi1 = calculate_bazi_pro(
                year1, month1, day1, hour1,
                gender=gender1,
                hour_confidence=hour_confidence1,
                longitude=longitude1
            )
            
            bazi2 = calculate_bazi_pro(
                year2, month2, day2, hour2,
                gender=gender2,
                hour_confidence=hour_confidence2,
                longitude=longitude2
            )
            
            if not bazi1 or not bazi2:
                raise ValueError("八字計算失敗")
            
            # 配對計算
            match_result = calculate_match(bazi1, bazi2, gender1, gender2, is_testpair=True)
            
            score = match_result.get('score', 0)
            expected_min, expected_max = test_case['expected_range']
            
            # 檢查結果
            if expected_min <= score <= expected_max:
                status = 'PASS'
            elif abs(score - expected_min) <= 1 or abs(score - expected_max) <= 1:
                status = '邊緣'
            else:
                status = 'FAIL'
            
            # 檢查模型
            model = match_result.get('relationship_model', '')
            expected_model = test_case.get('expected_model', '')
            model_match = model == expected_model
            
            # 提取分數細項（用於極簡格式）
            score_details = self._extract_score_details_correct(match_result)
            
            # 生成詳細信息
            details = [
                f"分數: {score:.1f}分 (預期: {expected_min}-{expected_max}分)",
                f"模型: {model} (預期: {expected_model})",
                f"評級: {match_result.get('rating', '未知')}"
            ]
            
            # 提取八字四柱用於顯示
            pillars1 = f"{bazi1.get('year_pillar', '')}{bazi1.get('month_pillar', '')}{bazi1.get('day_pillar', '')}{bazi1.get('hour_pillar', '')}"
            pillars2 = f"{bazi2.get('year_pillar', '')}{bazi2.get('month_pillar', '')}{bazi2.get('day_pillar', '')}{bazi2.get('hour_pillar', '')}"
            
            return TestResult(
                test_id=test_id,
                description=test_case.get('description', f'測試{test_id}'),
                status=status,
                score=score,
                expected_range=test_case['expected_range'],
                model=model,
                expected_model=expected_model,
                model_match=model_match,
                birth1=pillars1,
                birth2=pillars2,
                range_str=range_str,
                details=details,
                score_details=score_details
            )
            
        except Exception as e:
            logger.error(f"測試案例 {test_id} 運行失敗: {e}", exc_info=True)
            return TestResult(
                test_id=test_id,
                description=test_case.get('description', f'測試{test_id}'),
                status='ERROR',
                score=0,
                expected_range=test_case['expected_range'],
                model='',
                expected_model=test_case.get('expected_model', ''),
                model_match=False,
                error=str(e)
            )
    
    def _extract_score_details_correct(self, match_result: Dict) -> str:
        """從配對結果中正確提取分數細項 - 修復版本"""
        try:
            module_scores = match_result.get('module_scores', {})
            score_details = match_result.get('score_details', {})
            
            # 基準分從score_details獲取，如無則使用50
            base_score = score_details.get('base_score', 50)
            
            # 提取各模組分數
            energy = module_scores.get('energy_rescue', 0)
            structure = module_scores.get('structure_core', 0)
            shensha = module_scores.get('shen_sha_bonus', 0)
            resolution = module_scores.get('resolution_bonus', 0)
            personality = module_scores.get('personality_risk', 0)
            pressure = module_scores.get('pressure_penalty', 0)
            dayun = module_scores.get('dayun_risk', 0)
            
            # 計算正向加分和負向扣分
            positive_bonus = energy + structure + shensha + resolution
            negative_penalty = personality + pressure + dayun
            
            # 構建細項字符串
            details = []
            
            # 基準分
            details.append(f"基準分:{base_score}")
            
            # 正向加分
            if positive_bonus > 0:
                details.append(f"+{positive_bonus:.0f}")
            
            # 負向扣分
            if negative_penalty < 0:
                details.append(f"{negative_penalty:.0f}")
            
            # 詳細模組分數
            mod_details = []
            if energy != 0:
                mod_details.append(f"能量:{energy:+.0f}")
            if structure != 0:
                mod_details.append(f"結構:{structure:+.0f}")
            if shensha != 0:
                mod_details.append(f"神煞:{shensha:+.0f}")
            if resolution != 0:
                mod_details.append(f"化解:{resolution:+.0f}")
            if personality != 0:
                mod_details.append(f"人格:{personality:+.0f}")
            if pressure != 0:
                mod_details.append(f"刑沖:{pressure:+.0f}")
            if dayun != 0:
                mod_details.append(f"大運:{dayun:+.0f}")
            
            if mod_details:
                details.append("(" + " ".join(mod_details) + ")")
            
            return " ".join(details)
            
        except Exception as e:
            logger.error(f"提取分數細項失敗: {e}")
            return "分數細項提取失敗"
    
    def _format_single_test_result(self, test_result: TestResult) -> str:
        """格式化單個測試結果為極簡格式 - 已修復格式化問題"""
        status_emoji = {
            'PASS': '✅',
            'FAIL': '❌',
            'ERROR': '⚠️',
            '邊緣': '⚠️'
        }.get(test_result.status, '❓')
        
        # 提取類型名稱（從description中提取）
        test_type = test_result.description.split("：")[1] if "：" in test_result.description else test_result.description
        
        # 極簡格式：包含兩人四柱、類型、分數和分數細項
        formatted = f"{test_result.birth1} {test_result.birth2},{test_type},分數:{test_result.score:.1f} (預期:{test_result.range_str}) {status_emoji} {test_result.score_details}"
        
        return formatted
    # ========2.1 測試功能結束 ========#
    
    # ========2.2 系統統計開始 ========#
    async def get_system_stats(self) -> SystemStats:
        """獲取系統統計數據"""
        try:
            with closing(get_db_connection()) as conn:
                cur = conn.cursor()
                
                # 基本統計
                cur.execute("SELECT COUNT(*) FROM users")
                total_users = cur.fetchone()[0] or 0
                
                cur.execute("SELECT COUNT(*) FROM matches")
                total_matches = cur.fetchone()[0] or 0
                
                today = datetime.now().date()
                cur.execute("SELECT COUNT(*) FROM matches WHERE DATE(created_at) = %s", (today,))
                today_matches = cur.fetchone()[0] or 0
                
                # 平均分數
                cur.execute("SELECT AVG(score) FROM matches WHERE score > 0")
                avg_score = float(cur.fetchone()[0] or 0)
                
                # 成功率（使用55分及格線）
                cur.execute("""
                    SELECT COUNT(*) FROM matches 
                    WHERE user_a_accepted = 1 AND user_b_accepted = 1 AND score >= %s
                """, (THRESHOLD_CONTACT_ALLOWED,))
                successful_matches = cur.fetchone()[0] or 0
                
                success_rate = 0.0
                if total_matches > 0:
                    success_rate = (successful_matches / total_matches) * 100
                
                # 活躍用戶
                time_24h_ago = datetime.now() - timedelta(hours=24)
                cur.execute("""
                    SELECT COUNT(DISTINCT user_id) FROM ( 
                        SELECT user_a as user_id FROM matches WHERE created_at >= %s
                        UNION
                        SELECT user_b as user_id FROM matches WHERE created_at >= %s
                        UNION
                        SELECT user_id FROM daily_limits WHERE date = %s
                    ) as active_users
                """, (time_24h_ago, time_24h_ago, today))
                active_users_24h = cur.fetchone()[0] or 0
                
                # 模型統計
                model_stats = self._get_model_statistics(cur)
                
                # 高分配對
                top_matches = self._get_top_matches(cur)
                
                return SystemStats(
                    total_users=total_users,
                    total_matches=total_matches,
                    today_matches=today_matches,
                    avg_match_score=round(avg_score, 1),
                    success_rate=round(success_rate, 1),
                    model_stats=model_stats,
                    active_users_24h=active_users_24h,
                    top_matches=top_matches
                )
                
        except Exception as e:
            logger.error(f"獲取統計失敗: {e}")
            return SystemStats(
                total_users=0, total_matches=0, today_matches=0,
                avg_match_score=0.0, success_rate=0.0,
                model_stats=[], active_users_24h=0, top_matches=[],
            )
    
    def _get_model_statistics(self, cursor) -> List[Dict[str, Any]]:
        """獲取模型統計"""
        try:
            cursor.execute("""
                SELECT 
                    (match_details::json->>'relationship_model') as model,
                    COUNT(*) as count,
                    AVG(score) as avg_score
                FROM matches 
                WHERE match_details IS NOT NULL 
                GROUP BY match_details::json->>'relationship_model'
                ORDER BY count DESC
            """)
            
            rows = cursor.fetchall()
            return [
                {'model': row[0] or '未知', 'count': row[1] or 0, 'avg_score': round(float(row[2] or 0), 1)}
                for row in rows[:5]
            ]
            
        except Exception:
            return []
    
    def _get_top_matches(self, cursor) -> List[Dict[str, Any]]:
        """獲取高分配對"""
        try:
            cursor.execute("""
                SELECT 
                    m.score,
                    u1.username as user_a,
                    u2.username as user_b,
                    DATE(m.created_at) as match_date
                FROM matches m
                LEFT JOIN users u1 ON m.user_a = u1.id
                LEFT JOIN users u2 ON m.user_b = u2.id
                WHERE m.score > 0
                ORDER BY m.score DESC
                LIMIT 5
            """)
            
            rows = cursor.fetchall()
            return [
                {
                    'score': round(float(row[0] or 0), 1),
                    'user_a': row[1] or '未知用戶',
                    'user_b': row[2] or '未知用戶',
                    'date': row[3].strftime('%Y-%m-%d') if row[3] else '未知'
                }
                for row in rows
            ]
            
        except Exception:
            return []
    # ========2.2 系統統計結束 ========#
    
    # ========2.3 一鍵快速測試開始 ========#
    async def run_quick_test(self) -> Dict[str, Any]:
        """運行一鍵快速測試（系統健康檢查）"""
        results = {
            'components': [],
            'total': 0,
            'passed': 0,
            'failed': 0,
            'status': '進行中'
        }
        
        try:
            # 測試數據庫
            db_test = await self._test_database()
            results['components'].append(db_test)
            
            # 測試八字計算
            bazi_test = await self._test_bazi()
            results['components'].append(bazi_test)
            
            # 測試配對計算
            match_test = await self._test_match()
            results['components'].append(match_test)
            
            # 測試核心功能
            core_test = await self._test_core_functionality()
            results['components'].append(core_test)
            
            # 測試數據庫讀寫
            db_rw_test = await self._test_database_rw()
            results['components'].append(db_rw_test)
            
            # 統計結果
            for component in results['components']:
                results['total'] += 1
                if component.get('status') == 'PASS':
                    results['passed'] += 1
                else:
                    results['failed'] += 1
            
            results['status'] = '完成'
            
        except Exception as e:
            results['status'] = '失敗'
            results['error'] = str(e)
        
        return results
    
    async def _test_database(self) -> Dict[str, Any]:
        """測試數據庫連接"""
        try:
            with closing(get_db_connection()) as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                return {'name': '數據庫連接', 'status': 'PASS', 'message': '連接正常'}
        except Exception as e:
            return {'name': '數據庫連接', 'status': 'ERROR', 'message': f'連接失敗: {e}'}
    
    async def _test_database_rw(self) -> Dict[str, Any]:
        """測試數據庫讀寫"""
        try:
            import hashlib
            import time
            
            with closing(get_db_connection()) as conn:
                cur = conn.cursor()
                
                # 創建測試表
                test_table = f"test_{int(time.time())}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
                cur.execute(f"CREATE TEMP TABLE {test_table} (id SERIAL PRIMARY KEY, test_value TEXT)")
                
                # 寫入測試數據
                cur.execute(f"INSERT INTO {test_table} (test_value) VALUES (%s)", ('test_data',))
                
                # 讀取測試數據
                cur.execute(f"SELECT test_value FROM {test_table}")
                result = cur.fetchone()
                
                # 清理
                cur.execute(f"DROP TABLE {test_table}")
                conn.commit()
                
                if result and result[0] == 'test_data':
                    return {'name': '數據庫讀寫', 'status': 'PASS', 'message': '讀寫正常'}
                else:
                    return {'name': '數據庫讀寫', 'status': 'FAIL', 'message': '讀寫數據不一致'}
                    
        except Exception as e:
            return {'name': '數據庫讀寫', 'status': 'ERROR', 'message': f'讀寫測試失敗: {e}'}
    
    async def _test_bazi(self) -> Dict[str, Any]:
        """測試八字計算"""
        try:
            # 使用 calculate_bazi_pro 而不是 BaziCalculator.calculate
            bazi = calculate_bazi_pro(1990, 1, 1, 12, '男', hour_confidence='高')
            if bazi:
                pillars = f"{bazi.get('year_pillar', '')} {bazi.get('month_pillar', '')} {bazi.get('day_pillar', '')} {bazi.get('hour_pillar', '')}"
                return {'name': '八字計算', 'status': 'PASS', 'message': f'計算正常: {pillars}'}
            else:
                return {'name': '八字計算', 'status': 'FAIL', 'message': '返回空數據'}
        except Exception as e:
            return {'name': '八字計算', 'status': 'ERROR', 'message': f'計算失敗: {e}'}
    
    async def _test_match(self) -> Dict[str, Any]:
        """測試配對計算"""
        try:
            bazi1 = calculate_bazi_pro(1990, 1, 1, 12, '男', hour_confidence='高')
            bazi2 = calculate_bazi_pro(1991, 2, 2, 13, '女', hour_confidence='高')
            match_result = calculate_match(bazi1, bazi2, '男', '女', is_testpair=True)
            
            score = match_result.get('score')
            if score is not None:
                rating = match_result.get('rating', '未知')
                return {'name': '配對計算', 'status': 'PASS', 'message': f'分數: {score:.1f}, 評級: {rating}'}
            else:
                return {'name': '配對計算', 'status': 'FAIL', 'message': '返回空數據'}
        except Exception as e:
            return {'name': '配對計算', 'status': 'ERROR', 'message': f'計算失敗: {e}'}
    
    async def _test_core_functionality(self) -> Dict[str, Any]:
        """測試核心功能"""
        try:
            bazi = calculate_bazi_pro(1990, 1, 1, 12, '男', hour_confidence='高')
            bazi2 = calculate_bazi_pro(1991, 2, 2, 13, '女', hour_confidence='高')
            
            # 測試格式化功能
            formatted_personal = BaziFormatters.format_personal_data(bazi, "測試用戶")
            match_result = calculate_match(bazi, bazi2, '男', '女', is_testpair=True)
            formatted_match = BaziFormatters.format_match_result(match_result, bazi, bazi2)
            
            features = []
            if formatted_personal:
                features.append("個人資料格式化")
            if formatted_match:
                features.append("配對結果格式化")
            if match_result.get('relationship_model'):
                features.append("關係模型分析")
            if match_result.get('module_scores'):
                features.append("模組評分系統")
            
            return {
                'name': '核心功能', 
                'status': 'PASS', 
                'message': f'正常: {", ".join(features)}'
            }
        except Exception as e:
            return {'name': '核心功能', 'status': 'ERROR', 'message': f'測試失敗: {e}'}
    # ========2.3 一鍵快速測試結束 ========#
    
    # ========2.4 格式化功能開始 ========#
    def format_test_results(self, results: Dict[str, Any]) -> str:
        """格式化測試結果 - 極簡格式"""
        text = f"🧪 管理員測試報告 ({results['total']}組測試案例)\n"
        text += f"📈 總體統計: 通過 {results['passed']}/{results['total']} (成功率: {results['success_rate']:.1f}%)\n"
        
        # 詳細結果（極簡格式）
        for formatted_result in results['formatted_results']:
            text += "#" + formatted_result + "\n"
        
        # 總結
        text += f"\n🎯 測試完成: {results['passed']}通過 {results['failed']}失敗 {results['errors']}錯誤"
        text += f" 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return text
    
    def format_system_stats(self, stats: SystemStats) -> str:
        """格式化系統統計"""
        text = f"📈 系統統計報告\n"
        
        text += f"👥 用戶統計: 總用戶數: {stats.total_users}  24小時活躍: {stats.active_users_24h}\n"
        text += f"💖 配對統計: 總配對數: {stats.total_matches}  今日配對: {stats.today_matches}  平均分數: {stats.avg_match_score:.1f}分  成功率: {stats.success_rate:.1f}%\n"
        
        if stats.model_stats:
            text += f"🎭 關係模型: "
            model_texts = []
            for model_stat in stats.model_stats:
                model_texts.append(f"{model_stat['model']}: {model_stat['count']}次({model_stat['avg_score']:.1f}分)")
            text += " ".join(model_texts) + "\n"
        
        if stats.top_matches:
            text += f"🏆 高分配對: "
            top_texts = []
            for match in stats.top_matches[:3]:
                top_texts.append(f"{match['user_a']}↔{match['user_b']}:{match['score']:.1f}分")
            text += " ".join(top_texts) + "\n"
        
        # 修正日期格式化：%Y-%m-d → %Y-%m-%d
        text += f"📅 統計時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return text
    
    def format_quick_test_results(self, results: Dict[str, Any]) -> str:
        """格式化一鍵測試結果"""
        text = f"⚡ 系統健康檢查報告\n"
        
        text += f"📊 總體狀態: {results.get('status', '未知')}  ✅通過: {results.get('passed', 0)}/{results.get('total', 0)}  ❌失敗: {results.get('failed', 0)}/{results.get('total', 0)}\n"
        
        for component in results.get('components', []):
            status_emoji = '✅' if component.get('status') == 'PASS' else '❌'
            text += f"{status_emoji}{component.get('name', '未知')}: {component.get('message', '')}\n"
        
        if results.get('error'):
            text += f"❌錯誤: {results['error']}\n"
        
        # 添加健康狀態評估
        if results.get('passed', 0) == results.get('total', 0) and results.get('total', 0) > 0:
            text += "🏥系統健康狀態: ✅健康"
        elif results.get('passed', 0) >= results.get('total', 0) * 0.7:
            text += "🏥系統健康狀態: ⚠️警告(部分組件異常)"
        else:
            text += "🏥系統健康狀態: ❌故障(多個組件異常)"
        
        return text
    # ========2.4 格式化功能結束 ========#
# ========1.5 AdminService類結束 ========#

# ========文件信息開始 ========#
"""
文件: admin_service.py
功能: 管理員服務模組，處理管理員專用功能

引用文件: 
- new_calculator.py (八字計算核心)

被引用文件:
- bot.py (主程序)

主要修改：
1. 修正導入語句：使用 calculate_bazi_pro 和 calculate_match
2. 修正分數細項提取邏輯：從score_details獲取基準分
3. 統一常量引用：使用 THRESHOLD_CONTACT_ALLOWED 代替硬編碼值
4. 修正測試案例信心度參數：使用"高/中/低/估算"格式
5. 修正測試方法中的八字計算調用：使用 calculate_bazi_pro
6. 修復日期格式化錯誤：%Y-%m-d 修正為 %Y-%m-%d

修改記錄：
2026-02-03 第五次修正：
1. 完全重寫 _run_single_test 方法：使用 calculate_bazi_pro 函數
2. 修正測試方法：_test_bazi, _test_match, _test_core_functionality 都使用 calculate_bazi_pro
3. 修正導入語句：從 new_calculator 導入 calculate_bazi_pro 和 calculate_match
4. 移除錯誤的 BaziCalculator 調用
5. 保持所有測試功能正常運作，與新的評分系統兼容

2026-02-03 第四次修正：
1. 修正導入語句：使用 ProfessionalConfig as Config
2. 修正分數細項提取邏輯：從score_details獲取基準分，而不是debug_info
3. 修正測試案例信心度參數：使用"高/中/低/估算"格式，符合new_calculator.py標準
4. 統一常量引用：使用 THRESHOLD_CONTACT_ALLOWED 代替硬編碼的60分
5. 修正日期格式化錯誤：%Y-%m-d 修正為 %Y-%m-%d
6. 保持所有測試功能正常運作，與新的評分系統兼容

累積修正：
- 更新常數引用以匹配new_calculator.py的修改
- 調整分數細項提取，基準分從score_details獲取
- 修復日期格式化錯誤
- 完全修正八字計算函數調用方式
- 保持所有測試功能正常運作
- 符合繁體中文要求
- 無版本號標示
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
目錄:
1.1 導入模組 - 導入所需庫和模組
1.2 數據庫連接 - 獲取數據庫連接
1.3 數據類 - TestResult和SystemStats數據類定義
1.4 測試案例數據 - ADMIN_TEST_CASES和輔助函數
1.5 AdminService類 - 主服務類
  2.1 測試功能 - 運行管理員測試案例（極簡格式）
  2.2 系統統計 - 獲取系統統計數據
  2.3 一鍵快速測試 - 系統健康檢查
  2.4 格式化功能 - 各種結果的格式化輸出
"""
# ========目錄結束 ========#