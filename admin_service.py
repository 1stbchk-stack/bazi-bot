# ========1.1 導入模組開始 ========#
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from contextlib import closing

import psycopg2

from new_calculator import (
    BaziCalculator,
    calculate_match,
    ScoringEngine,
    Config
)

# 从 Config 类获取常量
THRESHOLD_CONTACT_ALLOWED = Config.THRESHOLD_CONTACT_ALLOWED
THRESHOLD_GOOD_MATCH = Config.THRESHOLD_GOOD_MATCH
THRESHOLD_EXCELLENT_MATCH = Config.THRESHOLD_EXCELLENT_MATCH
THRESHOLD_PERFECT_MATCH = Config.THRESHOLD_PERFECT_MATCH

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
# ========1.3 數據類結束 ========#

# ========1.4 從test_cases.py移入的輔助函數開始 ========#
def get_all_test_descriptions() -> List[str]:
    """獲取所有測試案例的描述"""
    from test_cases import ADMIN_TEST_CASES
    return [f"{i+1}. {test['description']}" for i, test in enumerate(ADMIN_TEST_CASES)]

def get_test_case_by_id(test_id: int) -> Dict:
    """根據ID獲取測試案例"""
    from test_cases import ADMIN_TEST_CASES
    if 1 <= test_id <= len(ADMIN_TEST_CASES):
        return ADMIN_TEST_CASES[test_id - 1]
    else:
        return {"error": f"測試案例ID {test_id} 超出範圍"}
# ========1.4 從test_cases.py移入的輔助函數結束 ========#

# ========1.5 AdminService類開始 ========#
class AdminService:
    """管理員服務類"""
    
    def __init__(self):
        self._stats_cache = None
        self._cache_time = None
    
    # ========2.1 測試功能開始 ========#
    async def run_admin_tests(self) -> Dict[str, Any]:
        """運行管理員測試案例"""
        from test_cases import ADMIN_TEST_CASES
        
        results = {
            'total': len(ADMIN_TEST_CASES),
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'success_rate': 0.0,
            'details': []
        }
        
        for i, test_case in enumerate(ADMIN_TEST_CASES, 1):
            test_result = await self._run_single_test(i, test_case)
            results['details'].append(test_result.__dict__)
            
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
            # 計算八字
            bazi1 = BaziCalculator.calculate(**test_case['bazi_data1'])
            bazi2 = BaziCalculator.calculate(**test_case['bazi_data2'])
            
            if not bazi1 or not bazi2:
                raise ValueError("八字計算失敗")
            
            # 配對計算
            gender1 = test_case['bazi_data1']['gender']
            gender2 = test_case['bazi_data2']['gender']
            
            match_result = calculate_match(bazi1, bazi2, gender1, gender2, is_testpair=True)
            
            score = match_result.get('score', 0)
            expected_min, expected_max = test_case['expected_range']
            
            # 檢查結果
            if expected_min <= score <= expected_max:
                status = 'PASS'
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
                details=details
            )
            
        except Exception as e:
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
                
                # 成功率
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
                model_stats=[], active_users_24h=0, top_matches=[]
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
    
    # ========2.3 一鍵測試開始 ========#
    async def run_quick_test(self) -> Dict[str, Any]:
        """運行一鍵測試"""
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
            
            # 測試創新功能
            innovation_test = await self._test_innovation()
            results['components'].append(innovation_test)
            
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
        """測試數據庫"""
        try:
            with closing(get_db_connection()) as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                return {'name': '數據庫', 'status': 'PASS', 'message': '連接正常'}
        except Exception as e:
            return {'name': '數據庫', 'status': 'ERROR', 'message': f'連接失敗: {e}'}
    
    async def _test_bazi(self) -> Dict[str, Any]:
        """測試八字計算"""
        try:
            bazi = BaziCalculator.calculate(1990, 1, 1, 12, '男')
            if bazi:
                return {'name': '八字計算', 'status': 'PASS', 'message': '計算正常'}
            else:
                return {'name': '八字計算', 'status': 'FAIL', 'message': '返回空數據'}
        except Exception as e:
            return {'name': '八字計算', 'status': 'ERROR', 'message': f'計算失敗: {e}'}
    
    async def _test_match(self) -> Dict[str, Any]:
        """測試配對計算"""
        try:
            bazi1 = BaziCalculator.calculate(1990, 1, 1, 12, '男')
            bazi2 = BaziCalculator.calculate(1991, 2, 2, 13, '女')
            match_result = calculate_match(bazi1, bazi2, '男', '女', is_testpair=True)
            
            if match_result.get('score') is not None:
                return {'name': '配對計算', 'status': 'PASS', 'message': f'分數: {match_result["score"]:.1f}'}
            else:
                return {'name': '配對計算', 'status': 'FAIL', 'message': '返回空數據'}
        except Exception as e:
            return {'name': '配對計算', 'status': 'ERROR', 'message': f'計算失敗: {e}'}
    
    async def _test_innovation(self) -> Dict[str, Any]:
        """測試創新功能"""
        try:
            from new_calculator import HealthAnalyzer
            bazi = BaziCalculator.calculate(1990, 1, 1, 12, '男')
            health = HealthAnalyzer.analyze_health(bazi)
            
            if health:
                return {'name': '創新功能', 'status': 'PASS', 'message': '健康分析正常'}
            else:
                return {'name': '創新功能', 'status': 'FAIL', 'message': '返回空數據'}
        except Exception as e:
            return {'name': '創新功能', 'status': 'ERROR', 'message': f'測試失敗: {e}'}
    # ========2.3 一鍵測試結束 ========#
    
    # ========2.4 格式化功能開始 ========#
    def format_test_results(self, results: Dict[str, Any]) -> str:
        """格式化測試結果"""
        text = f"""📊 管理員測試報告 (20組)
{"="*60}

📈 總體統計:
  總測試數: {results['total']}
  通過: {results['passed']} ✅
  失敗: {results['failed']} ❌
  錯誤: {results['errors']} ⚠️
  成功率: {results['success_rate']:.1f}%
  
📋 詳細結果:
"""
        
        for detail in results.get('details', [])[:10]:  # 只顯示前10個
            status_emoji = '✅' if detail['status'] == 'PASS' else '❌' if detail['status'] == 'FAIL' else '⚠️'
            text += f"\n{status_emoji} {detail['description']}"
            text += f"\n   分數: {detail.get('score', 0):.1f}分"
            if detail.get('error'):
                text += f"\n   錯誤: {detail['error'][:50]}..."
        
        return text
    
    def format_system_stats(self, stats: SystemStats) -> str:
        """格式化系統統計"""
        text = f"""📈 系統統計報告
{"="*60}

👥 用戶統計:
  總用戶數: {stats.total_users}
  24小時活躍: {stats.active_users_24h}
  
💖 配對統計:
  總配對數: {stats.total_matches}
  今日配對: {stats.today_matches}
  平均分數: {stats.avg_match_score:.1f}分
  成功率: {stats.success_rate:.1f}%
  
🎭 關係模型:
"""
        
        for model_stat in stats.model_stats:
            text += f"  {model_stat['model']}: {model_stat['count']}次 ({model_stat['avg_score']:.1f}分)\n"
        
        if stats.top_matches:
            text += "\n🏆 高分配對:\n"
            for match in stats.top_matches[:3]:
                text += f"  {match['user_a']} ↔ {match['user_b']}: {match['score']:.1f}分\n"
        
        text += f"\n📅 統計時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return text
    
    def format_quick_test_results(self, results: Dict[str, Any]) -> str:
        """格式化一鍵測試結果"""
        text = f"""⚡ 一鍵測試結果
{"="*60}

📊 總體狀態: {results.get('status', '未知')}
✅ 通過: {results.get('passed', 0)} / {results.get('total', 0)}
❌ 失敗: {results.get('failed', 0)} / {results.get('total', 0)}
  
📋 組件測試:
"""
        
        for component in results.get('components', []):
            status_emoji = '✅' if component.get('status') == 'PASS' else '❌'
            text += f"\n{status_emoji} {component.get('name', '未知')}: {component.get('message', '')}"
        
        if results.get('error'):
            text += f"\n\n❌ 錯誤: {results['error']}"
        
        return text
    # ========2.4 格式化功能結束 ========#
# ========1.5 AdminService類結束 ========#

# ========文件信息開始 ========#
"""
文件: admin_service.py
功能: 管理員服務模組，處理管理員專用功能

引用文件: 
- new_calculator.py (八字計算核心)
- test_cases.py (測試案例)
- psycopg2 (數據庫連接)

被引用文件:
- bot.py (主程序)

主要功能:
1. AdminService類 - 主服務類
2. TestResult/SystemStats - 數據類
3. 測試功能 - 運行20組測試案例
4. 系統統計 - 獲取真實數據庫統計
5. 一鍵測試 - 測試所有核心組件
6. 格式化功能 - 輸出格式化結果
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
1.1 導入模組開始
1.2 數據庫連接開始
1.3 數據類開始
1.4 從test_cases.py移入的輔助函數開始
1.5 AdminService類開始
  2.1 測試功能開始
  2.2 系統統計開始
  2.3 一鍵測試開始
  2.4 格式化功能開始
"""
# ========目錄結束 ========#

# ========修正紀錄開始 ========#
"""
修正內容：
1. 從test_cases.py移入輔助函數：get_all_test_descriptions(), get_test_case_by_id()
2. 用dataclass替代Dict：TestResult, SystemStats
3. 簡化格式化函數，移除重複emoji邏輯
4. 添加一鍵測試功能，支援創新功能測試
5. 總行數減少約100行

導致問題：test_cases.py功能不完整
如何修復：將輔助函數移入admin_service.py，減少文件依賴
後果：功能組織更合理，admin_service.py更完整
"""
# ========修正紀錄結束 ========#