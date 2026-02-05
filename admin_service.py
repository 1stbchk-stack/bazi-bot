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

# ========1.4 AdminService類開始 ========#
class AdminService:
    """管理員服務類"""
    
    def __init__(self):
        self._stats_cache = None
        self._cache_time = None
    
    # ========2.1 測試功能開始 ========#
    async def run_admin_tests(self) -> Dict[str, Any]:
        """運行管理員測試案例"""
        
        results = {
            'total': len(ADMIN_TEST_CASES),
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'success_rate': 0.0,
            'details': [],
            'formatted_results': []
        }
        
        for i, test_case in enumerate(ADMIN_TEST_CASES, 1):
            test_result = await self._run_single_test(i, test_case)
            results['details'].append(test_result.__dict__)
            
            # 生成格式結果
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
        """運行單個測試案例"""
        try:
            # 提取出生時間信息
            bazi_data1 = test_case['bazi_data1']
            bazi_data2 = test_case['bazi_data2']
            
            # 提取參數
            year1, month1, day1, hour1 = bazi_data1['year'], bazi_data1['month'], bazi_data1['day'], bazi_data1['hour']
            gender1 = bazi_data1['gender']
            hour_confidence1 = bazi_data1.get('hour_confidence', '高')
            longitude1 = bazi_data1.get('longitude', DEFAULT_LONGITUDE)
            
            year2, month2, day2, hour2 = bazi_data2['year'], bazi_data2['month'], bazi_data2['day'], bazi_data2['hour']
            gender2 = bazi_data2['gender']
            hour_confidence2 = bazi_data2.get('hour_confidence', '高')
            longitude2 = bazi_data2.get('longitude', DEFAULT_LONGITUDE)
            
            logger.info(f"測試案例 {test_id}: 計算八字1 - {year1}/{month1}/{day1} {hour1}:00")
            logger.info(f"測試案例 {test_id}: 計算八字2 - {year2}/{month2}/{day2} {hour2}:00")
            
            # 使用對外接口 calculate_bazi
            try:
                bazi1 = calculate_bazi(
                    year=year1,
                    month=month1,
                    day=day1,
                    hour=hour1,
                    gender=gender1,
                    hour_confidence=hour_confidence1,
                    longitude=longitude1
                )
            except Exception as e:
                logger.error(f"計算八字1失敗: {e}", exc_info=True)
                raise ValueError(f"計算八字1失敗: {str(e)}")
            
            try:
                bazi2 = calculate_bazi(
                    year=year2,
                    month=month2,
                    day=day2,
                    hour=hour2,
                    gender=gender2,
                    hour_confidence=hour_confidence2,
                    longitude=longitude2
                )
            except Exception as e:
                logger.error(f"計算八字2失敗: {e}", exc_info=True)
                raise ValueError(f"計算八字2失敗: {str(e)}")
            
            if not bazi1:
                raise ValueError("八字1計算返回空數據")
            if not bazi2:
                raise ValueError("八字2計算返回空數據")
            
            # 獲取四柱用於顯示
            pillars1 = f"{bazi1.get('year_pillar', '')}{bazi1.get('month_pillar', '')}{bazi1.get('day_pillar', '')}{bazi1.get('hour_pillar', '')}"
            pillars2 = f"{bazi2.get('year_pillar', '')}{bazi2.get('month_pillar', '')}{bazi2.get('day_pillar', '')}{bazi2.get('hour_pillar', '')}"
            
            logger.info(f"測試案例 {test_id}: 八字1計算完成 - {pillars1}")
            logger.info(f"測試案例 {test_id}: 八字2計算完成 - {pillars2}")
            
            # 配對計算 - 使用對外接口 calculate_match
            try:
                match_result = calculate_match(bazi1, bazi2, gender1, gender2, is_testpair=True)
            except Exception as e:
                logger.error(f"配對計算失敗: {e}", exc_info=True)
                raise ValueError(f"配對計算失敗: {str(e)}")
            
            score = match_result.get('score', 0)
            expected_min, expected_max = test_case['expected_range']
            
            logger.info(f"測試案例 {test_id}: 配對分數: {score:.1f}分 (預期: {expected_min}-{expected_max}分)")
            
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
            
            # 生成詳細信息
            details = [
                f"分數: {score:.1f}分 (預期: {expected_min}-{expected_max}分)",
                f"模型: {model} (預期: {expected_model})",
                f"評級: {match_result.get('rating', '未知')}"
            ]
            
            return TestResult(
                test_id=test_id,
                description=test_case.get('description', f'測試{test_id}'),
                status=status,
                score=score,
                expected_range=test_case['expected_range'],
                model=model,
                expected_model=expected_model,
                model_match=model_match,
                pillars1=pillars1,
                pillars2=pillars2,
                range_str=f"{expected_min}-{expected_max}",
                details=details
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
                error=str(e),
                range_str=f"{test_case['expected_range'][0]}-{test_case['expected_range'][1]}"
            )
    
    def _format_single_test_result(self, test_result: TestResult) -> str:
        """格式化單個測試結果"""
        status_emoji = {
            'PASS': '✅',
            'FAIL': '❌',
            'ERROR': '⚠️',
            '邊緣': '⚠️'
        }.get(test_result.status, '❓')
        
        # 提取類型名稱
        if "：" in test_result.description:
            test_type = test_result.description.split("：")[1]
        else:
            test_type = test_result.description
        
        # 簡化格式
        formatted = f"{test_result.test_id}. {test_result.pillars1} ↔ {test_result.pillars2}, {test_type}, 分數:{test_result.score:.1f} (預期:{test_result.range_str}) {status_emoji}"
        
        return formatted
    
    def format_test_results_pro(self, results: Dict[str, Any]) -> str:
        """格式化測試結果"""
        text = f"🧪 管理員測試報告 ({results['total']}組測試案例)\n"
        text += f"📈 總體統計: 通過 {results['passed']}/{results['total']} (成功率: {results['success_rate']:.1f}%)\n\n"
        
        # 詳細結果
        for formatted_result in results['formatted_results']:
            text += formatted_result + "\n"
        
        # 總結
        text += f"\n🎯 測試完成: {results['passed']}通過 {results['failed']}失敗 {results['errors']}錯誤"
        text += f" 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return text
    # ========2.1 測試功能結束 ========#
    
    # ========2.2 系統統計開始 ========#
    async def get_system_stats(self) -> SystemStats:
        """獲取系統統計數據"""
        try:
            # 由於bot.py中已經有數據庫連接，這裡簡化處理
            # 實際使用時需要從bot.py導入數據庫連接
            return SystemStats(
                total_users=0,
                total_matches=0,
                today_matches=0,
                avg_match_score=0.0,
                success_rate=0.0,
                model_stats=[],
                active_users_24h=0,
                top_matches=[]
            )
                
        except Exception as e:
            logger.error(f"獲取統計失敗: {e}")
            return SystemStats(
                total_users=0, total_matches=0, today_matches=0,
                avg_match_score=0.0, success_rate=0.0,
                model_stats=[], active_users_24h=0, top_matches=[],
            )
    
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
        
        text += f"📅 統計時間: {datetime.now().strftime('%Y-%m-d %H:%M')}"
        
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
    # ========2.2 系統統計結束 ========#
    
    # ========2.3 快速測試功能開始 ========#
    async def run_quick_test(self) -> Dict[str, Any]:
        """運行快速系統健康檢查"""
        components = []
        
        # 測試1：檢查八字計算
        try:
            bazi = calculate_bazi(1990, 1, 1, 12, gender="男")
            if bazi and bazi.get('year_pillar'):
                components.append({
                    "name": "八字計算",
                    "status": "PASS",
                    "message": "八字計算功能正常"
                })
            else:
                components.append({
                    "name": "八字計算",
                    "status": "FAIL",
                    "message": "八字計算返回空數據"
                })
        except Exception as e:
            components.append({
                "name": "八字計算",
                "status": "FAIL",
                "message": f"八字計算失敗: {str(e)}"
            })
        
        # 測試2：檢查配對計算
        try:
            bazi1 = calculate_bazi(1990, 1, 1, 12, gender="男")
            bazi2 = calculate_bazi(1991, 2, 2, 13, gender="女")
            match_result = calculate_match(bazi1, bazi2, "男", "女")
            if match_result and 'score' in match_result:
                components.append({
                    "name": "配對計算",
                    "status": "PASS",
                    "message": f"配對計算正常，分數: {match_result.get('score', 0):.1f}"
                })
            else:
                components.append({
                    "name": "配對計算",
                    "status": "FAIL",
                    "message": "配對計算返回空數據"
                })
        except Exception as e:
            components.append({
                "name": "配對計算",
                "status": "FAIL",
                "message": f"配對計算失敗: {str(e)}"
            })
        
        # 測試3：檢查測試案例
        try:
            from admin_service import ADMIN_TEST_CASES
            if ADMIN_TEST_CASES and len(ADMIN_TEST_CASES) > 0:
                components.append({
                    "name": "測試案例",
                    "status": "PASS",
                    "message": f"載入{len(ADMIN_TEST_CASES)}個測試案例"
                })
            else:
                components.append({
                    "name": "測試案例",
                    "status": "FAIL",
                    "message": "測試案例載入失敗"
                })
        except Exception as e:
            components.append({
                "name": "測試案例",
                "status": "FAIL",
                "message": f"測試案例載入失敗: {str(e)}"
            })
        
        # 計算總體狀態
        passed = sum(1 for c in components if c["status"] == "PASS")
        total = len(components)
        
        # 確定狀態
        if passed == total and total > 0:
            status = "健康"
        elif passed >= total * 0.7:
            status = "警告"
        else:
            status = "故障"
        
        return {
            "status": status,
            "passed": passed,
            "total": total,
            "failed": total - passed,
            "components": components
        }
    # ========2.3 快速測試功能結束 ========#
# ========1.4 AdminService類結束 ========#

# ========文件信息開始 ========#
"""
文件: admin_service.py
功能: 管理員服務模組，處理管理員專用功能

引用文件: 
- new_calculator.py (八字計算核心)

被引用文件:
- bot.py (主程序)

主要修正:
1. 添加了缺失的run_quick_test方法
2. 修正了測試結果顯示格式
3. 保持了向後兼容性

版本: 修正版
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
  2.3 快速測試功能 - 系統健康檢查
"""
# ========目錄結束 ========#

# ========修正紀錄開始 ========#
"""
修正紀錄:
2026-02-05 修正admin_service問題：
1. 問題：缺少run_quick_test方法
   位置：AdminService類
   後果：/quicktest命令無法運行
   修正：添加run_quick_test方法，實現基本的系統健康檢查

2. 問題：測試結果顯示格式問題
   位置：_format_single_test_result方法
   後果：顯示格式不符合要求
   修正：簡化測試結果顯示格式

2026-02-04 重新設計評分引擎：
1. 問題：原ProfessionalScoringEngine缺失多個必要方法
   修正：重新設計並實現所有缺失方法

2026-02-03 修正testpair命令：
1. 問題：test_pair_command函數變量作用域衝突
   修正：明確使用bazi1_result和bazi2_result避免衝突
"""
# ========修正紀錄結束 ========#