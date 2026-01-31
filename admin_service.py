#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理員服務模組
處理管理員專用功能
最後更新: 2026年1月31日
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

# 修正導入：從正確的文件導入
from config.test_cases import ADMIN_TEST_CASES
from config.constants import THRESHOLD_CONTACT_ALLOWED
from database.db_manager import DatabaseManager
from core.bazi_calculator import BaziCalculator
from core.scoring_engine import ScoringEngine

logger = logging.getLogger(__name__)


@dataclass
class SystemStats:
    """系統統計數據"""
    total_users: int
    total_matches: int
    today_matches: int
    avg_match_score: float
    success_rate: float  # 總成功率
    model_stats: List[Dict[str, Any]]  # 模型細分統計
    active_users_24h: int
    top_matches: List[Dict[str, Any]]
    elite_seeds_count: int  # ✅ 新增：精英種子數量


class AdminService:
    """管理員服務類"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化管理員服務
        
        Args:
            db_manager: 數據庫管理器實例
        """
        self.db = db_manager
        
    # ========== 1. 測試功能 ==========
    
    async def run_test_cases(self) -> Dict[str, Any]:
        """
        運行管理員測試案例
        
        Returns:
            測試結果字典
        """
        logger.info("開始運行管理員測試案例")
        
        results = {
            'total': len(ADMIN_TEST_CASES),
            'passed': 0,
            'failed': 0,
            'details': [],
            'summary': {}
        }
        
        for i, test_case in enumerate(ADMIN_TEST_CASES, 1):
            try:
                logger.info(f"運行測試案例 {i}/{len(ADMIN_TEST_CASES)}: {test_case['description']}")
                
                # ========== 1.1 獲取八字數據 ==========
                bazi1 = BaziCalculator.calculate(
                    year=test_case['bazi_data1']['year'],
                    month=test_case['bazi_data1']['month'],
                    day=test_case['bazi_data1']['day'],
                    hour=test_case['bazi_data1']['hour'],
                    gender=test_case['bazi_data1']['gender']
                )
                
                bazi2 = BaziCalculator.calculate(
                    year=test_case['bazi_data2']['year'],
                    month=test_case['bazi_data2']['month'],
                    day=test_case['bazi_data2']['day'],
                    hour=test_case['bazi_data2']['hour'],
                    gender=test_case['bazi_data2']['gender']
                )
                
                if not bazi1 or not bazi2:
                    raise ValueError("八字計算失敗")
                
                # ========== 1.2 計算八字配對 ==========
                result = ScoringEngine.calculate(
                    bazi1=bazi1,
                    bazi2=bazi2,
                    gender1=test_case['bazi_data1']['gender'],
                    gender2=test_case['bazi_data2']['gender']
                )
                
                score = result.get('score', 0)
                expected_min, expected_max = test_case['expected_range']
                
                # ========== 1.3 檢查分數是否在預期範圍內 ==========
                if expected_min <= score <= expected_max:
                    status = 'PASS'
                    results['passed'] += 1
                else:
                    status = 'FAIL'
                    results['failed'] += 1
                    
                # ========== 1.4 檢查關係模型 ==========
                model_match = result.get('relationship_model') == test_case['expected_model']
                
                results['details'].append({
                    'test_id': i,
                    'description': test_case['description'],
                    'status': status,
                    'score': score,
                    'expected_range': test_case['expected_range'],
                    'model': result.get('relationship_model'),
                    'expected_model': test_case['expected_model'],
                    'model_match': model_match,
                    'details': result.get('step_details', [])
                })
                
            except Exception as e:
                logger.error(f"測試案例 {i} 運行失敗: {str(e)}")
                results['failed'] += 1
                results['details'].append({
                    'test_id': i,
                    'description': test_case['description'],
                    'status': 'ERROR',
                    'error': str(e)
                })
        
        # ========== 1.5 計算成功率 ==========
        if results['total'] > 0:
            results['success_rate'] = (results['passed'] / results['total']) * 100
        
        logger.info(f"測試完成: {results['passed']} 通過, {results['failed']} 失敗")
        return results
    
    # ========== 2. 系統統計功能 ==========
    
    async def get_system_stats(self) -> SystemStats:
        """
        獲取系統統計數據
        
        Returns:
            系統統計數據對象
        """
        logger.info("獲取系統統計數據")
        
        try:
            # ========== 2.1 獲取總用戶數 ==========
            total_users = self.db.get_total_user_count()
            
            # ========== 2.2 獲取總配對數 ==========
            total_matches = self.db.get_total_match_count()
            
            # ========== 2.3 獲取今日配對數 ==========
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_matches = self.db.get_match_count_since(today_start)
            
            # ========== 2.4 獲取24小時內活躍用戶數 ==========
            day_ago = datetime.now() - timedelta(hours=24)
            active_users_24h = self.db.get_active_user_count_since(day_ago)
            
            # ========== 2.5 獲取平均配對分數 ==========
            avg_score_result = self.db.execute_query(
                "SELECT AVG(overall_score) as avg_score FROM match_records WHERE overall_score IS NOT NULL"
            )
            avg_match_score = avg_score_result[0]['avg_score'] if avg_score_result and avg_score_result[0]['avg_score'] else 0.0
            
            # ========== 2.6 計算總成功率（分數≥聯絡允許閾值為成功） ==========
            success_rate_result = self.db.execute_query("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN overall_score >= %s THEN 1 ELSE 0 END) as successful
                FROM match_records 
                WHERE overall_score IS NOT NULL
            """, (THRESHOLD_CONTACT_ALLOWED,))
            
            success_rate = 0.0
            if success_rate_result and success_rate_result[0]['total'] > 0:
                total_records = success_rate_result[0]['total']
                successful = success_rate_result[0]['successful'] or 0
                success_rate = (successful / total_records) * 100
            
            # ========== 2.7 按模型細分統計 ==========
            model_stats = self._get_model_statistics()
            
            # ========== 2.8 獲取高分配對（前10名） ==========
            top_matches = self.db.execute_query("""
                SELECT 
                    mr.id,
                    mr.user_a_id,
                    mr.user_b_id,
                    mr.overall_score as score,
                    mr.relationship_model,
                    mr.created_at,
                    u1.username as user_a_name,
                    u2.username as user_b_name
                FROM match_records mr
                LEFT JOIN users u1 ON mr.user_a_id = u1.id
                LEFT JOIN users u2 ON mr.user_b_id = u2.id
                WHERE mr.overall_score IS NOT NULL
                ORDER BY mr.overall_score DESC
                LIMIT 10
            """)
            
            # ========== 2.9 獲取精英種子數量 ==========
            elite_seeds_count = self.db.execute_query("SELECT COUNT(*) as count FROM elite_bazi_seeds")
            elite_seeds_count_val = elite_seeds_count[0]['count'] if elite_seeds_count else 0
            
            return SystemStats(
                total_users=total_users,
                total_matches=total_matches,
                today_matches=today_matches,
                avg_match_score=round(avg_match_score, 2),
                success_rate=round(success_rate, 2),
                model_stats=model_stats,
                active_users_24h=active_users_24h,
                top_matches=top_matches or [],
                elite_seeds_count=elite_seeds_count_val
            )
            
        except Exception as e:
            logger.error(f"獲取系統統計數據失敗: {str(e)}")
            raise
    
    # ========== 3. 模型統計功能 ==========
    
    def _get_model_statistics(self) -> List[Dict[str, Any]]:
        """
        獲取按關係模型細分的統計數據
        
        Returns:
            模型統計列表
        """
        try:
            # ========== 3.1 查詢各模型的配對統計 ==========
            query = """
                SELECT 
                    relationship_model,
                    COUNT(*) as total_count,
                    SUM(CASE WHEN overall_score >= %s THEN 1 ELSE 0 END) as success_count,
                    AVG(overall_score) as avg_score,
                    MIN(overall_score) as min_score,
                    MAX(overall_score) as max_score,
                    COUNT(DISTINCT user_a_id) as unique_users_a,
                    COUNT(DISTINCT user_b_id) as unique_users_b
                FROM match_records 
                WHERE relationship_model IS NOT NULL 
                  AND overall_score IS NOT NULL
                GROUP BY relationship_model
                ORDER BY total_count DESC
            """
            
            results = self.db.execute_query(query, (THRESHOLD_CONTACT_ALLOWED,))
            
            model_stats = []
            for row in results:
                total = row['total_count']
                success = row['success_count'] or 0
                
                model_stats.append({
                    'relationship_model': row['relationship_model'],
                    'total_matches': total,
                    'success_count': success,
                    'success_rate': round((success / total * 100), 2) if total > 0 else 0.0,
                    'avg_score': round(row['avg_score'] or 0.0, 2),
                    'min_score': row['min_score'] or 0,
                    'max_score': row['max_score'] or 0,
                    'unique_users_count': (row['unique_users_a'] or 0) + (row['unique_users_b'] or 0),
                    'performance_trend': self._get_model_trend(row['relationship_model'])
                })
            
            return model_stats
            
        except Exception as e:
            logger.error(f"獲取模型統計數據失敗: {str(e)}")
            return []
    
    # ========== 4. 模型趨勢分析 ==========
    
    def _get_model_trend(self, model: str) -> Dict[str, Any]:
        """
        獲取模型趨勢數據（最近7天）
        
        Args:
            model: 關係模型名稱
            
        Returns:
            趨勢數據
        """
        try:
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            query = """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as daily_count,
                    AVG(overall_score) as daily_avg_score
                FROM match_records 
                WHERE relationship_model = %s 
                  AND created_at >= %s
                GROUP BY DATE(created_at)
                ORDER BY date
            """
            
            params = [model, seven_days_ago]
            results = self.db.execute_query(query, params)
            
            return {
                'last_7_days': results,
                'trend_direction': self._calculate_trend_direction(results)
            }
            
        except Exception as e:
            logger.error(f"獲取模型趨勢數據失敗: {str(e)}")
            return {'last_7_days': [], 'trend_direction': 'stable'}
    
    def _calculate_trend_direction(self, daily_data: List[Dict]) -> str:
        """
        計算趨勢方向
        
        Args:
            daily_data: 每日數據
            
        Returns:
            'up', 'down', 或 'stable'
        """
        if len(daily_data) < 2:
            return 'stable'
        
        # ========== 4.1 計算最近幾天的增長趨勢 ==========
        recent_counts = [day['daily_count'] for day in daily_data[-3:]]
        if len(recent_counts) >= 2:
            if recent_counts[-1] > recent_counts[-2]:
                return 'up'
            elif recent_counts[-1] < recent_counts[-2]:
                return 'down'
        
        return 'stable'
    
    # ========== 5. 數據清理功能 ==========
    
    async def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """
        清理舊數據
        
        Args:
            days: 保留天數
            
        Returns:
            清理結果統計
        """
        logger.info(f"開始清理超過{days}天的舊數據")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # ========== 5.1 清理舊配對記錄 ==========
            deleted_matches = self.db.execute_query(
                "DELETE FROM match_records WHERE created_at < %s AND expired = TRUE",
                [cutoff_date]
            )
            
            # ========== 5.2 清理未驗證的用戶 ==========
            deleted_users = self.db.execute_query(
                """DELETE FROM users 
                   WHERE is_verified = FALSE 
                   AND created_at < %s""",
                [cutoff_date]
            )
            
            # ========== 5.3 清理舊日誌（如果存在日誌表） ==========
            deleted_logs = {'rowcount': 0}
            try:
                deleted_logs = self.db.execute_query(
                    "DELETE FROM system_logs WHERE timestamp < %s",
                    [cutoff_date]
                )
            except Exception:
                logger.info("系統日誌表可能不存在，跳過清理")
            
            result = {
                'deleted_matches': deleted_matches if isinstance(deleted_matches, int) else deleted_matches.rowcount,
                'deleted_users': deleted_users if isinstance(deleted_users, int) else deleted_users.rowcount,
                'deleted_logs': deleted_logs if isinstance(deleted_logs, int) else deleted_logs.rowcount,
                'cutoff_date': cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"數據清理完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"數據清理失敗: {str(e)}")
            raise
    
    # ========== 6. 數據導出功能 ==========
    
    async def export_match_data(self, format_type: str = 'csv') -> str:
        """
        導出配對數據
        
        Args:
            format_type: 導出格式 ('csv' 或 'json')
            
        Returns:
            導出文件路徑或數據
        """
        logger.info(f"導出配對數據，格式: {format_type}")
        
        try:
            # ========== 6.1 獲取配對數據 ==========
            query = """
                SELECT 
                    mr.*,
                    u1.username as user_a_name,
                    u1.bazi_data as user_a_bazi,
                    u2.username as user_b_name,
                    u2.bazi_data as user_b_bazi
                FROM match_records mr
                LEFT JOIN users u1 ON mr.user_a_id = u1.telegram_id
                LEFT JOIN users u2 ON mr.user_b_id = u2.telegram_id
                ORDER BY mr.created_at DESC
                LIMIT 1000
            """
            
            data = self.db.execute_query(query)
            
            if format_type == 'csv':
                import csv
                import tempfile
                
                # ========== 6.2 創建臨時CSV文件 ==========
                with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys() if data else [])
                    writer.writeheader()
                    writer.writerows(data)
                    return f.name
                    
            elif format_type == 'json':
                import json
                import tempfile
                
                # ========== 6.3 創建臨時JSON文件 ==========
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(data, f, indent=2, default=str)
                    return f.name
                    
            else:
                raise ValueError(f"不支持的格式: {format_type}")
                
        except Exception as e:
            logger.error(f"導出數據失敗: {str(e)}")
            raise

# ========== 文件結尾：Section目錄 ==========
"""
1. 測試功能
   1.1 獲取八字數據
   1.2 計算八字配對
   1.3 檢查分數是否在預期範圍內
   1.4 檢查關係模型
   1.5 計算成功率

2. 系統統計功能
   2.1 獲取總用戶數
   2.2 獲取總配對數
   2.3 獲取今日配對數
   2.4 獲取24小時內活躍用戶數
   2.5 獲取平均配對分數
   2.6 計算總成功率
   2.7 按模型細分統計
   2.8 獲取高分配對
   2.9 獲取精英種子數量

3. 模型統計功能
   3.1 查詢各模型的配對統計

4. 模型趨勢分析
   4.1 計算最近幾天的增長趨勢

5. 數據清理功能
   5.1 清理舊配對記錄
   5.2 清理未驗證的用戶
   5.3 清理舊日誌

6. 數據導出功能
   6.1 獲取配對數據
   6.2 創建臨時CSV文件
   6.3 創建臨時JSON文件
"""

# ========== 修正紀錄 ==========
"""
修正紀錄：
首次修正 (2026-01-31): 文件結構完整，功能齊全

本次修正 (2026-01-31): 
1. 確保所有方法都有完整的Section Header
2. 檢查導入語句正確性
3. 添加詳細的文檔說明
4. 保持與ARCHITECTURE.md規範一致
"""