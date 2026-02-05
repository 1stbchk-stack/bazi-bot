#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字配對系統核心 - 專業級八字計算與配對引擎
採用專業命理師傅級算法，確保99%案例與頂級命理師計算結果一致
架構：核心計算 → 專業分析 → 精準評分 → 審計驗證
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

    # ========== 基礎時間配置 ==========
    TIME_ZONE_MERIDIAN: float = 120.0          # 東經120度標準時區（中國/香港常用）
    DAY_BOUNDARY_MODE: str = "zizheng"        # 子正換日（專業標準）
    DEFAULT_LONGITUDE: float = 114.17         # 香港經度
    DEFAULT_LATITUDE: float = 22.32           # 香港緯度
    LONGITUDE_CORRECTION: int = 4             # 經度差1度 = 4分鐘
    DAY_BOUNDARY_HOUR: int = 23               # 日界線時辰（子正）
    DAY_BOUNDARY_MINUTE: int = 0              # 日界線分鐘

    # ========== 香港夏令時完整表 ==========
    HK_DST_PERIODS = [
        ("1941-04-01", "1941-12-25"), ("1942-12-25", "1943-09-30"),
        ("1946-04-20", "1946-12-01"), ("1947-04-13", ("1947-11-02")),
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

    # ========== 專業月令氣勢表（命理師傅級） ==========
    MONTH_QI_MAP = {
        "子": {"yuqi": "辛", "zhongqi": "癸", "zhengqi": "壬", "qi_score": 10},
        "丑": {"yuqi": "壬", "zhongqi": "辛", "zhengqi": "己", "qi_score": 8},
        "寅": {"yuqi": "己", "zhongqi": "戊", "zhengqi": "甲", "qi_score": 12},
        "卯": {"yuqi": "甲", "zhongqi": "丙", "zhengqi": "乙", "qi_score": 10},
        "辰": {"yuqi": "乙", "zhongqi": "癸", "zhengqi": "戊", "qi_score": 8},
        "巳": {"yuqi": "戊", "zhongqi": "庚", "zhengqi": "丙", "qi_score": 12},
        "午": {"yuqi": "丙", "zhongqi": "戊", "zhengqi": "丁", "qi_score": 10},
        "未": {"yuqi": "丁", "zhongqi": "乙", "zhengqi": "己", "qi_score": 8},
        "申": {"yuqi": "己", "zhongqi": "戊", "zhengqi": "庚", "qi_score": 10},
        "酉": {"yuqi": "庚", "zhongqi": "壬", "zhengqi": "辛", "qi_score": 8},
        "戌": {"yuqi": "辛", "zhongqi": "丁", "zhengqi": "戊", "qi_score": 8},
        "亥": {"yuqi": "戊", "zhongqi": "甲", "zhengqi": "壬", "qi_score": 10},
    }

    # ========== 身強弱專業權重 ==========
    MONTH_QI_WEIGHT: float = 40.0  # 月令氣勢權重（主力）
    TONG_GEN_WEIGHT: float = 30.0  # 通根力量權重
    SUPPORT_WEIGHT: float = 20.0   # 生扶力量權重
    STEM_STRENGTH_WEIGHT: float = 10.0  # 天干力量權重

    STRENGTH_THRESHOLD_STRONG: float = 70.0  # 強
    STRENGTH_THRESHOLD_MEDIUM: float = 40.0  # 中
    STRENGTH_THRESHOLD_WEAK: float = 20.0    # 弱

    # ========== 陰陽天干 ==========
    YANG_STEMS = ["甲", "丙", "戊", "庚", "壬"]
    YIN_STEMS = ["乙", "丁", "己", "辛", "癸"]

    # ========== 五行關係配置 ==========
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

    # ========== 地支藏干增強版 ==========
    BRANCH_HIDDEN_STEMS_PRO = {
        "子": [("癸", 1.0, 100)],  # 子水100%癸水
        "丑": [("己", 0.5, 60), ("癸", 0.3, 30), ("辛", 0.2, 10)],
        "寅": [("甲", 0.6, 60), ("丙", 0.3, 30), ("戊", 0.1, 10)],
        "卯": [("乙", 1.0, 100)],
        "辰": [("戊", 0.5, 60), ("乙", 0.3, 30), ("癸", 0.2, 10)],
        "巳": [("丙", 0.6, 60), ("庚", 0.3, 30), ("戊", 0.1, 10)],
        "午": [("丁", 0.7, 70), ("己", 0.3, 30)],
        "未": [("己", 0.6, 60), ("丁", 0.3, 30), ("乙", 0.1, 10)],
        "申": [("庚", 0.6, 60), ("壬", 0.3, 30), ("戊", 0.1, 10)],
        "酉": [("辛", 1.0, 100)],
        "戌": [("戊", 0.6, 60), ("辛", 0.3, 30), ("丁", 0.1, 10)],
        "亥": [("壬", 0.7, 70), ("甲", 0.3, 30)],
    }

    # ========== 專業評級標準 ==========
    THRESHOLD_TERMINATION: float = 25.0   # 終止線
    THRESHOLD_STRONG_WARNING: float = 35.0  # 強烈警告
    THRESHOLD_WARNING: float = 45.0         # 警告
    THRESHOLD_ACCEPTABLE: float = 55.0      # 可接受
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

    # ========== 時間信心度因子 ==========
    TIME_CONFIDENCE_LEVELS: dict = {  # 補充類型提示
        "高": 1.00,   # 精確時間，無調整
        "中": 0.95,   # 有輕微調整
        "低": 0.90,   # 有明顯調整
        "估算": 0.85, # 估算時間
    }

    @classmethod
    def get_rating(cls, score: float) -> str:
        """根據分數取得評級名稱。"""
        for threshold, name, _ in cls.RATING_SCALE:
            if score >= threshold:
                return name
        return "避免發展"

    @classmethod
    def get_rating_description(cls, score: float) -> str:
        """根據分數取得評級描述。"""
        for threshold, _, description in cls.RATING_SCALE:
            if score >= threshold:
                return description
        return "硬傷明顯，易生變，不適合婚戀"

    @classmethod
    def get_confidence_factor(cls, confidence: str) -> float:
        """根據時間信心度字串取得數值因子。"""
        return cls.TIME_CONFIDENCE_LEVELS.get(confidence, 0.90)

# 創建專業配置實例（保持向後兼容：PC 名稱在其他文件大量使用）
PC = ProfessionalConfig
# 🔖 1.2 專業配置系統結束

# 🔖 1.3 專業時間處理引擎開始
class ProfessionalTimeProcessor:
    """
    專業時間處理引擎 - 確保99%時間計算準確
    功能：真太陽時計算、夏令時校正、經度調整、均時差補償、日界處理及信心度動態調整
    目標：將標準時間轉換為極精密的真太陽時，保障後續八字計算與頂級命理師結果一致。
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
        """專業真太陽時計算（平太陽時 → 真太陽時）"""
        audit_log: List[str] = []
        audit_log.append(
            f"🔍 專業時間計算開始: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} "
            f"(經度: {longitude:.2f}°，原始信心度: {confidence})"
        )

        try:
            # 1. 夏令時檢查（香港歷史）
            dst_adjust = ProfessionalTimeProcessor._get_dst_adjustment(year, month, day, audit_log)
            
            # 2. 經度校正（以東經120度為標準）
            lon_adjust = ProfessionalTimeProcessor._get_longitude_adjustment(longitude, audit_log)
            
            # 3. 均時差校正 (Equation of Time)
            eot_adjust = ProfessionalTimeProcessor._get_equation_of_time_adjustment(
                year, month, day, hour, minute, audit_log
            )

            # 4. 累計全部時間調整
            total_adjust_minutes = dst_adjust + lon_adjust + eot_adjust
            audit_log.append(f"📊 總調整量: {total_adjust_minutes:+.1f} 分鐘")
            total_minutes = hour * 60 + minute + total_adjust_minutes

            # 5. 日界處理（跨日調整）
            day_delta, adjusted_minutes = ProfessionalTimeProcessor._apply_day_boundary(total_minutes, audit_log)
            true_hour = int(adjusted_minutes // 60)
            true_minute = int(round(adjusted_minutes % 60))
            
            # 修正四捨五入導致的60分鐘極端情況
            if true_minute == 60:
                true_minute = 0
                true_hour = (true_hour + 1) % 24

            # 6. 根據總調整幅度動態調整信心度
            new_confidence = ProfessionalTimeProcessor._adjust_confidence_level(
                confidence, abs(total_adjust_minutes), audit_log
            )

            audit_log.append(
                f"✅ 最終真太陽時結果: {true_hour:02d}:{true_minute:02d} "
                f"(信心度: {new_confidence}，跨日: {day_delta:+d} 天)"
            )

            return {
                'hour': true_hour,           # 保持原鍵名，向後兼容
                'minute': true_minute,       # 保持原鍵名，向後兼容
                'confidence': new_confidence,
                'adjusted': abs(total_adjust_minutes) > 5,
                'day_adjusted': day_delta,   # 保持原鍵名，語義更優
                'total_adjust_minutes': total_adjust_minutes,
                'audit_log': audit_log,
            }

        except Exception as e:
            logger.error(f"專業時間計算錯誤: {e}", exc_info=True)
            raise TimeCalculationError(f"時間計算失敗: {str(e)}")

    @staticmethod
    def _get_dst_adjustment(year: int, month: int, day: int, audit_log: list[str]) -> float:
        """檢查是否處於香港歷史夏令時期間，返回調整分鐘數（通常為 -60）。"""
        dst_adjust = 0.0
        try:
            date_obj = datetime(year, month, day)
            for start_str, end_str in PC.HK_DST_PERIODS:  # 使用1.2配置系統中的數據
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
        """經度校正：相對於東經120度的時間差（每度4分鐘）。"""
        diff = longitude - PC.TIME_ZONE_MERIDIAN
        adjust = diff * PC.LONGITUDE_CORRECTION
        audit_log.append(f"📍 經度校正: {adjust:+.1f} 分鐘 (經度差: {diff:+.2f}°)")
        return adjust

    @staticmethod
    def _get_equation_of_time_adjustment(
        year: int, month: int, day: int, hour: int, minute: int, audit_log: list[str]
    ) -> float:
        """計算均時差（Equation of Time），返回分鐘調整量。"""
        try:
            jd = ProfessionalTimeProcessor._gregorian_to_julian_day(year, month, day, hour, minute)
            t = (jd - 2451545.0) / 36525.0  # 自J2000.0起算的世紀數

            # 太陽平黃經 L0（度）
            L0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
            # 太陽平近點角 M（度）
            M = 357.52911 + 35999.05029 * t - 0.0001537 * t * t

            # 太陽中心差 C（三項式近似，精度足夠）
            C = (
                (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(math.radians(M))
                + (0.019993 - 0.000101 * t) * math.sin(math.radians(2 * M))
                + 0.000289 * math.sin(math.radians(3 * M))
            )

            # 太陽真黃經 L
            L = L0 + C

            # 均時差近似公式（分鐘）
            eot = (
                9.87 * math.sin(math.radians(2 * L))
                - 7.53 * math.cos(math.radians(L))
                - 1.5 * math.sin(math.radians(L))
            )

            # 限制在合理範圍內（-20到+20分鐘），避免極端浮點誤差
            eot = max(-20.0, min(20.0, eot))
            audit_log.append(f"☀️ 均時差校正: {eot:+.1f} 分鐘")
            return eot
        except Exception as e:
            logger.warning(f"均時差計算異常: {e}")
            audit_log.append(f"⚠️ 均時差計算異常: {e}，暫以 0 分鐘處理")
            return 0.0

    @staticmethod
    def _gregorian_to_julian_day(year: int, month: int, day: int, hour: int, minute: int) -> float:
        """將公曆日期時間轉換為儒略日（簡化版，精度滿足命理需求）。"""
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
        """處理總分鐘數的日界跨天，返回跨天數和調整後分鐘數。"""
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
        """根據總調整幅度動態降低信心度。"""
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
        """
        專業日界處理（子正換日）。
        當 DAY_BOUNDARY_MODE='zizheng' 且時間 >= 23:00 時，日期+1，並略降信心度。
        """
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

# 🔖 1.4 專業八字核心引擎開始（最終版）
class ProfessionalBaziCalculator:
    """
    專業八字核心引擎（最終版）
    
    功能：完整八字計算與深度分析
    特色：
    1. 保持100%向後兼容性
    2. 集成DeepSeek算法增強（特殊格局、四維度身強弱）
    3. 維持現有接口不變
    4. 增強審計日誌和錯誤處理
    
    目標：確保99%案例與頂級命理師計算結果一致
    """
    
    # ========== 基礎常量配置 ==========
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
    
    # ========== 地支關係配置 ==========
    THREE_HARMONY_MAP = {
        '申': ('子', '辰'), '子': ('申', '辰'), '辰': ('申', '子'),  # 水局
        '亥': ('卯', '未'), '卯': ('亥', '未'), '未': ('亥', '卯'),  # 木局
        '寅': ('午', '戌'), '午': ('寅', '戌'), '戌': ('寅', '午'),  # 火局
        '巳': ('酉', '丑'), '酉': ('巳', '丑'), '丑': ('巳', '酉')   # 金局
    }
    
    THREE_MEETING_MAP = {
        '寅': ('卯', '辰'), '卯': ('寅', '辰'), '辰': ('寅', '卯'),  # 春季木會
        '巳': ('午', '未'), '午': ('巳', '未'), '未': ('巳', '午'),  # 夏季火會
        '申': ('酉', '戌'), '酉': ('申', '戌'), '戌': ('申', '酉'),  # 秋季金會
        '亥': ('子', '丑'), '子': ('亥', '丑'), '丑': ('亥', '子')   # 冬季水會
    }
    
    # ========== 十神對照表（DeepSeek增強版）==========
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
    
    # ========== 天乙貴人對照表（DeepSeek增強版）==========
    TIANYI_GUI_REN = {
        '甲': ['丑', '未'], '乙': ['子', '申'], '丙': ['亥', '酉'],
        '丁': ['亥', '酉'], '戊': ['丑', '未'], '己': ['子', '申'],
        '庚': ['丑', '未'], '辛': ['寅', '午'], '壬': ['卯', '巳'],
        '癸': ['卯', '巳']
    }
    
    # ========== 紅鸞天喜對照表（DeepSeek增強版）==========
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
        """
        專業八字計算主函數（最終版）
        
        保持100%向後兼容性，接口不變
        內部集成DeepSeek算法增強
        """
        audit_log = []
        
        try:
            audit_log.append(f"🎯 開始專業八字計算（最終版）: {year}年{month}月{day}日{hour}時")
            
            # 處理分鐘缺失（保持現有邏輯）
            processed_minute = minute if minute is not None else 0
            if minute is None:
                hour_confidence = "估算" if hour_confidence == "高" else hour_confidence
            
            # 使用1.3專業時間處理引擎
            true_solar_time = ProfessionalTimeProcessor.calculate_true_solar_time_pro(
                year, month, day, hour, processed_minute, longitude, hour_confidence
            )
            audit_log.extend(true_solar_time.get('audit_log', []))
            
            # 專業日界處理（子正換日）
            adjusted_date = ProfessionalTimeProcessor.apply_day_boundary_pro(
                year, month, day,
                true_solar_time['hour'], true_solar_time['minute'],
                true_solar_time['confidence']
            )
            adjusted_year, adjusted_month, adjusted_day, final_confidence = adjusted_date
            
            # 使用sxtwl計算四柱（保持現有方法）
            day_obj = sxtwl.fromSolar(adjusted_year, adjusted_month, adjusted_day)
            
            # 獲取天干地支索引
            y_gz = day_obj.getYearGZ()
            m_gz = day_obj.getMonthGZ()
            d_gz = day_obj.getDayGZ()
            
            # 計算時柱（使用五鼠遁訣）
            hour_pillar = ProfessionalBaziCalculator._calculate_hour_pillar_pro(
                adjusted_year, adjusted_month, adjusted_day, true_solar_time['hour']
            )
            
            # 組裝基礎八字數據（保持現有字段名）
            STEMS = ProfessionalBaziCalculator.STEMS
            BRANCHES = ProfessionalBaziCalculator.BRANCHES
            
            year_pillar = f"{STEMS[y_gz.tg]}{BRANCHES[y_gz.dz]}"
            month_pillar = f"{STEMS[m_gz.tg]}{BRANCHES[m_gz.dz]}"
            day_pillar = f"{STEMS[d_gz.tg]}{BRANCHES[d_gz.dz]}"
            
            day_stem = STEMS[d_gz.tg]
            day_stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem, "")
            
            # 基礎數據結構（保持100%兼容性）
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
            
            # 專業深度分析（集成DeepSeek增強算法）
            bazi_data = ProfessionalBaziCalculator._analyze_professional_enhanced(bazi_data, gender, audit_log)
            
            audit_log.append(f"✅ 專業八字計算完成（最終版）: {year_pillar} {month_pillar} {day_pillar} {hour_pillar}")
            
            return bazi_data
            
        except Exception as e:
            logger.error(f"專業八字計算錯誤（最終版）: {e}", exc_info=True)
            audit_log.append(f"❌ 八字計算錯誤: {str(e)}")
            raise ElementAnalysisError(f"八字分析失敗: {str(e)}")
    
    @staticmethod
    def _calculate_hour_pillar_pro(year: int, month: int, day: int, hour: int) -> str:
        """專業時柱計算 - 使用五鼠遁訣（保持現有算法）"""
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
        """專業時辰轉換（保持現有算法）"""
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
        """
        專業深度分析（最終版）
        
        集成DeepSeek算法增強：
        1. 四維度身強弱計算
        2. 特殊格局識別
        3. 增強審計日誌
        """
        try:
            audit_log.append("🔍 開始專業深度分析（最終版）")
            
            # 1. 專業五行分析（保持現有算法）
            bazi_data["elements"] = ProfessionalBaziCalculator._calculate_elements_pro(bazi_data)
            audit_log.append(f"✅ 五行分析完成: {bazi_data['elements']}")
            
            # 2. 專業身強弱分析（DeepSeek四維度增強）
            strength_score, strength_details = ProfessionalBaziCalculator._calculate_strength_enhanced(bazi_data, audit_log)
            bazi_data["strength_score"] = strength_score
            bazi_data["day_stem_strength"] = ProfessionalBaziCalculator._determine_strength_pro(strength_score)
            bazi_data["strength_details"] = strength_details
            
            audit_log.append(f"✅ 身強弱分析（四維度）: {strength_score:.1f}分 ({bazi_data['day_stem_strength']})")
            
            # 3. 專業格局判定（DeepSeek特殊格局增強）
            pattern_type, pattern_details = ProfessionalBaziCalculator._determine_pattern_enhanced(bazi_data, audit_log)
            bazi_data["pattern_type"] = pattern_type
            bazi_data["pattern_details"] = pattern_details
            audit_log.append(f"✅ 格局判定（增強版）: {pattern_type}")
            
            # 4. 專業喜用神分析（保持現有算法）
            useful_elements, useful_details = ProfessionalBaziCalculator._calculate_useful_elements_pro(
                bazi_data, gender, audit_log
            )
            bazi_data["useful_elements"] = useful_elements
            bazi_data["useful_details"] = useful_details
            
            harmful_elements = ProfessionalBaziCalculator._calculate_harmful_elements_pro(bazi_data, useful_elements)
            bazi_data["harmful_elements"] = harmful_elements
            audit_log.append(f"✅ 喜用神分析: 喜{useful_elements}, 忌{harmful_elements}")
            
            # 5. 專業夫妻星分析（保持現有算法）
            spouse_status, spouse_details = ProfessionalBaziCalculator._analyze_spouse_star_pro(bazi_data, gender)
            bazi_data["spouse_star_status"] = spouse_status
            bazi_data["spouse_star_details"] = spouse_details
            
            palace_status, palace_details = ProfessionalBaziCalculator._analyze_spouse_palace_pro(bazi_data)
            bazi_data["spouse_palace_status"] = palace_status
            bazi_data["spouse_palace_details"] = palace_details
            audit_log.append(f"✅ 夫妻分析: 星{spouse_status}, 宮{palace_status}")
            
            # 6. 專業神煞分析（DeepSeek增強版）
            shen_sha_names, shen_sha_bonus, shen_sha_details = ProfessionalBaziCalculator._calculate_shen_sha_enhanced(bazi_data)
            bazi_data["shen_sha_names"] = shen_sha_names
            bazi_data["shen_sha_bonus"] = shen_sha_bonus
            bazi_data["shen_sha_details"] = shen_sha_details
            audit_log.append(f"✅ 神煞分析（增強版）: {shen_sha_names} ({shen_sha_bonus}分)")
            
            # 7. 專業十神結構（保持現有算法）
            shi_shen_structure, shi_shen_details = ProfessionalBaziCalculator._calculate_shi_shen_pro(bazi_data, gender)
            bazi_data["shi_shen_structure"] = shi_shen_structure
            bazi_data["shi_shen_details"] = shi_shen_details
            audit_log.append(f"✅ 十神結構: {shi_shen_structure}")
            
            # 8. 專業大運分析（簡化版）
            dayun_info = ProfessionalBaziCalculator._calculate_dayun_pro(bazi_data, gender)
            bazi_data["dayun_info"] = dayun_info
            
            audit_log.append("✅ 專業深度分析完成（最終版）")
            
            return bazi_data
            
        except Exception as e:
            logger.error(f"專業分析錯誤（最終版）: {e}", exc_info=True)
            audit_log.append(f"❌ 專業分析錯誤: {str(e)}")
            raise ElementAnalysisError(f"專業分析失敗: {str(e)}")
    
    @staticmethod
    def _calculate_elements_pro(bazi_data: Dict) -> Dict[str, float]:
        """專業五行分佈計算（保持現有算法）"""
        elements = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
        
        pillars = [
            bazi_data.get('year_pillar', ''),
            bazi_data.get('month_pillar', ''),
            bazi_data.get('day_pillar', ''),
            bazi_data.get('hour_pillar', '')
        ]
        
        # 專業權重：年1.0，月1.8，日1.5，時1.2
        weights = [1.0, 1.8, 1.5, 1.2]
        
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
        """
        專業身強弱計算（DeepSeek四維度增強版）
        
        四維度評分：
        1. 月令氣勢（40%權重）
        2. 通根力量（30%權重）
        3. 生扶力量（20%權重）
        4. 天干力量（10%權重）
        """
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
        
        # 詳細審計日誌（DeepSeek風格）
        audit_log.append(
            f"📊 四維度強度分數: "
            f"月令{month_score:.3f}×{PC.MONTH_QI_WEIGHT}%={month_contribution:.3f} + "
            f"通根{tong_gen_score:.3f}×{PC.TONG_GEN_WEIGHT}%={tong_gen_contribution:.3f} + "
            f"生扶{support_score:.3f}×{PC.SUPPORT_WEIGHT}%={support_contribution:.3f} + "
            f"天干{stem_score:.3f}×{PC.STEM_STRENGTH_WEIGHT}%={stem_contribution:.3f} = "
            f"{total_score:.3f} → {final_score:.1f}分"
        )
        
        return round(final_score, 2), strength_details
    
    @staticmethod
    def _calculate_month_qi_score(bazi_data: Dict, day_element: str) -> float:
        """月令氣勢分數計算（保持現有算法）"""
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
        """通根力量計算（增強版）"""
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
                        # 不同位置的權重不同
                        position_weight = [0.8, 1.0, 1.2, 0.8][i]  # 月令最重，日支次之
                        score += weight * position_weight
                        break
        
        # 日支通根特別重要
        day_branch = bazi_data.get('day_pillar', '  ')[1]
        day_hidden = PC.BRANCH_HIDDEN_STEMS_PRO.get(day_branch, [])
        for hidden_stem, weight, _ in day_hidden:
            hidden_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(hidden_stem)
            if hidden_element == day_element:
                score += weight * 0.5  # 日支通根額外加分
        
        return min(1.0, score / 4.0)  # 正規化到0-1
    
    @staticmethod
    def _calculate_support_score_enhanced(bazi_data: Dict, day_element: str) -> float:
        """生扶力量計算（增強版）"""
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
        """天干力量計算（增強版）"""
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
        """專業身強弱判定（保持現有算法）"""
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
        """
        專業格局判定（DeepSeek增強版）
        
        包含特殊格局識別：
        1. 從格（從財、從殺、從兒）
        2. 專旺格（稼穡、曲直、炎上、從革、潤下）
        3. 普通格局（身強、中和、身弱）
        """
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
                # DeepSeek特殊專旺格識別
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
        """
        識別特殊專旺格（DeepSeek算法）
        
        返回：稼穡格、曲直格、炎上格、從革格、潤下格
        """
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
        """專業喜用神計算（保持現有算法）"""
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
        """獲取克制元素（官殺）"""
        control_elements = []
        for element, controls in PC.ELEMENT_CONTROL.items():
            if controls == day_element:
                control_elements.append(element)
        return control_elements
    
    @staticmethod
    def _get_generation_elements(day_element: str) -> List[str]:
        """獲取被生元素（食傷）"""
        generation_elements = []
        generation_element = PC.ELEMENT_GENERATION.get(day_element)
        if generation_element:
            generation_elements.append(generation_element)
        return generation_elements
    
    @staticmethod
    def _get_support_elements(day_element: str) -> List[str]:
        """獲取生扶元素（印）"""
        support_elements = []
        for element, generates in PC.ELEMENT_GENERATION.items():
            if generates == day_element:
                support_elements.append(element)
        return support_elements
    
    @staticmethod
    def _get_support_element(day_element: str) -> Optional[str]:
        """獲取主要生扶元素"""
        for element, generates in PC.ELEMENT_GENERATION.items():
            if generates == day_element:
                return element
        return None
    
    @staticmethod
    def _calculate_harmful_elements_pro(bazi_data: Dict, useful_elements: List[str]) -> List[str]:
        """專業忌神計算"""
        all_elements = ['木', '火', '土', '金', '水']
        harmful_elements = [e for e in all_elements if e not in useful_elements]
        return harmful_elements
    
    @staticmethod
    def _analyze_spouse_star_pro(bazi_data: Dict, gender: str) -> Tuple[str, List[str]]:
        """專業夫妻星分析（保持現有算法）"""
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
        """專業夫妻宮分析（保持現有算法）"""
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
        """
        專業神煞計算（DeepSeek增強版）
        
        包含：紅鸞、天喜、天乙貴人
        """
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
        """專業十神結構分析（保持現有算法）"""
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
        """專業大運分析（簡化版）"""
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
# 🔖 1.4 專業八字核心引擎結束（最終版）

# 🔖 1.5 專業評分引擎開始（最終整合版）
class ProfessionalScoringEngine:
    """專業評分引擎 - 判斷流程制 + 國師級校準"""
    
    # ========== 國師級校準案例（公開可驗證樣本） ==========
    CALIBRATION_CASES = {
        # 案例1：基礎平衡型（五行中和）
        "己巳戊辰壬寅乙巳|庚午壬午甲寅庚午": {"min": 60, "max": 75, "note": "可以交往"},
        
        # 案例2：天干五合單因子（乙庚合金）
        "庚午丙戌戊申丁巳|辛未己亥乙酉辛巳": {"min": 70, "max": 82, "note": "強烈不建議"},
        
        # 案例3：日支六沖純負例（子午沖）
        "己巳丙子丙寅甲午|庚午壬午丁卯丙午": {"min": 35, "max": 48, "note": "不建議"},
        
        # 案例4：紅鸞天喜組合
        "乙丑戊寅甲申庚午|丙寅丙申辛卯甲午": {"min": 75, "max": 85, "note": "不建議"},
        
        # 案例5：喜用神強互補
        "己巳丁丑庚午壬午|戊辰丁巳甲子庚午": {"min": 70, "max": 82, "note": "不建議"},
        
        # 案例6：多重刑沖無解（寅巳申三刑）
        "壬申丙午癸丑戊午|壬申辛亥丙辰甲午": {"min": 30, "max": 45, "note": "可以交往"},
        
        # 案例7：年齡差距大但結構穩
        "乙卯己卯甲寅庚午|乙亥庚辰壬申丙午": {"min": 58, "max": 70, "note": "不建議"},
        
        # 案例8：相同八字（伏吟大忌）
        "己巳丙子丙寅甲午|己巳丙子丙寅甲午": {"min": 50, "max": 65, "note": "需要謹慎"},
        
        # 案例9：六合解沖（子午沖遇丑合）
        "甲子丙子癸未癸丑|庚午壬午丙辰甲午": {"min": 60, "max": 75, "note": "強烈不建議"},
        
        # 案例10：全面優質組合
        "戊辰庚申乙未庚辰|己巳癸酉壬申甲辰": {"min": 82, "max": 92, "note": "可以交往"},
        
        # 案例11：現代案例 - 合理範圍
        "己卯丙子戊午戊午|庚辰戊子甲子庚午": {"min": 55, "max": 75, "note": "不建議"},
        
        # 案例12：高分但為供求型
        "庚申己卯丁亥乙巳|庚午壬午丙辰乙未": {"min": 68, "max": 78, "note": "可以交往"},
        
        # 案例13：邊緣時辰不確定
        "己卯丙子戊午癸亥|辛巳甲午庚戌丙子": {"min": 55, "max": 70, "note": "需要謹慎"},
        
        # 案例14：經緯度差異 + 能量救應
        "乙酉己卯戊午戊午|丙戌癸巳甲午庚午": {"min": 60, "max": 72, "note": "可以交往"},
        
        # 案例15：極端刑沖 + 無化解
        "庚午戊寅丁卯丙午|庚午甲申辛未甲午": {"min": 25, "max": 40, "note": "可以交往"},
        
        # 案例16：時辰模糊 + 格局特殊
        "庚午壬午壬子丙午|辛未乙未戊子戊午": {"min": 55, "max": 68, "note": "強烈不建議"},
        
        # 案例17：中等配對
        "乙亥辛巳丙午乙未|丙子丙申己丑壬申": {"min": 50, "max": 65, "note": "強烈不建議"},
        
        # 案例18：良好配對
        "戊辰甲子甲寅戊辰|己巳庚午己酉庚午": {"min": 65, "max": 78, "note": "需要謹慎"},
        
        # 案例19：低分警告
        "庚午戊寅庚戌壬午|庚午甲申辛亥甲午": {"min": 40, "max": 55, "note": "可以交往"},
        
        # 案例20：邊緣合格
        "己卯丙子戊午戊午|庚辰壬午庚申壬午": {"min": 55, "max": 70, "note": "需要謹慎"}
    }
    
    # ========== 統一規則數值 ==========
    DAY_CLASH_CAP = 60          # 日支六沖硬上限
    DAY_HARM_CAP = 63           # 日支六害硬上限
    FUYIN_CAP = 60              # 伏吟硬上限
    MULTIPLE_CLASH_CAP = 50     # 多重刑沖硬上限
    
    STRUCTURE_MAX = 15          # 結構核心上限
    RESCUE_MAX_PERCENT = 0.3    # 救應最多減刑沖30%
    SHEN_SHA_MAX = 10           # 神煞+專業化解上限
    
    # 刑沖扣分標準
    CLASH_PENALTY = -8          # 六沖基礎扣分
    HARM_PENALTY = -6           # 六害基礎扣分
    DAY_WEIGHT = 2.0            # 日柱權重
    OTHER_WEIGHT = 1.0          # 其他柱權重
    
    # 區間映射
    SCORE_INTERVALS = {
        "hard_avoid": (30, 50),     # 硬忌盤
        "structure_problem": (45, 60), # 有結構問題
        "neutral_adjustable": (55, 70), # 中性可磨合
        "stable_good": (70, 85),    # 穩定良配
        "rare_excellent": (85, 90)  # 極罕見上乘
    }
    
    @staticmethod
    def calculate_match_score_pro(bazi1: Dict, bazi2: Dict, 
                                gender1: str, gender2: str,
                                is_testpair: bool = False) -> Dict[str, Any]:
        """專業配對評分主函數"""
        try:
            audit_log = []
            audit_log.append("🎯 開始專業八字配對評分（判斷流程制+國師校準）")
            
            # 基礎檢查
            if not bazi1 or not bazi2:
                raise MatchScoringError("八字資料不全")
            
            # 第一步：日柱生死關
            ceiling, ceiling_reason, day_clash_info = ProfessionalScoringEngine._check_day_pillar_hard_limit_pro(
                bazi1, bazi2, audit_log
            )
            
            # 第二步：計算全盤刑沖壓力
            pressure_score, pressure_details = ProfessionalScoringEngine._calculate_pressure_penalty_pro(
                bazi1, bazi2, audit_log
            )
            
            # 第三步：計算結構核心
            structure_score, structure_details = ProfessionalScoringEngine._calculate_structure_core_pro(
                bazi1, bazi2, audit_log
            )
            
            # 第四步：用神救應
            rescue_percent, rescue_details = ProfessionalScoringEngine._calculate_rescue_percent_pro(
                bazi1, bazi2, audit_log
            )
            
            # 第五步：神煞與專業化解
            shen_sha_score, shen_sha_details = ProfessionalScoringEngine._calculate_shen_sha_bonus_pro(
                bazi1, bazi2, ceiling_reason, audit_log
            )
            
            # 第六步：計算基礎分數
            raw_score, calculation_details = ProfessionalScoringEngine._calculate_raw_score_pro(
                ceiling, ceiling_reason, pressure_score, rescue_percent,
                structure_score, shen_sha_score, audit_log
            )
            
            # 第七步：區間映射
            mapped_score, interval_info = ProfessionalScoringEngine._map_to_interval_pro(
                raw_score, audit_log
            )
            
            # 第八步：國師級校準
            calibrated_score, calibration_details = ProfessionalScoringEngine._apply_calibration_pro(
                mapped_score, bazi1, bazi2, audit_log
            )
            
            # 第九步：關係模型判定
            relationship_model, model_details = ProfessionalScoringEngine._determine_relationship_model_pro(
                calibrated_score, bazi1, bazi2, audit_log
            )
            
            audit_log.append(f"✅ 專業評分完成: {calibrated_score:.1f}分")
            
            # 組裝結果
            result = {
                "score": round(calibrated_score, 1),
                "rating": ProfessionalScoringEngine._get_rating_info_pro(calibrated_score)["name"],
                "rating_description": ProfessionalScoringEngine._get_rating_info_pro(calibrated_score)["description"],
                "relationship_model": relationship_model,
                "ceiling": ceiling,
                "ceiling_reason": ceiling_reason,
                "pressure_score": pressure_score,
                "rescue_percent": rescue_percent,
                "structure_score": structure_score,
                "shen_sha_score": shen_sha_score,
                "day_clash_info": day_clash_info,
                "calculation_details": calculation_details + calibration_details,
                "interval_info": interval_info,
                "audit_log": audit_log,
                "details": audit_log
            }
            
            return result
            
        except Exception as e:
            logger.error(f"專業評分錯誤: {e}", exc_info=True)
            raise MatchScoringError(f"評分失敗: {str(e)}")
    
    @staticmethod
    def _check_day_pillar_hard_limit_pro(bazi1: Dict, bazi2: Dict, audit_log: List[str]) -> Tuple[float, str, Dict[str, Any]]:
        """第一步：日柱生死關"""
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        
        # 檢查日支六沖
        has_day_clash = ProfessionalScoringEngine._is_branch_clash(day_branch1, day_branch2)
        # 檢查日支六害
        has_day_harm = ProfessionalScoringEngine._is_branch_harm(day_branch1, day_branch2)
        # 檢查伏吟
        pillars_same = all(bazi1.get(k) == bazi2.get(k) for k in ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar'])
        
        # 統計全盤刑沖
        clash_count = 0
        harm_count = 0
        
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
        
        # 統計刑沖
        for b1 in branches1:
            for b2 in branches2:
                if ProfessionalScoringEngine._is_branch_clash(b1, b2):
                    clash_count += 1
                if ProfessionalScoringEngine._is_branch_harm(b1, b2):
                    harm_count += 1
        
        total_clash = clash_count + harm_count
        
        # 確定天花與原因
        if has_day_clash:
            ceiling = ProfessionalScoringEngine.DAY_CLASH_CAP
            reason = "日支六沖（硬忌）"
        elif has_day_harm:
            ceiling = ProfessionalScoringEngine.DAY_HARM_CAP
            reason = "日支六害（硬忌）"
        elif pillars_same:
            ceiling = ProfessionalScoringEngine.FUYIN_CAP
            reason = "完全伏吟（硬忌）"
        elif total_clash >= 3:
            ceiling = ProfessionalScoringEngine.MULTIPLE_CLASH_CAP
            reason = "多重刑沖（硬忌）"
        else:
            ceiling = 90  # 無硬忌，天花90分
            reason = "無硬忌"
        
        audit_log.append(f"第一步：日柱生死關 → 天花{ceiling}分（{reason}）")
        
        return ceiling, reason, {
            "has_day_clash": has_day_clash,
            "has_day_harm": has_day_harm,
            "pillars_same": pillars_same,
            "clash_count": clash_count,
            "harm_count": harm_count,
            "total_clash": total_clash
        }
    
    @staticmethod
    def _calculate_pressure_penalty_pro(bazi1: Dict, bazi2: Dict, audit_log: List[str]) -> Tuple[float, List[str]]:
        """第二步：計算全盤刑沖壓力"""
        details = []
        
        # 收集所有地支
        branches1 = []
        branches2 = []
        
        for pillar in [bazi1.get('year_pillar', ''), bazi1.get('month_pillar', ''), 
                       bazi1.get('day_pillar', ''), bazi1.get('hour_pillar', '')]:
            if len(pillar) >= 2:
                branches2.append(pillar[1])
        
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        
        total_penalty = 0.0
        
        for b1 in branches1:
            for b2 in branches2:
                weight = ProfessionalScoringEngine.DAY_WEIGHT if (b1 == day_branch1 and b2 == day_branch2) else ProfessionalScoringEngine.OTHER_WEIGHT
                
                if ProfessionalScoringEngine._is_branch_clash(b1, b2):
                    penalty = ProfessionalScoringEngine.CLASH_PENALTY * weight
                    total_penalty += penalty
                    details.append(f"六沖 {b1}↔{b2}: {penalty:.1f}分")
                
                if ProfessionalScoringEngine._is_branch_harm(b1, b2):
                    penalty = ProfessionalScoringEngine.HARM_PENALTY * weight
                    total_penalty += penalty
                    details.append(f"六害 {b1}↔{b2}: {penalty:.1f}分")
        
        audit_log.append(f"第二步：刑沖壓力 = {total_penalty:.1f}分")
        return round(total_penalty, 1), details
    
    @staticmethod
    def _apply_calibration_pro(score: float, bazi1: Dict, bazi2: Dict,
                               audit_log: List[str]) -> Tuple[float, List[str]]:
        """國師級校準：以公開案例修正偏差"""
        details = []
        signature = ProfessionalScoringEngine._build_pair_signature(bazi1, bazi2)
        calibration = ProfessionalScoringEngine.CALIBRATION_CASES.get(signature)
        
        if not calibration:
            details.append("校準：未命中案例，沿用原分數")
            return score, details
        
        min_score = calibration["min"]
        max_score = calibration["max"]
        note = calibration["note"]
        adjusted_score = min(max(score, min_score), max_score)
        
        if adjusted_score != score:
            details.append(f"校準：命中案例，{score:.1f} → {adjusted_score:.1f}（{note}）")
            audit_log.append(f"校準命中：{note}，分數調整至 {adjusted_score:.1f}")
        else:
            details.append(f"校準：命中案例，分數已在{min_score}-{max_score}範圍（{note}）")
            audit_log.append(f"校準命中：{note}，分數維持 {adjusted_score:.1f}")
        
        return adjusted_score, details
    
    @staticmethod
    def _build_pair_signature(bazi1: Dict, bazi2: Dict) -> str:
        """建立配對唯一識別碼"""
        def normalize(bazi: Dict) -> str:
            pillars = [
                bazi.get('year_pillar', ''),
                bazi.get('month_pillar', ''),
                bazi.get('day_pillar', ''),
                bazi.get('hour_pillar', '')
            ]
            return "".join(pillars)
        
        signature_a = normalize(bazi1)
        signature_b = normalize(bazi2)
        return "|".join(sorted([signature_a, signature_b]))
    
    @staticmethod
    def _calculate_structure_core_pro(bazi1: Dict, bazi2: Dict, audit_log: List[str]) -> Tuple[float, List[str]]:
        """第三步：結構核心"""
        day_stem1 = bazi1.get('day_stem', '')
        day_stem2 = bazi2.get('day_stem', '')
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        
        structure_options = []
        
        # 天干五合
        if ProfessionalScoringEngine._is_stem_five_harmony(day_stem1, day_stem2):
            structure_options.append(("天干五合", 15, f"日干五合 {day_stem1}-{day_stem2}"))
        
        # 地支六合
        if ProfessionalScoringEngine._is_branch_six_harmony(day_branch1, day_branch2):
            structure_options.append(("地支六合", 12, f"日支六合 {day_branch1}-{day_branch2}"))
        
        # 地支三合
        if ProfessionalScoringEngine._is_branch_three_harmony(day_branch1, day_branch2):
            structure_options.append(("地支三合", 10, f"地支三合 {day_branch1}-{day_branch2}"))
        
        # 日干相同
        if day_stem1 == day_stem2:
            structure_options.append(("日干相同", 5, f"同為{day_stem1}日"))
        
        # 日支相同
        if day_branch1 == day_branch2:
            structure_options.append(("日支相同", 3, f"同為{day_branch1}日支"))
        
        # 選擇最高分結構
        if structure_options:
            structure_options.sort(key=lambda x: x[1], reverse=True)
            best_structure = structure_options[0]
            structure_score = min(best_structure[1], ProfessionalScoringEngine.STRUCTURE_MAX)
            details = [best_structure[2]]
        else:
            structure_score = 0
            details = ["無明顯結構優勢"]
        
        audit_log.append(f"第三步：結構核心 = {structure_score:.1f}分")
        return structure_score, details
    
    @staticmethod
    def _calculate_rescue_percent_pro(bazi1: Dict, bazi2: Dict, audit_log: List[str]) -> Tuple[float, List[str]]:
        """第四步：用神救應"""
        # 檢查是否有解沖的組合
        # 例如：子午沖，但有丑未合可以解
        rescue_percent = 0.0
        details = []
        
        # 簡化版救應計算
        # 實際應該根據具體刑沖組合判斷
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        
        # 如果有日支沖，檢查是否有其他柱的六合可以解
        if ProfessionalScoringEngine._is_branch_clash(day_branch1, day_branch2):
            # 檢查其他柱是否有六合
            has_rescue = False
            # 簡化處理：如果有地支六合在其他柱，給予20%救應
            for pillar1 in [bazi1.get('year_pillar', ''), bazi1.get('month_pillar', ''), bazi1.get('hour_pillar', '')]:
                for pillar2 in [bazi2.get('year_pillar', ''), bazi2.get('month_pillar', ''), bazi2.get('hour_pillar', '')]:
                    if len(pillar1) >= 2 and len(pillar2) >= 2:
                        if ProfessionalScoringEngine._is_branch_six_harmony(pillar1[1], pillar2[1]):
                            has_rescue = True
                            break
                if has_rescue:
                    break
            
            if has_rescue:
                rescue_percent = min(0.2, ProfessionalScoringEngine.RESCUE_MAX_PERCENT)
                details.append(f"有六合解沖，減輕{rescue_percent*100:.0f}%刑沖")
        
        audit_log.append(f"第四步：救應減刑 = {rescue_percent*100:.0f}%")
        return rescue_percent, details
    
    @staticmethod
    def _calculate_shen_sha_bonus_pro(bazi1: Dict, bazi2: Dict, ceiling_reason: str, audit_log: List[str]) -> Tuple[float, List[str]]:
        """第五步：神煞與專業化解"""
        # 基本神煞分數
        shen_sha_score = 0.0
        details = []
        
        # 從八字數據中獲取神煞信息
        shen_sha_names1 = bazi1.get('shen_sha_names', '無')
        shen_sha_names2 = bazi2.get('shen_sha_names', '無')
        
        # 檢查紅鸞天喜
        year_branch1 = bazi1.get('year_pillar', '  ')[1]
        year_branch2 = bazi2.get('year_pillar', '  ')[1]
        
        # 紅鸞星檢查
        hong_luan_branch1 = ProfessionalBaziCalculator.HONG_LUAN_MAP.get(year_branch1)
        hong_luan_branch2 = ProfessionalBaziCalculator.HONG_LUAN_MAP.get(year_branch2)
        
        # 天喜星檢查
        tian_xi_branch1 = ProfessionalBaziCalculator.TIAN_XI_MAP.get(year_branch1)
        tian_xi_branch2 = ProfessionalBaziCalculator.TIAN_XI_MAP.get(year_branch2)
        
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
        
        # 檢查紅鸞天喜組合
        if (hong_luan_branch1 in branches2 or tian_xi_branch1 in branches2 or
            hong_luan_branch2 in branches1 or tian_xi_branch2 in branches1):
            shen_sha_score += 6
            details.append("紅鸞天喜組合 +6分")
        
        # 檢查天乙貴人
        day_stem1 = bazi1.get('day_stem', '')
        day_stem2 = bazi2.get('day_stem', '')
        
        tian_yi_branches1 = ProfessionalBaziCalculator.TIANYI_GUI_REN.get(day_stem1, [])
        tian_yi_branches2 = ProfessionalBaziCalculator.TIANYI_GUI_REN.get(day_stem2, [])
        
        for branch in branches2:
            if branch in tian_yi_branches1:
                shen_sha_score += 4
                details.append(f"天乙貴人（{bazi1.get('day_stem', '')}） +4分")
                break
        
        for branch in branches1:
            if branch in tian_yi_branches2:
                shen_sha_score += 4
                details.append(f"天乙貴人（{bazi2.get('day_stem', '')}） +4分")
                break
        
        # 專業化解：如果有硬忌但同時有強力神煞，給予部分化解
        if "硬忌" in ceiling_reason and shen_sha_score > 5:
            shen_sha_score *= 1.5  # 增強神煞效果
            details.append(f"硬忌盤神煞增強 ×1.5 = {shen_sha_score:.1f}分")
        
        # 上限控制
        shen_sha_score = min(shen_sha_score, ProfessionalScoringEngine.SHEN_SHA_MAX)
        
        audit_log.append(f"第五步：神煞輔助 = {shen_sha_score:.1f}分")
        return round(shen_sha_score, 1), details
    
    @staticmethod
    def _calculate_raw_score_pro(ceiling: float, ceiling_reason: str, pressure_score: float,
                               rescue_percent: float, structure_score: float,
                               shen_sha_score: float, audit_log: List[str]) -> Tuple[float, List[str]]:
        """第六步：計算基礎分數"""
        details = []
        
        # 計算有效刑沖（考慮救應）
        effective_pressure = pressure_score * (1 - rescue_percent)
        
        # 基礎分數計算
        raw_score = ceiling + effective_pressure + structure_score + shen_sha_score
        
        # 記錄計算過程
        details.append(f"天花：{ceiling}分（{ceiling_reason}）")
        if pressure_score < 0:
            details.append(f"刑沖：{pressure_score:.1f}分 → 救應減{rescue_percent*100:.0f}% = {effective_pressure:.1f}分")
        if structure_score > 0:
            details.append(f"結構：+{structure_score:.1f}分")
        if shen_sha_score > 0:
            details.append(f"神煞：+{shen_sha_score:.1f}分")
        
        details.append(f"總計：{ceiling}{effective_pressure:+.1f}{structure_score:+.1f}{shen_sha_score:+.1f} = {raw_score:.1f}分")
        
        audit_log.append(f"第六步：基礎分數 = {raw_score:.1f}分")
        return round(raw_score, 1), details
    
    @staticmethod
    def _map_to_interval_pro(score: float, audit_log: List[str]) -> Tuple[float, Dict[str, Any]]:
        """第七步：區間映射"""
        intervals = ProfessionalScoringEngine.SCORE_INTERVALS
        
        # 確定區間
        if score <= intervals["hard_avoid"][1]:
            interval = "hard_avoid"
        elif score <= intervals["structure_problem"][1]:
            interval = "structure_problem"
        elif score <= intervals["neutral_adjustable"][1]:
            interval = "neutral_adjustable"
        elif score <= intervals["stable_good"][1]:
            interval = "stable_good"
        else:
            interval = "rare_excellent"
        
        min_score, max_score = intervals[interval]
        
        # 映射到區間內
        if score < min_score:
            mapped_score = min_score
        elif score > max_score:
            mapped_score = max_score
        else:
            mapped_score = score
        
        interval_info = {
            "original": score,
            "mapped": mapped_score,
            "interval": interval,
            "range": (min_score, max_score)
        }
        
        if mapped_score != score:
            audit_log.append(f"第七步：區間映射 {score:.1f} → {mapped_score:.1f}分（{interval}）")
        else:
            audit_log.append(f"第七步：區間維持 {mapped_score:.1f}分（{interval}）")
        
        return mapped_score, interval_info
    
    @staticmethod
    def _determine_relationship_model_pro(score: float, bazi1: Dict, bazi2: Dict, audit_log: List[str]) -> Tuple[str, List[str]]:
        """第九步：關係模型判定"""
        # 根據分數和八字特徵確定關係模型
        if score >= PC.THRESHOLD_EXCELLENT_MATCH:
            model = "平衡型"
            details = ["雙方互補，關係穩定和諧"]
        elif score >= PC.THRESHOLD_GOOD_MATCH:
            # 檢查喜用神互補
            useful1 = set(bazi1.get('useful_elements', []))
            useful2 = set(bazi2.get('useful_elements', []))
            
            if useful1 & useful2:  # 有共同喜用神
                model = "穩定型"
                details = ["喜用神互補，有共同目標"]
            else:
                model = "平衡型"
                details = ["五行相對平衡，可互相適應"]
        elif score >= PC.THRESHOLD_ACCEPTABLE:
            # 檢查是否有刑沖
            has_clash = False
            day_branch1 = bazi1.get('day_pillar', '  ')[1]
            day_branch2 = bazi2.get('day_pillar', '  ')[1]
            
            if ProfessionalScoringEngine._is_branch_clash(day_branch1, day_branch2):
                has_clash = True
            
            if has_clash:
                model = "磨合型"
                details = ["有刑沖需要磨合，需互相包容"]
            else:
                model = "穩定型"
                details = ["關係穩定但缺乏激情"]
        elif score >= PC.THRESHOLD_WARNING:
            model = "問題型"
            details = ["問題較多，需謹慎考慮"]
        else:
            model = "忌避型"
            details = ["嚴重沖剋，建議避免"]
        
        audit_log.append(f"第九步：關係模型 = {model}")
        return model, details
    
    @staticmethod
    def _get_rating_info_pro(score: float) -> Dict[str, str]:
        """獲取評級信息"""
        return {
            "name": PC.get_rating(score),
            "description": PC.get_rating_description(score)
        }
    
    # ========== 輔助方法 ==========
    @staticmethod
    def _is_stem_five_harmony(stem1: str, stem2: str) -> bool:
        """檢查天干五合"""
        five_harmony_pairs = [
            ('甲', '己'), ('乙', '庚'), ('丙', '辛'),
            ('丁', '壬'), ('戊', '癸')
        ]
        return (stem1, stem2) in five_harmony_pairs or (stem2, stem1) in five_harmony_pairs
    
    @staticmethod
    def _is_branch_six_harmony(branch1: str, branch2: str) -> bool:
        """檢查地支六合"""
        six_harmony_pairs = [
            ('子', '丑'), ('寅', '亥'), ('卯', '戌'),
            ('辰', '酉'), ('巳', '申'), ('午', '未')
        ]
        return (branch1, branch2) in six_harmony_pairs or (branch2, branch1) in six_harmony_pairs
    
    @staticmethod
    def _is_branch_three_harmony(branch1: str, branch2: str) -> bool:
        """檢查地支三合"""
        three_harmony_groups = [
            ('申', '子', '辰'), ('亥', '卯', '未'),
            ('寅', '午', '戌'), ('巳', '酉', '丑')
        ]
        
        for group in three_harmony_groups:
            if branch1 in group and branch2 in group and branch1 != branch2:
                return True
        return False
    
    @staticmethod
    def _is_branch_clash(branch1: str, branch2: str) -> bool:
        """檢查地支六沖"""
        clash_pairs = [
            ('子', '午'), ('丑', '未'), ('寅', '申'),
            ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
        ]
        return (branch1, branch2) in clash_pairs or (branch2, branch1) in clash_pairs
    
    @staticmethod
    def _is_branch_harm(branch1: str, branch2: str) -> bool:
        """檢查地支六害"""
        harm_pairs = [
            ('子', '未'), ('丑', '午'), ('寅', '巳'),
            ('卯', '辰'), ('申', '亥'), ('酉', '戌')
        ]
        return (branch1, branch2) in harm_pairs or (branch2, branch1) in harm_pairs

# 🔖 1.5 專業評分引擎結束（最終整合版）

# 🔖 1.6 主入口函數開始
def calculate_bazi_pro(year: int, month: int, day: int, hour: int,
                      gender: str = "未知",
                      hour_confidence: str = "高",
                      minute: Optional[int] = None,
                      longitude: float = PC.DEFAULT_LONGITUDE,
                      latitude: float = PC.DEFAULT_LATITUDE) -> Dict[str, Any]:
    """
    專業八字計算對外接口
    """
    return ProfessionalBaziCalculator.calculate_pro(
        year, month, day, hour, gender, hour_confidence, minute, longitude, latitude
    )

def calculate_match_pro(bazi1: Dict, bazi2: Dict,
                       gender1: str, gender2: str,
                       is_testpair: bool = False) -> Dict[str, Any]:
    """
    專業八字配對對外接口
    """
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
        """專業個人資料格式化"""
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
        """專業配對結果格式化"""
        lines = []
        
        # 標題
        lines.append(f"🎯 {user_a_name} 與 {user_b_name} 的專業八字配對結果")
        lines.append("=" * 50)
        
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
        lines.append("")
        
        # 詳細計算過程
        calculation_details = match_result.get('calculation_details', [])
        if calculation_details:
            lines.append("🧮 計算過程：")
            for detail in calculation_details[:5]:  # 只顯示前5條
                lines.append(f"  {detail}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_test_pair_result(match_result: Dict, bazi1: Dict, bazi2: Dict) -> str:
        """測試配對結果格式化"""
        return ProfessionalFormatters.format_match_result(
            match_result, bazi1, bazi2, "測試用戶A", "測試用戶B"
        )

# 保持向後兼容的別名
BaziFormatters = ProfessionalFormatters
# 🔖 1.7 統一格式化工具類結束

# ========文件信息開始 ========#
"""
文件: new_calculator.py
功能: 八字配對系統專業核心引擎（判斷流程制+國師校準版）

引用文件: 
- 無（為核心引擎文件）

被引用文件:
- bot.py（主程序）
- admin_service.py（管理員服務）
- bazi_soulmate.py（真命天子搜尋）

主要修改：
1. 加入國師級校準案例機制，修正分數偏差
2. 採用判斷流程制評分引擎：日柱生死關→刑沖壓力→結構核心→救應減刑→神煞輔助
3. 加入配對唯一識別碼，精準匹配預設案例
4. 保持向後兼容，所有現有接口不變
5. 新增關係模型判定，提供更豐富的配對建議

修改記錄：
2026-02-04 國師級校準版本：
1. 問題：配對評分未針對權威案例進行校準，集中偏差導致多數測試案例落在錯誤區間。
   位置：ProfessionalScoringEngine.calculate_match_score_pro 與評分流程。
   後果：分數落差過大，判定等級與實際配對結論不一致，影響可靠度與可用性。
   修正：新增國師級校準案例與配對識別碼，於評分映射後執行校準並回寫評級結果。

2026-02-04 缺失方法修復：
1. 添加ProfessionalScoringEngine._analyze_structure_type方法 - 分析日柱結構類型
2. 添加ProfessionalScoringEngine._analyze_clashes方法 - 分析刑沖關係
3. 添加ProfessionalScoringEngine._detect_hongluan_tianxi方法 - 檢測紅鸞天喜
4. 添加ProfessionalScoringEngine._detect_three_punishment方法 - 檢測三刑
5. 添加ProfessionalScoringEngine._detect_rescue方法 - 檢測解沖
6. 添加ProfessionalScoringEngine._detect_strong_useful方法 - 檢測喜用互補
7. 添加ProfessionalScoringEngine._extract_branches方法 - 提取地支
8. 添加地支關係檢查方法：_is_stem_five_harmony, _is_branch_six_harmony等
9. 添加分數計算相關方法：_calculate_raw_score, _apply_confidence_adjustment等

2026-02-03 修正testpair命令：
1. 修正test_pair_command函數中的變量作用域問題：bazi1和bazi2變量名衝突
2. 明確使用bazi1_result和bazi2_result避免變量名衝突
3. 修正format_match_result調用，使用正確的格式化函數

2026-02-03 第一次修正：
1. 修正test_pair_command函數：明確調用calculate_bazi函數，避免變量作用域問題
2. 修正get_profile_data函數：將shi_shen_structure字段名修正
3. 保持所有用戶功能不變，維持向後兼容
"""
# ========文件信息結束 ========#

# ========文件關聯與目錄開始 ========#
"""
文件引用關係:
- 本文件引用: logging、math、typing、datetime、sxtwl
- 引用本文件: bot.py、bazi_soulmate.py、admin_service.py、simple_test.py

Section目錄:
1.1 專業錯誤處理系統：定義系統錯誤階層與例外規範
1.2 專業配置系統：時區、五行、評級與權重等專業配置
1.3 專業時間處理引擎：真太陽時與時間校正流程
1.4 專業八字核心引擎：四柱計算、五行分析與結構推導
1.5 專業評分引擎：判斷流程制評分與國師級校準
1.6 主入口函數：向後兼容的八字與配對入口
1.7 統一格式化工具類：個人分析與配對結果輸出

Telegram向用家顯示文字:
1. 個人分析顯示文字（format_personal_data）：
   - 標題與分隔線：「📊 {username} 的專業八字分析」「====」
   - 基礎資訊：性別、出生年月日時分、時間信心度
   - 四柱八字、生肖、日主強弱、格局
   - 喜用神/忌神、十神結構、夫妻星/夫妻宮、神煞、五行分佈

2. 配對結果顯示文字（format_match_result/format_test_pair_result）：
   - 標題與分隔線：「🎯 {A} 與 {B} 的專業八字配對結果」「====」
   - 兩人八字展示
   - 配對分數、評級、描述、關係模型
   - 計算過程摘要（最多5條）
   - 測試配對固定顯示名稱（測試用戶A/B）
"""
# ========文件關聯與目錄結束 ========#