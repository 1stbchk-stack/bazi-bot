#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理員服務模組 - 更新版，兼容new_calculator.py
處理管理員專用功能
最後更新: 2026年2月1日
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from contextlib import closing

import psycopg2

# ========== 1.1 導入模組開始 ==========
# 導入新的計算核心
from new_calculator import (
    BaziCalculator,
    calculate_match,
    BaziCalculatorError,
    ScoringEngineError,
    Config,
    THRESHOLD_CONTACT_ALLOWED
)

# 導入測試案例
from test_cases import ADMIN_TEST_CASES

logger = logging.getLogger(__name__)
# ========== 1.1 導入模組結束 ==========

# ========== 1.2 數據庫連接開始 ==========
def get_db_connection():
    """獲取數據庫連接"""
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL 環境變數未設定")
    
    # 修復 Railway PostgreSQL URL 格式
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    
    return psycopg2.connect(DATABASE_URL, sslmode='require')
# ========== 1.2 數據庫連接結束 ==========

# ========== 1.3 數據類開始 ==========
@dataclass
class TestResult:
    """測試結果數據類"""
    test_id: int
    description: str
    status: str  # 'PASS', 'FAIL', 'ERROR'
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
# ========== 1.3 數據類結束 ==========

# ========== 1.4 AdminService類開始 ==========
class AdminService:
    """管理員服務類 - 更新版，使用真實數據庫"""
    
    def __init__(self):
        """初始化管理員服務"""
        # 初始化統計緩存
        self._stats_cache = None
        self._cache_time = None
        
    # ========== 2.1 測試功能開始 ==========
    async def run_admin_tests(self) -> Dict[str, Any]:
        """
        運行管理員測試案例（20組）
        
        Returns:
            測試結果字典
        """
        logger.info(f"開始運行管理員測試案例，共{len(ADMIN_TEST_CASES)}組")
        
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
        
        # 計算成功率
        if results['total'] > 0:
            results['success_rate'] = (results['passed'] / results['total']) * 100
        
        logger.info(f"測試完成: {results['passed']}通過, {results['failed']}失敗, {results['errors']}錯誤")
        return results
    
    async def _run_single_test(self, test_id: int, test_case: Dict) -> TestResult:
        """運行單個測試案例"""
        try:
            logger.info(f"運行測試 {test_id}: {test_case.get('description', '未知')}")
            
            # 1. 獲取八字數據
            bazi1 = self._get_bazi_data(test_case['bazi_data1'])
            bazi2 = self._get_bazi_data(test_case['bazi_data2'])
            
            if not bazi1 or not bazi2:
                raise ValueError("八字計算失敗")
            
            # 2. 計算八字配對
            gender1 = test_case['bazi_data1']['gender']
            gender2 = test_case['bazi_data2']['gender']
            
            match_result = calculate_match(
                bazi1, bazi2, gender1, gender2, is_testpair=True
            )
            
            score = match_result.get('score', 0)
            expected_min, expected_max = test_case['expected_range']
            
            # 3. 檢查分數是否在預期範圍內
            if expected_min <= score <= expected_max:
                status = 'PASS'
            else:
                status = 'FAIL'
            
            # 4. 檢查關係模型
            model = match_result.get('relationship_model', '')
            expected_model = test_case.get('expected_model', '')
            model_match = model == expected_model
            
            # 5. 收集詳細信息
            details = [
                f"分數: {score:.1f}分 (預期: {expected_min}-{expected_max}分)",
                f"模型: {model} (預期: {expected_model}, 匹配: {model_match})",
                f"A: {bazi1.get('year_pillar', '')} {bazi1.get('month_pillar', '')} "
                f"{bazi1.get('day_pillar', '')} {bazi1.get('hour_pillar', '')}",
                f"B: {bazi2.get('year_pillar', '')} {bazi2.get('month_pillar', '')} "
                f"{bazi2.get('day_pillar', '')} {bazi2.get('hour_pillar', '')}",
                f"評級: {match_result.get('rating', '未知')}",
                f"雙向影響: A→B={match_result.get('a_to_b_score', 0):.1f}, B→A={match_result.get('b_to_a_score', 0):.1f}"
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
            logger.error(f"測試案例 {test_id} 運行失敗: {str(e)}")
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
    
    def _get_bazi_data(self, bazi_config: Dict) -> Dict:
        """根據配置獲取八字數據"""
        try:
            return BaziCalculator.calculate(
                year=bazi_config['year'],
                month=bazi_config['month'],
                day=bazi_config['day'],
                hour=bazi_config['hour'],
                gender=bazi_config['gender'],
                hour_confidence=bazi_config.get('hour_confidence', 'high'),
                minute=bazi_config.get('minute', 0),
                longitude=bazi_config.get('longitude', 114.17)
            )
        except Exception as e:
            logger.error(f"八字計算失敗: {e}")
            return None
    # ========== 2.1 測試功能結束 ==========
    
    # ========== 2.2 系統統計功能開始 ==========
    async def get_system_stats(self) -> SystemStats:
        """
        獲取系統統計數據 - 使用真實數據庫
        
        Returns:
            系統統計數據對象
        """
        logger.info("獲取系統統計數據")
        
        try:
            with closing(get_db_connection()) as conn:
                cur = conn.cursor()
                
                # 1. 總用戶數
                cur.execute("SELECT COUNT(*) FROM users")
                total_users = cur.fetchone()[0] or 0
                
                # 2. 總配對數
                cur.execute("SELECT COUNT(*) FROM matches")
                total_matches = cur.fetchone()[0] or 0
                
                # 3. 今日配對數
                today = datetime.now().date()
                cur.execute("""
                    SELECT COUNT(*) FROM matches 
                    WHERE DATE(created_at) = %s
                """, (today,))
                today_matches = cur.fetchone()[0] or 0
                
                # 4. 平均配對分數
                cur.execute("SELECT AVG(score) FROM matches WHERE score > 0")
                avg_score_result = cur.fetchone()[0]
                avg_match_score = float(avg_score_result) if avg_score_result else 0.0
                
                # 5. 成功率（配對成功且交換聯絡的比率）
                cur.execute("""
                    SELECT COUNT(*) FROM matches 
                    WHERE user_a_accepted = 1 AND user_b_accepted = 1 AND score >= %s
                """, (THRESHOLD_CONTACT_ALLOWED,))
                successful_matches = cur.fetchone()[0] or 0
                
                success_rate = 0.0
                if total_matches > 0:
                    success_rate = (successful_matches / total_matches) * 100
                
                # 6. 24小時內活躍用戶數
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
                
                # 7. 關係模型統計（需要從match_details中解析）
                model_stats = self._get_model_statistics_from_db(cur)
                
                # 8. 高分配對（前5名）
                top_matches = self._get_top_matches_from_db(cur)
                
                return SystemStats(
                    total_users=total_users,
                    total_matches=total_matches,
                    today_matches=today_matches,
                    avg_match_score=round(avg_match_score, 1),
                    success_rate=round(success_rate, 1),
                    model_stats=model_stats,
                    active_users_24h=active_users_24h,
                    top_matches=top_matches
                )
                
        except Exception as e:
            logger.error(f"獲取系統統計數據失敗: {str(e)}")
            # 返回空統計
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
    
    def _get_model_statistics_from_db(self, cursor) -> List[Dict[str, Any]]:
        """從數據庫獲取關係模型統計"""
        try:
            cursor.execute("""
                SELECT 
                    (match_details::json->>'relationship_model') as model,
                    COUNT(*) as count,
                    AVG(score) as avg_score
                FROM matches 
                WHERE match_details IS NOT NULL 
                AND match_details::json->>'relationship_model' IS NOT NULL
                GROUP BY match_details::json->>'relationship_model'
                ORDER BY count DESC
            """)
            
            rows = cursor.fetchall()
            model_stats = []
            
            for row in rows:
                model, count, avg_score = row
                if model:
                    model_stats.append({
                        'model': model,
                        'count': count or 0,
                        'avg_score': round(float(avg_score or 0), 1)
                    })
            
            # 如果沒有數據，返回默認統計
            if not model_stats:
                model_stats = [
                    {'model': '平衡型', 'count': 0, 'avg_score': 0.0},
                    {'model': '供求型', 'count': 0, 'avg_score': 0.0},
                    {'model': '相欠型', 'count': 0, 'avg_score': 0.0},
                    {'model': '混合型', 'count': 0, 'avg_score': 0.0}
                ]
            
            return model_stats
            
        except Exception as e:
            logger.error(f"獲取模型統計失敗: {e}")
            return []
    
    def _get_top_matches_from_db(self, cursor) -> List[Dict[str, Any]]:
        """從數據庫獲取高分配對"""
        try:
            cursor.execute("""
                SELECT 
                    m.score,
                    u1.username as user_a_name,
                    u2.username as user_b_name,
                    DATE(m.created_at) as match_date
                FROM matches m
                LEFT JOIN users u1 ON m.user_a = u1.id
                LEFT JOIN users u2 ON m.user_b = u2.id
                WHERE m.score > 0
                ORDER BY m.score DESC
                LIMIT 5
            """)
            
            rows = cursor.fetchall()
            top_matches = []
            
            for row in rows:
                score, user_a, user_b, match_date = row
                top_matches.append({
                    'score': round(float(score or 0), 1),
                    'user_a': user_a or '未知用戶',
                    'user_b': user_b or '未知用戶',
                    'date': match_date.strftime('%Y-%m-%d') if match_date else '未知'
                })
            
            return top_matches
            
        except Exception as e:
            logger.error(f"獲取高分配對失敗: {e}")
            return []
    # ========== 2.2 系統統計功能結束 ==========
    
    # ========== 2.3 數據清理功能開始 ==========
    async def cleanup_old_data(self, days: int = 30) -> Dict[str, Any]:
        """
        清理舊數據 - 使用真實數據庫
        
        Args:
            days: 保留天數
            
        Returns:
            清理結果統計
        """
        logger.info(f"開始清理超過{days}天的舊數據")
        
        try:
            with closing(get_db_connection()) as conn:
                cur = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                deleted_counts = {}
                
                # 1. 清理舊配對記錄
                cur.execute("""
                    DELETE FROM matches 
                    WHERE created_at < %s 
                    RETURNING id
                """, (cutoff_date,))
                deleted_matches = len(cur.fetchall())
                deleted_counts['matches'] = deleted_matches
                
                # 2. 清理舊日限記錄
                cur.execute("""
                    DELETE FROM daily_limits 
                    WHERE date < %s 
                    RETURNING id
                """, (cutoff_date,))
                deleted_limits = len(cur.fetchall())
                deleted_counts['daily_limits'] = deleted_limits
                
                # 3. 清理不活躍用戶（30天未活動且無成功配對）
                cur.execute("""
                    DELETE FROM users u
                    WHERE u.id NOT IN (
                        SELECT DISTINCT user_a FROM matches WHERE created_at >= %s
                        UNION
                        SELECT DISTINCT user_b FROM matches WHERE created_at >= %s
                    )
                    AND u.created_at < %s
                    AND NOT EXISTS (
                        SELECT 1 FROM matches m 
                        WHERE (m.user_a = u.id OR m.user_b = u.id) 
                        AND m.user_a_accepted = 1 AND m.user_b_accepted = 1
                    )
                    RETURNING u.id
                """, (cutoff_date, cutoff_date, cutoff_date))
                deleted_users = len(cur.fetchall())
                deleted_counts['users'] = deleted_users
                
                conn.commit()
                
                result = {
                    'deleted_matches': deleted_matches,
                    'deleted_daily_limits': deleted_limits,
                    'deleted_users': deleted_users,
                    'cutoff_date': cutoff_date.strftime('%Y-%m-%d'),
                    'status': '完成'
                }
                
                logger.info(f"數據清理完成: {result}")
                return result
                
        except Exception as e:
            logger.error(f"數據清理失敗: {str(e)}")
            return {
                'status': '失敗',
                'error': str(e)
            }
    # ========== 2.3 數據清理功能結束 ==========
    
    # ========== 2.4 數據導出功能開始 ==========
    async def export_match_data(self, format_type: str = 'json') -> Dict[str, Any]:
        """
        導出配對數據 - 使用真實數據庫
        
        Args:
            format_type: 導出格式 ('json' 或 'csv')
            
        Returns:
            導出結果
        """
        logger.info(f"導出配對數據，格式: {format_type}")
        
        try:
            with closing(get_db_connection()) as conn:
                cur = conn.cursor()
                
                # 獲取配對數據
                cur.execute("""
                    SELECT 
                        m.id,
                        u1.username as user_a,
                        u2.username as user_b,
                        m.score,
                        m.created_at,
                        m.match_details::json->>'relationship_model' as model
                    FROM matches m
                    LEFT JOIN users u1 ON m.user_a = u1.id
                    LEFT JOIN users u2 ON m.user_b = u2.id
                    ORDER BY m.created_at DESC
                    LIMIT 1000
                """)
                
                rows = cur.fetchall()
                
                if format_type == 'json':
                    data = {
                        'total': len(rows),
                        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'matches': []
                    }
                    
                    for row in rows:
                        match_id, user_a, user_b, score, created_at, model = row
                        data['matches'].append({
                            'id': match_id,
                            'user_a': user_a or '未知用戶',
                            'user_b': user_b or '未知用戶',
                            'score': float(score or 0),
                            'date': created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else '未知',
                            'model': model or '未知'
                        })
                    
                    export_data = json.dumps(data, ensure_ascii=False, indent=2)
                    
                elif format_type == 'csv':
                    # CSV 頭部
                    csv_lines = ['ID,用戶A,用戶B,分數,日期,模型']
                    
                    for row in rows:
                        match_id, user_a, user_b, score, created_at, model = row
                        user_a = user_a or '未知用戶'
                        user_b = user_b or '未知用戶'
                        score = score or 0
                        date_str = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else '未知'
                        model = model or '未知'
                        
                        # 處理特殊字符
                        user_a = user_a.replace(',', '，').replace('"', '""')
                        user_b = user_b.replace(',', '，').replace('"', '""')
                        model = model.replace(',', '，').replace('"', '""')
                        
                        csv_lines.append(f'{match_id},"{user_a}","{user_b}",{score},"{date_str}","{model}"')
                    
                    export_data = '\n'.join(csv_lines)
                    
                else:
                    raise ValueError(f"不支持的格式: {format_type}")
                
                return {
                    'format': format_type,
                    'data_size': len(export_data),
                    'records': len(rows),
                    'status': '完成',
                    'data_preview': export_data[:500] + '...' if len(export_data) > 500 else export_data
                }
                
        except Exception as e:
            logger.error(f"導出數據失敗: {str(e)}")
            return {
                'status': '失敗',
                'error': str(e)
            }
    # ========== 2.4 數據導出功能結束 ==========
    
    # ========== 2.5 一鍵測試功能開始 ==========
    async def run_quick_test(self) -> Dict[str, Any]:
        """
        運行一鍵測試 - 測試所有核心功能
        
        Returns:
            測試結果
        """
        logger.info("開始一鍵測試")
        
        results = {
            'components': [],
            'total': 0,
            'passed': 0,
            'failed': 0,
            'status': '進行中'
        }
        
        try:
            # 1. 測試數據庫連接
            db_test = await self._test_database_connection()
            results['components'].append(db_test)
            
            # 2. 測試八字計算
            bazi_test = await self._test_bazi_calculation()
            results['components'].append(bazi_test)
            
            # 3. 測試配對計算
            match_test = await self._test_match_calculation()
            results['components'].append(match_test)
            
            # 4. 測試管理員功能
            admin_test = await self._test_admin_functions()
            results['components'].append(admin_test)
            
            # 統計結果
            for component in results['components']:
                results['total'] += 1
                if component.get('status') == 'PASS':
                    results['passed'] += 1
                else:
                    results['failed'] += 1
            
            results['status'] = '完成'
            return results
            
        except Exception as e:
            logger.error(f"一鍵測試失敗: {str(e)}")
            results['status'] = '失敗'
            results['error'] = str(e)
            return results
    
    async def _test_database_connection(self) -> Dict[str, Any]:
        """測試數據庫連接"""
        try:
            with closing(get_db_connection()) as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                result = cur.fetchone()
                
                if result and result[0] == 1:
                    return {
                        'name': '數據庫連接',
                        'status': 'PASS',
                        'message': '數據庫連接正常'
                    }
                else:
                    return {
                        'name': '數據庫連接',
                        'status': 'FAIL',
                        'message': '數據庫連接測試失敗'
                    }
        except Exception as e:
            return {
                'name': '數據庫連接',
                'status': 'ERROR',
                'message': f'數據庫連接錯誤: {str(e)}'
            }
    
    async def _test_bazi_calculation(self) -> Dict[str, Any]:
        """測試八字計算"""
        try:
            bazi = BaziCalculator.calculate(
                year=1990,
                month=1,
                day=1,
                hour=12,
                gender='男',
                hour_confidence='high'
            )
            
            if bazi and bazi.get('year_pillar'):
                return {
                    'name': '八字計算',
                    'status': 'PASS',
                    'message': f'八字計算正常: {bazi.get("year_pillar")} {bazi.get("month_pillar")} {bazi.get("day_pillar")} {bazi.get("hour_pillar")}'
                }
            else:
                return {
                    'name': '八字計算',
                    'status': 'FAIL',
                    'message': '八字計算返回空數據'
                }
        except Exception as e:
            return {
                'name': '八字計算',
                'status': 'ERROR',
                'message': f'八字計算錯誤: {str(e)}'
            }
    
    async def _test_match_calculation(self) -> Dict[str, Any]:
        """測試配對計算"""
        try:
            # 計算兩個測試八字
            bazi1 = BaziCalculator.calculate(1990, 1, 1, 12, '男', 'high')
            bazi2 = BaziCalculator.calculate(1991, 2, 2, 13, '女', 'high')
            
            match_result = calculate_match(bazi1, bazi2, '男', '女', is_testpair=True)
            
            if match_result and match_result.get('score') is not None:
                return {
                    'name': '配對計算',
                    'status': 'PASS',
                    'message': f'配對計算正常: 分數={match_result.get("score", 0):.1f}分'
                }
            else:
                return {
                    'name': '配對計算',
                    'status': 'FAIL',
                    'message': '配對計算返回空數據'
                }
        except Exception as e:
            return {
                'name': '配對計算',
                'status': 'ERROR',
                'message': f'配對計算錯誤: {str(e)}'
            }
    
    async def _test_admin_functions(self) -> Dict[str, Any]:
        """測試管理員功能"""
        try:
            # 測試獲取統計數據
            stats = await self.get_system_stats()
            
            if stats and isinstance(stats.total_users, int):
                return {
                    'name': '管理員功能',
                    'status': 'PASS',
                    'message': f'管理員功能正常: 用戶數={stats.total_users}, 配對數={stats.total_matches}'
                }
            else:
                return {
                    'name': '管理員功能',
                    'status': 'FAIL',
                    'message': '管理員功能返回異常數據'
                }
        except Exception as e:
            return {
                'name': '管理員功能',
                'status': 'ERROR',
                'message': f'管理員功能錯誤: {str(e)}'
            }
    # ========== 2.5 一鍵測試功能結束 ==========
    
    # ========== 2.6 格式化功能開始 ==========
    def format_test_results(self, results: Dict[str, Any]) -> str:
        """格式化測試結果為可讀文本 - 顯示全部20組"""
        if not results:
            return "無測試結果"
        
        # 生成詳細報告
        text = f"""📊 管理員測試報告 (20組完整測試)
{"="*60}

📈 總體統計:
  總測試數: {results['total']}
  通過: {results['passed']} ✅
  失敗: {results['failed']} ❌
  錯誤: {results['errors']} ⚠️
  成功率: {results['success_rate']:.1f}%
  
📋 詳細結果 ({len(results['details'])}組):
"""
        
        # 顯示所有測試案例
        for i, detail in enumerate(results['details'], 1):
            status_emoji = '✅' if detail['status'] == 'PASS' else '❌' if detail['status'] == 'FAIL' else '⚠️'
            text += f"\n{i:2d}. {status_emoji} {detail['description']}\n"
            
            # 分數信息
            score = detail.get('score', 0)
            expected_min, expected_max = detail.get('expected_range', (0, 0))
            text += f"   分數: {score:.1f}分 (預期: {expected_min}-{expected_max}分)"
            
            # 模型信息
            model = detail.get('model', '')
            expected_model = detail.get('expected_model', '')
            model_match = detail.get('model_match', False)
            if model and expected_model:
                model_symbol = '✅' if model_match else '❌'
                text += f"\n   模型: {model} (預期: {expected_model}) {model_symbol}"
            
            # 錯誤信息
            if detail.get('error'):
                text += f"\n   錯誤: {detail['error'][:100]}..."
            
            # 分隔線
            if i < len(results['details']):
                text += "\n   " + "-"*40
        
        # 添加總結
        text += f"\n\n📊 總結:\n"
        
        if results['success_rate'] >= 90:
            text += "✅ 測試通過率超過90%，系統運行正常！"
        elif results['success_rate'] >= 70:
            text += "⚠️ 測試通過率70-90%，系統基本正常但有改進空間。"
        elif results['success_rate'] >= 50:
            text += "⚠️ 測試通過率50-70%，系統存在較多問題需要檢查。"
        else:
            text += "❌ 測試通過率低於50%，系統存在嚴重問題！"
        
        return text
    
    def format_system_stats(self, stats: SystemStats) -> str:
        """格式化系統統計為可讀文本 - 使用真實數據"""
        if not stats:
            return "無系統統計數據"
        
        text = f"""📈 系統統計報告 (真實數據)
{"="*60}

👥 用戶統計:
  總用戶數: {stats.total_users}
  24小時活躍用戶: {stats.active_users_24h}
  
💖 配對統計:
  總配對數: {stats.total_matches}
  今日配對: {stats.today_matches}
  平均分數: {stats.avg_match_score:.1f}分
  成功率: {stats.success_rate:.1f}%
  
🎭 關係模型分佈:
"""
        
        for model_stat in stats.model_stats[:5]:  # 只顯示前5個
            text += f"  {model_stat['model']}: {model_stat['count']}次 ({model_stat.get('avg_score', 0):.1f}分)\n"
        
        if stats.top_matches:
            text += "\n🏆 高分配對 (前5名):\n"
            for i, match in enumerate(stats.top_matches, 1):
                text += f"  {i}. {match.get('user_a', '?')} ↔ {match.get('user_b', '?')}: {match.get('score', 0):.1f}分 ({match.get('date', '?')})\n"
        
        # 添加數據時間戳
        text += f"\n📅 數據時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return text
    
    def format_quick_test_results(self, results: Dict[str, Any]) -> str:
        """格式化一鍵測試結果"""
        if not results:
            return "無測試結果"
        
        text = f"""⚡ 一鍵測試結果
{"="*60}

📊 總體狀態: {results.get('status', '未知')}
✅ 通過: {results.get('passed', 0)} / {results.get('total', 0)}
❌ 失敗: {results.get('failed', 0)} / {results.get('total', 0)}

📋 組件測試:
"""
        
        for component in results.get('components', []):
            name = component.get('name', '未知')
            status = component.get('status', '未知')
            message = component.get('message', '')
            
            status_emoji = '✅' if status == 'PASS' else '❌' if status == 'FAIL' else '⚠️'
            text += f"\n{status_emoji} {name}: {message}"
        
        if results.get('error'):
            text += f"\n\n❌ 錯誤信息: {results['error']}"
        
        # 添加建議
        text += "\n\n💡 建議:"
        if results.get('passed', 0) == results.get('total', 0):
            text += "\n✅ 所有組件正常，系統運行良好！"
        elif results.get('passed', 0) >= results.get('total', 0) * 0.7:
            text += "\n⚠️ 大部分組件正常，建議檢查失敗組件。"
        else:
            text += "\n❌ 多個組件異常，建議立即檢查系統！"
        
        return text
    # ========== 2.6 格式化功能結束 ==========

# ========== 1.4 AdminService類結束 ==========

# ========== 文件信息開始 ==========
"""
文件: admin_service.py
功能: 管理員服務模組 - 處理管理員專用功能

引用文件: 
- new_calculator.py (八字計算核心)
- test_cases.py (測試案例)
- psycopg2 (PostgreSQL數據庫連接)
- datetime, logging (Python標準庫)

被引用文件:
- bot.py (主程序將導入此文件的AdminService類)

功能:
1. 運行管理員測試案例（20組八字）- 顯示全部
2. 獲取真實系統統計數據（連接數據庫）
3. 清理舊數據（真實數據庫操作）
4. 導出配對數據（JSON/CSV格式）
5. 一鍵測試功能（測試所有核心組件）
6. 格式化輸出結果

主要修改：
1. 顯示全部20組測試案例
2. 使用真實數據庫統計
3. 添加一鍵測試功能
4. 連接真實PostgreSQL數據庫
5. 完善數據清理和導出功能
6. 改進格式化輸出
"""
# ========== 文件信息結束 ==========