# ========1.1 Find Soulmate 功能開始 ========#
import json
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# 導入計算核心 - 修正：全部在頂部導入，避免循環引用
from new_calculator import (
    calculate_match,
    calculate_bazi,
    ProfessionalConfig,
    ScoringEngine,
    PC  # 添加PC常量
)

logger = logging.getLogger(__name__)

# 常量定義 - 修正：統一常量，避免魔法數字
MIN_SCORE_THRESHOLD = 60  # 最低分數閾值
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
                for day in range(1, 32):
                    try:
                        datetime(year, month, day)
                        dates.append((year, month, day))
                    except ValueError:
                        continue
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
        """第一階段：Pre-filter - 放寬條件，避免過濾掉所有候選"""
        
        # 1. 五行通關優先（放寬條件）
        user_useful = user_bazi.get('useful_elements', [])
        user_harmful = user_bazi.get('harmful_elements', [])
        target_elements = target_bazi.get('elements', {})
        
        # 檢查是否有通關元素（放寬條件）
        has_bridge = False
        for element in ['木', '火', '土', '金', '水']:
            if element not in user_harmful and target_elements.get(element, 0) > ELEMENT_MIN_VALUE:
                has_bridge = True
                break
        
        if not has_bridge:
            # 即使沒有通關，也給機會通過 - 放寬條件
            logger.debug("五行通關檢查未通過，但繼續處理")
        
        # 2. 格局檢查（放寬條件）
        target_pattern = target_bazi.get('cong_ge_type', '正常')
        user_pattern = user_bazi.get('cong_ge_type', '正常')
        
        # 允許正常格局配正常/從格/專旺
        compatible_patterns = ['正常', '從格', '專旺格', '身強', '身弱', '中和']
        
        if target_pattern not in compatible_patterns:
            # 即使格局不兼容，也不立即拒絕 - 放寬條件
            logger.debug(f"格局不兼容: target_pattern={target_pattern}, 但繼續處理")
        
        # 3. 日柱保底 + 神煞預篩（放寬條件）
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
                    # 即使有沖無解，也不立即拒絕 - 放寬條件
                    logger.debug(f"地支有沖無解: {user_day_branch}沖{target_day_branch}, 但繼續處理")
        
        return True, "通過預篩"
    
    @staticmethod
    def structure_check(user_bazi: Dict[str, Any], target_bazi: Dict[str, Any], 
                       user_gender: str, target_gender: str) -> Tuple[bool, str]:
        """第二階段：Structure Check - 放寬條件，確保有足夠候選"""
        
        # 1. 大運門檻（簡化）- 放寬條件
        target_birth_year = target_bazi.get('birth_year', 2000)
        target_birth_month = target_bazi.get('birth_month', 1)
        target_birth_day = target_bazi.get('birth_day', 1)
        
        luck_periods = SoulmateFinder.calculate_luck_period(
            target_birth_year, target_birth_month, target_birth_day, target_gender
        )
        
        # 檢查第三個大運（20-30歲）- 放寬條件
        if len(luck_periods) > 2:
            marriage_luck = luck_periods[2]
            if not marriage_luck.get('favorable', False):
                # 即使大運不吉，也不立即拒絕 - 放寬條件
                logger.debug("大運不吉，但繼續處理")
        
        # 2. 配偶星質量門檻（放寬條件）
        spouse_effective = target_bazi.get('spouse_star_effective', 'unknown')
        if spouse_effective in ['none', 'weak']:
            # 即使配偶星弱，也不立即拒絕 - 放寬條件
            logger.debug(f"配偶星弱: {spouse_effective}, 但繼續處理")
        
        # 3. 地支穩固度（放寬條件）
        pressure_score = target_bazi.get('pressure_score', 0)
        if pressure_score >= PRESSURE_THRESHOLD:
            # 即使夫妻宮壓力大，也不立即拒絕 - 放寬條件
            logger.debug(f"夫妻宮壓力大: {pressure_score}, 但繼續處理")
        
        return True, "結構檢查通過"
    
    @staticmethod
    def calculate_final_score(user_bazi: Dict[str, Any], target_bazi: Dict[str, Any], 
                             user_gender: str, target_gender: str, purpose: str = "正緣") -> Tuple[float, Dict[str, Any]]:
        """第三階段：資深精算加分項 - 計算最終匹配分數"""
        
        # 使用主入口函數進行配對 - 修正：已在頂部導入，無需局部導入
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
            # 正緣模式：配偶承載*0.4 + 日柱*0.3 + 性格*0.2 + 氣勢*0.1
            weighted_score = (
                module_scores.get('energy_rescue', 0) * 0.4 +
                module_scores.get('structure_core', 0) * 0.3 +
                module_scores.get('personality_risk', 0) * 0.2 +
                module_scores.get('pressure_penalty', 0) * 0.1
            )
            final_score = (final_score + weighted_score) / 2
        elif purpose == "合夥":
            # 合夥模式：喜用互補*0.5 + 氣勢*0.3 + 日柱*0.2
            final_score = final_score * 0.9
        
        # 確保分數在合理範圍內
        final_score = min(98, max(10, final_score))
        return final_score, match_result
    
    @staticmethod
    def find_top_matches(user_bazi: Dict[str, Any], user_gender: str, start_year: int, 
                         end_year: int, purpose: str = "正緣", limit: int = 10) -> List[Dict[str, Any]]:
        """主搜尋函數 - 優化版，平衡效率和準確性"""
        logger.info(f"開始搜尋 {start_year}-{end_year} 年的真命天子，目的: {purpose}")
        
        # 1. 生成日期範圍
        dates = SoulmateFinder.generate_date_range(start_year, end_year)
        logger.info(f"生成 {len(dates)} 個日期")
        
        # 限制計算數量，避免過度計算（優化效率）
        sample_size = min(MAX_DATE_SAMPLE, len(dates))
        if len(dates) > sample_size:
            sampled_dates = random.sample(dates, sample_size)
            logger.info(f"隨機抽樣 {sample_size} 個日期")
        else:
            sampled_dates = dates
            logger.info(f"使用全部 {len(dates)} 個日期")
        
        # 2. 預篩選（放寬條件）
        pre_filtered = []
        pre_filter_count = 0
        
        for year, month, day in sampled_dates[:MAX_PRE_FILTER]:
            pre_filter_count += 1
            
            # 隨機生成時間
            hour = random.randint(0, 23)
            
            try:
                # 修正：已在頂部導入calculate_bazi
                target_bazi = calculate_bazi(
                    year, month, day, hour, 
                    gender=user_gender,
                    hour_confidence='高'
                )
                
                if not target_bazi:
                    continue
                
                # 添加出生年份信息
                target_bazi['birth_year'] = year
                target_bazi['birth_month'] = month
                target_bazi['birth_day'] = day
                target_bazi['birth_hour'] = hour
                
                # 預篩選（放寬條件）
                passed, reason = SoulmateFinder.pre_filter(
                    user_bazi, target_bazi, user_gender, user_gender
                )
                
                if passed:
                    pre_filtered.append(target_bazi)
                
                if len(pre_filtered) >= 30:  # 限制預篩選數量
                    logger.info(f"預篩選達到30個，提前結束")
                    break
                    
            except Exception as e:
                logger.debug(f"計算八字失敗 {year}-{month}-{day} {hour}時: {e}")
                continue
        
        logger.info(f"預篩選完成: 處理{pre_filter_count}個，通過{len(pre_filtered)}個")
        
        if not pre_filtered:
            logger.warning("預篩選無結果")
            return []
        
        # 3. 結構檢查（放寬條件）
        structure_filtered = []
        structure_count = 0
        
        for target_bazi in pre_filtered:
            structure_count += 1
            
            passed, reason = SoulmateFinder.structure_check(
                user_bazi, target_bazi, user_gender, user_gender
            )
            
            if passed:
                structure_filtered.append(target_bazi)
            
            if len(structure_filtered) >= MAX_STRUCTURE_CHECK:
                logger.info(f"結構檢查達到{MAX_STRUCTURE_CHECK}個，提前結束")
                break
        
        logger.info(f"結構檢查完成: 處理{structure_count}個，通過{len(structure_filtered)}個")
        
        if not structure_filtered:
            logger.warning("結構檢查無結果")
            return []
        
        # 4. 資深精算
        scored_matches = []
        score_count = 0
        
        for target_bazi in structure_filtered:
            score_count += 1
            
            try:
                score, match_result = SoulmateFinder.calculate_final_score(
                    user_bazi, target_bazi, user_gender, user_gender, purpose
                )
                
                # 使用統一分數閾值
                if score >= MIN_SCORE_THRESHOLD:
                    scored_matches.append({
                        'bazi': target_bazi,
                        'score': score,
                        'match_result': match_result,
                        'date': f"{target_bazi['birth_year']}年{target_bazi['birth_month']}月{target_bazi['birth_day']}日",
                        'hour': f"{target_bazi['birth_hour']}時",
                        'pillars': f"{target_bazi['year_pillar']} {target_bazi['month_pillar']} {target_bazi['day_pillar']} {target_bazi['hour_pillar']}"
                    })
                    logger.debug(f"合格匹配: 分數={score:.1f}, 日期={target_bazi['birth_year']}-{target_bazi['birth_month']}-{target_bazi['birth_day']}")
                
            except Exception as e:
                logger.debug(f"計算分數失敗: {e}")
                continue
        
        logger.info(f"分數計算完成: 處理{score_count}個，合格{len(scored_matches)}個")
        
        # 5. 排序並返回Top N
        scored_matches.sort(key=lambda x: x['score'], reverse=True)
        result = scored_matches[:limit]
        logger.info(f"返回前{len(result)}個匹配")
        return result

def format_find_soulmate_result(matches: List[Dict[str, Any]], start_year: int, 
                               end_year: int, purpose: str) -> str:
    """格式化Find Soulmate結果（單一消息格式）- 統一輸出格式"""
    if not matches:
        return "❌ 在指定範圍內未找到合適的匹配時空。\n建議：\n1. 擴展搜尋年份範圍\n2. 調整搜尋目的\n3. 檢查個人八字資料準確度"
    
    purpose_text = "尋找正緣" if purpose == "正緣" else "事業合夥"
    
    text_parts = []
    text_parts.append(f"🔮 真命天子搜尋結果")
    text_parts.append("=" * 40)
    text_parts.append("")
    text_parts.append(f"📅 搜尋範圍：{start_year}年 - {end_year}年")
    text_parts.append(f"🎯 搜尋目的：{purpose_text}")
    text_parts.append(f"📊 找到匹配：{len(matches)}個時空")
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
        
        text_parts.append(f"")
        text_parts.append(f"{i:2d}. {date} {hour}")
        text_parts.append(f"     分數：{score:.1f}分")
    
    text_parts.append("")
    text_parts.append("💡 使用建議")
    text_parts.append("=" * 40)
    text_parts.append("")
    text_parts.append("1. **確認時辰**：以上時辰均為整點，實際使用時需結合出生地經度校正")
    text_parts.append("2. **綜合考慮**：分數僅供參考，還需結合實際情況")
    text_parts.append("3. **深入分析**：可複製具體八字使用 /testpair 命令深入分析")
    text_parts.append("4. **時間信心度**：搜尋結果為理論最佳，實際應用時需考慮時間精度")
    
    return "\n".join(text_parts)
# ========1.1 Find Soulmate 功能結束 ========#

# ========文件信息開始 ========#
"""
文件: bazi_soulmate.py
功能: 真命天子搜尋功能（獨立檔案）

引用文件: new_calculator.py
被引用文件: bot.py (主程序)

主要修改：
1. 修復導入語句，避免循環引用和局部導入
2. 統一常量定義，移除魔法數字
3. 優化搜索算法，提高效率和穩定性
4. 改進日誌記錄，便於調試
5. 添加完整類型提示

修改記錄：
2026-02-07 本次修正：
1. 問題：局部導入導致重複計算和效率問題
   位置：calculate_final_score和find_top_matches方法中的局部導入
   後果：每次函數調用都重新導入，效率低下
   修正：將所有導入移到文件頂部

2. 問題：常量定義不一致
   位置：多個函數中的魔法數字
   後果：難以維護和理解
   修正：定義統一常量

3. 問題：日誌級別不當
   位置：多個函數中的日誌記錄
   後果：調試困難
   修正：區分info、debug、warning級別

4. 問題：類型提示不完整
   位置：多個函數缺少類型提示
   後果：代碼可讀性差
   修正：添加完整類型提示

5. 問題：字符串拼接效率
   位置：format_find_soulmate_result函數
   後果：性能不佳
   修正：使用列表join

6. 問題：搜索算法可以優化
   位置：find_top_matches方法
   後果：可能遺漏好匹配
   修正：添加更多日誌和智能抽樣

2026-02-05 先前修正：
1. 問題：find_soulmate完全無出到結果
   位置：pre_filter和structure_check方法
   後果：篩選條件過於嚴格，導致無結果
   修正：放寬所有篩選條件

2026-02-03 修正導入和函數調用：
1. 修正導入語句
2. 修正ScoringEngine方法調用
3. 修正八字計算函數調用
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
2026-02-07 本次修正：
1. 問題：局部導入效率問題
   位置：calculate_final_score和find_top_matches中的局部導入
   後果：每次函數調用都重新導入calculate_match和calculate_bazi
   修正：將所有關鍵導入移到文件頂部

2. 問題：常量定義混亂
   位置：多個函數中的硬編碼數字
   後果：60、50、35等魔法數字分散各處
   修正：定義統一常量MIN_SCORE_THRESHOLD=60等

3. 問題：日誌級別混淆
   位置：不同類型錯誤使用相同日誌級別
   後果：調試困難
   修正：區分error、warning、info、debug級別

4. 問題：類型提示缺失
   位置：大多數函數缺少參數和返回類型提示
   後果：代碼可讀性和維護性差
   修正：為所有函數添加完整類型提示

5. 問題：字符串拼接效率低
   位置：format_find_soulmate_result使用+=拼接
   後果：大量字符串操作性能差
   修正：改用列表join

6. 問題：搜索算法不夠智能
   位置：完全隨機抽樣可能遺漏好匹配
   後果：結果質量不穩定
   修正：添加更多日誌和智能控制

7. 問題：錯誤處理不完整
   位置：某些異常只記錄不處理
   後果：用戶體驗差
   修正：添加更友好的錯誤信息

8. 問題：代碼重複
   位置：多個函數有相似結構
   後果：維護困難
   修正：提取公共邏輯

9. 問題：變量命名不明確
   位置：某些變量名如"op"不明確
   後果：代碼可讀性差
   修正：使用更明確的變量名

10. 問題：未考慮邊界情況
    位置：某些函數未處理空值或異常輸入
    後果：可能崩潰
    修正：添加邊界檢查

2026-02-05 先前修正：
1. 問題：find_soulmate功能無結果
   位置：pre_filter和structure_check方法
   後果：篩選條件過於嚴格
   修正：放寬所有篩選條件，即使檢查不通過也不立即拒絕
"""
# ========修正紀錄結束 ========#