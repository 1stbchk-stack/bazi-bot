#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字配對系統核心 - 八字計算與配對引擎
採用判斷引擎優先架構：時間→核心→評分→審計
"""

import logging
import math
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import sxtwl

logger = logging.getLogger(__name__)

# 🔖 1.1 錯誤處理類開始
class BaziCalculatorError(Exception):
    """八字計算錯誤"""
    pass

class ScoringEngineError(Exception):
    """評分引擎錯誤"""
    pass

class TimeProcessingError(Exception):
    """時間處理錯誤"""
    pass
# 🔖 1.1 錯誤處理類結束

# 🔖 1.2 配置常量類開始
class Config:
    """配置常量集中管理類"""
    
    # 時間配置
    TIME_ZONE_MERIDIAN = 120.0  # 東經120度為標準時區
    DAY_BOUNDARY_MODE = 'zizheng'  # 子正換日
    DEFAULT_LONGITUDE = 114.17    # 香港經度
    DEFAULT_LATITUDE = 22.32      # 香港緯度
    LONGITUDE_CORRECTION = 4      # 經度差1度 = 4分鐘
    DAY_BOUNDARY_HOUR = 23        # 日界線時辰
    DAY_BOUNDARY_MINUTE = 0       # 日界線分鐘
    MISSING_MINUTE_HANDLING = 0   # 分鐘缺失時使用0分鐘
    
    # 香港夏令時完整表 (1941-1979)
    HK_DST_PERIODS = [
        ("1941-04-01", "1941-12-25"), ("1942-12-25", "1943-09-30"),
        ("1946-04-20", "1946-12-01"), ("1947-04-13", "1947-11-02"),
        ("1950-04-02", "1950-10-29"), ("1951-04-01", "1951-10-28"),
        ("1952-04-06", "1952-10-26"), ("1953-04-05", "1953-10-25"),
        ("1954-04-04", "1954-10-31"), ("1955-04-03", "1955-10-30"),
        ("1956-04-01", "1956-10-28"), ("1957-04-07", "1957-10-27"),
        ("1958-04-06", "1958-10-26"), ("1959-04-05", "1959-10-25"),
        ("1960-04-03", "1960-10-30"), ("1961-04-02", "1961-10-29"),
        ("1962-04-01", "1962-10-28"), ("1963-04-07", "1963-10-27"),
        ("1964-04-05", "1964-10-25"), ("1965-04-04", "1965-10-31"),
        ("1966-04-03", "1966-10-30"), ("1967-04-02", "1967-10-29"),
        ("1968-04-07", "1968-10-27"), ("1969-04-06", "1969-10-26"),
        ("1970-04-05", "1970-10-25"), ("1971-04-04", "1971-10-31"),
        ("1972-04-02", "1972-10-29"), ("1973-04-01", "1973-10-28"),
        ("1974-04-07", "1974-10-27"), ("1975-04-06", "1975-10-26"),
        ("1976-04-04", "1976-10-31"), ("1977-04-03", "1977-10-30"),
        ("1978-04-02", "1978-10-29"), ("1979-05-06", "1979-10-21")
    ]
    
    # 月令氣勢表
    MONTH_QI_MAP = {
        '子': {'yuqi': '辛', 'zhongqi': '癸', 'zhengqi': '壬'},
        '丑': {'yuqi': '壬', 'zhongqi': '辛', 'zhengqi': '己'},
        '寅': {'yuqi': '己', 'zhongqi': '戊', 'zhengqi': '甲'},
        '卯': {'yuqi': '甲', 'zhongqi': '丙', 'zhengqi': '乙'},
        '辰': {'yuqi': '乙', 'zhongqi': '癸', 'zhengqi': '戊'},
        '巳': {'yuqi': '戊', 'zhongqi': '庚', 'zhengqi': '丙'},
        '午': {'yuqi': '丙', 'zhongqi': '戊', 'zhengqi': '丁'},
        '未': {'yuqi': '丁', 'zhongqi': '乙', 'zhengqi': '己'},
        '申': {'yuqi': '己', 'zhongqi': '戊', 'zhengqi': '庚'},
        '酉': {'yuqi': '庚', 'zhongqi': '壬', 'zhengqi': '辛'},
        '戌': {'yuqi': '辛', 'zhongqi': '丁', 'zhengqi': '戊'},
        '亥': {'yuqi': '戊', 'zhongqi': '甲', 'zhengqi': '壬'}
    }
    
    # 身強弱計算權重
    MONTH_WEIGHT = 35
    TONG_GEN_WEIGHT = 25
    SUPPORT_WEIGHT = 15
    STRENGTH_THRESHOLD_STRONG = 65
    STRENGTH_THRESHOLD_MEDIUM = 35
    DEFAULT_STRENGTH_SCORE = 50
    
    # 陰陽天干
    YANG_STEMS = ['甲', '丙', '戊', '庚', '壬']
    YIN_STEMS = ['乙', '丁', '己', '辛', '癸']
    
    # 墓庫地支
    TOMB_BRANCHES = {'木': '未', '火': '戌', '土': '戌', '金': '丑', '水': '辰'}
    
    # ========== 評分系統配置 ==========
    # 基準分調整（55分基礎緣分） - 降低基準分，留出分數空間
    BASE_SCORE = 55
    REALITY_FLOOR = 35  # 降低保底分，讓大凶組合顯現
    
    # 專業評分閾值 - 重新調整閾值
    THRESHOLD_TERMINATION = 30      # 保持不變
    THRESHOLD_STRONG_WARNING = 40   # 保持不變
    THRESHOLD_WARNING = 45          # 保持不變
    THRESHOLD_ACCEPTABLE = 55       # 提升門檻
    THRESHOLD_GOOD_MATCH = 70       # 提升門檻
    THRESHOLD_EXCELLENT_MATCH = 80  # 提升門檻
    THRESHOLD_PERFECT_MATCH = 90    # 提升門檻
    
    # ========== 刑沖硬傷系統 ==========
    DAY_CLASH_HARD_CAP = 45         # 日支沖硬上限
    DAY_HARM_HARD_CAP = 50          # 日支害硬上限
    FATAL_RISK_CAP = 30             # 致命風險上限
    
    # ========== 模組分數上限 ==========
    POSITIVE_BONUS_CAP = 45         # 提高上限，讓優質組合能跑出高分
    POSITIVE_SATURATION_FACTOR = 0.6  # 提高飽和係數
    
    # 各模組上限
    ENERGY_RESCUE_CAP = 35          # 大幅提高能量救應權重
    STRUCTURE_CORE_CAP = 30         # 提高結構核心權重
    PERSONALITY_RISK_CAP = -25      # 加深人格風險扣分
    PRESSURE_PENALTY_CAP = -40      # 允許更大刑沖扣分
    SHEN_SHA_BONUS_CAP = 15         # 提高神煞上限
    SHEN_SHA_FLOOR = 0              # 刪除神煞保底分 - 關鍵修改
    RESOLUTION_BONUS_CAP = 10       # 保持不變
    DAYUN_RISK_CAP = -15            # 保持不變
    
    # 總扣分上限保護
    TOTAL_PENALTY_CAP = -35         # 調整總扣分上限
    
    # ========== 能量救應配置 ==========
    WEAK_THRESHOLD = 15
    EXTREME_WEAK_BONUS = 15         # 提高極弱救應分數
    DEMAND_MATCH_BONUS_BASE = 18    # 大幅提高基礎分數 - 關鍵修改
    CONCENTRATION_BOOST_THRESHOLD = 20  # 降低濃度閾值
    CONCENTRATION_BOOST_FACTOR = 1.5    # 提高加成係數
    
    # 能量抵銷比例
    RESCUE_DEDUCTION_RATIO = 0.3    # 調整抵銷比例
    
    # ========== 結構核心配置 ==========
    STEM_COMBINATION_FIVE_HARMONY = 25  # 提高天合分數
    STEM_COMBINATION_GENERATION = 6     # 提高相生分數
    STEM_COMBINATION_SAME = 2           # 提高比和分數
    
    BRANCH_COMBINATION_SIX_HARMONY = 20  # 提高地合分數
    BRANCH_COMBINATION_THREE_HARMONY = 12 # 保持不變
    
    # ========== 刑沖壓力配置 ==========
    BRANCH_CLASH_PENALTY = -12      # 加重六沖懲罰
    BRANCH_HARM_PENALTY = -8        # 加重六害懲罰
    DAY_CLASH_PENALTY = -25         # 大幅加重日支沖懲罰 - 關鍵修改
    DAY_HARM_PENALTY = -18          # 大幅加重日支害懲罰 - 關鍵修改
    
    # 沖合抵銷
    TRIAD_RESOLUTION_RATIO = 0.7    # 提高三合解沖能力
    HARMONY_RESOLUTION_RATIO = 0.5  # 提高六合解沖能力
    
    # ========== 人格風險配置 ==========
    PERSONALITY_RISK_PATTERNS = {
        "傷官見官": -15,
        "官殺混雜": -12,
        "財星遇劫": -10,
        "羊刃坐財": -8,
        "梟神奪食": -8,
        "半三刑": -6
    }
    PERSONALITY_STACKED_PENALTY = -12  # 調整疊加懲罰
    
    # ========== 神煞系統配置 ==========
    SHEN_SHA_POSITIVE = {
        "紅鸞": 3,
        "天喜": 2,
        "天乙貴人": 4,
        "文昌": 2,
    }
    
    SHEN_SHA_NEGATIVE = {
        "羊刃": -4,
        "劫煞": -3,
        "亡神": -3,
        "孤辰": -3,
        "寡宿": -3,
        "陰差陽錯": -4
    }
    
    # 神煞互動加成
    SHEN_SHA_COMBO_BONUS = {
        ("紅鸞", "天喜"): 5,
        ("天乙貴人", "天乙貴人"): 4,
    }
    
    # ========== 專業化解配置 ==========
    RESOLUTION_PATTERNS = {
        "殺印相生": 8,
        "財官相生": 7,
        "傷官生財": 6,
        "食傷配印": 5,
    }
    
    # ========== 現實校準配置 ==========
    AGE_GAP_PENALTY_5_8 = -2
    AGE_GAP_PENALTY_9_12 = -5
    AGE_GAP_PENALTY_13_PLUS = -8
    
    # ========== 關係模型判定 ==========
    BALANCED_MAX_DIFF = 12
    SUPPLY_MIN_DIFF = 15
    
    # ========== 時間信心度映射 ==========
    TIME_CONFIDENCE_LEVELS = {
        '高': 0.95,
        '中': 0.90,
        '低': 0.85,
        '估算': 0.80
    }
    
    # ========== 評級標準 ==========
    RATING_SCALE = [
        (THRESHOLD_PERFECT_MATCH, "極品組合", "極品組合，互相成就"),
        (THRESHOLD_EXCELLENT_MATCH, "上等婚配", "明顯互補，幸福率高"),
        (THRESHOLD_GOOD_MATCH, "良好婚配", "現實高成功率，可經營"),
        (THRESHOLD_ACCEPTABLE, "可以交往", "有缺點但可努力經營"),
        (THRESHOLD_WARNING, "需要謹慎", "問題較多，需謹慎考慮"),
        (THRESHOLD_STRONG_WARNING, "不建議", "沖剋嚴重，難長久"),
        (THRESHOLD_TERMINATION, "強烈不建議", "嚴重沖剋，極難長久"),
        (0, "避免發展", "硬傷明顯，易生變")
    ]
    
    @classmethod
    def get_rating(cls, score: float) -> str:
        """根據分數獲取評級"""
        for threshold, name, _ in cls.RATING_SCALE:
            if score >= threshold:
                return name
        return "避免發展"
    
    @classmethod
    def get_rating_description(cls, score: float) -> str:
        """根據分數獲取評級描述"""
        for threshold, _, description in cls.RATING_SCALE:
            if score >= threshold:
                return description
        return "硬傷明顯，易生變"
    
    @classmethod
    def format_confidence(cls, confidence: str) -> str:
        """格式化信心度"""
        confidence_map = {
            'high': '高', '高': '高',
            'medium': '中', '中': '中',
            'low': '低', '低': '低',
            'estimated': '估算', '估算': '估算'
        }
        return confidence_map.get(confidence, confidence)
    
    @classmethod
    def get_confidence_factor(cls, confidence_str: str) -> float:
        """獲取信心度因子"""
        confidence_map = {
            'high': '高', '高': '高',
            'medium': '中', '中': '中',
            'low': '低', '低': '低',
            'estimated': '估算', '估算': '估算'
        }
        
        confidence = confidence_map.get(confidence_str, confidence_str)
        return cls.TIME_CONFIDENCE_LEVELS.get(confidence, 0.85)

# 創建配置實例方便使用
C = Config
# 🔖 1.2 配置常量類結束

# 🔖 1.3 時間處理引擎開始
class TimeProcessor:
    """時間處理引擎 - 處理真太陽時、DST、EOT、日界"""
    
    @staticmethod
    def is_dst_date(date: datetime) -> bool:
        """檢查是否為夏令時日期"""
        date_str = date.strftime("%Y-%m-%d")
        
        for start_str, end_str in C.HK_DST_PERIODS:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
            
            if start_date <= date <= end_date:
                return True
        return False
    
    @staticmethod
    def calculate_eot(jd: float) -> float:
        """計算均時差 (Equation of Time)"""
        n = jd - 2451545.0
        L = 280.460 + 0.9856474 * n
        g = 357.528 + 0.9856003 * n
        L = L % 360
        g = g % 360
        
        L_rad = math.radians(L)
        g_rad = math.radians(g)
        
        eot = 229.18 * (0.000075 + 0.001868 * math.cos(g_rad) - 
                        0.032077 * math.sin(g_rad) - 
                        0.014615 * math.cos(2*g_rad) - 
                        0.040849 * math.sin(2*g_rad))
        return eot
    
    @staticmethod
    def calculate_true_solar_time(year: int, month: int, day: int, 
                                  hour: int, minute: int, 
                                  longitude: float, confidence: str) -> Dict:
        """
        計算真太陽時（包含DST、EOT、經度校正）
        返回: {'hour': int, 'minute': int, 'confidence': str, 'adjusted': bool}
        """
        audit_log = []
        audit_log.append(f"原始時間: {year}-{month}-{day} {hour}:{minute:02d}")
        
        dst_adjust = 0
        try:
            date_obj = datetime(year, month, day)
            if TimeProcessor.is_dst_date(date_obj):
                dst_adjust = -60
                audit_log.append(f"DST調整: {dst_adjust}分鐘（香港夏令時）")
            else:
                audit_log.append(f"非夏令時日期: 無調整")
        except Exception as e:
            logger.warning(f"DST檢查失敗: {e}")
            audit_log.append(f"DST檢查失敗: {e}")
        
        longitude_diff = longitude - C.TIME_ZONE_MERIDIAN
        longitude_adjust = longitude_diff * C.LONGITUDE_CORRECTION
        audit_log.append(f"經度差調整: {longitude_adjust:.2f}分鐘")
        
        try:
            day_obj = sxtwl.fromSolar(year, month, day)
            jd = day_obj.getJulianDay() + (hour + minute/60.0)/24.0
            eot_adjust = TimeProcessor.calculate_eot(jd)
            audit_log.append(f"EOT調整: {eot_adjust:.2f}分鐘")
        except Exception as e:
            logger.warning(f"EOT計算失敗: {e}")
            eot_adjust = 0
            audit_log.append(f"EOT計算失敗: {e}")
        
        total_adjust = dst_adjust + longitude_adjust + eot_adjust
        total_minutes = hour * 60 + minute + total_adjust
        
        day_adjusted = 0
        if total_minutes < 0:
            total_minutes += 24 * 60
            day_adjusted = -1
            audit_log.append(f"跨日調整: 向前跨1日")
        elif total_minutes >= 24 * 60:
            total_minutes -= 24 * 60
            day_adjusted = 1
            audit_log.append(f"跨日調整: 向後跨1日")
        
        true_hour = int(total_minutes // 60)
        true_minute = int(total_minutes % 60)
        
        if abs(total_adjust) > 30:
            new_confidence = "中" if confidence == "高" else "低"
        else:
            new_confidence = confidence
        
        return {
            'hour': true_hour,
            'minute': true_minute,
            'confidence': new_confidence,
            'adjusted': abs(total_adjust) > 1,
            'day_adjusted': day_adjusted,
            'total_adjust_minutes': total_adjust,
            'audit_log': audit_log
        }
    
    @staticmethod
    def apply_day_boundary(year: int, month: int, day: int, 
                           hour: int, minute: int, confidence: str) -> Tuple[int, int, int, str]:
        """
        應用日界規則
        返回: (year, month, day, confidence)
        """
        if C.DAY_BOUNDARY_MODE == 'none':
            return (year, month, day, confidence)
        
        if C.DAY_BOUNDARY_MODE == 'zizheng':
            if hour >= C.DAY_BOUNDARY_HOUR and minute >= C.DAY_BOUNDARY_MINUTE:
                current_date = datetime(year, month, day)
                next_date = current_date + timedelta(days=1)
                new_confidence = "中" if confidence == "高" else confidence
                return (next_date.year, next_date.month, next_date.day, new_confidence)
        
        return (year, month, day, confidence)
    
    @staticmethod
    def handle_missing_minute(hour: int, minute: Optional[int], confidence: str) -> Tuple[int, str]:
        """處理分鐘缺失"""
        if minute is None:
            use_minute = C.MISSING_MINUTE_HANDLING
            confidence_map = {
                "高": "中",
                "中": "低", 
                "低": "估算",
                "估算": "估算"
            }
            new_confidence = confidence_map.get(confidence, "估算")
            return use_minute, new_confidence
        return minute, confidence
# 🔖 1.3 時間處理引擎結束

# 🔖 1.4 八字核心引擎開始
class BaziCalculator:
    """八字核心引擎 - 專業八字計算"""
    
    STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    STEM_ELEMENTS = {
        '甲': '木', '乙': '木', '丙': '火', '丁': '火',
        '戊': '土', '己': '土', '庚': '金', '辛': '金',
        '壬': '水', '癸': '水'
    }
    
    BRANCH_ELEMENTS = {
        '子': '水', '丑': '土', '寅': '木', '卯': '木',
        '辰': '土', '巳': '火', '午': '火', '未': '土',
        '申': '金', '酉': '金', '戌': '土', '亥': '水'
    }
    
    BRANCH_HIDDEN_STEMS = {
        '子': [('癸', 1.0)],
        '丑': [('己', 0.6), ('癸', 0.3), ('辛', 0.1)],
        '寅': [('甲', 0.6), ('丙', 0.3), ('戊', 0.1)],
        '卯': [('乙', 1.0)],
        '辰': [('戊', 0.6), ('乙', 0.3), ('癸', 0.1)],
        '巳': [('丙', 0.6), ('庚', 0.3), ('戊', 0.1)],
        '午': [('丁', 0.7), ('己', 0.3)],
        '未': [('己', 0.6), ('丁', 0.3), ('乙', 0.1)],
        '申': [('庚', 0.6), ('壬', 0.3), ('戊', 0.1)],
        '酉': [('辛', 1.0)],
        '戌': [('戊', 0.6), ('辛', 0.3), ('丁', 0.1)],
        '亥': [('壬', 0.7), ('甲', 0.3)]
    }
    
    @staticmethod
    def calculate(year: int, month: int, day: int, hour: int, 
                  gender: str = "未知", 
                  hour_confidence: str = "高",
                  minute: Optional[int] = None,
                  longitude: float = C.DEFAULT_LONGITUDE,
                  latitude: float = C.DEFAULT_LATITUDE) -> Dict:
        """
        八字計算主函數 - 唯一對外接口
        返回完整的八字數據
        """
        audit_log = []
        
        try:
            # 檢查年份是否支持
            if year < 1900 or year > 2200:
                logger.warning(f"年份{year}超出常規範圍，可能不準確")
            
            # 1. 處理分鐘缺失
            processed_minute, processed_confidence = TimeProcessor.handle_missing_minute(
                hour, minute, hour_confidence
            )
            
            # 2. 計算真太陽時
            true_solar_time = TimeProcessor.calculate_true_solar_time(
                year, month, day, hour, processed_minute, longitude, processed_confidence
            )
            
            # 3. 應用日界規則
            adjusted_date = TimeProcessor.apply_day_boundary(
                year, month, day, 
                true_solar_time['hour'], true_solar_time['minute'],
                true_solar_time['confidence']
            )
            adjusted_year, adjusted_month, adjusted_day, final_confidence = adjusted_date
            
            # 4. 使用sxtwl計算四柱
            day_obj = sxtwl.fromSolar(adjusted_year, adjusted_month, adjusted_day)
            
            y_gz = day_obj.getYearGZ()
            m_gz = day_obj.getMonthGZ()
            d_gz = day_obj.getDayGZ()
            
            # 計算時柱
            hour_pillar = BaziCalculator._calculate_hour_pillar(
                adjusted_year, adjusted_month, adjusted_day, true_solar_time['hour']
            )
            
            # 5. 組裝基礎八字數據
            bazi_data = {
                "year_pillar": f"{BaziCalculator._get_stem_name(y_gz.tg)}{BaziCalculator._get_branch_name(y_gz.dz)}",
                "month_pillar": f"{BaziCalculator._get_stem_name(m_gz.tg)}{BaziCalculator._get_branch_name(m_gz.dz)}",
                "day_pillar": f"{BaziCalculator._get_stem_name(d_gz.tg)}{BaziCalculator._get_branch_name(d_gz.dz)}",
                "hour_pillar": hour_pillar,
                "zodiac": BaziCalculator._get_zodiac(y_gz.dz),
                "day_stem": BaziCalculator._get_stem_name(d_gz.tg),
                "day_stem_element": BaziCalculator.STEM_ELEMENTS.get(
                    BaziCalculator._get_stem_name(d_gz.tg), ""
                ),
                "hour_confidence": final_confidence,
                "gender": gender,
                "birth_year": year,
                "birth_month": month,
                "birth_day": day,
                "birth_hour": hour,
                "birth_minute": processed_minute,
                "true_solar_hour": true_solar_time['hour'],
                "true_solar_minute": true_solar_time['minute'],
                "adjusted_year": adjusted_year,
                "adjusted_month": adjusted_month,
                "adjusted_day": adjusted_day,
                "time_adjusted": true_solar_time['adjusted'],
                "day_adjusted": true_solar_time.get('day_adjusted', 0),
                "audit_log": audit_log
            }
            
            # 6. 深度分析
            bazi_data = BaziCalculator._analyze_details(bazi_data, gender, audit_log)
            
            logger.info(f"八字計算完成: {bazi_data['year_pillar']} {bazi_data['month_pillar']} "
                       f"{bazi_data['day_pillar']} {bazi_data['hour_pillar']}")
            
            return bazi_data
            
        except Exception as e:
            logger.error(f"八字計算錯誤: {e}", exc_info=True)
            # 返回基本數據，不深度分析
            return BaziCalculator._create_fallback_bazi(year, month, day, hour, gender, processed_minute)
    
    @staticmethod
    def _create_fallback_bazi(year: int, month: int, day: int, hour: int, 
                             gender: str, minute: int) -> Dict:
        """創建基本的八字數據（備用）"""
        return {
            "year_pillar": "未知",
            "month_pillar": "未知",
            "day_pillar": "未知",
            "hour_pillar": "未知",
            "zodiac": "未知",
            "day_stem": "未知",
            "day_stem_element": "未知",
            "hour_confidence": "低",
            "gender": gender,
            "birth_year": year,
            "birth_month": month,
            "birth_day": day,
            "birth_hour": hour,
            "birth_minute": minute,
            "true_solar_hour": hour,
            "true_solar_minute": minute,
            "adjusted_year": year,
            "adjusted_month": month,
            "adjusted_day": day,
            "time_adjusted": False,
            "day_adjusted": 0,
            "elements": {"木": 20.0, "火": 20.0, "土": 20.0, "金": 20.0, "水": 20.0},
            "strength_score": 50.0,
            "day_stem_strength": "中",
            "pattern_type": "正格",
            "useful_elements": ["土", "金"],
            "harmful_elements": ["木", "火"],
            "spouse_star_status": "未知",
            "spouse_star_effective": "未知",
            "spouse_palace_status": "未知",
            "pressure_score": 0.0,
            "shen_sha_names": "無",
            "shen_sha_bonus": 0.0,
            "shi_shen_structure": "普通結構"
        }
    
    @staticmethod
    def _calculate_hour_pillar(year: int, month: int, day: int, hour: int) -> str:
        """計算時柱"""
        day_obj = sxtwl.fromSolar(year, month, day)
        d_gz = day_obj.getDayGZ()
        day_stem = d_gz.tg
        
        hour_branch = BaziCalculator._hour_to_branch(hour)
        day_stem_mod = day_stem % 5
        start_stem_map = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8}
        start_stem = start_stem_map.get(day_stem_mod, 0)
        
        hour_stem = (start_stem + hour_branch) % 10
        
        return f"{BaziCalculator.STEMS[hour_stem]}{BaziCalculator.BRANCHES[hour_branch]}"
    
    @staticmethod
    def _hour_to_branch(hour: int) -> int:
        """將24小時制轉換為地支時辰"""
        hour_map = {
            23: 0, 0: 0,    # 子
            1: 1, 2: 1,     # 丑
            3: 2, 4: 2,     # 寅
            5: 3, 6: 3,     # 卯
            7: 4, 8: 4,     # 辰
            9: 5, 10: 5,    # 巳
            11: 6, 12: 6,   # 午
            13: 7, 14: 7,   # 未
            15: 8, 16: 8,   # 申
            17: 9, 18: 9,   # 酉
            19: 10, 20: 10, # 戌
            21: 11, 22: 11  # 亥
        }
        return hour_map.get(hour % 24, 0)
    
    @staticmethod
    def _get_stem_name(code: int) -> str:
        """獲取天干名稱"""
        return BaziCalculator.STEMS[code] if 0 <= code < 10 else ''
    
    @staticmethod
    def _get_branch_name(code: int) -> str:
        """獲取地支名稱"""
        return BaziCalculator.BRANCHES[code] if 0 <= code < 12 else ''
    
    @staticmethod
    def _get_zodiac(branch_code: int) -> str:
        """獲取生肖"""
        zodiacs = ['鼠', '牛', '虎', '兔', '龍', '蛇', 
                  '馬', '羊', '猴', '雞', '狗', '豬']
        return zodiacs[branch_code] if 0 <= branch_code < 12 else '未知'
    
    @staticmethod
    def _analyze_details(bazi_data: Dict, gender: str, audit_log: List[str]) -> Dict:
        """深度分析八字細節"""
        # 1. 計算五行分佈
        bazi_data["elements"] = BaziCalculator._calculate_elements(bazi_data)
        
        # 2. 計算身強弱
        strength_score = BaziCalculator._calculate_strength_score(bazi_data, audit_log)
        bazi_data["strength_score"] = strength_score
        bazi_data["day_stem_strength"] = BaziCalculator._determine_strength(strength_score)
        
        # 3. 判斷格局
        bazi_data["pattern_type"] = BaziCalculator._determine_pattern(bazi_data, audit_log)
        
        # 4. 計算喜用神
        bazi_data["useful_elements"] = BaziCalculator._calculate_useful_elements(bazi_data, gender, audit_log)
        bazi_data["harmful_elements"] = BaziCalculator._calculate_harmful_elements(bazi_data, gender)
        
        # 5. 分析夫妻星
        spouse_status, spouse_effective = BaziCalculator._analyze_spouse_star(bazi_data, gender)
        bazi_data["spouse_star_status"] = spouse_status
        bazi_data["spouse_star_effective"] = spouse_effective
        
        # 6. 分析夫妻宮
        palace_status, pressure_score = BaziCalculator._analyze_spouse_palace(bazi_data)
        bazi_data["spouse_palace_status"] = palace_status
        bazi_data["pressure_score"] = pressure_score
        
        # 7. 計算神煞
        shen_sha_names, shen_sha_bonus = BaziCalculator._calculate_shen_sha(bazi_data)
        bazi_data["shen_sha_names"] = shen_sha_names
        bazi_data["shen_sha_bonus"] = shen_sha_bonus
        
        # 8. 計算十神結構
        bazi_data["shi_shen_structure"] = BaziCalculator._calculate_shi_shen(bazi_data, gender)
        
        return bazi_data
    
    @staticmethod
    def _calculate_elements(bazi_data: Dict) -> Dict[str, float]:
        """計算五行分佈"""
        elements = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
        
        pillars = [
            bazi_data.get('year_pillar', ''),
            bazi_data.get('month_pillar', ''),
            bazi_data.get('day_pillar', ''),
            bazi_data.get('hour_pillar', '')
        ]
        
        weights = [1.0, 1.8, 1.5, 1.2]
        
        for pillar, weight in zip(pillars, weights):
            if len(pillar) >= 2:
                stem = pillar[0]
                branch = pillar[1]
                
                stem_element = BaziCalculator.STEM_ELEMENTS.get(stem)
                if stem_element:
                    elements[stem_element] += weight
                
                branch_element = BaziCalculator.BRANCH_ELEMENTS.get(branch)
                if branch_element:
                    elements[branch_element] += weight * 0.5
                
                hidden_stems = BaziCalculator.BRANCH_HIDDEN_STEMS.get(branch, [])
                for hidden_stem, hidden_weight in hidden_stems:
                    hidden_element = BaziCalculator.STEM_ELEMENTS.get(hidden_stem)
                    if hidden_element:
                        elements[hidden_element] += weight * hidden_weight
        
        total = sum(elements.values())
        if total > 0:
            for element in elements:
                elements[element] = round(elements[element] * 100 / total, 1)
        
        return elements
    
    @staticmethod
    def _calculate_strength_score(bazi_data: Dict, audit_log: List[str]) -> float:
        """計算身強弱分數"""
        day_stem = bazi_data.get('day_stem', '')
        day_element = BaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        
        if not day_element:
            return C.DEFAULT_STRENGTH_SCORE
        
        score = 0
        
        # 月令氣勢
        month_strength = BaziCalculator._get_month_qi_strength(bazi_data, day_element)
        score += month_strength
        
        # 通根力量
        tong_gen_score = BaziCalculator._calculate_tong_gen(bazi_data, day_element)
        score += tong_gen_score
        
        # 生扶力量
        support_score = BaziCalculator._calculate_support(bazi_data, day_element)
        score += support_score
        
        final_score = min(100, max(0, score))
        return final_score
    
    @staticmethod
    def _get_month_qi_strength(bazi_data: Dict, day_element: str) -> float:
        """獲取月令氣勢"""
        try:
            month_branch_code = sxtwl.fromSolar(
                bazi_data.get('adjusted_year', bazi_data.get('birth_year', 2000)),
                bazi_data.get('adjusted_month', bazi_data.get('birth_month', 1)),
                1
            ).getMonthGZ().dz
            month_branch = BaziCalculator.BRANCHES[month_branch_code]
            
            qi_info = C.MONTH_QI_MAP.get(month_branch, {})
            
            score = 0.0
            if BaziCalculator.STEM_ELEMENTS.get(qi_info.get('yuqi')) == day_element:
                score += C.MONTH_WEIGHT * 0.3
            if BaziCalculator.STEM_ELEMENTS.get(qi_info.get('zhongqi')) == day_element:
                score += C.MONTH_WEIGHT * 0.4
            if BaziCalculator.STEM_ELEMENTS.get(qi_info.get('zhengqi')) == day_element:
                score += C.MONTH_WEIGHT * 0.3
            
            return score
            
        except Exception as e:
            logger.warning(f"月令氣勢計算失敗: {e}")
            return C.MONTH_WEIGHT * 0.5
    
    @staticmethod
    def _calculate_tong_gen(bazi_data: Dict, day_element: str) -> float:
        """計算通根力量"""
        pillars = [
            bazi_data.get('year_pillar', ''),
            bazi_data.get('month_pillar', ''),
            bazi_data.get('day_pillar', ''),
            bazi_data.get('hour_pillar', '')
        ]
        
        score = 0
        for pillar in pillars:
            if len(pillar) >= 2:
                branch = pillar[1]
                hidden_stems = BaziCalculator.BRANCH_HIDDEN_STEMS.get(branch, [])
                for stem, weight in hidden_stems:
                    if BaziCalculator.STEM_ELEMENTS.get(stem) == day_element:
                        score += weight * C.TONG_GEN_WEIGHT
                        break
        
        return score
    
    @staticmethod
    def _calculate_support(bazi_data: Dict, day_element: str) -> float:
        """計算生扶力量"""
        pillars = [
            bazi_data.get('year_pillar', ''),
            bazi_data.get('month_pillar', ''),
            bazi_data.get('day_pillar', ''),
            bazi_data.get('hour_pillar', '')
        ]
        
        score = 0
        
        # 印星生扶
        for pillar in pillars:
            if len(pillar) >= 2:
                stem = pillar[0]
                stem_element = BaziCalculator.STEM_ELEMENTS.get(stem)
                
                if stem_element == '水' and day_element == '木':
                    score += C.SUPPORT_WEIGHT * 0.8
                elif stem_element == '木' and day_element == '火':
                    score += C.SUPPORT_WEIGHT * 0.8
                elif stem_element == '火' and day_element == '土':
                    score += C.SUPPORT_WEIGHT * 0.8
                elif stem_element == '土' and day_element == '金':
                    score += C.SUPPORT_WEIGHT * 0.8
                elif stem_element == '金' and day_element == '水':
                    score += C.SUPPORT_WEIGHT * 0.8
        
        # 比肩劫財
        for pillar in pillars:
            if len(pillar) >= 2:
                stem = pillar[0]
                if BaziCalculator.STEM_ELEMENTS.get(stem) == day_element:
                    score += C.SUPPORT_WEIGHT * 0.2
        
        return score
    
    @staticmethod
    def _determine_strength(score: float) -> str:
        """判斷身強弱"""
        if score >= C.STRENGTH_THRESHOLD_STRONG:
            return '強'
        elif score >= C.STRENGTH_THRESHOLD_MEDIUM:
            return '中'
        else:
            return '弱'
    
    @staticmethod
    def _determine_pattern(bazi_data: Dict, audit_log: List[str]) -> str:
        """判斷格局類型"""
        strength_score = bazi_data.get('strength_score', 50)
        day_stem = bazi_data.get('day_stem', '')
        
        if day_stem in C.YANG_STEMS:
            if strength_score < 20:
                return '從格'
        elif day_stem in C.YIN_STEMS:
            if strength_score < 20:
                return '從格'
        
        if strength_score > 80:
            return '專旺格'
        
        return '正格'
    
    @staticmethod
    def _calculate_useful_elements(bazi_data: Dict, gender: str, audit_log: List[str]) -> List[str]:
        """計算喜用神"""
        pattern_type = bazi_data.get('pattern_type', '正格')
        strength_score = bazi_data.get('strength_score', 50)
        day_element = bazi_data.get('day_stem_element', '')
        
        useful_elements = []
        
        if pattern_type == '從格':
            elements = bazi_data.get('elements', {})
            other_elements = {k: v for k, v in elements.items() if k != day_element}
            if other_elements:
                max_element = max(other_elements.items(), key=lambda x: x[1])[0]
                useful_elements.append(max_element)
            else:
                useful_elements.append(day_element)
            
        elif pattern_type == '專旺格':
            useful_elements.append(day_element)
            
        else:
            if strength_score >= C.STRENGTH_THRESHOLD_STRONG:
                if day_element == '木':
                    useful_elements.extend(['金', '火', '土'])
                elif day_element == '火':
                    useful_elements.extend(['水', '土', '金'])
                elif day_element == '土':
                    useful_elements.extend(['木', '金', '水'])
                elif day_element == '金':
                    useful_elements.extend(['火', '水', '木'])
                elif day_element == '水':
                    useful_elements.extend(['土', '木', '火'])
                    
            elif strength_score < C.STRENGTH_THRESHOLD_MEDIUM:
                if day_element == '木':
                    useful_elements.extend(['水', '木'])
                elif day_element == '火':
                    useful_elements.extend(['木', '火'])
                elif day_element == '土':
                    useful_elements.extend(['火', '土'])
                elif day_element == '金':
                    useful_elements.extend(['土', '金'])
                elif day_element == '水':
                    useful_elements.extend(['金', '水'])
                    
            else:
                useful_elements.append(day_element)
                if day_element == '木':
                    useful_elements.append('水')
                elif day_element == '火':
                    useful_elements.append('木')
                elif day_element == '土':
                    useful_elements.append('火')
                elif day_element == '金':
                    useful_elements.append('土')
                elif day_element == '水':
                    useful_elements.append('金')
        
        useful_elements = list(set([e for e in useful_elements if e]))
        
        if not useful_elements:
            useful_elements.append(day_element)
        
        return useful_elements
    
    @staticmethod
    def _calculate_harmful_elements(bazi_data: Dict, gender: str) -> List[str]:
        """計算忌神"""
        useful_elements = bazi_data.get('useful_elements', [])
        day_element = bazi_data.get('day_stem_element', '')
        
        all_elements = ['木', '火', '土', '金', '水']
        
        harmful_elements = []
        for element in all_elements:
            if element not in useful_elements:
                harmful_elements.append(element)
        
        if day_element in harmful_elements:
            harmful_elements.remove(day_element)
        
        return harmful_elements
    
    @staticmethod
    def _analyze_spouse_star(bazi_data: Dict, gender: str) -> Tuple[str, str]:
        """分析夫妻星"""
        SPOUSE_STARS = {
            '男': {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'},
            '女': {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
        }
        
        day_stem = bazi_data.get('day_stem', '')
        day_element = BaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        
        if gender not in ['男', '女'] or not day_element:
            return "未知", "未知"
        
        spouse_element = SPOUSE_STARS[gender].get(day_element, '')
        if not spouse_element:
            return "無夫妻星", "無"
        
        pillars = [
            bazi_data.get('year_pillar', ''),
            bazi_data.get('month_pillar', ''),
            bazi_data.get('day_pillar', ''),
            bazi_data.get('hour_pillar', '')
        ]
        
        spouse_count = 0
        for pillar in pillars:
            if len(pillar) >= 2:
                stem = pillar[0]
                branch = pillar[1]
                
                if BaziCalculator.STEM_ELEMENTS.get(stem) == spouse_element:
                    spouse_count += 1
                
                if BaziCalculator.BRANCH_ELEMENTS.get(branch) == spouse_element:
                    spouse_count += 1
        
        if spouse_count == 0:
            return "無夫妻星", "無"
        elif spouse_count == 1:
            return "夫妻星單一", "弱"
        elif spouse_count == 2:
            return "夫妻星明顯", "中"
        else:
            return "夫妻星旺盛", "強"
    
    @staticmethod
    def _analyze_spouse_palace(bazi_data: Dict) -> Tuple[str, float]:
        """分析夫妻宮"""
        day_pillar = bazi_data.get('day_pillar', '')
        if len(day_pillar) < 2:
            return "未知", 0
        
        day_branch = day_pillar[1]
        pressure_score = 0
        status = "穩定"
        
        return status, pressure_score
    
    @staticmethod
    def _calculate_shen_sha(bazi_data: Dict) -> Tuple[str, float]:
        """計算神煞"""
        shen_sha_list = []
        total_bonus = 0
        
        day_stem = bazi_data.get('day_stem', '')
        year_branch = bazi_data.get('year_pillar', '  ')[1]
        
        hong_luan_map = {
            '子': '午', '丑': '巳', '寅': '辰', '卯': '卯',
            '辰': '寅', '巳': '丑', '午': '子', '未': '亥',
            '申': '戌', '酉': '酉', '戌': '申', '亥': '未'
        }
        
        hong_luan_branch = hong_luan_map.get(year_branch)
        all_branches = [
            bazi_data.get('year_pillar', '  ')[1],
            bazi_data.get('month_pillar', '  ')[1],
            bazi_data.get('day_pillar', '  ')[1],
            bazi_data.get('hour_pillar', '  ')[1]
        ]
        
        if hong_luan_branch in all_branches:
            shen_sha_list.append("紅鸞")
            total_bonus += C.SHEN_SHA_POSITIVE.get("紅鸞", 0)
        
        tian_yi_map = {
            '甲': ['丑', '未'], '乙': ['子', '申'], '丙': ['亥', '酉'],
            '丁': ['亥', '酉'], '戊': ['丑', '未'], '己': ['子', '申'],
            '庚': ['丑', '未'], '辛': ['寅', '午'], '壬': ['寅', '午'],
            '癸': ['寅', '午']
        }
        
        tian_yi_branches = tian_yi_map.get(day_stem, [])
        for branch in all_branches:
            if branch in tian_yi_branches:
                shen_sha_list.append("天乙貴人")
                total_bonus += C.SHEN_SHA_POSITIVE.get("天乙貴人", 0)
                break
        
        shen_sha_names = "、".join(shen_sha_list) if shen_sha_list else "無"
        return shen_sha_names, total_bonus
    
    @staticmethod
    def _calculate_shi_shen(bazi_data: Dict, gender: str) -> str:
        """計算十神結構"""
        day_stem = bazi_data.get('day_stem', '')
        
        if not day_stem:
            return "普通結構"
        
        shi_shen_map = {
            '甲': {'甲': '比肩', '乙': '劫財', '丙': '食神', '丁': '傷官', '戊': '偏財',
                  '己': '正財', '庚': '七殺', '辛': '正官', '壬': '偏印', '癸': '正印'},
            '乙': {'甲': '劫財', '乙': '比肩', '丙': '傷官', '丁': '食神', '戊': '正財',
                  '己': '偏財', '庚': '正官', '辛': '七殺', '壬': '正印', '癸': '偏印'},
        }
        
        stems = []
        for pillar in [bazi_data.get('year_pillar', ''), 
                      bazi_data.get('month_pillar', ''), 
                      bazi_data.get('hour_pillar', '')]:
            if len(pillar) >= 1:
                stems.append(pillar[0])
        
        shi_shen_list = []
        mapping = shi_shen_map.get(day_stem, {})
        for stem in stems:
            if stem in mapping:
                shi_shen_list.append(mapping[stem])
        
        structure_features = []
        
        if '七殺' in shi_shen_list and '正印' in shi_shen_list:
            structure_features.append("殺印相生")
        
        if '正官' in shi_shen_list and '正財' in shi_shen_list:
            structure_features.append("財官相生")
        
        if structure_features:
            return "、".join(structure_features)
        else:
            return "普通結構"
# 🔖 1.4 八字核心引擎結束

# 🔖 1.5 評分引擎開始
class ScoringEngine:
    """評分引擎 - 專業命理評分"""
    
    @staticmethod
    def calculate_score_parts(bazi1: Dict, bazi2: Dict, gender1: str, gender2: str) -> Dict:
        """
        計算命理評分部分
        返回各模組分數供主入口計算最終分數
        """
        try:
            audit_log = []
            score_parts = {
                "energy_rescue": 0,
                "structure_core": 0,
                "personality_risk": 0,
                "pressure_penalty": 0,
                "shen_sha_bonus": 0,
                "resolution_bonus": 0,
                "a_to_b_influence": 0,
                "b_to_a_influence": 0,
                "dayun_risk": 0,
                "relationship_model": "未知",
                "audit_log": audit_log
            }
            
            # 1. 能量救應 - 使用增強版計算
            rescue_score, rescue_details = ScoringEngine._calculate_energy_rescue_enhanced(bazi1, bazi2)
            score_parts["energy_rescue"] = rescue_score
            audit_log.append(f"能量救應: {rescue_score:.1f}分")
            audit_log.extend(rescue_details)
            
            # 2. 結構核心 - 天合地合優先
            structure_score, structure_details = ScoringEngine._calculate_structure_core_professional(bazi1, bazi2)
            score_parts["structure_core"] = structure_score
            audit_log.append(f"結構核心: {structure_score:.1f}分")
            audit_log.extend(structure_details)
            
            # 3. 人格風險 - 十神衝突
            personality_score, personality_details = ScoringEngine._calculate_personality_risk_professional(bazi1, bazi2)
            score_parts["personality_risk"] = personality_score
            audit_log.append(f"人格風險: {personality_score:.1f}分")
            audit_log.extend(personality_details)
            
            # 4. 刑沖壓力 - 沖合抵銷
            pressure_score, pressure_details = ScoringEngine._calculate_pressure_penalty_professional(bazi1, bazi2)
            score_parts["pressure_penalty"] = pressure_score
            audit_log.append(f"刑沖壓力: {pressure_score:.1f}分")
            audit_log.extend(pressure_details)
            
            # 5. 神煞加持 - 成對有效
            shen_sha_score, shen_sha_details = ScoringEngine._calculate_shen_sha_bonus_professional(bazi1, bazi2)
            score_parts["shen_sha_bonus"] = shen_sha_score
            audit_log.append(f"神煞加持: {shen_sha_score:.1f}分")
            audit_log.extend(shen_sha_details)
            
            # 6. 專業化解 - 模式匹配
            resolution_score, resolution_details = ScoringEngine._calculate_resolution_bonus_professional(bazi1, bazi2)
            score_parts["resolution_bonus"] = resolution_score
            audit_log.append(f"專業化解: {resolution_score:.1f}分")
            audit_log.extend(resolution_details)
            
            # 7. 雙向影響 - 不對稱分析
            a_to_b, b_to_a, directional_details = ScoringEngine._calculate_asymmetric_scores_professional(bazi1, bazi2, gender1, gender2)
            score_parts["a_to_b_influence"] = a_to_b
            score_parts["b_to_a_influence"] = b_to_a
            audit_log.append(f"雙向影響: A→B={a_to_b:.1f}, B→A={b_to_a:.1f}")
            audit_log.extend(directional_details)
            
            # 8. 大運風險 - 未來同步
            dayun_risk, dayun_details = ScoringEngine._calculate_dayun_risk_professional(bazi1, bazi2)
            score_parts["dayun_risk"] = dayun_risk
            audit_log.append(f"大運風險: {dayun_risk:.1f}分")
            audit_log.extend(dayun_details)
            
            # 9. 關係模型 - 分數推導
            relationship_model, model_details = ScoringEngine._determine_relationship_model_professional(
                a_to_b, b_to_a, score_parts
            )
            score_parts["relationship_model"] = relationship_model
            audit_log.append(f"關係模型: {relationship_model}")
            audit_log.extend(model_details)
            
            logger.info(f"命理評分計算完成: 各模組分數就緒")
            return score_parts
            
        except Exception as e:
            logger.error(f"評分計算錯誤: {e}", exc_info=True)
            raise ScoringEngineError(f"評分計算失敗: {str(e)}")
    
    # ========== 基礎工具方法開始 ==========
    @staticmethod
    def is_clash(branch1: str, branch2: str) -> bool:
        """檢查是否六沖"""
        clashes = {'子': '午', '午': '子', '丑': '未', '未': '丑',
              '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
              '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
        return clashes.get(branch1) == branch2
    
    @staticmethod
    def is_harm(branch1: str, branch2: str) -> bool:
        """檢查是否六害"""
        harms = {'子': '未', '未': '子', '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅', '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申', '酉': '戌', '戌': '酉'}
        return harms.get(branch1) == branch2
    
    @staticmethod
    def is_stem_harmony(stem1: str, stem2: str) -> bool:
        """檢查天干是否五合"""
        five_harmony_pairs = [('甲', '己'), ('乙', '庚'), ('丙', '辛'), ('丁', '壬'), ('戊', '癸')]
        return tuple(sorted([stem1, stem2])) in five_harmony_pairs
    
    @staticmethod
    def is_branch_harmony(branch1: str, branch2: str) -> bool:
        """檢查地支是否六合"""
        six_harmony_pairs = [('子', '丑'), ('寅', '亥'), ('卯', '戌'), 
                            ('辰', '酉'), ('巳', '申'), ('午', '未')]
        return tuple(sorted([branch1, branch2])) in six_harmony_pairs
    # ========== 基礎工具方法結束 ==========
    
    @staticmethod
    def _calculate_energy_rescue_enhanced(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算能量救應分數 - 增強版"""
        score = 0
        details = []
        
        elements1 = bazi1.get('elements', {})
        elements2 = bazi2.get('elements', {})
        useful1 = bazi1.get('useful_elements', [])
        useful2 = bazi2.get('useful_elements', [])
        
        # 輔助函數：計算單向救應
        def calc_rescue(needed_elements, supplier_elements, person_name):
            sub_score = 0
            for element in needed_elements:
                if element in supplier_elements:
                    concentration = supplier_elements[element]
                    if concentration > 5:  # 降低閾值，讓更多匹配生效
                        # 新公式：濃度/30，分母變小，分數變大
                        factor = min(1.5, concentration / 30.0)
                        bonus = C.DEMAND_MATCH_BONUS_BASE * factor
                        sub_score += bonus
                        details.append(f"{person_name}喜{element}，對方有{concentration:.1f}%: +{bonus:.1f}分")
            return sub_score

        # A喜用 vs B五行
        score += calc_rescue(useful1, elements2, "A")
        # B喜用 vs A五行
        score += calc_rescue(useful2, elements1, "B")
        
        # 極弱救應 - 增強
        if bazi1.get('strength_score', 50) < C.WEAK_THRESHOLD:
            day_element = bazi1.get('day_stem_element', '')
            if elements2.get(day_element, 0) > 25:
                score += C.EXTREME_WEAK_BONUS
                details.append(f"A身極弱，B強{day_element}救應: +{C.EXTREME_WEAK_BONUS}分")
                
        if bazi2.get('strength_score', 50) < C.WEAK_THRESHOLD:
            day_element = bazi2.get('day_stem_element', '')
            if elements1.get(day_element, 0) > 25:
                score += C.EXTREME_WEAK_BONUS
                details.append(f"B身極弱，A強{day_element}救應: +{C.EXTREME_WEAK_BONUS}分")

        final_score = min(C.ENERGY_RESCUE_CAP, max(0, score))
        if final_score != score:
            details.append(f"能量救應上限控制: {score:.1f}→{final_score:.1f}分")
        
        return final_score, details
    
    @staticmethod
    def _calculate_structure_core_professional(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算結構核心分數 - 天合地合優先"""
        score = 0
        details = []
        
        # 日柱天干關係
        day_stem1 = bazi1.get('day_stem', '')
        day_stem2 = bazi2.get('day_stem', '')
        
        # 天干五合（天作之合）
        if ScoringEngine.is_stem_harmony(day_stem1, day_stem2):
            score += C.STEM_COMBINATION_FIVE_HARMONY
            details.append(f"日干五合 {day_stem1}-{day_stem2}: +{C.STEM_COMBINATION_FIVE_HARMONY:.1f}分")
        
        # 日柱地支關係
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        
        # 地支六合（地合人和）
        if ScoringEngine.is_branch_harmony(day_branch1, day_branch2):
            score += C.BRANCH_COMBINATION_SIX_HARMONY
            details.append(f"日支六合 {day_branch1}-{day_branch2}: +{C.BRANCH_COMBINATION_SIX_HARMONY:.1f}分")
        
        # 檢查天干相生
        stem_elements = {
            '甲': '木', '乙': '木', '丙': '火', '丁': '火',
            '戊': '土', '己': '土', '庚': '金', '辛': '金',
            '壬': '水', '癸': '水'
        }
        
        element1 = stem_elements.get(day_stem1, '')
        element2 = stem_elements.get(day_stem2, '')
        
        # 相生關係
        if (element1 == '木' and element2 == '火') or (element1 == '火' and element2 == '木'):
            score += C.STEM_COMBINATION_GENERATION
            details.append(f"日干相生 {day_stem1}→{day_stem2}: +{C.STEM_COMBINATION_GENERATION:.1f}分")
        elif (element1 == '火' and element2 == '土') or (element1 == '土' and element2 == '火'):
            score += C.STEM_COMBINATION_GENERATION
            details.append(f"日干相生 {day_stem1}→{day_stem2}: +{C.STEM_COMBINATION_GENERATION:.1f}分")
        elif (element1 == '土' and element2 == '金') or (element1 == '金' and element2 == '土'):
            score += C.STEM_COMBINATION_GENERATION
            details.append(f"日干相生 {day_stem1}→{day_stem2}: +{C.STEM_COMBINATION_GENERATION:.1f}分")
        elif (element1 == '金' and element2 == '水') or (element1 == '水' and element2 == '金'):
            score += C.STEM_COMBINATION_GENERATION
            details.append(f"日干相生 {day_stem1}→{day_stem2}: +{C.STEM_COMBINATION_GENERATION:.1f}分")
        elif (element1 == '水' and element2 == '木') or (element1 == '木' and element2 == '水'):
            score += C.STEM_COMBINATION_GENERATION
            details.append(f"日干相生 {day_stem1}→{day_stem2}: +{C.STEM_COMBINATION_GENERATION:.1f}分")
        
        # 相同五行
        if element1 == element2:
            score += C.STEM_COMBINATION_SAME
            details.append(f"日干比和 {day_stem1}-{day_stem2}: +{C.STEM_COMBINATION_SAME:.1f}分")
        
        # 上限控制
        final_score = min(C.STRUCTURE_CORE_CAP, max(0, score))
        if final_score != score:
            details.append(f"結構核心上限控制: {score:.1f}→{final_score:.1f}分")
        
        return final_score, details
    
    @staticmethod
    def _calculate_personality_risk_professional(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算人格風險分數 - 十神衝突"""
        score = 0
        details = []
        
        structure1 = bazi1.get('shi_shen_structure', '')
        structure2 = bazi2.get('shi_shen_structure', '')
        
        risk_count = 0
        
        for pattern, penalty in C.PERSONALITY_RISK_PATTERNS.items():
            if pattern in structure1:
                score += penalty
                risk_count += 1
                details.append(f"A方{pattern}: {penalty:.1f}分")
            
            if pattern in structure2:
                score += penalty
                risk_count += 1
                details.append(f"B方{pattern}: {penalty:.1f}分")
        
        # 疊加風險額外扣分
        if risk_count >= 2:
            score += C.PERSONALITY_STACKED_PENALTY
            details.append(f"疊加風險({risk_count}個): {C.PERSONALITY_STACKED_PENALTY:.1f}分")
        
        # 人格風險上限
        if score < C.PERSONALITY_RISK_CAP:
            details.append(f"人格風險上限控制: {score:.1f}→{C.PERSONALITY_RISK_CAP:.1f}分")
            score = C.PERSONALITY_RISK_CAP
        
        return score, details
    
    @staticmethod
    def _calculate_pressure_penalty_professional(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算刑沖壓力分數 - 沖合抵銷"""
        score = 0
        details = []
        
        # 收集所有地支
        branches1 = []
        branches2 = []
        
        for pillar in [bazi1.get('year_pillar', ''), bazi1.get('month_pillar', ''), 
                      bazi1.get('day_pillar', ''), bazi1.get('hour_pillar', '')]:
            if len(pillar) >= 2:
                branches1.append(pillar[1])
        
        for pillar in [bazi2.get('year_pillar', ''), bazi2.get('month_pillar', ''), 
                      bazi2.get('day_pillar', ''), bazi2.get('hour_pillar', '')]:
            if len(pillar) >= 2:
                branches2.append(pillar[1])
        
        if not branches1 or not branches2:
            details.append("地支收集失敗，無刑沖")
            return 0, details
        
        clash_count = 0
        harm_count = 0
        
        for b1 in branches1:
            for b2 in branches2:
                # 檢查六沖
                if ScoringEngine.is_clash(b1, b2):
                    # 日支六沖特別重扣
                    if b1 == bazi1.get('day_pillar', '  ')[1] and b2 == bazi2.get('day_pillar', '  ')[1]:
                        penalty = C.DAY_CLASH_PENALTY
                        details.append(f"日支六沖 {b1}↔{b2}: {penalty:.1f}分")
                    else:
                        penalty = C.BRANCH_CLASH_PENALTY
                        details.append(f"六沖 {b1}↔{b2}: {penalty:.1f}分")
                    
                    score += penalty
                    clash_count += 1
                
                # 檢查六害
                if ScoringEngine.is_harm(b1, b2):
                    # 日支六害特別重扣
                    if b1 == bazi1.get('day_pillar', '  ')[1] and b2 == bazi2.get('day_pillar', '  ')[1]:
                        penalty = C.DAY_HARM_PENALTY
                        details.append(f"日支六害 {b1}↔{b2}: {penalty:.1f}分")
                    else:
                        penalty = C.BRANCH_HARM_PENALTY
                        details.append(f"六害 {b1}↔{b2}: {penalty:.1f}分")
                    
                    score += penalty
                    harm_count += 1
        
        if clash_count > 0 or harm_count > 0:
            details.append(f"總計: 六沖{clash_count}個, 六害{harm_count}個")
        else:
            details.append("無刑沖")
        
        # 刑沖壓力上限控制
        if score < C.PRESSURE_PENALTY_CAP:
            details.append(f"刑沖壓力上限控制: {score:.1f}→{C.PRESSURE_PENALTY_CAP:.1f}分")
            score = C.PRESSURE_PENALTY_CAP
        
        return score, details
    
    @staticmethod
    def _calculate_shen_sha_bonus_professional(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算神煞加持分數 - 成對有效"""
        details = []
        
        bonus1 = bazi1.get('shen_sha_bonus', 0)
        bonus2 = bazi2.get('shen_sha_bonus', 0)
        
        total_bonus = bonus1 + bonus2
        
        details.append(f"A方神煞: {bazi1.get('shen_sha_names', '無')} ({bonus1:.1f}分)")
        details.append(f"B方神煞: {bazi2.get('shen_sha_names', '無')} ({bonus2:.1f}分)")
        
        # 神煞組合加成檢查
        shen_sha_names1 = bazi1.get('shen_sha_names', '').split('、')
        shen_sha_names2 = bazi2.get('shen_sha_names', '').split('、')
        
        for sha1 in shen_sha_names1:
            for sha2 in shen_sha_names2:
                if sha1 and sha2 and (sha1, sha2) in C.SHEN_SHA_COMBO_BONUS:
                    combo_bonus = C.SHEN_SHA_COMBO_BONUS[(sha1, sha2)]
                    total_bonus += combo_bonus
                    details.append(f"神煞組合 {sha1}+{sha2}: +{combo_bonus:.1f}分")
        
        # 上限控制
        if total_bonus > C.SHEN_SHA_BONUS_CAP:
            details.append(f"神煞上限控制: {total_bonus:.1f}→{C.SHEN_SHA_BONUS_CAP:.1f}分")
            total_bonus = C.SHEN_SHA_BONUS_CAP
        
        # 注意：已刪除神煞保底分，不再有最低分保證
        
        return total_bonus, details
    
    @staticmethod
    def _calculate_resolution_bonus_professional(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算專業化解分數 - 模式匹配"""
        score = 0
        details = []
        
        structure1 = bazi1.get('shi_shen_structure', '')
        structure2 = bazi2.get('shi_shen_structure', '')
        
        for pattern, bonus in C.RESOLUTION_PATTERNS.items():
            if pattern in structure1 or pattern in structure2:
                score += bonus
                details.append(f"化解組合 {pattern}: +{bonus:.1f}分")
        
        final_score = min(C.RESOLUTION_BONUS_CAP, score)
        if final_score != score:
            details.append(f"專業化解上限控制: {score:.1f}→{final_score:.1f}分")
        
        return final_score, details
    
    @staticmethod
    def _calculate_asymmetric_scores_professional(bazi1: Dict, bazi2: Dict, 
                                                gender1: str, gender2: str) -> Tuple[float, float, List[str]]:
        """計算雙向不對稱分數 - 互動分析"""
        details = []
        
        a_to_b, a_to_b_details = ScoringEngine._calculate_directional_score_professional(
            bazi1, bazi2, gender1, gender2, "用戶A對用戶B"
        )
        details.extend(a_to_b_details)
        
        b_to_a, b_to_a_details = ScoringEngine._calculate_directional_score_professional(
            bazi2, bazi1, gender2, gender1, "用戶B對用戶A"
        )
        details.extend(b_to_a_details)
        
        return a_to_b, b_to_a, details
    
    @staticmethod
    def _calculate_directional_score_professional(source_bazi: Dict, target_bazi: Dict,
                                                source_gender: str, target_gender: str,
                                                direction: str) -> Tuple[float, List[str]]:
        """計算單向影響分數"""
        score = 50  # 中性起點
        details = []
        
        source_useful = source_bazi.get('useful_elements', [])
        target_elements = target_bazi.get('elements', {})
        
        # 喜用神匹配 - 增強計算
        useful_match_score = 0
        for element in source_useful:
            if element in target_elements:
                concentration = target_elements[element]
                if concentration > 25:  # 提高閾值
                    useful_match_score += 8  # 提高分數
                elif concentration > 15:
                    useful_match_score += 5
                else:
                    useful_match_score += 2
        
        score += useful_match_score
        
        # 配偶星影響 - 增強計算
        target_spouse_effective = target_bazi.get('spouse_star_effective', '未知')
        if target_spouse_effective == '強':
            score += 5  # 提高分數
        elif target_spouse_effective == '中':
            score += 3
        elif target_spouse_effective == '弱':
            score += 1
        
        final_score = max(0, min(100, round(score, 1)))
        details.append(f"{direction} 最終分數: {final_score:.1f}")
        
        return final_score, details
    
    @staticmethod
    def _calculate_dayun_risk_professional(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算大運風險 - 未來同步"""
        score = 0
        details = []
        
        # 簡單年齡差判斷大運同步率
        year1 = bazi1.get('birth_year', 2000)
        year2 = bazi2.get('birth_year', 2000)
        age_diff = abs(year1 - year2)
        
        if age_diff <= 3:
            details.append(f"年齡差{age_diff}歲，大運同步率高")
        elif age_diff <= 8:
            score -= 4
            details.append(f"年齡差{age_diff}歲，大運同步率中: -4分")
        elif age_diff <= 12:
            score -= 8
            details.append(f"年齡差{age_diff}歲，大運同步率低: -8分")
        else:
            score -= 12
            details.append(f"年齡差{age_diff}歲，大運同步率很低: -12分")
        
        # 大運風險上限
        if score < C.DAYUN_RISK_CAP:
            details.append(f"大運風險上限控制: {score:.1f}→{C.DAYUN_RISK_CAP:.1f}分")
            score = C.DAYUN_RISK_CAP
        
        return score, details
    
    @staticmethod
    def _determine_relationship_model_professional(a_to_b: float, b_to_a: float, 
                                                 score_parts: Dict) -> Tuple[str, List[str]]:
        """確定關係模型 - 分數推導"""
        details = []
        
        diff = abs(a_to_b - b_to_a)
        avg = (a_to_b + b_to_a) / 2
        
        details.append(f"雙向差異: {diff:.1f}分，平均: {avg:.1f}分")
        
        if avg >= 65 and diff < C.BALANCED_MAX_DIFF:
            model = "平衡型"
            details.append(f"平均分≥65且差異<{C.BALANCED_MAX_DIFF}，判定為平衡型")
        elif avg >= 55 and diff >= C.SUPPLY_MIN_DIFF:
            if a_to_b > b_to_a:
                model = "供求型 (用戶A供應用戶B)"
                details.append(f"平均分≥55且差異≥{C.SUPPLY_MIN_DIFF}，用戶A>用戶B，判定為供求型")
            else:
                model = "供求型 (用戶B供應用戶A)"
                details.append(f"平均分≥55且差異≥{C.SUPPLY_MIN_DIFF}，用戶B>用戶A，判定為供求型")
        else:
            model = "混合型"
            details.append("不符合平衡型或供求型條件，判定為混合型")
        
        return model, details
    
    @staticmethod
    def get_rating(score: float) -> str:
        """獲取評級"""
        return C.get_rating(score)
    
    @staticmethod
    def get_rating_with_description(score: float) -> Dict[str, str]:
        """獲取評級和描述"""
        return {
            "name": C.get_rating(score),
            "description": C.get_rating_description(score)
        }
# 🔖 1.5 評分引擎結束

# 🔖 1.6 主入口函數開始
def calculate_match(bazi1: Dict, bazi2: Dict, gender1: str, gender2: str, is_testpair: bool = False) -> Dict:
    """
    八字配對主入口函數
    """
    try:
        audit_log = []
        audit_log.append("八字配對計算開始")
        audit_log.append(f"基準分數: {C.BASE_SCORE}分")
        audit_log.append(f"現實保底分: {C.REALITY_FLOOR}分")
        
        # 檢查日支六沖/害
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        has_day_clash = ScoringEngine.is_clash(day_branch1, day_branch2)
        has_day_harm = ScoringEngine.is_harm(day_branch1, day_branch2)
        
        audit_log.append(f"日支檢測: A日支={day_branch1}, B日支={day_branch2}")
        audit_log.append(f"是否日支六沖: {has_day_clash}")
        audit_log.append(f"是否日支六害: {has_day_harm}")
        
        # 檢查相同八字（伏吟）
        pillars_same = all(bazi1.get(k) == bazi2.get(k) for k in ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar'])
        if pillars_same:
            audit_log.append("⚠️ 相同八字(伏吟)")
        
        # ========== 核心分數計算開始 ==========
        
        # 1. 計算命理評分部分
        audit_log.append("📊 開始計算命理評分模組...")
        score_parts = ScoringEngine.calculate_score_parts(bazi1, bazi2, gender1, gender2)
        audit_log.extend(score_parts.get("audit_log", []))
        
        # 2. 相同八字懲罰
        if pillars_same:
            audit_log.append(f"⚠️ 相同八字(伏吟)懲罰: 結構-15分")
            score_parts["structure_core"] = max(0, score_parts["structure_core"] - 15)
        
        # 3. 計算干涉係數 (Interference Factor) - 關鍵新增邏輯
        interference_factor = 1.0
        pressure_score = score_parts["pressure_penalty"]
        
        if has_day_clash:
            interference_factor = 0.4  # 日支沖，加分只剩4成
            audit_log.append("⚠️ 日支相沖，啟動強力干涉：所有正向加分 x 0.4")
        elif pressure_score < -15:
            interference_factor = 0.7  # 普通刑沖重，加分7折
            audit_log.append(f"⚠️ 刑沖壓力大({pressure_score:.1f})，啟動干涉：所有正向加分 x 0.7")
        
        # 4. 計算基礎總分
        base_score = C.BASE_SCORE
        audit_log.append(f"📈 起始基準分: {base_score}分")
        
        # 5. 正向加分計算（應用干涉係數）
        raw_bonus = (
            score_parts["energy_rescue"] + 
            score_parts["structure_core"] + 
            score_parts["shen_sha_bonus"] + 
            score_parts["resolution_bonus"]
        ) * interference_factor  # 應用干涉係數
        
        audit_log.append(f"📈 正向加分原始值: {raw_bonus:.1f}分")
        
        # 6. 負向扣分計算
        negative_scores = (
            score_parts["personality_risk"] + 
            score_parts["pressure_penalty"] + 
            score_parts["dayun_risk"]
        )
        audit_log.append(f"📉 負向扣分: {negative_scores:.1f}分")
        
        # 7. 能量救應抵銷負面分數
        rescue_deduction = 0
        if score_parts["energy_rescue"] > 0:
            rescue_deduction = abs(negative_scores) * C.RESCUE_DEDUCTION_RATIO * (score_parts["energy_rescue"] / C.ENERGY_RESCUE_CAP)
            negative_scores_after_rescue = negative_scores + rescue_deduction
            audit_log.append(f"🛡️ 能量救應抵銷負面分數: {rescue_deduction:.1f}分")
            audit_log.append(f"🛡️ 救應後負向扣分: {negative_scores_after_rescue:.1f}分")
        else:
            negative_scores_after_rescue = negative_scores
        
        # 8. 總扣分上限保護
        if negative_scores_after_rescue < C.TOTAL_PENALTY_CAP:
            audit_log.append(f"🛡️ 總扣分上限保護: {negative_scores_after_rescue:.1f}→{C.TOTAL_PENALTY_CAP:.1f}分")
            negative_scores_after_rescue = C.TOTAL_PENALTY_CAP
        
        # 9. 總分計算
        adjusted_score = base_score + raw_bonus + negative_scores_after_rescue
        audit_log.append(f"🧮 基礎總分計算: {base_score} + {raw_bonus:.1f} + {negative_scores_after_rescue:.1f} = {adjusted_score:.1f}分")
        
        # 10. 刑沖硬上限機制 - 強化處理
        if has_day_clash:
            hard_cap = C.DAY_CLASH_HARD_CAP
            if adjusted_score > hard_cap:
                audit_log.append(f"⚠️ 日支六沖硬上限截斷: {adjusted_score:.1f}→{hard_cap}分")
                adjusted_score = hard_cap
        elif has_day_harm:
            hard_cap = C.DAY_HARM_HARD_CAP
            if adjusted_score > hard_cap:
                audit_log.append(f"⚠️ 日支六害硬上限截斷: {adjusted_score:.1f}→{hard_cap}分")
                adjusted_score = hard_cap
        
        # 11. 相同八字上限
        if pillars_same and adjusted_score > 60:  # 相同八字上限60分
            adjusted_score = min(adjusted_score, 60)
            audit_log.append(f"⚠️ 相同八字上限: 最高60分")
        
        # 12. 正向加分飽和（防通脹）
        if raw_bonus > C.POSITIVE_BONUS_CAP:
            excess = raw_bonus - C.POSITIVE_BONUS_CAP
            adjusted_score = adjusted_score - excess + (excess * C.POSITIVE_SATURATION_FACTOR)
            audit_log.append(f"📊 正向加分飽和控制: 超過{C.POSITIVE_BONUS_CAP}部分打{C.POSITIVE_SATURATION_FACTOR*100:.0f}%折扣")
        
        # 13. 應用現實校準
        calibrated_score = adjusted_score
        
        # 年齡差距調整
        age_diff = abs(bazi1.get('birth_year', 0) - bazi2.get('birth_year', 0))
        if age_diff > 12:
            calibrated_score += C.AGE_GAP_PENALTY_13_PLUS
            audit_log.append(f"👥 年齡差距>12歲: {C.AGE_GAP_PENALTY_13_PLUS}分")
        elif age_diff > 8:
            calibrated_score += C.AGE_GAP_PENALTY_9_12
            audit_log.append(f"👥 年齡差距9-12歲: {C.AGE_GAP_PENALTY_9_12}分")
        elif age_diff > 4:
            calibrated_score += C.AGE_GAP_PENALTY_5_8
            audit_log.append(f"👥 年齡差距5-8歲: {C.AGE_GAP_PENALTY_5_8}分")
        
        # 現實保底分 - 只在沒有重大刑沖時激活
        if calibrated_score < C.REALITY_FLOOR and not has_day_clash and not has_day_harm:
            calibrated_score = C.REALITY_FLOOR
            audit_log.append(f"🛡️ 現實保底分激活: {calibrated_score:.1f}分")
        
        # 14. 應用置信度調整
        confidence_adjust_applied = False
        
        if not is_testpair:
            confidence1 = bazi1.get('hour_confidence', '高')
            confidence2 = bazi2.get('hour_confidence', '高')
            
            adjusted1 = bazi1.get('time_adjusted', False) or bazi1.get('day_adjusted', 0) != 0
            adjusted2 = bazi2.get('time_adjusted', False) or bazi2.get('day_adjusted', 0) != 0
            
            if adjusted1 or adjusted2:
                confidence_factor = C.get_confidence_factor(confidence1) * C.get_confidence_factor(confidence2)
                calibrated_score = calibrated_score * confidence_factor
                confidence_adjust_applied = True
                audit_log.append(f"⏱️ 置信度調整: {confidence1}×{confidence2}={confidence_factor:.3f}, 調整後: {calibrated_score:.1f}分")
            else:
                audit_log.append(f"⏱️ 無時間調整，不使用置信度折扣")
        else:
            audit_log.append(f"⏱️ testpair命令，不使用置信度調整")
        
        # 15. 最終分數範圍限制
        final_score = max(10.0, min(98.0, round(calibrated_score, 1)))
        audit_log.append(f"🎯 最終分數: {calibrated_score:.1f}→{final_score:.1f}分")
        
        # 16. 獲取評級
        rating_info = ScoringEngine.get_rating_with_description(final_score)
        rating = rating_info["name"]
        rating_description = rating_info["description"]
        
        audit_log.append(f"🏆 最終評級: {rating} ({rating_description})")
        
        # 17. 組裝結果
        result = {
            "score": final_score,
            "rating": rating,
            "a_to_b_score": score_parts["a_to_b_influence"],
            "b_to_a_score": score_parts["b_to_a_influence"],
            "relationship_model": score_parts["relationship_model"],
            "module_scores": {
                "energy_rescue": score_parts["energy_rescue"],
                "structure_core": score_parts["structure_core"],
                "personality_risk": score_parts["personality_risk"],
                "pressure_penalty": score_parts["pressure_penalty"],
                "shen_sha_bonus": score_parts["shen_sha_bonus"],
                "resolution_bonus": score_parts["resolution_bonus"],
                "dayun_risk": score_parts["dayun_risk"]
            },
            "confidence_adjust_applied": confidence_adjust_applied,
            "audit_log": audit_log,
            "details": audit_log,
            "debug_info": {
                "day_branch1": day_branch1,
                "day_branch2": day_branch2,
                "has_day_clash": has_day_clash,
                "has_day_harm": has_day_harm,
                "pillars_same": pillars_same,
                "base_score": base_score,
                "raw_bonus": raw_bonus,
                "rescue_deduction": rescue_deduction,
                "interference_factor": interference_factor
            }
        }
        
        audit_log.append("八字配對計算完成")
        
        logger.info(f"八字配對完成: 最終分數 {final_score:.1f}分, 評級: {rating}")
        
        return result
        
    except Exception as e:
        logger.error(f"配對計算錯誤: {e}", exc_info=True)
        raise ScoringEngineError(f"配對計算失敗: {str(e)}")

def calculate_bazi(year: int, month: int, day: int, hour: int, 
                  gender: str = "未知", 
                  hour_confidence: str = "高",
                  minute: Optional[int] = None,
                  longitude: float = C.DEFAULT_LONGITUDE,
                  latitude: float = C.DEFAULT_LATITUDE) -> Dict:
    """
    八字計算對外接口 - 保持向後兼容
    """
    return BaziCalculator.calculate(year, month, day, hour, gender, hour_confidence, minute, longitude, latitude)

# 保持向後兼容的別名
ProfessionalBaziCalculator = BaziCalculator
MasterBaziMatcher = ScoringEngine
BaziError = BaziCalculatorError
MatchError = ScoringEngineError
# 🔖 1.6 主入口函數結束

# 🔖 1.7 統一格式化工具類開始
class BaziFormatters:
    """八字格式化工具類 - 統一個人資料和配對結果格式"""
    
    @staticmethod
    def format_personal_data(bazi_data: Dict, username: str = "用戶") -> str:
        """統一個人資料格式化"""
        # 提取基本資料
        gender = bazi_data.get('gender', '')
        birth_year = bazi_data.get('birth_year', '')
        birth_month = bazi_data.get('birth_month', '')
        birth_day = bazi_data.get('birth_day', '')
        birth_hour = bazi_data.get('birth_hour', '')
        
        # 信心度處理
        hour_confidence = bazi_data.get('hour_confidence', '中')
        confidence_text = C.format_confidence(hour_confidence)
        
        # 八字四柱
        year_pillar = bazi_data.get('year_pillar', '')
        month_pillar = bazi_data.get('month_pillar', '')
        day_pillar = bazi_data.get('day_pillar', '')
        hour_pillar = bazi_data.get('hour_pillar', '')
        
        # 生肖
        zodiac = bazi_data.get('zodiac', '')
        
        # 日主信息
        day_stem = bazi_data.get('day_stem', '')
        day_stem_element = bazi_data.get('day_stem_element', '')
        day_stem_strength = bazi_data.get('day_stem_strength', '中')
        strength_score = bazi_data.get('strength_score', 50)
        
        # 格局類型
        pattern_type = bazi_data.get('pattern_type', '正格')
        
        # 十神結構
        shi_shen_structure = bazi_data.get('shi_shen_structure', '普通結構')
        
        # 喜用神和忌神
        useful_elements = bazi_data.get('useful_elements', [])
        harmful_elements = bazi_data.get('harmful_elements', [])
        
        # 夫妻星和夫妻宮
        spouse_star_status = bazi_data.get('spouse_star_status', '未知')
        spouse_palace_status = bazi_data.get('spouse_palace_status', '未知')
        
        # 神煞
        shen_sha_names = bazi_data.get('shen_sha_names', '無')
        
        # 五行分佈
        elements = bazi_data.get('elements', {})
        wood = elements.get('木', 0)
        fire = elements.get('火', 0)
        earth = elements.get('土', 0)
        metal = elements.get('金', 0)
        water = elements.get('水', 0)
        
        # 構建個人資料文本
        personal_text = f"📊 {username} 的八字分析\n"
        
        # 個人資料
        personal_text += f"性別：{gender}\n"
        personal_text += f"出生：{birth_year}年{birth_month}月{birth_day}日{birth_hour}時（時間信心度{confidence_text}）\n"
        personal_text += f"八字：{year_pillar} {month_pillar} {day_pillar} {hour_pillar}\n"
        personal_text += f"生肖：{zodiac}，日主：{day_stem}{day_stem_element}（{day_stem_strength}，{strength_score:.1f}分）\n"
        
        personal_text += f"格局：{pattern_type}\n"
        personal_text += f"十神結構：{shi_shen_structure}\n"
        personal_text += f"喜用神：{', '.join(useful_elements) if useful_elements else '無'}\n"
        personal_text += f"忌神：{', '.join(harmful_elements) if harmful_elements else '無'}\n"
        
        personal_text += f"夫妻星：{spouse_star_status}\n"
        personal_text += f"夫妻宮：{spouse_palace_status}\n"
        personal_text += f"神煞：{shen_sha_names}\n"
        
        personal_text += f"五行分佈：木{wood:.1f}% 火{fire:.1f}% 土{earth:.1f}% 金{metal:.1f}% 水{water:.1f}%"
        
        return personal_text
    
    @staticmethod
    def format_match_result(match_result: Dict, bazi1: Dict, bazi2: Dict, 
                          user_a_name: str = "用戶A", user_b_name: str = "用戶B") -> str:
        """統一配對結果格式化"""
        score = match_result.get('score', 0)
        rating = match_result.get('rating', '未知')
        model = match_result.get('relationship_model', '')
        
        # 模組分數
        module_scores = match_result.get('module_scores', {})
        
        # 提取八字四柱
        pillars1 = f"{bazi1.get('year_pillar', '')} {bazi1.get('month_pillar', '')} {bazi1.get('day_pillar', '')} {bazi1.get('hour_pillar', '')}"
        pillars2 = f"{bazi2.get('year_pillar', '')} {bazi2.get('month_pillar', '')} {bazi2.get('day_pillar', '')} {bazi2.get('hour_pillar', '')}"
        
        # 構建配對結果文本
        result_text = f"🎯 {user_a_name} 與 {user_b_name} 的八字配對結果\n"
        
        # 八字信息
        result_text += f"{user_a_name}八字：{pillars1}\n"
        result_text += f"{user_b_name}八字：{pillars2}\n\n"
        
        # 核心分數和評級
        result_text += f"📊 配對分數：{score:.1f}分\n"
        result_text += f"✨ 評級：{rating}\n"
        result_text += f"🎭 關係模型：{model}\n"
        
        # 模組分數
        result_text += "📈 分數構成："
        result_text += f"能量救應：{module_scores.get('energy_rescue', 0):.1f}分 "
        result_text += f"結構核心：{module_scores.get('structure_core', 0):.1f}分 "
        result_text += f"人格風險：{module_scores.get('personality_risk', 0):.1f}分 "
        result_text += f"刑沖壓力：{module_scores.get('pressure_penalty', 0):.1f}分 "
        result_text += f"神煞加持：{module_scores.get('shen_sha_bonus', 0):.1f}分 "
        result_text += f"專業化解：{module_scores.get('resolution_bonus', 0):.1f}分 "
        result_text += f"大運風險：{module_scores.get('dayun_risk', 0):.1f}分\n"
        
        # 雙向影響
        a_to_b = match_result.get('a_to_b_score', 0)
        b_to_a = match_result.get('b_to_a_score', 0)
        result_text += f"🤝 雙向影響："
        result_text += f"{user_a_name} 對 {user_b_name}：{a_to_b:.1f}分 "
        result_text += f"{user_b_name} 對 {user_a_name}：{b_to_a:.1f}分\n"
        
        # 關鍵發現
        result_text += f"🔍 關鍵發現："
        
        # 優勢
        if score >= C.THRESHOLD_EXCELLENT_MATCH:
            result_text += "✅ 優勢：五行能量高度互補、結構穩定無硬傷、有明顯的救應機制 "
        elif score >= C.THRESHOLD_GOOD_MATCH:
            result_text += "✅ 優勢：核心需求能夠對接、主要結構無大沖、有化解機制 "
        elif score >= C.THRESHOLD_ACCEPTABLE:
            result_text += "✅ 優勢：基本能量可以互補、需要努力經營關係 "
        else:
            result_text += "✅ 優勢：優勢不明顯，需謹慎考慮 "
        
        # 挑戰
        challenges = []
        if module_scores.get('personality_risk', 0) < -10:
            challenges.append("人格風險較高，可能性格衝突")
        if module_scores.get('pressure_penalty', 0) < -15:
            challenges.append("刑沖壓力較大，容易產生矛盾")
        if module_scores.get('dayun_risk', 0) < -10:
            challenges.append("未來大運有挑戰，需要提前準備")
        
        if challenges:
            result_text += "⚠️ 挑戰：" + " ".join(challenges)
        else:
            result_text += "⚠️ 挑戰：無明顯重大挑戰"
        
        return result_text
    
    @staticmethod
    def format_test_pair_result(match_result: Dict, bazi1: Dict, bazi2: Dict) -> str:
        """八字測試結果格式化 - 使用統一格式"""
        # 直接使用format_match_result格式
        return BaziFormatters.format_match_result(match_result, bazi1, bazi2, "測試用戶A", "測試用戶B")
# 🔖 1.7 統一格式化工具類結束

# ========文件信息開始 ========#
"""
文件: new_calculator.py
功能: 八字配對系統核心引擎

引用文件: 
- sxtwl (農曆計算庫)
- 無其他自定義模組

被引用文件:
- bot.py (主程序)
- admin_service.py (管理員服務)
- bazi_soulmate.py (真命天子搜索)

主要修改：
1. 重新設計評分系統配置，解決分數通脹問題
2. 增加干涉係數機制，刑沖嚴重時打折正向加分
3. 刪除神煞保底分，避免低分區分數扭曲
4. 大幅提高能量救應和結構核心分數
5. 加重刑沖懲罰，特別是日支沖剋
6. 統一四方功能格式化輸出

修改記錄：
2026-02-02 深度重構版：
1. 降低基準分：從60降至55，留出分數空間
2. 刪除神煞保底分：SHEN_SHA_FLOOR從7改為0，解決低分區分數扭曲問題
3. 提高能量救應：DEMAND_MATCH_BONUS_BASE從6提升到18，讓喜用神互補真正有效
4. 加重刑沖懲罰：DAY_CLASH_PENALTY從-12提升到-25，反映日支沖的嚴重性
5. 增加干涉係數機制：日支沖時所有正向加分打4折，普通刑沖重打7折
6. 提高正向加分上限：POSITIVE_BONUS_CAP從30提升到45
7. 提高評級閾值：重新調整各級別分數標準
8. 增強能量救應計算：使用濃度/30的新公式，讓分數更合理
9. 統一格式化輸出：讓四方功能輸出格式一致

累積修正：
- 解決分數通脹問題，讓刑沖組合能真正顯現低分
- 增強喜用神互補的分數，讓優質組合能跑出高分
- 統一所有功能的計算和輸出邏輯
- 保持向後兼容，所有現有接口不變
- 符合繁體中文要求
- 無版本號標示
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
目錄:
1.1 錯誤處理類 - 自定義異常類
1.2 配置常量類 - 系統配置和參數
1.3 時間處理引擎 - 真太陽時計算
1.4 八字核心引擎 - 八字計算和分析
1.5 評分引擎 - 命理評分算法
1.6 主入口函數 - 八字配對主要邏輯
1.7 統一格式化工具類 - 結果格式化輸出
"""
# ========目錄結束 ========#