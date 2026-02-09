#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真命天子搜索服務 - 處理搜索最佳八字匹配
最後更新: 2026年1月31日
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from database.db_manager import DatabaseManager
from core.scoring_engine import ScoringEngine
from config.constants import (
    SOULMATE_YEAR_RANGE, DAILY_SOULMATE_LIMIT,
    THRESHOLD_GOOD_MATCH, THRESHOLD_EXCELLENT_MATCH, THRESHOLD_PERFECT_MATCH
)

logger = logging.getLogger(__name__)


class SoulmateService:
    """真命天子搜索服務"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    # ========== 1. 主要搜索方法 ==========
    
    async def find_soulmate_for_user(self, user_data: Dict, 
                                    start_year: int, end_year: int, 
                                    purpose: str = "正緣") -> List[Dict]:
        """
        為用戶搜索真命天子
        
        Args:
            user_data: 用戶數據
            start_year: 開始年份
            end_year: 結束年份
            purpose: 搜索目的（正緣/合夥）
            
        Returns:
            匹配結果列表
        """
        try:
            # ========== 1.1 驗證參數 ==========
            if end_year - start_year > 4:
                logger.warning(f"搜索範圍過大: {start_year}-{end_year} (最大5年)")
                return []
            
            min_year = SOULMATE_YEAR_RANGE.get('MIN_YEAR', 1925)
            max_year = SOULMATE_YEAR_RANGE.get('MAX_YEAR', 2025)
            if start_year < min_year or end_year > max_year:
                logger.warning(f"年份超出範圍: {start_year}-{end_year} (允許{min_year}-{max_year})")
                return []
            
            # ========== 1.2 獲取用戶八字數據 ==========
            user_bazi = user_data.get('bazi_data', {})
            user_gender = user_data.get('gender', '未知')
            
            if not user_bazi:
                logger.error("用戶八字數據為空")
                return []
            
            # ========== 1.3 確定搜索性別 ==========
            search_gender = self._get_search_gender(user_gender, purpose)
            
            # ========== 1.4 從精英庫獲取候選 ==========
            candidates = self.db_manager.get_elite_bazi_seeds(
                start_year=start_year,
                end_year=end_year,
                gender_suitability=search_gender,
                limit=500
            )
            
            if not candidates:
                logger.warning(f"在{start_year}-{end_year}年未找到候選")
                return []
            
            logger.info(f"從精英庫獲取到 {len(candidates)} 個候選")
            
            # ========== 1.5 計算匹配分數 ==========
            matched_results = []
            candidates_processed = 0
            
            for candidate in candidates:
                try:
                    # ========== 1.5.1 檢查候選數據完整性 ==========
                    if not candidate.get('bazi_data'):
                        continue
                    
                    candidate_bazi = candidate['bazi_data']
                    
                    # ========== 1.5.2 計算配對分數 ==========
                    match_result = ScoringEngine.calculate(
                        bazi1=user_bazi,
                        bazi2=candidate_bazi,
                        gender1=user_gender,
                        gender2=search_gender
                    )
                    
                    candidates_processed += 1
                    
                    # ========== 1.5.3 只保留高質量匹配 ==========
                    score = match_result.get('score', 0)
                    if score >= THRESHOLD_GOOD_MATCH:
                        matched_result = {
                            'seed_bazi_id': candidate.get('seed_bazi_id'),
                            'birth_timestamp': candidate.get('birth_timestamp'),
                            'score': score,
                            'relationship_model': match_result.get('relationship_model', '未知'),
                            'bazi_data': candidate_bazi,
                            'bazi_score_base': candidate.get('bazi_score_base', 0),
                            'primary_element': candidate.get('primary_element', '未知'),
                            'gender_suitability': candidate.get('gender_suitability', '未知')
                        }
                        matched_results.append(matched_result)
                    
                    # ========== 1.5.4 提前停止條件 ==========
                    if len(matched_results) >= 10:
                        logger.info(f"已找到10個高質量匹配，提前停止搜索")
                        break
                    
                except Exception as e:
                    logger.error(f"處理候選 {candidate.get('seed_bazi_id')} 時出錯: {e}")
                    continue
            
            logger.info(f"處理了 {candidates_processed} 個候選，找到 {len(matched_results)} 個匹配")
            
            # ========== 1.6 按分數排序 ==========
            matched_results.sort(key=lambda x: x['score'], reverse=True)
            
            return matched_results[:10]  # 只返回前10名
            
        except Exception as e:
            logger.error(f"搜索真命天子失敗: {e}", exc_info=True)
            return []
    
    # ========== 2. 輔助方法 ==========
    
    def _get_search_gender(self, user_gender: str, purpose: str) -> str:
        """
        確定搜索的性別
        
        Args:
            user_gender: 用戶性別
            purpose: 搜索目的
            
        Returns:
            搜索性別
        """
        if purpose == "正緣":
            # 正緣搜索異性
            return "男" if user_gender == "女" else "女"
        else:
            # 合夥搜索不限性別
            return "通用"
    
    # ========== 3. 結果格式化方法 ==========
    
    def format_soulmate_results(self, user_bazi: Dict, results: List[Dict], purpose: str) -> str:
        """
        格式化真命天子搜索結果
        
        Args:
            user_bazi: 用戶八字數據
            results: 匹配結果列表
            purpose: 搜索目的
            
        Returns:
            格式化後的文本
        """
        if not results:
            return f"🔍 在指定年份範圍內未找到合適的{purpose}對象。\n\n建議：\n1. 嘗試其他年份範圍\n2. 調整搜索目的\n3. 稍後再試"
        
        # ========== 3.1 獲取用戶日主信息 ==========
        user_day_stem = user_bazi.get('day_stem', '未知')
        user_day_element = user_bazi.get('day_stem_element', '未知')
        
        # ========== 3.2 構建結果文本 ==========
        result_text = f"🔍 **{purpose}搜索結果**\n\n"
        result_text += f"👤 你的日主：{user_day_stem} ({user_day_element})\n"
        result_text += f"📊 共找到 {len(results)} 個匹配對象\n\n"
        
        # ========== 3.3 添加結果列表 ==========
        for i, result in enumerate(results[:10], 1):
            score = result.get('score', 0)
            model = result.get('relationship_model', '未知')
            
            # 獲取候選八字信息
            candidate_bazi = result.get('bazi_data', {})
            candidate_stem = candidate_bazi.get('day_stem', '未知')
            candidate_element = candidate_bazi.get('day_stem_element', '未知')
            
            # 獲取出生時間
            birth_timestamp = result.get('birth_timestamp')
            if birth_timestamp:
                if hasattr(birth_timestamp, 'year'):
                    birth_year = birth_timestamp.year
                else:
                    birth_year = "未知"
            else:
                birth_year = "未知"
            
            # 評級標籤
            rating_tag = ""
            if score >= THRESHOLD_PERFECT_MATCH:
                rating_tag = "🏆 極品"
            elif score >= THRESHOLD_EXCELLENT_MATCH:
                rating_tag = "⭐ 上等"
            elif score >= THRESHOLD_GOOD_MATCH:
                rating_tag = "✅ 良好"
            else:
                rating_tag = "🔄 可考慮"
            
            result_text += f"{i}. **{rating_tag}婚配** - {score:.1f}分\n"
            result_text += f"   • 關係模型：{model}\n"
            result_text += f"   • 對方日主：{candidate_stem} ({candidate_element})\n"
            result_text += f"   • 出生年份：{birth_year}\n"
            result_text += f"   • 五行能量：{result.get('primary_element', '未知')}\n"
            
            # 添加簡要分析
            brief_analysis = self._get_brief_analysis(user_day_element, candidate_element, model)
            if brief_analysis:
                result_text += f"   • 簡要分析：{brief_analysis}\n"
            
            result_text += "\n"
        
        # ========== 3.4 添加使用建議 ==========
        result_text += "💡 **使用建議**\n"
        result_text += "• 分數越高代表八字配合度越好\n"
        result_text += "• 關係模型反映雙方互動模式\n"
        result_text += "• 可記下高分對象的出生時間進一步了解\n"
        result_text += "• 實際相處仍需雙方共同努力\n"
        
        return result_text
    
    def _get_brief_analysis(self, user_element: str, candidate_element: str, model: str) -> str:
        """
        獲取簡要分析
        
        Args:
            user_element: 用戶五行
            candidate_element: 候選五行
            model: 關係模型
            
        Returns:
            簡要分析文本
        """
        # 五行相生關係
        element_relationships = {
            '木': {'生': '火', '被生': '水', '剋': '土', '被剋': '金'},
            '火': {'生': '土', '被生': '木', '剋': '金', '被剋': '水'},
            '土': {'生': '金', '被生': '火', '剋': '水', '被剋': '木'},
            '金': {'生': '水', '被生': '土', '剋': '木', '被剋': '火'},
            '水': {'生': '木', '被生': '金', '剋': '火', '被剋': '土'}
        }
        
        if user_element not in element_relationships or candidate_element not in element_relationships:
            return ""
        
        user_rel = element_relationships[user_element]
        
        if candidate_element == user_rel['生']:
            return "對方五行生你（相生）"
        elif candidate_element == user_rel['被生']:
            return "你生對方五行（付出型）"
        elif candidate_element == user_rel['剋']:
            return "你剋對方五行（主導型）"
        elif candidate_element == user_rel['被剋']:
            return "對方五行剋你（被動型）"
        else:
            return "五行相同（同類）"
    
    # ========== 4. 批量搜索方法 ==========
    
    async def batch_search_soulmates(self, user_data: Dict, year_ranges: List[Tuple[int, int]], 
                                    purpose: str = "正緣") -> Dict[str, List[Dict]]:
        """
        批量搜索多個年份範圍
        
        Args:
            user_data: 用戶數據
            year_ranges: 年份範圍列表 [(start1, end1), (start2, end2), ...]
            purpose: 搜索目的
            
        Returns:
            各年份範圍的結果
        """
        all_results = {}
        
        for start_year, end_year in year_ranges:
            try:
                results = await self.find_soulmate_for_user(
                    user_data, start_year, end_year, purpose
                )
                all_results[f"{start_year}-{end_year}"] = results
                
                # 防止過度查詢
                if len(all_results) >= 3:
                    logger.info("已搜索3個範圍，提前停止")
                    break
                    
            except Exception as e:
                logger.error(f"搜索範圍 {start_year}-{end_year} 失敗: {e}")
                all_results[f"{start_year}-{end_year}"] = []
        
        return all_results

# ========== 文件結尾：Section目錄 ==========
"""
1. 主要搜索方法
   1.1 驗證參數
   1.2 獲取用戶八字數據
   1.3 確定搜索性別
   1.4 從精英庫獲取候選
   1.5 計算匹配分數
      1.5.1 檢查候選數據完整性
      1.5.2 計算配對分數
      1.5.3 只保留高質量匹配
      1.5.4 提前停止條件
   1.6 按分數排序

2. 輔助方法

3. 結果格式化方法
   3.1 獲取用戶日主信息
   3.2 構建結果文本
   3.3 添加結果列表
   3.4 添加使用建議

4. 批量搜索方法
"""
