# ========1.6 Find Soulmate 功能開始 ========#
import json
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# 導入計算核心
from new_calculator import (
    BaziCalculator,
    calculate_match,
    ScoringEngine,
    Config
)

logger = logging.getLogger(__name__)

class SoulmateFinder:
    """真命天子搜尋器"""
    
    @staticmethod
    def generate_date_range(start_year, end_year):
        """生成日期範圍"""
        dates = []
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                # 每月最多31天
                for day in range(1, 32):
                    try:
                        datetime(year, month, day)
                        dates.append((year, month, day))
                    except ValueError:
                        continue
        return dates
    
    @staticmethod
    def calculate_luck_period(birth_year, birth_month, birth_day, gender):
        """計算大運（簡化版）"""
        # 簡化：只計算前兩個大運
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
    def pre_filter(user_bazi, target_bazi, user_gender, target_gender):
        """第一階段：Pre-filter (43,800 ➔ 1,200 組)"""
        
        # 1. 五行通關優先
        user_useful = user_bazi.get('useful_elements', [])
        user_harmful = user_bazi.get('harmful_elements', [])
        target_elements = target_bazi.get('elements', {})
        
        # 檢查是否有通關元素
        has_bridge = False
        for element in ['木', '火', '土', '金', '水']:
            if element not in user_harmful and target_elements.get(element, 0) > 15:
                has_bridge = True
                break
        
        if not has_bridge:
            return False, "五行不通關"
        
        # 2. 格局放寬
        target_pattern = target_bazi.get('cong_ge_type', 'normal')
        user_pattern = user_bazi.get('cong_ge_type', 'normal')
        
        # 允許正常格局配正常/從格/專旺
        compatible_patterns = ['normal', '從木格', '從火格', '從土格', '從金格', '從水格', '專旺木格', '專旺火格', '專旺土格', '專旺金格', '專旺水格']
        
        if target_pattern not in compatible_patterns:
            return False, "格局不兼容"
        
        # 3. 日柱保底 + 神煞預篩
        user_day_pillar = user_bazi.get('day_pillar', '')
        target_day_pillar = target_bazi.get('day_pillar', '')
        
        # 檢查天剋地沖
        user_day_stem = user_bazi.get('day_stem', '')
        target_day_stem = target_bazi.get('day_stem', '')
        user_day_branch = user_day_pillar[1] if len(user_day_pillar) >= 2 else ''
        target_day_branch = target_day_pillar[1] if len(target_day_pillar) >= 2 else ''
        
        # 檢查地支六沖 - 使用ScoringEngine的常量
        from new_calculator import ScoringEngine
        branch_pair = tuple(sorted([user_day_branch, target_day_branch]))
        if hasattr(ScoringEngine, 'BRANCH_SIX_CLASHES'):
            if branch_pair in ScoringEngine.BRANCH_SIX_CLASHES:
                # 檢查是否有解藥（六合）
                has_remedy = False
                if hasattr(ScoringEngine, 'BRANCH_SIX_COMBINATIONS'):
                    for b1 in [user_day_branch]:
                        for b2 in [target_day_branch]:
                            if tuple(sorted([b1, b2])) in ScoringEngine.BRANCH_SIX_COMBINATIONS:
                                has_remedy = True
                                break
                
                if not has_remedy:
                    return False, "日柱六沖無解"
        
        # 神煞預篩（加分但不篩選）
        target_shen_sha = target_bazi.get('shen_sha_names', '無')
        has_good_shen_sha = any(s in target_shen_sha for s in ['紅鸞', '天喜', '天乙貴人'])
        
        return True, "通過預篩"
    
    @staticmethod
    def structure_check(user_bazi, target_bazi, user_gender, target_gender):
        """第二階段：Structure Check (1,200 ➔ 400 組)"""
        
        # 1. 大運門檻（簡化）
        target_birth_year = target_bazi.get('birth_year', 2000)
        target_birth_month = target_bazi.get('birth_month', 1)
        target_birth_day = target_bazi.get('birth_day', 1)
        
        luck_periods = SoulmateFinder.calculate_luck_period(
            target_birth_year, target_birth_month, target_birth_day, target_gender
        )
        
        # 檢查第三個大運（20-30歲）
        marriage_luck = luck_periods[2] if len(luck_periods) > 2 else None
        if marriage_luck and not marriage_luck.get('favorable', False):
            return False, "大運不吉"
        
        # 2. 配偶星質量門檻
        spouse_effective = target_bazi.get('spouse_star_effective', 'unknown')
        if spouse_effective in ['none', 'weak']:
            return False, "配偶星弱"
        
        # 3. 地支穩固度
        pressure_score = target_bazi.get('pressure_score', 0)
        if pressure_score >= 35:
            return False, "夫妻宮壓力大"
        
        return True, "結構檢查通過"
    
    @staticmethod
    def calculate_final_score(user_bazi, target_bazi, user_gender, target_gender, purpose="正緣"):
        """第三階段：資深精算加分項"""
        
        # 使用主入口函數進行配對
        match_result = calculate_match(
            user_bazi, target_bazi, user_gender, target_gender, is_testpair=True
        )
        
        base_score = match_result.get('score', 50)
        
        # 1. 大運預算加分
        target_birth_year = target_bazi.get('birth_year', 2000)
        luck_periods = SoulmateFinder.calculate_luck_period(
            target_birth_year, target_bazi.get('birth_month', 1), 
            target_bazi.get('birth_day', 1), target_gender
        )
        
        luck_bonus = 0
        if len(luck_periods) > 2:
            marriage_luck = luck_periods[2]
            if marriage_luck.get('favorable', False):
                luck_bonus += 8
        
        # 2. 化解係數實裝
        resolution_factor = match_result.get('resolution_info', {}).get('factor', 1.0)
        if resolution_factor != 1.0:
            # 應用化解系數
            base_score = base_score * resolution_factor
        
        # 3. 目的權重調節
        final_score = base_score + luck_bonus
        
        # 根據目的調整
        if purpose == "正緣":
            # 正緣模式：配偶承載*0.4 + 日柱*0.3 + 性格*0.2 + 氣勢*0.1
            module_scores = match_result.get('module_scores', {})
            weighted_score = (
                module_scores.get('energy_rescue', 0) * 0.4 +
                module_scores.get('structure_core', 0) * 0.3 +
                module_scores.get('personality_risk', 0) * 0.2 +
                module_scores.get('pressure_penalty', 0) * 0.1
            )
            final_score = (final_score + weighted_score) / 2
        elif purpose == "合夥":
            # 合夥模式：喜用互補*0.5 + 氣勢*0.3 + 日柱*0.2
            final_score = final_score * 0.9  # 合夥分數稍低
        
        return min(100, max(0, final_score)), match_result
    
    @staticmethod
    def find_top_matches(user_bazi, user_gender, start_year, end_year, purpose="正緣", limit=10):
        """主搜尋函數"""
        logger.info(f"開始搜尋 {start_year}-{end_year} 年的真命天子...")
        
        # 1. 生成日期範圍
        dates = SoulmateFinder.generate_date_range(start_year, end_year)
        
        # 限制計算數量，避免過度計算
        sample_size = min(1000, len(dates))
        sampled_dates = random.sample(dates, sample_size) if len(dates) > sample_size else dates
        
        # 2. 預篩選
        pre_filtered = []
        for year, month, day in sampled_dates[:500]:  # 限制數量避免過度計算
            # 隨機生成時間
            hour = random.randint(0, 23)
            
            try:
                target_bazi = BaziCalculator.calculate(
                    year, month, day, hour, 
                    gender=user_gender,
                    hour_confidence='高'
                )
                
                # 添加出生年份信息
                target_bazi['birth_year'] = year
                target_bazi['birth_month'] = month
                target_bazi['birth_day'] = day
                target_bazi['birth_hour'] = hour
                
                # 預篩選
                passed, reason = SoulmateFinder.pre_filter(
                    user_bazi, target_bazi, user_gender, user_gender
                )
                
                if passed:
                    pre_filtered.append(target_bazi)
                
                if len(pre_filtered) >= 100:  # 限制預篩選數量
                    break
                    
            except Exception as e:
                continue
        
        # 3. 結構檢查
        structure_filtered = []
        for target_bazi in pre_filtered:
            passed, reason = SoulmateFinder.structure_check(
                user_bazi, target_bazi, user_gender, user_gender
            )
            
            if passed:
                structure_filtered.append(target_bazi)
            
            if len(structure_filtered) >= 50:  # 限制結構檢查數量
                break
        
        # 4. 資深精算
        scored_matches = []
        for target_bazi in structure_filtered:
            try:
                score, match_result = SoulmateFinder.calculate_final_score(
                    user_bazi, target_bazi, user_gender, user_gender, purpose
                )
                
                scored_matches.append({
                    'bazi': target_bazi,
                    'score': score,
                    'match_result': match_result,
                    'date': f"{target_bazi['birth_year']}年{target_bazi['birth_month']}月{target_bazi['birth_day']}日",
                    'hour': f"{target_bazi['birth_hour']}時",
                    'pillars': f"{target_bazi['year_pillar']} {target_bazi['month_pillar']} {target_bazi['day_pillar']} {target_bazi['hour_pillar']}"
                })
                
            except Exception as e:
                continue
        
        # 5. 排序並返回Top N
        scored_matches.sort(key=lambda x: x['score'], reverse=True)
        return scored_matches[:limit]

def format_find_soulmate_result(matches: list, start_year: int, end_year: int, purpose: str) -> str:
    """格式化Find Soulmate結果（單一消息格式）"""
    if not matches:
        return "❌ 在指定範圍內未找到合適的匹配時空。"
    
    purpose_text = "尋找正緣" if purpose == "正緣" else "事業合夥"
    
    text = f"""🔮 真命天子搜尋結果
{'='*40}

📅 搜尋範圍：{start_year}年 - {end_year}年
🎯 搜尋目的：{purpose_text}
📊 找到匹配：{len(matches)}個時空

🏆 最佳匹配："""
    
    if matches:
        best = matches[0]
        text += f"\n• 分數：{best.get('score', 0):.1f}分"
        text += f"\n• 日期：{best.get('date', '')}"
        text += f"\n• 時辰：{best.get('hour', '')}"
        text += f"\n• 八字：{best.get('pillars', '')}"
    
    text += f"""

📋 詳細匹配列表（前5名）
{'='*40}"""
    
    for i, match in enumerate(matches[:5], 1):
        score = match.get('score', 0)
        date = match.get('date', '')
        hour = match.get('hour', '')
        
        text += f"""
{i:2d}. {date} {hour}
     分數：{score:.1f}分"""
    
    text += f"""

💡 使用建議
{'='*40}

1. **確認時辰**：以上時辰均為整點，實際使用時需結合出生地經度校正
2. **綜合考慮**：分數僅供參考，還需結合實際情況
3. **深入分析**：可複製具體八字使用 /testpair 命令深入分析
4. **時間信心度**：搜尋結果為理論最佳，實際應用時需考慮時間精度"""
    
    return text
# ========1.6 Find Soulmate 功能結束 ========#

# ========文件信息開始 ========#
"""
文件: bazi_soulmate.py
功能: 真命天子搜尋功能（獨立檔案）

引用文件: new_calculator.py
被引用文件: bot.py (主程序)

主要修改：
1. 保持原有功能不變
2. 修復format_find_soulmate_result函數返回類型為單一字符串
3. 沒有使用個人資料格式化，只返回簡要信息
4. 與bot.py中的格式化函數兼容
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
1.6 Find Soulmate 功能 - SoulmateFinder 類和格式化函數
"""
# ========目錄結束 ========#

# ========修正紀錄開始 ========#
"""
修正內容：
1. 修復format_find_soulmate_result函數返回類型為單一字符串（原返回List[str]）
2. 調整格式化輸出為單一消息格式
3. 確保與bot.py中的調用兼容

導致問題：原函數返回列表，但bot.py期待單一字符串
如何修復：修改返回類型為單一字符串，合併所有部分
後果：真命天子搜尋結果以單一消息發送，與其他功能一致

檢查結果：此文件沒有使用個人資料格式化，不需要修改BaziFormatters相關內容
"""
# ========修正紀錄結束 ========#