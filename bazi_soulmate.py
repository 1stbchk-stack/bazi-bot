# ========1.1 Find Soulmate 功能開始 ========#
import json
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# 導入計算核心
try:
    from new_calculator import calculate_match, calculate_bazi, ProfessionalConfig
    from new_calculator import PC
    logger = logging.getLogger(__name__)
except ImportError as e:
    # 為避免循環引用，如果導入失敗則定義基本結構
    logger = logging.getLogger(__name__)
    logger.warning(f"部分導入失敗，使用簡化模式: {e}")
    
    class PC:
        """1.1.1 地支常量（簡化版）"""
        @staticmethod
        def is_branch_clash(branch1, branch2):
            """1.1.1.1 檢查地支六沖（簡化版）"""
            clashes = {
                '子': '午', '午': '子',
                '丑': '未', '未': '丑',
                '寅': '申', '申': '寅',
                '卯': '酉', '酉': '卯',
                '辰': '戌', '戌': '辰',
                '巳': '亥', '亥': '巳'
            }
            return clashes.get(branch1) == branch2 or clashes.get(branch2) == branch1

# 常量定義
try:
    MIN_SCORE_THRESHOLD = 65  # 降低分數閾值以提高匹配率
except ImportError:
    MIN_SCORE_THRESHOLD = 65

MAX_DATE_SAMPLE = 200     # 最大日期抽樣數
MAX_PRE_FILTER = 100      # 最大預篩選數
MAX_STRUCTURE_CHECK = 20  # 最大結構檢查數
TOKEN_EXPIRY_MINUTES = 10 # token有效期（分鐘）

class SoulmateFinder:
    """1.1.3 真命天子搜尋器 - 用於在指定年份範圍內尋找最佳八字匹配"""
    
    @staticmethod
    def generate_date_range(start_year: int, end_year: int) -> List[Tuple[int, int, int]]:
        """1.1.3.1 生成日期範圍 - 生成指定年份範圍內的所有有效日期"""
        dates = []
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                # 每月最多31天，實際天數由datetime驗證
                max_day = 31
                if month in [4, 6, 9, 11]:
                    max_day = 30
                elif month == 2:
                    # 閏年檢查
                    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                        max_day = 29
                    else:
                        max_day = 28
                
                for day in range(1, max_day + 1):
                    dates.append((year, month, day))
        return dates
    
    @staticmethod
    def calculate_luck_period(birth_year: int, birth_month: int, birth_day: int, gender: str) -> List[Dict[str, Any]]:
        """1.1.3.2 計算大運（簡化版）- 用於評估大運影響"""
        # 簡化：只返回一個基本的評估
        return [{
            "age_range": "20-40歲",
            "element": "需結合具體八字",
            "favorable": True,
            "simplified_score": 0  # 簡單評分，不影響總分
        }]
    
    @staticmethod
    def pre_filter(user_bazi: Dict[str, Any], target_bazi: Dict[str, Any], 
                  user_gender: str, target_gender: str) -> Tuple[bool, str]:
        """1.1.3.3 第一階段：Pre-filter - 極度簡化篩選，只保留最基本檢查"""
        
        # 1. 基本數據檢查
        if not target_bazi.get('year_pillar') or not target_bazi.get('day_stem'):
            return False, "八字數據不完整"
        
        # 2. 日柱相沖檢查（保留，重要檢查）
        user_day_pillar = user_bazi.get('day_pillar', '')
        target_day_pillar = target_bazi.get('day_pillar', '')
        
        if len(user_day_pillar) >= 2 and len(target_day_pillar) >= 2:
            user_day_branch = user_day_pillar[1]
            target_day_branch = target_day_pillar[1]
            
            # 檢查地支六沖
            if PC.is_branch_clash(user_day_branch, target_day_branch):
                return False, f"日柱相沖: {user_day_branch}沖{target_day_branch}"
        
        # 3. 日主極端情況檢查（放寬到只檢查極端無效值）
        target_strength_score = target_bazi.get('strength_score', 50)
        if target_strength_score < 5 or target_strength_score > 99:
            return False, f"日主強度極端無效: {target_strength_score}"
        
        return True, "通過預篩"
    
    @staticmethod
    def structure_check(user_bazi: Dict[str, Any], target_bazi: Dict[str, Any], 
                       user_gender: str, target_gender: str) -> Tuple[bool, str]:
        """1.1.3.4 第二階段：Structure Check - 極度簡化結構檢查"""
        
        # 1. 配偶星質量檢查（只檢查完全無配偶星的情況）
        spouse_effective = target_bazi.get('spouse_star_effective', 'unknown')
        if spouse_effective in ['none']:  # 只過濾完全無配偶星的情況
            return False, f"無配偶星"
        
        # 2. 只檢查極端十神結構問題
        shi_shen_structure = target_bazi.get('shi_shen_structure', '普通結構')
        # 只檢查極端問題結構
        problematic_structures = ['官殺混雜極重', '財星壞印嚴重']
        
        if any(problem in shi_shen_structure for problem in problematic_structures):
            return False, f"十神結構有問題: {shi_shen_structure}"
        
        return True, "結構檢查通過"
    
    @staticmethod
    def calculate_final_score(user_bazi: Dict[str, Any], target_bazi: Dict[str, Any], 
                             user_gender: str, target_gender: str, purpose: str = "正緣") -> Tuple[float, Dict[str, Any]]:
        """1.1.3.5 第三階段：資深精算加分項 - 計算最終匹配分數"""
        
        try:
            # 使用主入口函數進行配對
            match_result = calculate_match(
                user_bazi, target_bazi, user_gender, target_gender, is_testpair=True
            )
            
            base_score = match_result.get('score', 50)
            
            # 1. 大運預算加分（簡化）
            luck_bonus = 0
            
            # 2. 化解係數實裝
            resolution_factor = 1.0
            module_scores = match_result.get('module_scores', {})
            resolution_bonus = module_scores.get('resolution_bonus', 0)
            if resolution_bonus > 0:
                resolution_factor = 1.0 + (resolution_bonus / 100)
            
            # 3. 目的權重調節
            final_score = base_score * resolution_factor + luck_bonus
            
            # 根據目的調整
            if purpose == "正緣":
                # 正緣模式：配偶承載*0.3 + 日柱*0.3 + 性格*0.2 + 氣勢*0.2
                weighted_score = (
                    module_scores.get('energy_rescue', 0) * 0.3 +
                    module_scores.get('structure_core', 0) * 0.3 +
                    module_scores.get('personality_risk', 0) * 0.2 +
                    module_scores.get('pressure_penalty', 0) * 0.2
                )
                final_score = (final_score * 0.7) + (weighted_score * 0.3)
            elif purpose == "合夥":
                # 合夥模式：喜用互補*0.4 + 氣勢*0.3 + 日柱*0.3
                final_score = final_score * 1.05  # 合夥模式略微加分
            
            # 確保分數在合理範圍內
            final_score = min(98, max(20, final_score))
            return final_score, match_result
            
        except Exception as e:
            logger.error(f"計算最終分數失敗: {e}")
            # 返回基礎分數
            return 50.0, {'score': 50, 'error': str(e)}
    
    @staticmethod
    def find_top_matches(user_bazi: Dict[str, Any], user_gender: str, start_year: int, 
                         end_year: int, purpose: str = "正緣", limit: int = 10) -> List[Dict[str, Any]]:
        """1.1.3.6 主搜尋函數 - 提高匹配率，放寬篩選條件"""
        logger.info(f"開始搜尋 {start_year}-{end_year} 年的真命天子，目的: {purpose}")
        
        # 1. 生成日期範圍
        dates = SoulmateFinder.generate_date_range(start_year, end_year)
        logger.info(f"生成 {len(dates)} 個日期")
        
        # 限制計算數量，避免過度計算
        sample_size = min(MAX_DATE_SAMPLE, len(dates))
        if len(dates) > sample_size:
            sampled_dates = random.sample(dates, sample_size)
            logger.info(f"隨機抽樣 {sample_size} 個日期")
        else:
            sampled_dates = dates
            logger.info(f"使用全部 {len(dates)} 個日期")
        
        # 2. 預篩選（極度放寬條件）
        pre_filtered = []
        pre_filter_count = 0
        
        for year, month, day in sampled_dates[:MAX_PRE_FILTER]:
            pre_filter_count += 1
            
            # 隨機生成時間（0-23時）
            hour = random.randint(0, 23)
            
            try:
                # 計算目標八字
                target_bazi = calculate_bazi(
                    year, month, day, hour, 
                    gender=user_gender,  # 使用用戶性別作為目標性別
                    hour_confidence='高'
                )
                
                if not target_bazi:
                    logger.debug(f"八字計算返回空: {year}-{month}-{day} {hour}時")
                    continue
                
                # 添加出生年份信息
                target_bazi['birth_year'] = year
                target_bazi['birth_month'] = month
                target_bazi['birth_day'] = day
                target_bazi['birth_hour'] = hour
                
                # 預篩選（極度放寬條件）
                passed, reason = SoulmateFinder.pre_filter(
                    user_bazi, target_bazi, user_gender, user_gender
                )
                
                if passed:
                    pre_filtered.append(target_bazi)
                    logger.debug(f"預篩選通過: {year}-{month}-{day} {hour}時")
                else:
                    logger.debug(f"預篩選未通過: {reason}")
                
                if len(pre_filtered) >= 30:  # 限制預篩選數量
                    logger.info(f"預篩選達到30個，提前結束")
                    break
                    
            except Exception as e:
                logger.debug(f"計算八字失敗 {year}-{month}-{day} {hour}時: {e}")
                continue
        
        logger.info(f"預篩選完成: 處理{pre_filter_count}個，通過{len(pre_filtered)}個")
        
        if not pre_filtered:
            logger.warning("預篩選無結果，嘗試直接計算幾個日期")
            # 如果預篩選無結果，嘗試直接計算幾個日期
            backup_dates = [
                (start_year, 6, 15, 12),  # 年中中午
                (start_year + (end_year - start_year) // 2, 3, 21, 6),  # 中間年份春分早上
                (end_year, 12, 25, 18)   # 結束年份聖誕節傍晚
            ]
            
            for year, month, day, hour in backup_dates:
                try:
                    target_bazi = calculate_bazi(
                        year, month, day, hour, 
                        gender=user_gender,
                        hour_confidence='高'
                    )
                    if target_bazi:
                        target_bazi['birth_year'] = year
                        target_bazi['birth_month'] = month
                        target_bazi['birth_day'] = day
                        target_bazi['birth_hour'] = hour
                        pre_filtered.append(target_bazi)
                        logger.info(f"添加備用日期: {year}-{month}-{day} {hour}時")
                except Exception as e:
                    logger.debug(f"備用日期計算失敗: {e}")
            
            if not pre_filtered:
                logger.error("即使備用日期也無結果")
                return []
        
        # 3. 結構檢查（極度放寬條件）
        structure_filtered = []
        structure_count = 0
        
        for target_bazi in pre_filtered:
            structure_count += 1
            
            passed, reason = SoulmateFinder.structure_check(
                user_bazi, target_bazi, user_gender, user_gender
            )
            
            if passed:
                structure_filtered.append(target_bazi)
                logger.debug(f"結構檢查通過: {target_bazi.get('birth_year')}-{target_bazi.get('birth_month')}-{target_bazi.get('birth_day')}")
            else:
                logger.debug(f"結構檢查未通過: {reason}")
            
            if len(structure_filtered) >= MAX_STRUCTURE_CHECK:
                logger.info(f"結構檢查達到{MAX_STRUCTURE_CHECK}個，提前結束")
                break
        
        logger.info(f"結構檢查完成: 處理{structure_count}個，通過{len(structure_filtered)}個")
        
        if not structure_filtered:
            logger.warning("結構檢查無結果，使用預篩選結果")
            structure_filtered = pre_filtered[:5]  # 使用前5個預篩選結果
        
        # 4. 資深精算
        scored_matches = []
        score_count = 0
        
        for target_bazi in structure_filtered:
            score_count += 1
            
            try:
                score, match_result = SoulmateFinder.calculate_final_score(
                    user_bazi, target_bazi, user_gender, user_gender, purpose
                )
                
                # 使用降低的分數閾值以提高匹配率
                if score >= MIN_SCORE_THRESHOLD:
                    scored_matches.append({
                        'bazi': target_bazi,
                        'score': score,
                        'match_result': match_result,
                        'date': f"{target_bazi['birth_year']}年{target_bazi['birth_month']}月{target_bazi['birth_day']}日",
                        'hour': f"{target_bazi['birth_hour']}時",
                        'pillars': f"{target_bazi['year_pillar']} {target_bazi['month_pillar']} {target_bazi['day_pillar']} {target_bazi['hour_pillar']}"
                    })
                    logger.info(f"合格匹配: 分數={score:.1f}, 日期={target_bazi['birth_year']}-{target_bazi['birth_month']}-{target_bazi['birth_day']}")
                else:
                    logger.debug(f"分數不足: {score:.1f} < {MIN_SCORE_THRESHOLD}")
                
            except Exception as e:
                logger.debug(f"計算分數失敗: {e}")
                continue
        
        logger.info(f"分數計算完成: 處理{score_count}個，合格{len(scored_matches)}個")
        
        # 5. 如果沒有合格匹配，嘗試進一步降低標準
        if not scored_matches and structure_filtered:
            logger.warning("無合格匹配，嘗試降低標準...")
            # 選擇分數最高的幾個
            scored_matches = []
            for target_bazi in structure_filtered[:3]:
                try:
                    score, match_result = SoulmateFinder.calculate_final_score(
                        user_bazi, target_bazi, user_gender, user_gender, purpose
                    )
                    
                    # 進一步降低標準
                    if score >= 60:  # 降低到60分
                        scored_matches.append({
                            'bazi': target_bazi,
                            'score': score,
                            'match_result': match_result,
                            'date': f"{target_bazi['birth_year']}年{target_bazi['birth_month']}月{target_bazi['birth_day']}日",
                            'hour': f"{target_bazi['birth_hour']}時",
                            'pillars': f"{target_bazi['year_pillar']} {target_bazi['month_pillar']} {target_bazi['day_pillar']} {target_bazi['hour_pillar']}"
                        })
                        logger.info(f"降低標準後合格匹配: 分數={score:.1f}")
                except Exception as e:
                    logger.debug(f"降低標準計算分數失敗: {e}")
                    continue
        
        if not scored_matches:
            logger.warning("即使降低標準也無合格匹配，返回空列表")
            return []
        
        # 6. 排序並返回Top N
        if scored_matches:
            scored_matches.sort(key=lambda x: x['score'], reverse=True)
            result = scored_matches[:limit]
            logger.info(f"返回前{len(result)}個匹配，最低分數={result[-1]['score']:.1f}")
            return result
        else:
            logger.error("最終無任何匹配結果")
            return []

def format_find_soulmate_result(matches: List[Dict[str, Any]], start_year: int, 
                               end_year: int, purpose: str) -> str:
    """1.1.4 格式化Find Soulmate結果（單一消息格式）- 統一輸出格式"""
    if not matches:
        return "❌ 在指定範圍內未找到合適的匹配時空。\n\n可能原因：\n1. 搜尋範圍太窄或八字條件特殊\n2. 暫時沒有高質量匹配\n3. 建議嘗試不同年份範圍\n\n💡 提示：可以稍後再試或擴大搜尋範圍"
    
    purpose_text = "尋找正緣" if purpose == "正緣" else "事業合夥"
    
    text_parts = []
    text_parts.append(f"🔮 真命天子搜尋結果")
    text_parts.append("=" * 40)
    text_parts.append("")
    text_parts.append(f"📅 搜尋範圍：{start_year}年 - {end_year}年")
    text_parts.append(f"🎯 搜尋目的：{purpose_text}")
    text_parts.append(f"📊 找到匹配：{len(matches)}個高質量時空")
    text_parts.append("")
    
    if matches:
        best = matches[0]
        text_parts.append("🏆 最佳匹配：")
        text_parts.append(f"• 分數：{best.get('score', 0):.1f}分")
        text_parts.append(f"• 日期：{best.get('date', '')}")
        text_parts.append(f"• 時辰：{best.get('hour', '')}")
        text_parts.append(f"• 八字：{best.get('pillars', '')}")
    
    text_parts.append("")
    text_parts.append(f"📋 詳細匹配列表（前{min(5, len(matches))}名）")
    text_parts.append("=" * 40)
    
    for i, match in enumerate(matches[:5], 1):
        score = match.get('score', 0)
        date = match.get('date', '')
        hour = match.get('hour', '')
        pillars = match.get('pillars', '')
        
        # 根據分數添加評級
        if score >= 80:
            rating = "💎 極佳"
        elif score >= 70:
            rating = "✨ 優秀"
        elif score >= 65:
            rating = "👍 良好"
        elif score >= 60:
            rating = "⚡ 合格"
        else:
            rating = "📊 尚可"
        
        text_parts.append(f"")
        text_parts.append(f"{i:2d}. {rating} {date} {hour}")
        text_parts.append(f"     八字：{pillars}")
        text_parts.append(f"     分數：{score:.1f}分")
    
    text_parts.append("")
    text_parts.append("💡 使用建議")
    text_parts.append("=" * 40)
    text_parts.append("")
    text_parts.append("1. **理論最佳**：以上結果為理論上最匹配的出生時空")
    text_parts.append("2. **確認時辰**：時辰為整點，實際使用時需結合出生地經度校正")
    text_parts.append("3. **綜合考慮**：分數僅供參考，需結合實際情況")
    text_parts.append("4. **深入分析**：可複製具體八字使用 /testpair 命令深入分析")
    text_parts.append("5. **時間信心度**：搜尋結果為理論最佳，實際應用時需考慮時間精度")
    
    return "\n".join(text_parts)
# ========1.1 Find Soulmate 功能結束 ========#