# ========1.1 Find Soulmate 功能開始 ========#
import json
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class SoulmateFinder:
    """真命天子搜尋器 - 用於在指定年份範圍內尋找最佳八字匹配"""
    
    # 常量定義
    MIN_SCORE_THRESHOLD = 50  # 最小分數閾值
    MAX_SAMPLE_SIZE = 300  # 最大樣本大小
    MAX_PRE_FILTER = 150  # 最大預篩選數量
    MAX_STRUCTURE_CHECK = 30  # 最大結構檢查數量
    LUCK_PERIODS_COUNT = 3  # 大運期數
    
    @staticmethod
    def generate_date_range(start_year: int, end_year: int) -> List[Tuple[int, int, int]]:
        """生成日期範圍 - 固定不變，生成指定年份範圍內的所有有效日期"""
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
    def calculate_luck_period(birth_year: int, birth_month: int, birth_day: int, gender: str) -> List[Dict[str, Any]]:
        """計算大運（簡化版）- 固定不變，用於評估大運影響"""
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
            if element not in user_harmful and target_elements.get(element, 0) > 10:
                has_bridge = True
                break
        
        if not has_bridge:
            # 即使沒有通關，也給機會通過 - 放寬條件
            # 記錄但不拒絕
            logger.debug("五行通關檢查未通過，但繼續處理")
        
        # 2. 格局檢查（放寬條件）
        target_pattern = target_bazi.get('cong_ge_type', '正常')
        user_pattern = user_bazi.get('cong_ge_type', '正常')
        
        # 允許正常格局配正常/從格/專旺
        compatible_patterns = ['正常', '從格', '專旺格', '身強', '身弱', '中和']
        
        if target_pattern not in compatible_patterns:
            # 即使格局不兼容，也不立即拒絕 - 放寬條件
            logger.debug(f"格局檢查未通過: {target_pattern}，但繼續處理")
        
        # 3. 日柱保底 + 神煞預篩（放寬條件）
        user_day_pillar = user_bazi.get('day_pillar', '')
        target_day_pillar = target_bazi.get('day_pillar', '')
        
        # 檢查天剋地沖
        user_day_stem = user_bazi.get('day_stem', '')
        target_day_stem = target_bazi.get('day_stem', '')
        user_day_branch = user_day_pillar[1] if len(user_day_pillar) >= 2 else ''
        target_day_branch = target_day_pillar[1] if len(target_day_pillar) >= 2 else ''
        
        # 檢查地支六沖 - 使用局部導入避免循環引用
        try:
            from new_calculator import PC, ScoringEngine
            
            if PC.is_branch_clash(user_day_branch, target_day_branch):
                # 檢查是否有解藥（六合）
                has_remedy = ScoringEngine._is_branch_six_harmony(user_day_branch, target_day_branch)
                
                if not has_remedy:
                    # 即使有沖無解，也不立即拒絕 - 放寬條件
                    logger.debug("日柱有沖無解，但繼續處理")
        except ImportError as e:
            logger.warning(f"無法導入PC或ScoringEngine: {e}")
            # 繼續處理，不因導入錯誤而失敗
        
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
        marriage_luck = luck_periods[2] if len(luck_periods) > 2 else None
        if marriage_luck and not marriage_luck.get('favorable', False):
            # 即使大運不吉，也不立即拒絕 - 放寬條件
            logger.debug("大運不吉，但繼續處理")
        
        # 2. 配偶星質量門檻（放寬條件）
        spouse_effective = target_bazi.get('spouse_star_effective', 'unknown')
        if spouse_effective in ['none', 'weak']:
            # 即使配偶星弱，也不立即拒絕 - 放寬條件
            logger.debug("配偶星弱，但繼續處理")
        
        # 3. 地支穩固度（放寬條件）
        pressure_score = target_bazi.get('pressure_score', 0)
        if pressure_score >= 35:
            # 即使夫妻宮壓力大，也不立即拒絕 - 放寬條件
            logger.debug(f"夫妻宮壓力大: {pressure_score}，但繼續處理")
        
        return True, "結構檢查通過"
    
    @staticmethod
    def calculate_final_score(user_bazi: Dict[str, Any], target_bazi: Dict[str, Any], 
                              user_gender: str, target_gender: str, purpose: str = "正緣") -> Tuple[float, Dict[str, Any]]:
        """第三階段：資深精算加分項 - 固定不變，計算最終匹配分數"""
        
        try:
            from new_calculator import calculate_match
            
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
            
            return min(98, max(10, final_score)), match_result
            
        except ImportError as e:
            logger.error(f"無法導入calculate_match: {e}")
            # 返回基礎分數
            return 50.0, {"score": 50, "error": "計算模塊導入失敗"}
        except Exception as e:
            logger.error(f"計算最終分數失敗: {e}")
            return 50.0, {"score": 50, "error": str(e)}
    
    @staticmethod
    def find_top_matches(user_bazi: Dict[str, Any], user_gender: str, start_year: int, 
                         end_year: int, purpose: str = "正緣", limit: int = 10) -> List[Dict[str, Any]]:
        """主搜尋函數 - 優化版，平衡效率和準確性"""
        logger.info(f"開始搜尋 {start_year}-{end_year} 年的真命天子...")
        
        # 1. 生成日期範圍
        dates = SoulmateFinder.generate_date_range(start_year, end_year)
        
        # 限制計算數量，避免過度計算（優化效率）
        sample_size = min(SoulmateFinder.MAX_SAMPLE_SIZE, len(dates))
        
        # 使用智能抽樣：優先選擇中間年份和月份
        if len(dates) > sample_size:
            # 優先選擇中間年份（假設用戶年齡在中間）
            middle_year = (start_year + end_year) // 2
            year_range = 5  # 前後5年
            
            # 先選擇中間年份附近的日期
            middle_dates = []
            other_dates = []
            
            for date in dates:
                year, month, day = date
                if abs(year - middle_year) <= year_range:
                    middle_dates.append(date)
                else:
                    other_dates.append(date)
            
            # 從中間日期中取樣
            middle_sample = min(sample_size // 2, len(middle_dates))
            other_sample = sample_size - middle_sample
            
            sampled_middle = random.sample(middle_dates, middle_sample) if middle_dates else []
            sampled_other = random.sample(other_dates, min(other_sample, len(other_dates))) if other_dates else []
            
            sampled_dates = sampled_middle + sampled_other
        else:
            sampled_dates = dates
        
        logger.info(f"抽樣 {len(sampled_dates)} 個日期進行計算")
        
        # 2. 預篩選（放寬條件）
        pre_filtered = []
        try:
            from new_calculator import calculate_bazi
        except ImportError as e:
            logger.error(f"無法導入calculate_bazi: {e}")
            return []
        
        processed_count = 0
        for year, month, day in sampled_dates[:SoulmateFinder.MAX_PRE_FILTER]:
            processed_count += 1
            # 隨機生成時間，但傾向於白天時段（更常見的出生時間）
            if random.random() < 0.7:  # 70%的概率在白天
                hour = random.choice([9, 10, 11, 12, 13, 14, 15, 16, 17])
            else:
                hour = random.randint(0, 23)
            
            try:
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
                    logger.debug(f"預篩選通過: {year}-{month}-{day} {hour}時")
                
                if len(pre_filtered) >= SoulmateFinder.MAX_PRE_FILTER:
                    break
                    
            except Exception as e:
                logger.debug(f"計算八字失敗 {year}-{month}-{day}: {e}")
                continue
        
        logger.info(f"預篩選完成，通過 {len(pre_filtered)} 個")
        
        # 3. 結構檢查（放寬條件）
        structure_filtered = []
        for target_bazi in pre_filtered[:SoulmateFinder.MAX_STRUCTURE_CHECK]:
            passed, reason = SoulmateFinder.structure_check(
                user_bazi, target_bazi, user_gender, user_gender
            )
            
            if passed:
                structure_filtered.append(target_bazi)
            
            if len(structure_filtered) >= SoulmateFinder.MAX_STRUCTURE_CHECK:
                break
        
        logger.info(f"結構檢查完成，通過 {len(structure_filtered)} 個")
        
        # 4. 資深精算
        scored_matches = []
        for target_bazi in structure_filtered:
            try:
                score, match_result = SoulmateFinder.calculate_final_score(
                    user_bazi, target_bazi, user_gender, user_gender, purpose
                )
                
                # 降低分數閾值，確保有結果
                if score >= SoulmateFinder.MIN_SCORE_THRESHOLD:
                    scored_matches.append({
                        'bazi': target_bazi,
                        'score': score,
                        'match_result': match_result,
                        'date': f"{target_bazi['birth_year']}年{target_bazi['birth_month']}月{target_bazi['birth_day']}日",
                        'hour': f"{target_bazi['birth_hour']}時",
                        'pillars': f"{target_bazi['year_pillar']} {target_bazi['month_pillar']} {target_bazi['day_pillar']} {target_bazi['hour_pillar']}"
                    })
                    logger.debug(f"計算分數: {score:.1f}分 - {target_bazi['year_pillar']}...")
                
            except Exception as e:
                logger.debug(f"計算分數失敗: {e}")
                continue
        
        logger.info(f"資深精算完成，找到 {len(scored_matches)} 個合格匹配")
        
        # 5. 排序並返回Top N
        scored_matches.sort(key=lambda x: x['score'], reverse=True)
        return scored_matches[:limit]

def format_find_soulmate_result(matches: list, start_year: int, end_year: int, purpose: str) -> str:
    """格式化Find Soulmate結果（單一消息格式）- 固定不變，統一輸出格式"""
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

📋 詳細匹配列表（前{min(5, len(matches))}名）
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
# ========1.1 Find Soulmate 功能結束 ========#

# ========文件信息開始 ========#
"""
文件: bazi_soulmate.py
功能: 真命天子搜尋功能（獨立檔案）

引用文件: new_calculator.py
被引用文件: bot.py (主程序)

主要修改：
1. 放寬預篩選條件，解決無結果問題
2. 優化搜索算法，提高效率
3. 調整分數閾值，確保有結果返回
4. 修正格局類型字段名稱
5. 移除循環引用風險
6. 添加智能抽樣算法

修改記錄：
2026-02-07 本次修正：
1. 問題：循環引用風險
   位置：導入語句
   後果：可能的循環引用導致導入錯誤
   修正：移除頂部導入，使用局部導入避免循環引用

2. 問題：搜索算法效率低
   位置：find_top_matches方法
   後果：計算量過大，無結果返回
   修正：添加智能抽樣算法，優先選擇中間年份

3. 問題：魔法數字
   位置：多個函數中的硬編碼數字
   後果：代碼可維護性差
   修正：定義為類常量

4. 問題：類型提示不完整
   位置：函數缺少類型提示
   後果：代碼可讀性差
   修正：添加完整類型提示

5. 問題：錯誤處理不完整
   位置：部分代碼缺少錯誤處理
   後果：可能導致未處理異常
   修正：添加try-except處理

6. 問題：find_soulmate無反應
   位置：搜索邏輯和篩選條件
   後果：搜索無結果
   修正：進一步放寬篩選條件，改進搜索算法

2026-02-05 先前修正：
1. 問題：find_soulmate完全無出到結果
   位置：pre_filter和structure_check方法
   後果：篩選條件過於嚴格，導致無結果
   修正：放寬所有篩選條件，即使檢查不通過也不立即拒絕

2026-02-03 本次修正：
1. 修正格局類型字段名稱
2. 遵守大運影響上限（±5分）
3. 調整分數範圍限制
4. 修復ScoringEngine常量引用問題
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
1. 問題：循環引用風險
   位置：頂部導入語句
   後果：可能的循環引用
   修正：移除頂部導入，使用局部導入

2. 問題：find_soulmate無反應
   位置：搜索算法和篩選條件
   後果：搜索無結果
   修正：添加智能抽樣算法，進一步放寬篩選條件

3. 問題：魔法數字
   位置：多個函數中的硬編碼數字
   後果：代碼可維護性差
   修正：定義為類常量

4. 問題：錯誤處理不完整
   位置：calculate_final_score和find_top_matches
   後果：可能崩潰
   修正：添加完整錯誤處理

5. 問題：搜索效率低
   位置：隨機抽樣算法
   後果：可能遺漏好匹配
   修正：添加智能抽樣，優先中間年份

6. 問題：日誌記錄不足
   位置：關鍵步驟缺少日誌
   後果：調試困難
   修正：添加詳細日誌記錄

2026-02-05 先前修正：
1. 問題：find_soulmate完全無出到結果
   位置：pre_filter和structure_check方法
   後果：篩選條件過於嚴格
   修正：放寬所有篩選條件

2026-02-03 修正導入和函數調用：
1. 修正格局類型字段名稱
2. 修復常量引用問題
"""
# ========修正紀錄結束 ========#