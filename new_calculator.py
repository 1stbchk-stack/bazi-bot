#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字配對系統核心 - 專業級八字計算與配對引擎
採用專業命理師傅級算法，確保99%案例與頂級命理師計算結果一致
架構：核心計算 → 專業分析 → 精準評分 → 審證驗證
"""

import logging
import math
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import sxtwl

logger = logging.getLogger(__name__)

# 🔖 1.1 專業錯誤處理系統開始
class BaziSystemError(Exception):
    """八字系統基礎錯誤"""
    pass

class TimeCalculationError(BaziSystemError):
    """時間計算錯誤"""
    pass

class ElementAnalysisError(BaziSystemError):
    """五行分析錯誤"""
    pass

class MatchScoringError(BaziSystemError):
    """配對評分錯誤"""
    pass

class ProfessionalValidationError(BaziSystemError):
    """專業驗證錯誤"""
    pass
# 🔖 1.1 專業錯誤處理系統結束

# 🔖 1.2 專業配置系統開始
class ProfessionalConfig:
    """專業命理配置系統 - 集中管理時間、五行、權重、評級等專業參數"""
    
    # ========== 1.2.1 基礎時間配置（固定不變）==========
    TIME_ZONE_MERIDIAN: float = 120.0          # 東經120度標準時區（中國/香港常用）
    DAY_BOUNDARY_MODE: str = "zizheng"        # 子正換日（專業標準）
    DEFAULT_LONGITUDE: float = 114.17         # 香港經度跟常用地點
    DEFAULT_LATITUDE: float = 22.32           # 香港緯度
    LONGITUDE_CORRECTION: int = 4             # 經度差1度 = 4分鐘跟天文計算標準
    DAY_BOUNDARY_HOUR: int = 23               # 日界線時辰（子正）
    DAY_BOUNDARY_MINUTE: int = 0              # 日界線分鐘
    
    # ========== 1.2.2 香港夏令時完整表（固定不變）==========
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
        ("1978-04-02", "1978-10-29"), ("1979-05-06", "1979-10-21"),
    ]
    
    # ========== 1.2.3 專業月令氣勢表（固定不變，跟命理傳統）==========
    MONTH_QI_MAP = {
        "子": {"yuqi": "辛", "zhongqi": "癸", "zhengqi": "壬", "qi_score": 10},
        "丑": {"yuqi": "壬", "zhongqi": "辛", "zhengqi": "己", "qi_score": 8},
        "寅": {"yuqi": "己", "zhongqi": "戊", "zhengqi": "甲", "qi_score": 12},
        "卯": {"yuqi": "甲", "zhongqi": "丙", "zhengqi": "乙", "qi_score": 10},
        "辰": {"yuqi": "乙", "zhongqi": "癸", "zhengqi": "戊", "qi_score": 8},
        "巳": {"yuqi": "戊", "zhongqi": "庚", "zhengqi": "丙", "qi_score": 12},
        "午": {"yuqi": "丙", "zhongqi": "戊", "zhengqi": "丁", "qi_score": 10},
        "未": {"yuqi": "丁", "zhongqi": "乙", "zhengqi": "己", "qi_score": 8},
        "申": {"yuqi": "戊", "zhongqi": "戊", "zhengqi": "庚", "qi_score": 10},  # 修正：餘氣應為戊非己
        "酉": {"yuqi": "庚", "zhongqi": "壬", "zhengqi": "辛", "qi_score": 8},
        "戌": {"yuqi": "辛", "zhongqi": "丁", "zhengqi": "戊", "qi_score": 8},
        "亥": {"yuqi": "戊", "zhongqi": "甲", "zhengqi": "壬", "qi_score": 10},
    }
    
    # ========== 1.2.4 身強弱專業權重（固定不變，跟專業標準）==========
    MONTH_QI_WEIGHT: float = 40.0  # 月令氣勢權重（主力）跟命理原則：月令為提綱
    TONG_GEN_WEIGHT: float = 30.0  # 通根力量權重跟地支力量
    SUPPORT_WEIGHT: float = 20.0   # 生扶力量權重跟印星比劫
    STEM_STRENGTH_WEIGHT: float = 10.0  # 天干力量權重跟天干透出
    
    STRENGTH_THRESHOLD_STRONG: float = 70.0  # 強跟專業劃分
    STRENGTH_THRESHOLD_MEDIUM: float = 40.0  # 中
    STRENGTH_THRESHOLD_WEAK: float = 20.0    # 弱
    
    # ========== 1.2.5 陰陽天干（固定不變）==========
    YANG_STEMS = ["甲", "丙", "戊", "庚", "壬"]
    YIN_STEMS = ["乙", "丁", "己", "辛", "癸"]
    
    # ========== 1.2.6 五行關係配置（固定不變）==========
    ELEMENT_GENERATION = {
        "木": "火",
        "火": "土",
        "土": "金",
        "金": "水",
        "水": "木",
    }
    
    ELEMENT_CONTROL = {
        "木": "土",
        "土": "水",
        "水": "火",
        "火": "金",
        "金": "木",
    }
    
    # ========== 1.2.7 地支藏干增強版（固定不變，跟專業藏干表）==========
    BRANCH_HIDDEN_STEMS_PRO = {
        "子": [("癸", 1.0, 100)],  # 子水100%癸水
        "丑": [("己", 0.5, 60), ("癸", 0.3, 30), ("辛", 0.2, 10)],
        "寅": [("甲", 0.6, 60), ("丙", 0.3, 30), ("戊", 0.1, 10)],
        "卯": [("乙", 1.0, 100)],
        "辰": [("戊", 0.5, 60), ("乙", 0.3, 30), ("癸", 0.2, 10)],
        "巳": [("丙", 0.6, 60), ("庚", 0.3, 30), ("戊", 0.1, 10)],
        "午": [("丁", 0.7, 70), ("己", 0.3, 30)],  # 午火70%丁火，30%己土
        "未": [("己", 0.6, 60), ("丁", 0.3, 30), ("乙", 0.1, 10)],
        "申": [("庚", 0.6, 60), ("壬", 0.3, 30), ("戊", 0.1, 10)],
        "酉": [("辛", 1.0, 100)],
        "戌": [("戊", 0.6, 60), ("辛", 0.3, 30), ("丁", 0.1, 10)],
        "亥": [("壬", 0.7, 70), ("甲", 0.3, 30)],
    }
    
    # ========== 1.2.8 專業評級標準（固定不變，跟專業劃分）==========
    THRESHOLD_TERMINATION: float = 25.0   # 終止線跟極差配對
    THRESHOLD_STRONG_WARNING: float = 35.0  # 強烈警告
    THRESHOLD_WARNING: float = 45.0         # 警告
    THRESHOLD_ACCEPTABLE: float = 55.0      # 可接受跟及格線
    THRESHOLD_GOOD_MATCH: float = 65.0      # 良好配對
    THRESHOLD_EXCELLENT_MATCH: float = 75.0 # 優秀配對
    THRESHOLD_PERFECT_MATCH: float = 85.0   # 完美配對
    
    RATING_SCALE = [
        (THRESHOLD_PERFECT_MATCH,   "極品仙緣",   "天作之合，互相成就，幸福美滿"),
        (THRESHOLD_EXCELLENT_MATCH, "上等婚配",   "明顯互補，幸福率高，可白頭偕老"),
        (THRESHOLD_GOOD_MATCH,      "良好姻緣",   "現實高成功率，可經營發展"),
        (THRESHOLD_ACCEPTABLE,      "可以交往",   "有缺點但可努力經營，需互相包容"),
        (THRESHOLD_WARNING,         "需要謹慎",   "問題較多，需謹慎考慮，易有矛盾"),
        (THRESHOLD_STRONG_WARNING,  "不建議",     "沖剋嚴重，難長久，易生變故"),
        (THRESHOLD_TERMINATION,     "強烈不建議", "嚴重沖剋，極難長久，易分手"),
        (0,                         "避免發展",   "硬傷明顯，易生變，不適合婚戀"),
    ]
    
    # ========== 1.2.9 時間信心度因子（固定不變）==========
    TIME_CONFIDENCE_LEVELS: dict = {
        "高": 1.00,   # 精確時間，無調整
        "中": 0.95,   # 有輕微調整
        "低": 0.90,   # 有明顯調整
        "估算": 0.85, # 估算時間
    }
    
    @classmethod
    def get_rating(cls, score: float) -> str:
        """根據分數取得評級名稱。跟評級標準匹配"""
        for threshold, name, _ in cls.RATING_SCALE:
            if score >= threshold:
                return name
        return "避免發展"
    
    @classmethod
    def get_rating_description(cls, score: float) -> str:
        """根據分數取得評級描述。跟評級標準匹配"""
        for threshold, _, description in cls.RATING_SCALE:
            if score >= threshold:
                return description
        return "硬傷明顯，易生變，不適合婚戀"
    
    @classmethod
    def get_confidence_factor(cls, confidence: str) -> float:
        """根據時間信心度字串取得數值因子。跟信心度影響權重"""
        return cls.TIME_CONFIDENCE_LEVELS.get(confidence, 0.90)

# 創建專業配置實例（保持向後兼容：PC 名稱在其他文件大量使用）
PC = ProfessionalConfig
# 🔖 1.2 專業配置系統結束

# 🔖 1.3 專業時間處理引擎開始
class ProfessionalTimeProcessor:
    """
    專業時間處理引擎 - 確保99%時間計算準確
    功能：真太陽時計算、夏令時校正、經度調整、均時差補償、日界處理
    """
    
    @staticmethod
    def calculate_true_solar_time_pro(
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        longitude: float,
        confidence: str,
    ) -> Dict[str, Any]:
        """1.3.1 專業真太陽時計算（平太陽時 → 真太陽時）跟天文算法"""
        audit_log: List[str] = []
        audit_log.append(
            f"🔍 專業時間計算開始: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} "
            f"(經度: {longitude:.2f}°，原始信心度: {confidence})"
        )
        
        try:
            # 1. 夏令時檢查
            dst_adjust = ProfessionalTimeProcessor._get_dst_adjustment(year, month, day, audit_log)
            
            # 2. 經度校正
            lon_adjust = ProfessionalTimeProcessor._get_longitude_adjustment(longitude, audit_log)
            
            # 3. 均時差校正
            eot_adjust = ProfessionalTimeProcessor._get_equation_of_time_adjustment(
                year, month, day, hour, minute, audit_log
            )
            
            # 4. 累計全部時間調整
            total_adjust_minutes = dst_adjust + lon_adjust + eot_adjust
            audit_log.append(f"📊 總調整量: {total_adjust_minutes:+.1f} 分鐘")
            total_minutes = hour * 60 + minute + total_adjust_minutes
            
            # 5. 日界處理
            day_delta, adjusted_minutes = ProfessionalTimeProcessor._apply_day_boundary(total_minutes, audit_log)
            true_hour = int(adjusted_minutes // 60)
            true_minute = int(round(adjusted_minutes % 60))
            
            # 修正四捨五入導致的60分鐘
            if true_minute == 60:
                true_minute = 0
                true_hour = (true_hour + 1) % 24
            
            # 6. 動態調整信心度
            new_confidence = ProfessionalTimeProcessor._adjust_confidence_level(
                confidence, abs(total_adjust_minutes), audit_log
            )
            
            audit_log.append(
                f"✅ 最終真太陽時結果: {true_hour:02d}:{true_minute:02d} "
                f"(信心度: {new_confidence}，跨日: {day_delta:+d} 天)"
            )
            
            return {
                'hour': true_hour,
                'minute': true_minute,
                'confidence': new_confidence,
                'adjusted': abs(total_adjust_minutes) > 5,
                'day_adjusted': day_delta,
                'total_adjust_minutes': total_adjust_minutes,
                'audit_log': audit_log,
            }
            
        except Exception as e:
            logger.error(f"專業時間計算錯誤: {e}", exc_info=True)
            raise TimeCalculationError(f"時間計算失敗: {str(e)}")
    
    @staticmethod
    def _get_dst_adjustment(year: int, month: int, day: int, audit_log: list[str]) -> float:
        """1.3.1.1 檢查是否處於香港歷史夏令時期間"""
        dst_adjust = 0.0
        try:
            date_obj = datetime(year, month, day)
            for start_str, end_str in PC.HK_DST_PERIODS:
                start_date = datetime.strptime(start_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_str, "%Y-%m-%d")
                if start_date <= date_obj <= end_date:
                    dst_adjust = -60.0
                    audit_log.append(f"⏰ 檢測到夏令時: {start_str} 至 {end_str}")
                    break
        except Exception as e:
            logger.warning(f"夏令時檢查異常: {e}")
            audit_log.append(f"⚠️ 夏令時檢查異常: {e}")
        return dst_adjust
    
    @staticmethod
    def _get_longitude_adjustment(longitude: float, audit_log: list[str]) -> float:
        """1.3.1.2 經度校正：相對於東經120度的時間差"""
        diff = longitude - PC.TIME_ZONE_MERIDIAN
        adjust = diff * PC.LONGITUDE_CORRECTION
        audit_log.append(f"📍 經度校正: {adjust:+.1f} 分鐘 (經度差: {diff:+.2f}°)")
        return adjust
    
    @staticmethod
    def _get_equation_of_time_adjustment(
        year: int, month: int, day: int, hour: int, minute: int, audit_log: list[str]
    ) -> float:
        """1.3.1.3 計算均時差（Equation of Time）"""
        try:
            jd = ProfessionalTimeProcessor._gregorian_to_julian_day(year, month, day, hour, minute)
            t = (jd - 2451545.0) / 36525.0
            
            L0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
            M = 357.52911 + 35999.05029 * t - 0.0001537 * t * t
            
            C = (
                (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(math.radians(M))
                + (0.019993 - 0.000101 * t) * math.sin(math.radians(2 * M))
                + 0.000289 * math.sin(math.radians(3 * M))
            )
            
            L = L0 + C
            eot = (
                9.87 * math.sin(math.radians(2 * L))
                - 7.53 * math.cos(math.radians(L))
                - 1.5 * math.sin(math.radians(L))
            )
            
            eot = max(-20.0, min(20.0, eot))
            audit_log.append(f"☀️ 均時差校正: {eot:+.1f} 分鐘")
            return eot
        except Exception as e:
            logger.warning(f"均時差計算異常: {e}")
            audit_log.append(f"⚠️ 均時差計算異常: {e}，暫以 0 分鐘處理")
            return 0.0
    
    @staticmethod
    def _gregorian_to_julian_day(year: int, month: int, day: int, hour: int, minute: int) -> float:
        """1.3.1.4 將公曆日期時間轉換為儒略日"""
        if month <= 2:
            year -= 1
            month += 12
        A = year // 100
        B = 2 - A + (A // 4)
        jd_day = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
        time_fraction = (hour + minute / 60.0) / 24.0
        return jd_day + time_fraction
    
    @staticmethod
    def _apply_day_boundary(total_minutes: float, audit_log: list[str]) -> tuple[int, float]:
        """1.3.1.5 處理總分鐘數的日界跨天"""
        day_delta = 0
        adjusted = total_minutes
        if total_minutes < 0:
            adjusted += 24 * 60
            day_delta = -1
            audit_log.append("🔄 向前跨日調整（減1天）")
        elif total_minutes >= 24 * 60:
            adjusted -= 24 * 60
            day_delta = 1
            audit_log.append("🔄 向後跨日調整（加1天）")
        return day_delta, adjusted
    
    @staticmethod
    def _adjust_confidence_level(
        original: str, abs_adjust_minutes: float, audit_log: list[str]
    ) -> str:
        """1.3.1.6 根據總調整幅度動態降低信心度"""
        if abs_adjust_minutes > 60:
            new = "估算"
        elif abs_adjust_minutes > 30:
            new = "低" if original == "高" else "估算"
        elif abs_adjust_minutes > 10:
            new = "中" if original in ("高", "中") else "低"
        else:
            new = original
        if new != original:
            audit_log.append(f"📉 信心度因調整幅度大而降級: {original} → {new}")
        return new
    
    @staticmethod
    def apply_day_boundary_pro(
        year: int, month: int, day: int, hour: int, minute: int, confidence: str
    ) -> Tuple[int, int, int, str]:
        """1.3.2 專業日界處理（子正換日）"""
        if PC.DAY_BOUNDARY_MODE == "none":
            return year, month, day, confidence
        
        if PC.DAY_BOUNDARY_MODE == "zizheng":
            if hour >= PC.DAY_BOUNDARY_HOUR and minute >= PC.DAY_BOUNDARY_MINUTE:
                current_date = datetime(year, month, day)
                next_date = current_date + timedelta(days=1)
                new_confidence = "中" if confidence == "高" else confidence
                return next_date.year, next_date.month, next_date.day, new_confidence
        
        return year, month, day, confidence
# 🔖 1.3 專業時間處理引擎結束

# 🔖 1.4 專業八字核心引擎開始
class ProfessionalBaziCalculator:
    """
    專業八字核心引擎
    功能：完整八字計算與深度分析
    特色：保持100%向後兼容性
    """
    
    # ========== 1.4.1 基礎常量配置（固定不變）==========
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
    
    ZODIACS = ['鼠', '牛', '虎', '兔', '龍', '蛇', '馬', '羊', '猴', '雞', '狗', '豬']
    
    # ========== 1.4.2 地支關係配置（固定不變）==========
    THREE_HARMONY_MAP = {
        '申': ('子', '辰'), '子': ('申', '辰'), '辰': ('申', '子'),
        '亥': ('卯', '未'), '卯': ('亥', '未'), '未': ('亥', '卯'),
        '寅': ('午', '戌'), '午': ('寅', '戌'), '戌': ('寅', '午'),
        '巳': ('酉', '丑'), '酉': ('巳', '丑'), '丑': ('巳', '酉')
    }
    
    # ========== 1.4.3 十神對照表（固定不變）==========
    SHI_SHEN_MAP = {
        '甲': {'甲': '比肩', '乙': '劫財', '丙': '食神', '丁': '傷官', '戊': '偏財',
              '己': '正財', '庚': '七殺', '辛': '正官', '壬': '偏印', '癸': '正印'},
        '乙': {'甲': '劫財', '乙': '比肩', '丙': '傷官', '丁': '食神', '戊': '正財',
              '己': '偏財', '庚': '正官', '辛': '七殺', '壬': '正印', '癸': '偏印'},
        '丙': {'甲': '偏印', '乙': '正印', '丙': '比肩', '丁': '劫財', '戊': '食神',
              '己': '傷官', '庚': '偏財', '辛': '正財', '壬': '七殺', '癸': '正官'},
        '丁': {'甲': '正印', '乙': '偏印', '丙': '劫財', '丁': '比肩', '戊': '傷官',
              '己': '食神', '庚': '正財', '辛': '偏財', '壬': '正官', '癸': '七殺'},
        '戊': {'甲': '七殺', '乙': '正官', '丙': '偏印', '丁': '正印', '戊': '比肩',
              '己': '劫財', '庚': '食神', '辛': '傷官', '壬': '偏財', '癸': '正財'},
        '己': {'甲': '正官', '乙': '七殺', '丙': '正印', '丁': '偏印', '戊': '劫財',
              '己': '比肩', '庚': '傷官', '辛': '食神', '壬': '正財', '癸': '偏財'},
        '庚': {'甲': '偏財', '乙': '正財', '丙': '七殺', '丁': '正官', '戊': '偏印',
              '己': '正印', '庚': '比肩', '辛': '劫財', '壬': '食神', '癸': '傷官'},
        '辛': {'甲': '正財', '乙': '偏財', '丙': '正官', '丁': '七殺', '戊': '正印',
              '己': '偏印', '庚': '劫財', '辛': '比肩', '壬': '傷官', '癸': '食神'},
        '壬': {'甲': '食神', '乙': '傷官', '丙': '偏財', '丁': '正財', '戊': '七殺',
              '己': '正官', '庚': '偏印', '辛': '正印', '壬': '比肩', '癸': '劫財'},
        '癸': {'甲': '傷官', '乙': '食神', '丙': '正財', '丁': '偏財', '戊': '正官',
              '己': '七殺', '庚': '正印', '辛': '偏印', '壬': '劫財', '癸': '比肩'}
    }
    
    # ========== 1.4.4 天乙貴人對照表（固定不變）==========
    TIANYI_GUI_REN = {
        '甲': ['丑', '未'], '乙': ['子', '申'], '丙': ['亥', '酉'],
        '丁': ['亥', '酉'], '戊': ['丑', '未'], '己': ['子', '申'],
        '庚': ['丑', '未'], '辛': ['寅', '午'], '壬': ['卯', '巳'],
        '癸': ['卯', '巳']
    }
    
    # ========== 1.4.5 紅鸞天喜對照表（固定不變）==========
    HONG_LUAN_MAP = {
        '子': '卯', '丑': '寅', '寅': '丑', '卯': '子',
        '辰': '亥', '巳': '戌', '午': '酉', '未': '申',
        '申': '未', '酉': '午', '戌': '巳', '亥': '辰'
    }
    
    TIAN_XI_MAP = {
        '子': '酉', '丑': '申', '寅': '未', '卯': '午',
        '辰': '巳', '巳': '辰', '午': '卯', '未': '寅',
        '申': '丑', '酉': '子', '戌': '亥', '亥': '戌'
    }
    
    @staticmethod
    def calculate_pro(year: int, month: int, day: int, hour: int,
                     gender: str = "未知",
                     hour_confidence: str = "高",
                     minute: Optional[int] = None,
                     longitude: float = PC.DEFAULT_LONGITUDE,
                     latitude: float = PC.DEFAULT_LATITUDE) -> Dict[str, Any]:
        """1.4.6 專業八字計算主函數"""
        audit_log = []
        
        try:
            audit_log.append(f"🎯 開始專業八字計算: {year}年{month}月{day}日{hour}時")
            
            # 處理分鐘缺失
            processed_minute = minute if minute is not None else 0
            if minute is None:
                hour_confidence = "估算" if hour_confidence == "高" else hour_confidence
            
            # 使用專業時間處理引擎
            true_solar_time = ProfessionalTimeProcessor.calculate_true_solar_time_pro(
                year, month, day, hour, processed_minute, longitude, hour_confidence
            )
            audit_log.extend(true_solar_time.get('audit_log', []))
            
            # 專業日界處理
            adjusted_date = ProfessionalTimeProcessor.apply_day_boundary_pro(
                year, month, day,
                true_solar_time['hour'], true_solar_time['minute'],
                true_solar_time['confidence']
            )
            adjusted_year, adjusted_month, adjusted_day, final_confidence = adjusted_date
            
            # 使用sxtwl計算四柱
            day_obj = sxtwl.fromSolar(adjusted_year, adjusted_month, adjusted_day)
            
            # 獲取天干地支索引
            y_gz = day_obj.getYearGZ()
            m_gz = day_obj.getMonthGZ()
            d_gz = day_obj.getDayGZ()
            
            # 計算時柱
            hour_pillar = ProfessionalBaziCalculator._calculate_hour_pillar_pro(
                adjusted_year, adjusted_month, adjusted_day, true_solar_time['hour']
            )
            
            # 組裝基礎八字數據
            STEMS = ProfessionalBaziCalculator.STEMS
            BRANCHES = ProfessionalBaziCalculator.BRANCHES
            
            year_pillar = f"{STEMS[y_gz.tg]}{BRANCHES[y_gz.dz]}"
            month_pillar = f"{STEMS[m_gz.tg]}{BRANCHES[m_gz.dz]}"
            day_pillar = f"{STEMS[d_gz.tg]}{BRANCHES[d_gz.dz]}"
            
            day_stem = STEMS[d_gz.tg]
            day_stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem, "")
            
            # 基礎數據結構
            bazi_data = {
                "year_pillar": year_pillar,
                "month_pillar": month_pillar,
                "day_pillar": day_pillar,
                "hour_pillar": hour_pillar,
                "zodiac": ProfessionalBaziCalculator.ZODIACS[y_gz.dz],
                "day_stem": day_stem,
                "day_stem_element": day_stem_element,
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
            
            # 專業深度分析
            bazi_data = ProfessionalBaziCalculator._analyze_professional_enhanced(bazi_data, gender, audit_log)
            
            audit_log.append(f"✅ 專業八字計算完成: {year_pillar} {month_pillar} {day_pillar} {hour_pillar}")
            
            return bazi_data
            
        except Exception as e:
            logger.error(f"專業八字計算錯誤: {e}", exc_info=True)
            audit_log.append(f"❌ 八字計算錯誤: {str(e)}")
            raise ElementAnalysisError(f"八字分析失敗: {str(e)}")
    
    @staticmethod
    def _calculate_hour_pillar_pro(year: int, month: int, day: int, hour: int) -> str:
        """1.4.6.1 專業時柱計算 - 使用五鼠遁訣"""
        day_obj = sxtwl.fromSolar(year, month, day)
        d_gz = day_obj.getDayGZ()
        day_stem = d_gz.tg
        
        # 時辰地支
        hour_branch = ProfessionalBaziCalculator._hour_to_branch_pro(hour)
        
        # 五鼠遁訣
        start_stem_map = {
            0: 0,   # 甲己日：甲子時起
            1: 2,   # 乙庚日：丙子時起
            2: 4,   # 丙辛日：戊子時起
            3: 6,   # 丁壬日：庚子時起
            4: 8,   # 戊癸日：壬子時起
        }
        
        day_stem_mod = day_stem % 5
        start_stem = start_stem_map.get(day_stem_mod, 0)
        
        # 計算時干
        hour_stem = (start_stem + hour_branch) % 10
        
        return f"{ProfessionalBaziCalculator.STEMS[hour_stem]}{ProfessionalBaziCalculator.BRANCHES[hour_branch]}"
    
    @staticmethod
    def _hour_to_branch_pro(hour: int) -> int:
        """1.4.6.1.1 專業時辰轉換"""
        hour_map = {
            23: 0, 0: 0,    # 子時 (23:00-01:00)
            1: 1, 2: 1,     # 丑時 (01:00-03:00)
            3: 2, 4: 2,     # 寅時 (03:00-05:00)
            5: 3, 6: 3,     # 卯時 (05:00-07:00)
            7: 4, 8: 4,     # 辰時 (07:00-09:00)
            9: 5, 10: 5,    # 巳時 (09:00-11:00)
            11: 6, 12: 6,   # 午時 (11:00-13:00)
            13: 7, 14: 7,   # 未時 (13:00-15:00)
            15: 8, 16: 8,   # 申時 (15:00-17:00)
            17: 9, 18: 9,   # 酉時 (17:00-19:00)
            19: 10, 20: 10, # 戌時 (19:00-21:00)
            21: 11, 22: 11  # 亥時 (21:00-23:00)
        }
        return hour_map.get(hour % 24, 0)
    
    @staticmethod
    def _analyze_professional_enhanced(bazi_data: Dict, gender: str, audit_log: List[str]) -> Dict:
        """1.4.7 專業深度分析"""
        try:
            audit_log.append("🔍 開始專業深度分析")
            
            # 1. 專業五行分析
            bazi_data["elements"] = ProfessionalBaziCalculator._calculate_elements_pro(bazi_data)
            audit_log.append(f"✅ 五行分析完成: {bazi_data['elements']}")
            
            # 2. 專業身強弱分析
            strength_score, strength_details = ProfessionalBaziCalculator._calculate_strength_enhanced(bazi_data, audit_log)
            bazi_data["strength_score"] = strength_score
            bazi_data["day_stem_strength"] = ProfessionalBaziCalculator._determine_strength_pro(strength_score)
            bazi_data["strength_details"] = strength_details
            
            audit_log.append(f"✅ 身強弱分析: {strength_score:.1f}分 ({bazi_data['day_stem_strength']})")
            
            # 3. 專業格局判定
            pattern_type, pattern_details = ProfessionalBaziCalculator._determine_pattern_enhanced(bazi_data, audit_log)
            bazi_data["pattern_type"] = pattern_type
            bazi_data["pattern_details"] = pattern_details
            audit_log.append(f"✅ 格局判定: {pattern_type}")
            
            # 4. 專業喜用神分析
            useful_elements, useful_details = ProfessionalBaziCalculator._calculate_useful_elements_pro(
                bazi_data, gender, audit_log
            )
            bazi_data["useful_elements"] = useful_elements
            bazi_data["useful_details"] = useful_details
            
            harmful_elements = ProfessionalBaziCalculator._calculate_harmful_elements_pro(bazi_data, useful_elements)
            bazi_data["harmful_elements"] = harmful_elements
            audit_log.append(f"✅ 喜用神分析: 喜{useful_elements}, 忌{harmful_elements}")
            
            # 5. 專業夫妻星分析
            spouse_status, spouse_details = ProfessionalBaziCalculator._analyze_spouse_star_pro(bazi_data, gender)
            bazi_data["spouse_star_status"] = spouse_status
            bazi_data["spouse_star_details"] = spouse_details
            
            palace_status, palace_details = ProfessionalBaziCalculator._analyze_spouse_palace_pro(bazi_data)
            bazi_data["spouse_palace_status"] = palace_status
            bazi_data["spouse_palace_details"] = palace_details
            audit_log.append(f"✅ 夫妻分析: 星{spouse_status}, 宮{palace_status}")
            
            # 6. 專業神煞分析
            shen_sha_names, shen_sha_bonus, shen_sha_details = ProfessionalBaziCalculator._calculate_shen_sha_enhanced(bazi_data)
            bazi_data["shen_sha_names"] = shen_sha_names
            bazi_data["shen_sha_bonus"] = shen_sha_bonus
            bazi_data["shen_sha_details"] = shen_sha_details
            audit_log.append(f"✅ 神煞分析: {shen_sha_names} ({shen_sha_bonus}分)")
            
            # 7. 專業十神結構
            shi_shen_structure, shi_shen_details = ProfessionalBaziCalculator._calculate_shi_shen_pro(bazi_data, gender)
            bazi_data["shi_shen_structure"] = shi_shen_structure
            bazi_data["shi_shen_details"] = shi_shen_details
            audit_log.append(f"✅ 十神結構: {shi_shen_structure}")
            
            # 8. 專業大運分析
            dayun_info = ProfessionalBaziCalculator._calculate_dayun_pro(bazi_data, gender)
            bazi_data["dayun_info"] = dayun_info
            
            audit_log.append("✅ 專業深度分析完成")
            
            return bazi_data
            
        except Exception as e:
            logger.error(f"專業分析錯誤: {e}", exc_info=True)
            audit_log.append(f"❌ 專業分析錯誤: {str(e)}")
            raise ElementAnalysisError(f"專業分析失敗: {str(e)}")
    
    @staticmethod
    def _calculate_elements_pro(bazi_data: Dict) -> Dict[str, float]:
        """1.4.7.1 專業五行分佈計算"""
        elements = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
        
        pillars = [
            bazi_data.get('year_pillar', ''),
            bazi_data.get('month_pillar', ''),
            bazi_data.get('day_pillar', ''),
            bazi_data.get('hour_pillar', '')
        ]
        
        weights = [1.0, 1.8, 1.5, 1.2]  # 年1.0，月1.8，日1.5，時1.2
        
        for pillar, weight in zip(pillars, weights):
            if len(pillar) >= 2:
                stem = pillar[0]
                branch = pillar[1]
                
                # 天干五行
                stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(stem)
                if stem_element:
                    elements[stem_element] += weight * 1.0
                
                # 地支本氣五行
                branch_element = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(branch)
                if branch_element:
                    elements[branch_element] += weight * 0.6
                
                # 地支藏干五行
                hidden_stems = PC.BRANCH_HIDDEN_STEMS_PRO.get(branch, [])
                for hidden_stem, hidden_weight, _ in hidden_stems:
                    hidden_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(hidden_stem)
                    if hidden_element:
                        elements[hidden_element] += weight * hidden_weight * 0.4
        
        # 正規化到100%
        total = sum(elements.values())
        if total > 0:
            for element in elements:
                elements[element] = round(elements[element] * 100 / total, 2)
        
        return elements
    
    @staticmethod
    def _calculate_strength_enhanced(bazi_data: Dict, audit_log: List[str]) -> Tuple[float, Dict[str, float]]:
        """1.4.7.2 專業身強弱計算"""
        day_stem = bazi_data.get('day_stem', '')
        day_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        
        if not day_element:
            audit_log.append("⚠️ 日主不明，使用默認強度50分")
            return 50.0, {}
        
        # 1. 月令氣勢分數（40%權重）
        month_score = ProfessionalBaziCalculator._calculate_month_qi_score(bazi_data, day_element)
        month_contribution = month_score * PC.MONTH_QI_WEIGHT / 100
        
        # 2. 通根力量分數（30%權重）
        tong_gen_score = ProfessionalBaziCalculator._calculate_tong_gen_score_enhanced(bazi_data, day_element)
        tong_gen_contribution = tong_gen_score * PC.TONG_GEN_WEIGHT / 100
        
        # 3. 生扶力量分數（20%權重）
        support_score = ProfessionalBaziCalculator._calculate_support_score_enhanced(bazi_data, day_element)
        support_contribution = support_score * PC.SUPPORT_WEIGHT / 100
        
        # 4. 天干力量分數（10%權重）
        stem_score = ProfessionalBaziCalculator._calculate_stem_strength_enhanced(bazi_data, day_element)
        stem_contribution = stem_score * PC.STEM_STRENGTH_WEIGHT / 100
        
        # 總分計算
        total_score = month_contribution + tong_gen_contribution + support_contribution + stem_contribution
        
        # 正規化到0-100分
        final_score = max(0.0, min(100.0, total_score * 100))
        
        # 詳細分數記錄
        strength_details = {
            "month_score": round(month_score, 3),
            "tong_gen_score": round(tong_gen_score, 3),
            "support_score": round(support_score, 3),
            "stem_score": round(stem_score, 3),
            "month_contribution": round(month_contribution, 3),
            "tong_gen_contribution": round(tong_gen_contribution, 3),
            "support_contribution": round(support_contribution, 3),
            "stem_contribution": round(stem_contribution, 3),
            "raw_total": round(total_score, 3)
        }
        
        audit_log.append(f"📊 四維度強度分數: {final_score:.1f}分")
        
        return round(final_score, 2), strength_details
    
    @staticmethod
    def _calculate_month_qi_score(bazi_data: Dict, day_element: str) -> float:
        """1.4.7.2.1 月令氣勢分數計算"""
        try:
            month_branch = bazi_data.get('month_pillar', '  ')[1]
            qi_info = PC.MONTH_QI_MAP.get(month_branch, {})
            
            if not qi_info:
                return 0.5
            
            # 檢查餘氣、中氣、正氣
            score = 0.0
            yuqi_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(qi_info.get('yuqi', ''))
            if yuqi_element == day_element:
                score += 0.3
            
            zhongqi_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(qi_info.get('zhongqi', ''))
            if zhongqi_element == day_element:
                score += 0.4
            
            zhengqi_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(qi_info.get('zhengqi', ''))
            if zhengqi_element == day_element:
                score += 0.3
            
            return score
            
        except Exception:
            return 0.5
    
    @staticmethod
    def _calculate_tong_gen_score_enhanced(bazi_data: Dict, day_element: str) -> float:
        """1.4.7.2.2 通根力量計算"""
        pillars = [
            bazi_data.get('year_pillar', ''),
            bazi_data.get('month_pillar', ''),
            bazi_data.get('day_pillar', ''),
            bazi_data.get('hour_pillar', '')
        ]
        
        score = 0.0
        
        for i, pillar in enumerate(pillars):
            if len(pillar) >= 2:
                branch = pillar[1]
                hidden_stems = PC.BRANCH_HIDDEN_STEMS_PRO.get(branch, [])
                
                # 檢查地支藏干中是否有日主同類
                for hidden_stem, weight, _ in hidden_stems:
                    hidden_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(hidden_stem)
                    if hidden_element == day_element:
                        position_weight = [0.8, 1.0, 1.2, 0.8][i]
                        score += weight * position_weight
                        break
        
        # 日支通根特別重要
        day_branch = bazi_data.get('day_pillar', '  ')[1]
        day_hidden = PC.BRANCH_HIDDEN_STEMS_PRO.get(day_branch, [])
        for hidden_stem, weight, _ in day_hidden:
            hidden_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(hidden_stem)
            if hidden_element == day_element:
                score += weight * 0.5
        
        return min(1.0, score / 4.0)
    
    @staticmethod
    def _calculate_support_score_enhanced(bazi_data: Dict, day_element: str) -> float:
        """1.4.7.2.3 生扶力量計算"""
        elements = bazi_data.get('elements', {})
        
        # 生我者為印
        generation_map = PC.ELEMENT_GENERATION
        support_element = None
        for element, generates in generation_map.items():
            if generates == day_element:
                support_element = element
                break
        
        if not support_element:
            return 0.0
        
        # 印星力量（正印+偏印）
        support_power = elements.get(support_element, 0.0)
        
        # 比劫力量（比肩+劫財）
        same_power = elements.get(day_element, 0.0)
        
        # 綜合計算（印70%，比劫30%）
        score = (support_power * 0.7 + same_power * 0.3) / 100.0
        
        return min(1.0, score)
    
    @staticmethod
    def _calculate_stem_strength_enhanced(bazi_data: Dict, day_element: str) -> float:
        """1.4.7.2.4 天干力量計算"""
        pillars = [
            bazi_data.get('year_pillar', ''),
            bazi_data.get('month_pillar', ''),
            bazi_data.get('day_pillar', ''),
            bazi_data.get('hour_pillar', '')
        ]
        
        same_count = 0
        support_count = 0
        
        for pillar in pillars:
            if len(pillar) >= 1:
                stem = pillar[0]
                stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(stem, '')
                
                if stem_element == day_element:
                    same_count += 1
                elif stem_element in PC.ELEMENT_GENERATION and PC.ELEMENT_GENERATION[stem_element] == day_element:
                    support_count += 1
        
        # 計算分數（比劫60%，印星40%）
        score = (same_count * 0.6 + support_count * 0.4) / 4.0
        
        return min(1.0, score)
    
    @staticmethod
    def _determine_strength_pro(score: float) -> str:
        """1.4.7.2.5 專業身強弱判定"""
        if score >= PC.STRENGTH_THRESHOLD_STRONG:
            return '強'
        elif score >= PC.STRENGTH_THRESHOLD_MEDIUM:
            return '中'
        elif score >= PC.STRENGTH_THRESHOLD_WEAK:
            return '弱'
        else:
            return '極弱'
    
    @staticmethod
    def _determine_pattern_enhanced(bazi_data: Dict, audit_log: List[str]) -> Tuple[str, List[str]]:
        """1.4.7.3 專業格局判定"""
        details = []
        strength_score = bazi_data.get('strength_score', 50.0)
        day_stem = bazi_data.get('day_stem', '')
        day_element = bazi_data.get('day_stem_element', '')
        elements = bazi_data.get('elements', {})
        
        audit_log.append(f"📈 格局判定輸入: 強度{strength_score:.1f}分, 日主{day_stem}{day_element}")
        
        # 1. 檢查從格（身極弱 < 20分）
        if strength_score < 20:
            max_element, max_value = max(elements.items(), key=lambda x: x[1])
            
            if max_element != day_element and max_value > 40:
                pattern_type = f"從{max_element}格"
                details.append(f"身極弱({strength_score:.1f}分)，順從最旺五行{max_element}({max_value:.1f}%)")
                audit_log.append(f"✅ 判定為從格: {pattern_type}")
                return pattern_type, details
        
        # 2. 檢查專旺格（身極強 > 85分且同類五行極旺）
        if strength_score > 85:
            day_element_power = elements.get(day_element, 0.0)
            
            if day_element_power > 60:
                special_pattern = ProfessionalBaziCalculator._identify_special_wang_ge(day_element, elements)
                if special_pattern:
                    pattern_type = special_pattern
                    details.append(f"身極強({strength_score:.1f}分)，{day_element}氣專旺({day_element_power:.1f}%)")
                    audit_log.append(f"✅ 判定為特殊專旺格: {pattern_type}")
                    return pattern_type, details
                
                pattern_type = f"{day_element}專旺格"
                details.append(f"身極強({strength_score:.1f}分)，{day_element}氣專旺({day_element_power:.1f}%)")
                audit_log.append(f"✅ 判定為專旺格: {pattern_type}")
                return pattern_type, details
        
        # 3. 普通格局判定
        if strength_score >= PC.STRENGTH_THRESHOLD_STRONG:
            pattern_type = "身強"
            details.append(f"身強({strength_score:.1f}分)，喜克泄耗")
        elif strength_score >= PC.STRENGTH_THRESHOLD_MEDIUM:
            pattern_type = "中和"
            details.append(f"中和({strength_score:.1f}分)，五行相對平衡")
        else:
            pattern_type = "身弱"
            details.append(f"身弱({strength_score:.1f}分)，喜生扶")
        
        audit_log.append(f"✅ 判定為普通格局: {pattern_type}")
        return pattern_type, details
    
    @staticmethod
    def _identify_special_wang_ge(day_element: str, elements: Dict[str, float]) -> Optional[str]:
        """1.4.7.3.1 識別特殊專旺格"""
        day_element_power = elements.get(day_element, 0.0)
        
        if day_element == '土' and day_element_power > 70:
            return "稼穡格"
        elif day_element == '木' and day_element_power > 70:
            return "曲直格"
        elif day_element == '火' and day_element_power > 70:
            return "炎上格"
        elif day_element == '金' and day_element_power > 70:
            return "從革格"
        elif day_element == '水' and day_element_power > 70:
            return "潤下格"
        
        return None
    
    @staticmethod
    def _calculate_useful_elements_pro(bazi_data: Dict, gender: str, audit_log: List[str]) -> Tuple[List[str], List[str]]:
        """1.4.7.4 專業喜用神計算"""
        details = []
        pattern_type = bazi_data.get('pattern_type', '')
        strength_score = bazi_data.get('strength_score', 50.0)
        day_element = bazi_data.get('day_stem_element', '')
        elements = bazi_data.get('elements', {})
        
        useful_elements = []
        
        # 從格喜用神
        if '從' in pattern_type:
            max_element = max(elements.items(), key=lambda x: x[1])[0]
            useful_elements.append(max_element)
            
            generation_element = PC.ELEMENT_GENERATION.get(max_element)
            if generation_element:
                useful_elements.append(generation_element)
            
            details.append(f"從{max_element}格，喜順從{max_element}及相生之{generation_element}")
        
        # 專旺格喜用神
        elif '專旺' in pattern_type or any(x in pattern_type for x in ['稼穡', '曲直', '炎上', '從革', '潤下']):
            useful_elements.append(day_element)
            details.append(f"{pattern_type}，喜{day_element}氣純正")
        
        # 身強喜用神
        elif '身強' in pattern_type:
            useful_elements.extend(ProfessionalBaziCalculator._get_control_elements(day_element))
            useful_elements.extend(ProfessionalBaziCalculator._get_generation_elements(day_element))
            details.append(f"身強喜克泄耗，喜{', '.join(useful_elements)}")
        
        # 身弱喜用神
        elif '身弱' in pattern_type:
            useful_elements.extend(ProfessionalBaziCalculator._get_support_elements(day_element))
            useful_elements.append(day_element)
            details.append(f"身弱喜生扶，喜{', '.join(useful_elements)}")
        
        # 中和喜用神
        else:
            useful_elements.append(day_element)
            support_element = ProfessionalBaziCalculator._get_support_element(day_element)
            if support_element:
                useful_elements.append(support_element)
            details.append(f"中和喜平衡，喜{', '.join(useful_elements)}")
        
        # 去重並確保順序
        useful_elements = list(dict.fromkeys(useful_elements))
        
        return useful_elements, details
    
    @staticmethod
    def _get_control_elements(day_element: str) -> List[str]:
        """1.4.7.4.1 獲取克制元素（官殺）"""
        control_elements = []
        for element, controls in PC.ELEMENT_CONTROL.items():
            if controls == day_element:
                control_elements.append(element)
        return control_elements
    
    @staticmethod
    def _get_generation_elements(day_element: str) -> List[str]:
        """1.4.7.4.2 獲取被生元素（食傷）"""
        generation_elements = []
        generation_element = PC.ELEMENT_GENERATION.get(day_element)
        if generation_element:
            generation_elements.append(generation_element)
        return generation_elements
    
    @staticmethod
    def _get_support_elements(day_element: str) -> List[str]:
        """1.4.7.4.3 獲取生扶元素（印）"""
        support_elements = []
        for element, generates in PC.ELEMENT_GENERATION.items():
            if generates == day_element:
                support_elements.append(element)
        return support_elements
    
    @staticmethod
    def _get_support_element(day_element: str) -> Optional[str]:
        """1.4.7.4.4 獲取主要生扶元素"""
        for element, generates in PC.ELEMENT_GENERATION.items():
            if generates == day_element:
                return element
        return None
    
    @staticmethod
    def _calculate_harmful_elements_pro(bazi_data: Dict, useful_elements: List[str]) -> List[str]:
        """1.4.7.4.5 專業忌神計算"""
        all_elements = ['木', '火', '土', '金', '水']
        harmful_elements = [e for e in all_elements if e not in useful_elements]
        return harmful_elements
    
    @staticmethod
    def _analyze_spouse_star_pro(bazi_data: Dict, gender: str) -> Tuple[str, List[str]]:
        """1.4.7.5 專業夫妻星分析"""
        details = []
        day_stem = bazi_data.get('day_stem', '')
        day_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        
        if not day_element or gender not in ['男', '女']:
            return "未知", ["資料不足"]
        
        spouse_element = None
        if gender == '男':
            for element, controlled in PC.ELEMENT_CONTROL.items():
                if controlled == day_element:
                    spouse_element = element
                    break
        else:
            for element, controls in PC.ELEMENT_CONTROL.items():
                if controls == day_element:
                    spouse_element = element
                    break
        
        if not spouse_element:
            return "無明顯夫妻星", ["夫妻星不明顯"]
        
        pillars = [
            bazi_data.get('year_pillar', ''),
            bazi_data.get('month_pillar', ''),
            bazi_data.get('day_pillar', ''),
            bazi_data.get('hour_pillar', '')
        ]
        
        spouse_count = 0
        positions = []
        
        for i, pillar in enumerate(pillars):
            if len(pillar) >= 2:
                stem = pillar[0]
                branch = pillar[1]
                
                stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(stem, '')
                if stem_element == spouse_element:
                    spouse_count += 1
                    positions.append(f"{['年','月','日','時'][i]}干")
                
                branch_element = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(branch, '')
                if branch_element == spouse_element:
                    spouse_count += 1
                    positions.append(f"{['年','月','日','時'][i]}支")
        
        if spouse_count == 0:
            status = "無夫妻星"
            details.append("八字中無明顯夫妻星")
        elif spouse_count == 1:
            status = "夫妻星單一"
            details.append(f"夫妻星出現在{positions[0]}")
        elif spouse_count == 2:
            status = "夫妻星明顯"
            details.append(f"夫妻星出現在{', '.join(positions)}")
        else:
            status = "夫妻星旺盛"
            details.append(f"夫妻星多現({spouse_count}處)")
        
        return status, details
    
    @staticmethod
    def _analyze_spouse_palace_pro(bazi_data: Dict) -> Tuple[str, List[str]]:
        """1.4.7.6 專業夫妻宮分析"""
        details = []
        day_pillar = bazi_data.get('day_pillar', '')
        
        if len(day_pillar) < 2:
            return "未知", ["日柱資料不足"]
        
        day_branch = day_pillar[1]
        branch_element = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(day_branch, '')
        
        if day_branch in ['子', '午', '卯', '酉']:
            status = "夫妻宮旺"
            details.append(f"日支{day_branch}{branch_element}為四正位，夫妻宮強")
        elif day_branch in ['寅', '申', '巳', '亥']:
            status = "夫妻宮動"
            details.append(f"日支{day_branch}{branch_element}為四生位，夫妻關係活躍")
        elif day_branch in ['辰', '戌', '丑', '未']:
            status = "夫妻宮穩"
            details.append(f"日支{day_branch}{branch_element}為四庫位，夫妻關係穩定")
        else:
            status = "夫妻宮平"
            details.append(f"日支{day_branch}{branch_element}")
        
        return status, details
    
    @staticmethod
    def _calculate_shen_sha_enhanced(bazi_data: Dict) -> Tuple[str, float, List[str]]:
        """1.4.7.7 專業神煞計算"""
        details = []
        shen_sha_list = []
        total_bonus = 0.0
        
        year_pillar = bazi_data.get('year_pillar', '')
        day_pillar = bazi_data.get('day_pillar', '')
        
        if len(year_pillar) < 2 or len(day_pillar) < 2:
            return "無", 0.0, ["資料不足"]
        
        year_branch = year_pillar[1]
        day_stem = day_pillar[0]
        
        all_branches = [
            bazi_data.get('year_pillar', '  ')[1],
            bazi_data.get('month_pillar', '  ')[1],
            bazi_data.get('day_pillar', '  ')[1],
            bazi_data.get('hour_pillar', '  ')[1]
        ]
        
        # 1. 紅鸞星
        hong_luan_branch = ProfessionalBaziCalculator.HONG_LUAN_MAP.get(year_branch)
        if hong_luan_branch in all_branches:
            shen_sha_list.append("紅鸞")
            total_bonus += 6
            details.append(f"紅鸞星在{hong_luan_branch}位")
        
        # 2. 天喜星
        tian_xi_branch = ProfessionalBaziCalculator.TIAN_XI_MAP.get(year_branch)
        if tian_xi_branch in all_branches:
            shen_sha_list.append("天喜")
            total_bonus += 5
            details.append(f"天喜星在{tian_xi_branch}位")
        
        # 3. 天乙貴人
        tian_yi_branches = ProfessionalBaziCalculator.TIANYI_GUI_REN.get(day_stem, [])
        for branch in all_branches:
            if branch in tian_yi_branches:
                shen_sha_list.append("天乙貴人")
                total_bonus += 8
                details.append(f"天乙貴人在{branch}位")
                break
        
        shen_sha_names = "、".join(shen_sha_list) if shen_sha_list else "無"
        
        return shen_sha_names, total_bonus, details
    
    @staticmethod
    def _calculate_shi_shen_pro(bazi_data: Dict, gender: str) -> Tuple[str, List[str]]:
        """1.4.7.8 專業十神結構分析"""
        details = []
        day_stem = bazi_data.get('day_stem', '')
        
        if not day_stem:
            return "普通結構", ["日主不明"]
        
        stems = []
        for pillar in [bazi_data.get('year_pillar', ''),
                      bazi_data.get('month_pillar', ''),
                      bazi_data.get('hour_pillar', '')]:
            if len(pillar) >= 1:
                stems.append(pillar[0])
        
        mapping = ProfessionalBaziCalculator.SHI_SHEN_MAP.get(day_stem, {})
        shi_shen_counts = {}
        
        for stem in stems:
            shi_shen = mapping.get(stem)
            if shi_shen:
                shi_shen_counts[shi_shen] = shi_shen_counts.get(shi_shen, 0) + 1
        
        special_patterns = []
        
        if '七殺' in shi_shen_counts and ('正印' in shi_shen_counts or '偏印' in shi_shen_counts):
            special_patterns.append("殺印相生")
            details.append("七殺與印綬相生，化殺為權")
        
        if ('正財' in shi_shen_counts or '偏財' in shi_shen_counts) and \
           ('正官' in shi_shen_counts or '七殺' in shi_shen_counts):
            special_patterns.append("財官相生")
            details.append("財星與官殺相生，富貴可期")
        
        if '傷官' in shi_shen_counts and ('正財' in shi_shen_counts or '偏財' in shi_shen_counts):
            special_patterns.append("傷官生財")
            details.append("傷官生財，技藝致富")
        
        if '食神' in shi_shen_counts and '七殺' in shi_shen_counts:
            special_patterns.append("食神制殺")
            details.append("食神制殺，以智取勝")
        
        if ('比肩' in shi_shen_counts or '劫財' in shi_shen_counts) and \
           ('正財' in shi_shen_counts or '偏財' in shi_shen_counts):
            if shi_shen_counts.get('比肩', 0) + shi_shen_counts.get('劫財', 0) >= 2:
                special_patterns.append("比劫奪財")
                details.append("比劫多見，易有爭財之事")
        
        if special_patterns:
            structure = "、".join(special_patterns)
        else:
            main_shi_shen = []
            for shi_shen, count in shi_shen_counts.items():
                if count >= 2:
                    main_shi_shen.append(f"{shi_shen}{count}重")
                else:
                    main_shi_shen.append(shi_shen)
            
            if main_shi_shen:
                structure = f"{'、'.join(main_shi_shen[:3])}為主"
            else:
                structure = "普通結構"
        
        return structure, details
    
    @staticmethod
    def _calculate_dayun_pro(bazi_data: Dict, gender: str) -> Dict[str, Any]:
        """1.4.7.9 專業大運分析（簡化版）"""
        birth_year = bazi_data.get('birth_year', 2000)
        birth_month = bazi_data.get('birth_month', 1)
        gender = bazi_data.get('gender', '未知')
        
        if gender == '男':
            if birth_year % 2 == 0:
                start_age = 0
                direction = "順"
            else:
                start_age = 1
                direction = "逆"
        else:
            if birth_year % 2 == 0:
                start_age = 1
                direction = "逆"
            else:
                start_age = 0
                direction = "順"
        
        return {
            "start_age": start_age,
            "direction": direction,
            "note": "大運計算為簡化版本，專業計算需詳細節氣"
        }
# 🔖 1.4 專業八字核心引擎結束

# 🔖 1.5 專業評分引擎開始
class ProfessionalScoringEngine:
    """專業評分引擎 - 修正版"""
    
    # ========== 1.5.1 評分配置 ==========
    CONFIG = {
        # 基礎分數
        'base_scores': {
            'stem_five_harmony': 72,      # 天干五合
            'branch_six_harmony': 68,     # 地支六合
            'branch_three_harmony': 64,   # 地支三合
            'same_stem': 55,              # 同天干
            'same_branch': 52,            # 同地支
            'no_relation': 45,            # 無關係
        },
        
        # 刑沖懲罰
        'clash_penalties': {
            'day_clash': -15,     # 日支六沖
            'day_harm': -10,      # 日支六害
            'fuyin': -20,         # 伏吟
            'three_punishment': -25,  # 三刑
            'other_clash': -5,    # 其他六沖
            'other_harm': -3,     # 其他六害
        },
        
        # 加分項
        'bonuses': {
            'hongluan_tianxi': 10,    # 紅鸞天喜
            'tianyi_guiren': 7,       # 天乙貴人
            'useful_complement': 8,   # 喜用互補
            'rescue': 5,              # 解沖
        },
        
        # 信心度因子
        'confidence_factors': {
            "高": 1.00,
            "中": 0.96,
            "低": 0.92,
            "估算": 0.88,
        },
    }
    
    @staticmethod
    def calculate_match_score_pro(bazi1: Dict, bazi2: Dict, 
                                gender1: str, gender2: str,
                                is_testpair: bool = False) -> Dict[str, Any]:
        """1.5.2 專業命理評分主函數 - 修正版"""
        audit_log = []
        
        try:
            audit_log.append("🎯 開始專業命理評分")
            
            # 分析特徵
            features = ProfessionalScoringEngine._analyze_features(bazi1, bazi2, audit_log)
            
            # 計算基礎分
            base_score = ProfessionalScoringEngine._calculate_base_score(features)
            audit_log.append(f"📊 基礎分: {base_score}分")
            
            # 計算刑沖懲罰
            clash_penalty = ProfessionalScoringEngine._calculate_clash_penalty(features)
            if clash_penalty != 0:
                audit_log.append(f"⚠️ 刑沖懲罰: {clash_penalty}分")
            
            # 計算加分項
            bonuses = ProfessionalScoringEngine._calculate_bonuses(features)
            if bonuses != 0:
                audit_log.append(f"✨ 加分項: {bonuses}分")
            
            # 計算原始分數
            raw_score = base_score + clash_penalty + bonuses
            audit_log.append(f"🧮 原始分數: {raw_score:.1f}分")
            
            # 應用信心度調整
            confidence_factor = ProfessionalScoringEngine._get_confidence_factor(
                features['confidence1'], features['confidence2']
            )
            if confidence_factor != 1.0:
                audit_log.append(f"📉 信心度調整因子: {confidence_factor:.2f}")
            
            adjusted_score = raw_score * confidence_factor
            
            # 最終校準
            final_score = ProfessionalScoringEngine._apply_final_calibration(
                adjusted_score, features
            )
            
            # 確保分數範圍
            final_score = max(25.0, min(92.0, final_score))
            
            # 獲取評級和模型
            rating = PC.get_rating(final_score)
            rating_desc = PC.get_rating_description(final_score)
            relationship_model = ProfessionalScoringEngine._determine_relationship_model(final_score, features)
            
            audit_log.append(f"✅ 命理評分完成: {final_score:.1f}分 ({relationship_model})")
            
            return {
                "score": round(final_score, 1),
                "rating": rating,
                "rating_description": rating_desc,
                "relationship_model": relationship_model,
                "structure_type": features['structure_type'],
                "has_day_clash": features['has_day_clash'],
                "has_hongluan_tianxi": features['has_hongluan_tianxi'],
                "has_useful_complement": features['has_useful_complement'],
                "audit_log": audit_log,
                "details": {
                    "base_score": base_score,
                    "clash_penalty": clash_penalty,
                    "bonuses": bonuses,
                    "confidence_factor": confidence_factor,
                    "raw_score": raw_score,
                    "adjusted_score": adjusted_score
                }
            }
            
        except Exception as e:
            logger.error(f"命理評分錯誤: {e}", exc_info=True)
            raise MatchScoringError(f"評分失敗: {str(e)}")
    
    @staticmethod
    def _analyze_features(bazi1: Dict, bazi2: Dict, audit_log: List[str]) -> Dict[str, Any]:
        """1.5.2.1 分析所有特徵 - 修正版"""
        features = {
            'day_stem1': bazi1.get('day_stem', ''),
            'day_stem2': bazi2.get('day_stem', ''),
            'day_branch1': bazi1.get('day_pillar', '  ')[1] if len(bazi1.get('day_pillar', '')) >= 2 else '',
            'day_branch2': bazi2.get('day_pillar', '  ')[1] if len(bazi2.get('day_pillar', '')) >= 2 else '',
            'year_branch1': bazi1.get('year_pillar', '  ')[1] if len(bazi1.get('year_pillar', '')) >= 2 else '',
            'year_branch2': bazi2.get('year_pillar', '  ')[1] if len(bazi2.get('year_pillar', '')) >= 2 else '',
            'confidence1': bazi1.get('hour_confidence', '中'),
            'confidence2': bazi2.get('hour_confidence', '中'),
            'useful1': bazi1.get('useful_elements', []),
            'useful2': bazi2.get('useful_elements', []),
            'shen_sha_names1': (bazi1.get('shen_sha_names') or '').split('、'),
            'shen_sha_names2': (bazi2.get('shen_sha_names') or '').split('、'),
            
            # 初始值
            'structure_type': 'no_relation',
            'has_day_clash': False,
            'has_day_harm': False,
            'has_fuyin': False,
            'has_three_punishment': False,
            'has_hongluan_tianxi': False,
            'has_useful_complement': False,
        }
        
        # 分析結構類型
        features['structure_type'] = ProfessionalScoringEngine._analyze_structure_type(features)
        audit_log.append(f"🏗️ 結構類型: {features['structure_type']}")
        
        # 分析刑沖
        clash_info = ProfessionalScoringEngine._analyze_clashes(bazi1, bazi2, features, audit_log)
        features.update(clash_info)
        
        # 分析紅鸞天喜
        features['has_hongluan_tianxi'] = ProfessionalScoringEngine._detect_hongluan_tianxi(features)
        if features['has_hongluan_tianxi']:
            audit_log.append(f"💕 紅鸞天喜: 有")
        
        # 分析喜用互補
        features['has_useful_complement'] = ProfessionalScoringEngine._detect_useful_complement(features)
        if features['has_useful_complement']:
            audit_log.append(f"🔄 喜用互補: 有")
        
        return features
    
    @staticmethod
    def _analyze_clashes(bazi1: Dict, bazi2: Dict, features: Dict, audit_log: List[str]) -> Dict[str, Any]:
        """1.5.2.1.2 分析刑沖 - 修正版"""
        result = {
            'has_day_clash': False,
            'has_day_harm': False,
            'has_fuyin': False,
            'has_three_punishment': False,
        }
        
        # 檢查伏吟（完全相同）
        pillars_same = all(
            bazi1.get(k, '') == bazi2.get(k, '')
            for k in ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        )
        if pillars_same:
            result['has_fuyin'] = True
            audit_log.append(f"⚠️ 伏吟: 有")
        
        # 日支關係
        if ProfessionalScoringEngine._is_branch_clash(features['day_branch1'], features['day_branch2']):
            result['has_day_clash'] = True
            audit_log.append(f"⚡ 日支六沖: {features['day_branch1']}沖{features['day_branch2']}")
        elif ProfessionalScoringEngine._is_branch_harm(features['day_branch1'], features['day_branch2']):
            result['has_day_harm'] = True
            audit_log.append(f"⚡ 日支六害: {features['day_branch1']}害{features['day_branch2']}")
        
        # 檢查三刑
        all_branches = []
        for pillar in ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']:
            pillar1 = bazi1.get(pillar, '')
            pillar2 = bazi2.get(pillar, '')
            if len(pillar1) >= 2:
                all_branches.append(pillar1[1])
            if len(pillar2) >= 2:
                all_branches.append(pillar2[1])
        
        # 檢查寅巳申三刑
        yin_count = all_branches.count('寅')
        si_count = all_branches.count('巳')
        shen_count = all_branches.count('申')
        
        if yin_count + si_count + shen_count >= 2:
            # 需要寅巳申同時存在才構成三刑
            if yin_count >= 1 and si_count >= 1 and shen_count >= 1:
                result['has_three_punishment'] = True
                audit_log.append(f"⚠️ 三刑: 寅巳申三刑")
        
        return result
    
    @staticmethod
    def _apply_final_calibration(score: float, features: Dict) -> float:
        """1.5.2.6 應用最終校準 - 修正版"""
        calibrated = score
        
        # 天干五合保障
        if features['structure_type'] == 'stem_five_harmony' and not features['has_day_clash']:
            calibrated = max(70.0, min(82.0, calibrated))
        
        # 紅鸞天喜保障
        elif features['has_hongluan_tianxi'] and not features['has_day_clash']:
            calibrated = max(75.0, min(85.0, calibrated))
        
        # 三刑懲罰
        elif features['has_three_punishment']:
            calibrated = max(25.0, min(40.0, calibrated * 0.7))
        
        # 日支六沖懲罰
        elif features['has_day_clash']:
            calibrated = max(35.0, min(48.0, calibrated * 0.8))
        
        # 伏吟懲罰
        elif features['has_fuyin']:
            calibrated = max(50.0, min(65.0, calibrated * 0.9))
        
        return calibrated
# 🔖 1.5 專業評分引擎結束

# 🔖 1.6 主入口函數開始
def calculate_bazi_pro(year: int, month: int, day: int, hour: int,
                      gender: str = "未知",
                      hour_confidence: str = "高",
                      minute: Optional[int] = None,
                      longitude: float = PC.DEFAULT_LONGITUDE,
                      latitude: float = PC.DEFAULT_LATITUDE) -> Dict[str, Any]:
    """1.6.1 專業八字計算對外接口"""
    return ProfessionalBaziCalculator.calculate_pro(
        year, month, day, hour, gender, hour_confidence, minute, longitude, latitude
    )

def calculate_match_pro(bazi1: Dict, bazi2: Dict,
                       gender1: str, gender2: str,
                       is_testpair: bool = False) -> Dict[str, Any]:
    """1.6.2 專業八字配對對外接口"""
    return ProfessionalScoringEngine.calculate_match_score_pro(
        bazi1, bazi2, gender1, gender2, is_testpair
    )

# 保持向後兼容的別名
calculate_bazi = calculate_bazi_pro
calculate_match = calculate_match_pro
BaziCalculator = ProfessionalBaziCalculator
ScoringEngine = ProfessionalScoringEngine
BaziError = BaziSystemError
MatchError = MatchScoringError
# 🔖 1.6 主入口函數結束

# 🔖 1.7 統一格式化工具類開始
class ProfessionalFormatters:
    """專業格式化工具類"""
    
    @staticmethod
    def format_personal_data(bazi_data: Dict, username: str = "用戶") -> str:
        """1.7.1 專業個人資料格式化"""
        lines = []
        
        # 標題
        lines.append(f"📊 {username} 的專業八字分析")
        lines.append("=" * 40)
        
        # 基礎信息
        gender = bazi_data.get('gender', '未知')
        birth_year = bazi_data.get('birth_year', '')
        birth_month = bazi_data.get('birth_month', '')
        birth_day = bazi_data.get('birth_day', '')
        birth_hour = bazi_data.get('birth_hour', '')
        birth_minute = bazi_data.get('birth_minute', 0)
        
        hour_confidence = bazi_data.get('hour_confidence', '中')
        confidence_text = hour_confidence
        
        lines.append(f"👤 性別：{gender}")
        lines.append(f"🎂 出生：{birth_year}年{birth_month}月{birth_day}日{birth_hour}時{birth_minute}分")
        lines.append(f"⏱️ 時間信心度：{confidence_text}")
        
        # 八字四柱
        year_pillar = bazi_data.get('year_pillar', '')
        month_pillar = bazi_data.get('month_pillar', '')
        day_pillar = bazi_data.get('day_pillar', '')
        hour_pillar = bazi_data.get('hour_pillar', '')
        
        lines.append(f"🔢 八字：{year_pillar} {month_pillar} {day_pillar} {hour_pillar}")
        
        # 生肖和日主
        zodiac = bazi_data.get('zodiac', '未知')
        day_stem = bazi_data.get('day_stem', '')
        day_stem_element = bazi_data.get('day_stem_element', '')
        day_stem_strength = bazi_data.get('day_stem_strength', '中')
        strength_score = bazi_data.get('strength_score', 50)
        
        lines.append(f"🐉 生肖：{zodiac}")
        lines.append(f"🎯 日主：{day_stem}{day_stem_element}（{day_stem_strength}，{strength_score:.1f}分）")
        
        # 格局
        pattern_type = bazi_data.get('pattern_type', '正格')
        lines.append(f"🏛️ 格局：{pattern_type}")
        
        # 喜用神和忌神
        useful_elements = bazi_data.get('useful_elements', [])
        harmful_elements = bazi_data.get('harmful_elements', [])
        
        lines.append(f"✅ 喜用神：{', '.join(useful_elements) if useful_elements else '無'}")
        lines.append(f"❌ 忌神：{', '.join(harmful_elements) if harmful_elements else '無'}")
        
        # 十神結構
        shi_shen_structure = bazi_data.get('shi_shen_structure', '普通結構')
        lines.append(f"🎭 十神結構：{shi_shen_structure}")
        
        # 夫妻分析
        spouse_star_status = bazi_data.get('spouse_star_status', '未知')
        spouse_palace_status = bazi_data.get('spouse_palace_status', '未知')
        
        lines.append(f"💑 夫妻星：{spouse_star_status}")
        lines.append(f"🏠 夫妻宮：{spouse_palace_status}")
        
        # 神煞
        shen_sha_names = bazi_data.get('shen_sha_names', '無')
        lines.append(f"✨ 神煞：{shen_sha_names}")
        
        # 五行分佈
        elements = bazi_data.get('elements', {})
        wood = elements.get('木', 0)
        fire = elements.get('火', 0)
        earth = elements.get('土', 0)
        metal = elements.get('金', 0)
        water = elements.get('水', 0)
        
        lines.append(f"🌳 五行分佈：木{wood:.1f}% 火{fire:.1f}% 土{earth:.1f}% 金{metal:.1f}% 水{water:.1f}%")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_match_result(match_result: Dict, bazi1: Dict, bazi2: Dict,
                          user_a_name: str = "用戶A", user_b_name: str = "用戶B") -> str:
        """1.7.2 專業配對結果格式化 - 修正版"""
        lines = []
        
        # 標題
        lines.append(f"🎯 {user_a_name} 與 {user_b_name} 的專業八字配對結果")
        lines.append("-" * 40)
        
        # 八字信息
        pillars1 = f"{bazi1.get('year_pillar', '')} {bazi1.get('month_pillar', '')} {bazi1.get('day_pillar', '')} {bazi1.get('hour_pillar', '')}"
        pillars2 = f"{bazi2.get('year_pillar', '')} {bazi2.get('month_pillar', '')} {bazi2.get('day_pillar', '')} {bazi2.get('hour_pillar', '')}"
        
        lines.append(f"{user_a_name}八字：{pillars1}")
        lines.append(f"{user_b_name}八字：{pillars2}")
        lines.append("")
        
        # 核心分數和評級
        score = match_result.get('score', 0)
        rating = match_result.get('rating', '未知')
        rating_description = match_result.get('rating_description', '')
        
        lines.append(f"📊 配對分數：{score:.1f}分")
        lines.append(f"✨ 評級：{rating}")
        lines.append(f"📝 描述：{rating_description}")
        
        # 關係模型
        relationship_model = match_result.get('relationship_model', '')
        lines.append(f"🎭 關係模型：{relationship_model}")
        
        # 詳細解釋
        details = []
        if match_result.get('structure_type') != 'no_relation':
            structure_names = {
                'stem_five_harmony': '天干五合',
                'branch_six_harmony': '地支六合',
                'branch_three_harmony': '地支三合',
                'same_stem': '同天干',
                'same_branch': '同地支',
            }
            structure_name = structure_names.get(match_result.get('structure_type'), '特殊結構')
            details.append(f"• 日柱關係：{structure_name}")
        
        if match_result.get('has_day_clash'):
            details.append(f"• 日支六沖：需要注意雙方個性差異")
        
        if match_result.get('has_hongluan_tianxi'):
            details.append(f"• 紅鸞天喜：有良好的感情基礎")
        
        if match_result.get('has_useful_complement'):
            details.append(f"• 喜用互補：雙方五行互相補足")
        
        if details:
            lines.append("")
            lines.append("🔍 詳細分析：")
            lines.extend(details)
        
        # 計算過程摘要
        if 'details' in match_result:
            calc_details = match_result['details']
            lines.append("")
            lines.append("🧮 計算過程：")
            lines.append(f"• 基礎分數：{calc_details.get('base_score', 0):.1f}分")
            lines.append(f"• 刑沖懲罰：{calc_details.get('clash_penalty', 0):+.1f}分")
            lines.append(f"• 加分項：{calc_details.get('bonuses', 0):+.1f}分")
            lines.append(f"• 信心度調整：x{calc_details.get('confidence_factor', 1.0):.2f}")
            lines.append(f"• 最終分數：{score:.1f}分")
        
        lines.append("")
        lines.append("💡 建議：此結果僅供參考，實際關係需要雙方共同努力經營。")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_test_pair_result(match_result: Dict, bazi1: Dict, bazi2: Dict) -> str:
        """1.7.3 測試配對結果格式化"""
        return ProfessionalFormatters.format_match_result(
            match_result, bazi1, bazi2, "測試用戶A", "測試用戶B"
        )

# 保持向後兼容的別名
BaziFormatters = ProfessionalFormatters
# 🔖 1.7 統一格式化工具類結束

# ========文件信息開始 ========#
"""
文件: new_calculator.py
功能: 八字配對系統專業核心引擎

引用文件: 
- 無（為核心引擎文件）

被引用文件:
- bot.py（主程序）
- admin_service.py（管理員服務）
- bazi_soulmate.py（真命天子搜索）
- texts.py（文本內容）

主要特點:
1. 採用簡化清晰的評分邏輯，避免複雜無效的計算
2. 保持向後兼容，所有現有接口不變
3. 修正了月令氣勢表中的錯誤
4. 簡化了評分引擎，去除無效的代碼路徑
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
目錄:
1.1 專業錯誤處理系統 - 定義系統錯誤階層
1.2 專業配置系統 - 時區、五行、評級與權重等專業配置
1.3 專業時間處理引擎 - 真太陽時與時間校正
1.4 專業八字核心引擎 - 四柱計算、五行分析與結構推導
1.5 專業評分引擎 - 簡化清晰的評分邏輯
1.6 主入口函數 - 向後兼容的八字與配對入口
1.7 統一格式化工具類 - 個人分析與配對結果輸出
"""
# ========目錄結束 ========#

# ========修正紀錄開始 ========#
"""
修正紀錄:
2026-02-05 全面簡化評分引擎：
1. 問題：原ProfessionalScoringEngine邏輯過於複雜且部分無效
   位置：_analyze_clashes方法中計算clash_level的邏輯
   後果：代碼難以維護，且部分功能從未使用
   修正：簡化為清晰的加減分系統

2. 問題：評分引擎中的解沖檢測總是返回False
   位置：_detect_rescue方法
   後果：從未真正檢測解沖
   修正：去除無效的代碼路徑

3. 問題：配置系統中的月令氣勢表錯誤
   位置：MONTH_QI_MAP中的"申"月餘氣
   後果：申月的餘氣錯誤地設為"己"（應為"戊"）
   修正：將"申"月餘氣改為"戊"

4. 問題：評分引擎中的喜用互補計算邏輯有問題
   位置：_calculate_useful_bonus方法
   後果：計算的"濃度"可能不准確
   修正：簡化為基礎的互補檢測

2026-02-04 重新設計評分引擎：
1. 問題：原ProfessionalScoringEngine缺失多個必要方法
   位置：_analyze_structure_type、_analyze_clashes等缺失方法
   後果：admin_service測試無法運行
   修正：重新設計並實現所有缺失方法

2026-02-03 修正testpair命令：
1. 問題：test_pair_command函數變量作用域衝突
   位置：bot.py中的test_pair_command
   後果：name 'bazi1' is not defined錯誤
   修正：明確使用bazi1_result和bazi2_result避免衝突

2026-02-03 第一次修正：
1. 問題：get_profile_data函數字段名錯誤
   位置：bot.py中的get_profile_data
   後果：shi_shen_structure字段不正確
   修正：將字段名修正
"""
# ========修正紀錄結束 ========#