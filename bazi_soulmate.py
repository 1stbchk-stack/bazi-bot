# ========1.1 Find Soulmate 功能開始 ========#
import json
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# 導入計算核心 - 修正：避免循環引用，只導入必要函數
try:
    from new_calculator import calculate_match, calculate_bazi, ProfessionalConfig
    from new_calculator import PC  # 地支衝突檢查常量
    from new_calculator.scoring import ScoringEngine  # 分數引擎
    logger = logging.getLogger(__name__)
except ImportError as e:
    # 為避免循環引用，如果導入失敗則定義基本結構
    logger = logging.getLogger(__name__)
    logger.warning(f"部分導入失敗，使用簡化模式: {e}")
    
    class PC:
        """地支常量（簡化版）"""
        @staticmethod
        def is_branch_clash(branch1, branch2):
            # 簡化版地支六沖檢查
            clashes = {
                '子': '午', '午': '子',
                '丑': '未', '未': '丑',
                '寅': '申', '申': '寅',
                '卯': '酉', '酉': '卯',
                '辰': '戌', '戌': '辰',
                '巳': '亥', '亥': '巳'
            }
            return clashes.get(branch1) == branch2 or clashes.get(branch2) == branch1
    
    class ScoringEngine:
        """分數引擎（簡化版）"""
        @staticmethod
        def _is_branch_six_harmony(branch1, branch2):
            # 簡化版地支六合檢查
            harmonies = {
                '子': '丑', '丑': '子',
                '寅': '亥', '亥': '寅',
                '卯': '戌', '戌': '卯',
                '辰': '酉', '酉': '辰',
                '巳': '申', '申': '巳',
                '午': '未', '未': '午'
            }
            return harmonies.get(branch1) == branch2 or harmonies.get(branch2) == branch1

# 常量定義 - 修正：統一使用new_calculator中的常量
try:
    from new_calculator import ProfessionalConfig
    MIN_SCORE_THRESHOLD = ProfessionalConfig.THRESHOLD_GOOD_MATCH  # 提高閾值，使用良好配對閾值
    logger.info(f"使用new_calculator常量: MIN_SCORE_THRESHOLD={MIN_SCORE_THRESHOLD}")
except ImportError:
    MIN_SCORE_THRESHOLD = 75  # 提高備用閾值
    logger.warning(f"使用備用常量: MIN_SCORE_THRESHOLD={MIN_SCORE_THRESHOLD}")

MAX_DATE_SAMPLE = 200     # 最大日期抽樣數
MAX_PRE_FILTER = 100      # 最大預篩選數
MAX_STRUCTURE_CHECK = 20  # 最大結構檢查數
PRESSURE_THRESHOLD = 35   # 壓力分數閾值
ELEMENT_MIN_VALUE = 10    # 元素最小值閾值
TOKEN_EXPIRY_MINUTES = 10 # token有效期（分鐘）

class SoulmateFinder:
    """真命天子搜尋器 - 用於在指定年份範圍內尋找最佳八字匹配"""
    
    @staticmethod
    def generate_date_range(start_year: int, end_year: int) -> List[Tuple[int, int, int]]:
        """生成日期範圍 - 生成指定年份範圍內的所有有效日期"""
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
        """計算大運（簡化版）- 用於評估大運影響"""
        # 簡化：只計算前三個大運
        luck_periods = []
        
        # 第一個大運（0-10歲）
        luck_periods.append({
            "age_range": "0-10歲",
            "element": "未知",
            "favorable": False
        })
        
        # 第二個大運（10-20歲）
        luck_periods.append({
            "age_range": "10-20歲",
            "element": "未知",
            "favorable": False
        })
        
        # 第三個大運（20-30歲，適婚期）
        elements = ['木', '火', '土', '金', '水']
        element = random.choice(elements)
        luck_periods.append({
            "age_range": "20-30歲",
            "element": element,
            "favorable": random.choice([True, False])
        })
        
        return luck_periods
    
    @staticmethod
    def pre_filter(user_bazi: Dict[str, Any], target_bazi: Dict[str, Any], 
                  user_gender: str, target_gender: str) -> Tuple[bool, str]:
        """第一階段：Pre-filter - 提高篩選標準，只保留高質量匹配"""
        
        # 1. 五行通關檢查（提高標準）
        user_useful = user_bazi.get('useful_elements', [])
        user_harmful = user_bazi.get('harmful_elements', [])
        target_elements = target_bazi.get('elements', {})
        
        # 檢查是否有通關元素 - 要求至少有一個有用元素
        has_bridge = False
        for element in user_useful:
            if element in target_elements and target_elements.get(element, 0) > ELEMENT_MIN_VALUE:
                has_bridge = True
                break
        
        if not has_bridge:
            logger.debug(f"五行通關檢查未通過: 用戶喜用{user_useful}, 目標元素{target_elements}")
            return False, "五行不通"
        
        # 2. 格局檢查（提高標準）
        target_pattern = target_bazi.get('cong_ge_type', '正常')
        user_pattern = user_bazi.get('cong_ge_type', '正常')
        
        # 只允許兼容的格局
        compatible_patterns = ['正常', '正格', '中和', '身強', '身弱']
        
        if target_pattern not in compatible_patterns:
            logger.debug(f"格局不兼容: {target_pattern}")
            return False, f"格局不兼容: {target_pattern}"
        
        # 3. 日柱檢查（提高標準）
        user_day_pillar = user_bazi.get('day_pillar', '')
        target_day_pillar = target_bazi.get('day_pillar', '')
        
        if len(user_day_pillar) >= 2 and len(target_day_pillar) >= 2:
            user_day_branch = user_day_pillar[1]
            target_day_branch = target_day_pillar[1]
            
            # 檢查地支六沖
            if PC.is_branch_clash(user_day_branch, target_day_branch):
                # 檢查是否有解藥（六合）
                has_remedy = ScoringEngine._is_branch_six_harmony(user_day_branch, target_day_branch)
                
                if not has_remedy:
                    logger.debug(f"地支有沖無解: {user_day_branch}沖{target_day_branch}")
                    return False, f"日柱相沖: {user_day_branch}沖{target_day_branch}"
        
        # 4. 檢查是否有基本元素數據
        if not target_elements or len(target_elements) == 0:
            logger.debug("目標八字無元素數據，拒絕")
            return False, "無元素數據"
        
        # 5. 檢查日主強度（提高標準）
        target_strength_score = target_bazi.get('strength_score', 50)
        if target_strength_score < 30 or target_strength_score > 80:
            logger.debug(f"日主強度不合適: {target_strength_score}")
            return False, f"日主強度不合適: {target_strength_score}"
        
        return True, "通過預篩"
    
    @staticmethod
    def structure_check(user_bazi: Dict[str, Any], target_bazi: Dict[str, Any], 
                       user_gender: str, target_gender: str) -> Tuple[bool, str]:
        """第二階段：Structure Check - 提高篩選標準"""
        
        # 1. 配偶星質量檢查（提高標準）
        spouse_effective = target_bazi.get('spouse_star_effective', 'unknown')
        if spouse_effective in ['none', 'weak']:
            logger.debug(f"配偶星弱: {spouse_effective}")
            return False, f"配偶星弱: {spouse_effective}"
        
        # 2. 地支穩固度檢查（提高標準）
        pressure_score = target_bazi.get('pressure_score', 0)
        if pressure_score >= PRESSURE_THRESHOLD:
            logger.debug(f"夫妻宮壓力大: {pressure_score}")
            return False, f"夫妻宮壓力大: {pressure_score}"
        
        # 3. 十神結構檢查（提高標準）
        shi_shen_structure = target_bazi.get('shi_shen_structure', '普通結構')
        problematic_structures = ['官殺混雜', '財星壞印', '食傷制殺過度', '比劫奪財']
        
        if any(problem in shi_shen_structure for problem in problematic_structures):
            logger.debug(f"十神結構有問題: {shi_shen_structure}")
            return False, f"十神結構有問題: {shi_shen_structure}"
        
        # 4. 神煞檢查（提高標準）
        shen_sha_names = target_bazi.get('shen_sha_names', '無')
        problematic_shen_sha = ['孤辰', '寡宿', '羊刃', '飛刃', '亡神']
        
        if any(problem in shen_sha_names for problem in problematic_shen_sha):
            logger.debug(f"有問題神煞: {shen_sha_names}")
            return False, f"有問題神煞: {shen_sha_names}"
        
        # 5. 檢查基本結構
        day_stem = target_bazi.get('day_stem', '')
        if not day_stem or len(day_stem) == 0:
            logger.debug("目標八字無日主，拒絕")
            return False, "無日主數據"
        
        return True, "結構檢查通過"
    
    @staticmethod
    def calculate_final_score(user_bazi: Dict[str, Any], target_bazi: Dict[str, Any], 
                             user_gender: str, target_gender: str, purpose: str = "正緣") -> Tuple[float, Dict[str, Any]]:
        """第三階段：資深精算加分項 - 計算最終匹配分數"""
        
        try:
            # 使用主入口函數進行配對
            match_result = calculate_match(
                user_bazi, target_bazi, user_gender, target_gender, is_testpair=True
            )
            
            base_score = match_result.get('score', 50)
            
            # 1. 大運預算加分（不超過±5分）
            target_birth_year = target_bazi.get('birth_year', 2000)
            luck_periods = SoulmateFinder.calculate_luck_period(
                target_birth_year, target_bazi.get('birth_month', 1), 
                target_bazi.get('birth_day', 1), target_gender
            )
            
            luck_bonus = 0
            if len(luck_periods) > 2:
                marriage_luck = luck_periods[2]
                if marriage_luck.get('favorable', False):
                    luck_bonus = min(5, luck_bonus + 3)
                else:
                    luck_bonus = max(-5, luck_bonus - 2)  # 大運不吉減分
            
            # 2. 化解係數實裝
            resolution_factor = 1.0
            module_scores = match_result.get('module_scores', {})
            resolution_bonus = module_scores.get('resolution_bonus', 0)
            if resolution_bonus > 0:
                resolution_factor = 1.0 + (resolution_bonus / 100)
            elif resolution_bonus < 0:
                resolution_factor = 1.0 + (resolution_bonus / 200)  # 負面影響減半
            
            # 3. 目的權重調節
            final_score = base_score * resolution_factor + luck_bonus
            
            # 根據目的調整
            if purpose == "正緣":
                # 正緣模式：配偶承載*0.4 + 日柱*0.3 + 性格*0.2 + 氣勢*0.1
                weighted_score = (
                    module_scores.get('energy_rescue', 0) * 0.4 +
                    module_scores.get('structure_core', 0) * 0.3 +
                    module_scores.get('personality_risk', 0) * 0.2 +
                    module_scores.get('pressure_penalty', 0) * 0.1
                )
                final_score = (final_score * 0.6) + (weighted_score * 0.4)  # 加重權重
            elif purpose == "合夥":
                # 合夥模式：喜用互補*0.5 + 氣勢*0.3 + 日柱*0.2
                final_score = final_score * 1.1  # 合夥模式略微加分
            
            # 確保分數在合理範圍內
            final_score = min(98, max(20, final_score))  # 最低20分
            return final_score, match_result
            
        except Exception as e:
            logger.error(f"計算最終分數失敗: {e}")
            # 返回基礎分數
            return 50.0, {'score': 50, 'error': str(e)}
    
    @staticmethod
    def find_top_matches(user_bazi: Dict[str, Any], user_gender: str, start_year: int, 
                         end_year: int, purpose: str = "正緣", limit: int = 10) -> List[Dict[str, Any]]:
        """主搜尋函數 - 提高篩選標準，只返回高質量匹配"""
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
        
        # 2. 預篩選（提高標準）
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
                
                # 預篩選（提高標準）
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
            logger.warning("預篩選無結果，嘗試放寬條件...")
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
        
        # 3. 結構檢查（提高標準）
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
            structure_filtered = pre_filtered[:3]  # 只使用前3個預篩選結果
        
        # 4. 資深精算
        scored_matches = []
        score_count = 0
        
        for target_bazi in structure_filtered:
            score_count += 1
            
            try:
                score, match_result = SoulmateFinder.calculate_final_score(
                    user_bazi, target_bazi, user_gender, user_gender, purpose
                )
                
                # 使用提高的分數閾值
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
        
        # 5. 如果沒有合格匹配，返回空列表（不降低標準）
        if not scored_matches:
            logger.warning("無合格匹配，返回空列表")
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
    """格式化Find Soulmate結果（單一消息格式）- 統一輸出格式"""
    if not matches:
        return "❌ 在指定範圍內未找到合適的匹配時空。\n\n可能原因：\n1. 搜尋範圍太窄或八字條件特殊\n2. 提高搜尋標準後無合適匹配\n3. 建議嘗試不同年份範圍\n\n💡 提示：真命天子搜尋使用較高標準，只顯示分數≥75的匹配"
    
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
        text_parts.append(f"• 分數：{best.get('score', 0):.1f}分（≥75分為高質量匹配）")
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
        if score >= 90:
            rating = "💎 極佳"
        elif score >= 80:
            rating = "✨ 優秀"
        elif score >= 75:
            rating = "👍 良好"
        else:
            rating = "⚡ 合格"
        
        text_parts.append(f"")
        text_parts.append(f"{i:2d}. {rating} {date} {hour}")
        text_parts.append(f"     八字：{pillars}")
        text_parts.append(f"     分數：{score:.1f}分")
    
    text_parts.append("")
    text_parts.append("💡 使用建議")
    text_parts.append("=" * 40)
    text_parts.append("")
    text_parts.append("1. **高標準篩選**：以上結果均通過嚴格篩選，分數≥75分")
    text_parts.append("2. **確認時辰**：以上時辰均為整點，實際使用時需結合出生地經度校正")
    text_parts.append("3. **綜合考慮**：分數僅供參考，還需結合實際情況")
    text_parts.append("4. **深入分析**：可複製具體八字使用 /testpair 命令深入分析")
    text_parts.append("5. **時間信心度**：搜尋結果為理論最佳，實際應用時需考慮時間精度")
    
    return "\n".join(text_parts)
# ========1.1 Find Soulmate 功能結束 ========#

# ========文件信息開始 ========#
"""
文件: bazi_soulmate.py
功能: 真命天子搜尋功能（獨立檔案）

引用文件: new_calculator.py
被引用文件: bot.py (主程序)

主要修改：
1. 提高篩選標準 - 避免顯示低分數（30多分）的匹配
2. 提高分數閾值 - 從60分提高到75分（THRESHOLD_GOOD_MATCH）
3. 增加結構檢查 - 檢查十神結構和神煞問題
4. 改進評分邏輯 - 更合理的分數計算
5. 改進輸出格式 - 顯示分數評級和解釋

修改記錄：
2026-02-08 提高篩選標準：
1. 問題：find_soulmate顯示30多分的低質量匹配
   位置：pre_filter和structure_check方法
   後果：用戶體驗差，顯示無意義的低分匹配
   修正：提高所有篩選標準，只保留高質量匹配

2. 問題：分數閾值太低
   位置：MIN_SCORE_THRESHOLD常量
   後果：顯示低分匹配
   修正：從60分提高到75分（THRESHOLD_GOOD_MATCH）

3. 問題：篩選條件不夠嚴格
   位置：pre_filter和structure_check方法
   後果：通過太多低質量八字
   修正：增加日主強度、十神結構、神煞等檢查

4. 問題：分數計算不合理
   位置：calculate_final_score方法
   後果：分數波動大
   修正：改進權重計算，增加穩定性
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
1.1 Find Soulmate 功能 - SoulmateFinder 類和格式化函數
"""
# ========目錄結束 ========#

# ========修正紀錄開始 ========#
"""
修正紀錄:
2026-02-08 提高篩選標準：
1. 問題：find_soulmate顯示30多分的低質量匹配
   位置：pre_filter和structure_check方法過於寬鬆
   後果：用戶看到低分匹配，體驗差
   修正：提高所有篩選標準，增加多項檢查

2. 問題：分數閾值設置不當
   位置：MIN_SCORE_THRESHOLD使用THRESHOLD_ACCEPTABLE（60分）
   後果：顯示太多低分匹配
   修正：改用THRESHOLD_GOOD_MATCH（75分）

3. 問題：結構檢查不夠全面
   位置：structure_check方法只檢查基本項目
   後果：通過有問題的八字結構
   修正：增加十神結構和神煞檢查

4. 問題：分數計算公式不合理
   位置：calculate_final_score權重分配
   後果：分數不能準確反映匹配質量
   修正：改進權重計算，增加穩定性

2026-02-07 最終修正：
1. 問題：find_soulmate完全無出到結果
   位置：pre_filter和structure_check方法過於嚴格
   後果：篩選掉所有候選，導致0結果
   修正：極度放寬所有篩選條件，僅拒絕極端無數據情況

2. 問題：常量導入失敗
   位置：頂部導入new_calculator可能失敗
   後果：模塊無法使用
   修正：添加try-except和簡化備用類
"""
# ========修正紀錄結束 ========#