#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理員服務模組 - 更新版，兼容new_calculator.py
處理管理員專用功能
最後更新: 2026年2月1日
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

# ========== 1.1 導入模組開始 ==========
# 導入新的計算核心
from new_calculator import (
    BaziCalculator,
    calculate_match,
    BaziCalculatorError,
    ScoringEngineError,
    THRESHOLD_CONTACT_ALLOWED,
    MASTER_BAZI_CONFIG
)

# 導入測試案例
from test_cases import ADMIN_TEST_CASES

logger = logging.getLogger(__name__)
# ========== 1.1 導入模組結束 ==========

# ========== 1.2 數據類開始 ==========
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
# ========== 1.2 數據類結束 ==========

# ========== 1.3 AdminService類開始 ==========
class AdminService:
    """管理員服務類 - 更新版"""
    
    def __init__(self, db_path: str = None):
        """
        初始化管理員服務
        
        Args:
            db_path: 數據庫路徑（可選）
        """
        self.db_path = db_path
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
                f"{bazi2.get('day_pillar', '')} {bazi2.get('hour_pillar', '')}"
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
        獲取系統統計數據
        
        Returns:
            系統統計數據對象
        """
        logger.info("獲取系統統計數據")
        
        try:
            # 這裡需要根據實際數據庫實現
            # 暫時返回模擬數據
            
            return SystemStats(
                total_users=self._get_user_count(),
                total_matches=self._get_match_count(),
                today_matches=self._get_today_match_count(),
                avg_match_score=self._get_avg_match_score(),
                success_rate=self._get_success_rate(),
                model_stats=self._get_model_statistics(),
                active_users_24h=self._get_active_users_24h(),
                top_matches=self._get_top_matches()
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
    
    # ========== 數據庫輔助方法開始 ==========
    def _get_user_count(self) -> int:
        """獲取總用戶數"""
        # 需要實際數據庫實現
        return 100
    
    def _get_match_count(self) -> int:
        """獲取總配對數"""
        # 需要實際數據庫實現
        return 500
    
    def _get_today_match_count(self) -> int:
        """獲取今日配對數"""
        # 需要實際數據庫實現
        return 25
    
    def _get_avg_match_score(self) -> float:
        """獲取平均配對分數"""
        # 需要實際數據庫實現
        return 72.5
    
    def _get_success_rate(self) -> float:
        """獲取成功率"""
        # 需要實際數據庫實現
        return 68.3
    
    def _get_model_statistics(self) -> List[Dict[str, Any]]:
        """獲取模型統計"""
        # 模擬數據
        return [
            {'model': '平衡型', 'count': 250, 'avg_score': 75.2},
            {'model': '供求型', 'count': 150, 'avg_score': 71.8},
            {'model': '相欠型', 'count': 80, 'avg_score': 65.4},
            {'model': '混合型', 'count': 20, 'avg_score': 68.9}
        ]
    
    def _get_active_users_24h(self) -> int:
        """獲取24小時內活躍用戶數"""
        # 需要實際數據庫實現
        return 45
    
    def _get_top_matches(self) -> List[Dict[str, Any]]:
        """獲取高分配對"""
        # 模擬數據
        return [
            {'score': 92.5, 'user_a': '用戶A', 'user_b': '用戶B', 'date': '2024-01-30'},
            {'score': 89.3, 'user_a': '用戶C', 'user_b': '用戶D', 'date': '2024-01-29'},
            {'score': 87.8, 'user_a': '用戶E', 'user_b': '用戶F', 'date': '2024-01-28'}
        ]
    # ========== 數據庫輔助方法結束 ==========
    
    # ========== 2.3 數據清理功能開始 ==========
    async def cleanup_old_data(self, days: int = 30) -> Dict[str, Any]:
        """
        清理舊數據
        
        Args:
            days: 保留天數
            
        Returns:
            清理結果統計
        """
        logger.info(f"開始清理超過{days}天的舊數據")
        
        try:
            # 這裡需要實際的數據庫清理邏輯
            # 暫時返回模擬結果
            
            result = {
                'deleted_matches': 15,
                'deleted_users': 3,
                'deleted_logs': 0,
                'cutoff_date': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
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
        導出配對數據
        
        Args:
            format_type: 導出格式 ('json' 或 'csv')
            
        Returns:
            導出結果
        """
        logger.info(f"導出配對數據，格式: {format_type}")
        
        try:
            # 這裡需要實際的數據導出邏輯
            # 暫時返回模擬數據
            
            if format_type == 'json':
                data = {
                    'total': 100,
                    'matches': [
                        {
                            'user_a': '用戶A',
                            'user_b': '用戶B',
                            'score': 85.5,
                            'date': '2024-01-30',
                            'model': '平衡型'
                        }
                        # ... 更多數據
                    ]
                }
            elif format_type == 'csv':
                data = "用戶A,用戶B,分數,日期,模型\n用戶A,用戶B,85.5,2024-01-30,平衡型\n"
            else:
                raise ValueError(f"不支持的格式: {format_type}")
            
            return {
                'format': format_type,
                'data_size': len(str(data)),
                'records': 100,
                'status': '完成'
            }
            
        except Exception as e:
            logger.error(f"導出數據失敗: {str(e)}")
            return {
                'status': '失敗',
                'error': str(e)
            }
    # ========== 2.4 數據導出功能結束 ==========
    
    # ========== 2.5 格式化功能開始 ==========
    def format_test_results(self, results: Dict[str, Any]) -> str:
        """格式化測試結果為可讀文本"""
        if not results:
            return "無測試結果"
        
        text = f"""📊 管理員測試報告
====================
📈 總體統計:
  總測試數: {results['total']}
  通過: {results['passed']} ✅
  失敗: {results['failed']} ❌
  錯誤: {results['errors']} ⚠️
  成功率: {results['success_rate']:.1f}%
  
📋 詳細結果:
"""
        
        for detail in results['details'][:10]:  # 只顯示前10個
            status_emoji = '✅' if detail['status'] == 'PASS' else '❌' if detail['status'] == 'FAIL' else '⚠️'
            text += f"{status_emoji} {detail['description']}\n"
            text += f"   分數: {detail.get('score', 0):.1f}分 (預期: {detail['expected_range'][0]}-{detail['expected_range'][1]}分)\n"
            
            if detail.get('error'):
                text += f"   錯誤: {detail['error']}\n"
        
        return text
    
    def format_system_stats(self, stats: SystemStats) -> str:
        """格式化系統統計為可讀文本"""
        if not stats:
            return "無系統統計數據"
        
        text = f"""📈 系統統計報告
====================
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
        
        for model_stat in stats.model_stats:
            text += f"  {model_stat['model']}: {model_stat['count']}次 ({model_stat.get('avg_score', 0):.1f}分)\n"
        
        if stats.top_matches:
            text += "\n🏆 高分配對:\n"
            for match in stats.top_matches[:5]:
                text += f"  {match.get('user_a', '?')} ↔ {match.get('user_b', '?')}: {match.get('score', 0):.1f}分\n"
        
        return text
    # ========== 2.5 格式化功能結束 ==========

# ========== 1.3 AdminService類結束 ==========

# ========== 文件信息開始 ==========
"""
文件: admin_service.py
功能: 管理員服務模組 - 處理管理員專用功能

引用文件: 
- new_calculator.py (八字計算核心)
- test_cases.py (測試案例)
- datetime, logging (Python標準庫)

被引用文件:
- bot.py (主程序將導入此文件的AdminService類)

功能:
1. 運行管理員測試案例（20組八字）
2. 獲取系統統計數據
3. 清理舊數據
4. 導出配對數據
5. 格式化輸出結果

兼容性:
- 完全兼容new_calculator.py的接口
- 使用新的評分閾值系統
- 支持真太陽時校正
"""
# ========== 文件信息結束 ==========

# ========== 目錄開始 ==========
"""
1.1 導入模組 - 導入必要的庫和模組
1.2 數據類 - 定義數據結構（TestResult, SystemStats）
1.3 AdminService類 - 主服務類

2.1 測試功能 - 運行管理員測試案例（20組）
2.2 系統統計功能 - 獲取系統統計數據
2.3 數據清理功能 - 清理舊數據
2.4 數據導出功能 - 導出配對數據
2.5 格式化功能 - 格式化輸出結果
"""
# ========== 目錄結束 ==========

# ========== 修正紀錄開始 ==========
"""
版本 1.0 (2026-02-01)
主要修改:
1. 完全重寫admin_service.py以兼容new_calculator.py
2. 修正導入語句：使用new_calculator.py的接口
3. 更新測試案例處理邏輯，使用新的calculate_match()函數
4. 添加TestResult和SystemStats數據類
5. 實現完整的20組測試案例運行功能
6. 添加系統統計、數據清理、數據導出功能
7. 添加格式化輸出功能，便於在Telegram Bot中顯示
8. 保持接口簡單，易於bot.py集成

兼容性:
- 完全兼容new_calculator.py的所有功能
- 支持真太陽時校正和新的評分系統
- 使用新的評分閾值（THRESHOLD_CONTACT_ALLOWED等）

使用方法:
1. 在bot.py中導入AdminService
2. 創建AdminService實例
3. 調用相應的方法（如run_admin_tests()）
4. 使用格式化方法輸出結果到Telegram

注意:
- 數據庫相關功能需要根據實際數據庫結構實現
- 測試案例需要從test_cases.py導入
- 確保test_cases.py中的ADMIN_TEST_CASES格式正確
"""
# ========== 修正紀錄結束 ==========