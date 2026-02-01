#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字配對系統核心 - 專業級八字計算與配對引擎
採用判斷引擎優先架構：時間→核心→評分→審計
"""

import logging
import math
import random
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import sxtwl

logger = logging.getLogger(__name__)

# 🔖 1.1 錯誤處理類開始 [行: 50-100]
class BaziCalculatorError(Exception):
    """八字計算錯誤"""
    pass

class ScoringEngineError(Exception):
    """評分引擎錯誤"""
    pass

class TimeProcessingError(Exception):
    """時間處理錯誤"""
    pass

class ValidationError(Exception):
    """數據驗證錯誤"""
    pass
# 🔖 1.1 錯誤處理類結束

# 🔖 1.2 配置常量類開始 [行: 110-600]
class Config:
    """配置常量集中管理類"""
    
    # 時間配置
    TIME_ZONE_MERIDIAN = 120.0  # 東經120度為標準時區
    DAY_BOUNDARY_MODE = 'zizheng'  # 子正換日 ('zizheng', 'zichu', 'none')
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
    
    # 月令氣勢表（餘氣/中氣/本氣）
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
    MONTH_WEIGHT = 35          # 月令權重
    TONG_GEN_WEIGHT = 25       # 通根權重
    SUPPORT_WEIGHT = 15        # 生扶權重
    STRENGTH_THRESHOLD_STRONG = 65  # 身強閾值
    STRENGTH_THRESHOLD_MEDIUM = 35  # 身中閾值
    DEFAULT_STRENGTH_SCORE = 50     # 默認身強弱分數
    
    # 陰陽天干
    YANG_STEMS = ['甲', '丙', '戊', '庚', '壬']  # 五陽從氣不從勢
    YIN_STEMS = ['乙', '丁', '己', '辛', '癸']   # 五陰從勢無情義
    
    # 墓庫地支
    TOMB_BRANCHES = {'木': '未', '火': '戌', '土': '戌', '金': '丑', '水': '辰'}
    
    # 評分系統配置 - 修正為合理標準
    BASE_SCORE = 65                      # 起始基準分
    REALITY_FLOOR = 45                   # 現實保底分
    TERMINATION_SCORE = 35               # 終止評級分
    STRONG_WARNING_FLOOR = 55            # 強烈警告下限
    
    # 評分閾值 - 修正為合理標準
    THRESHOLD_TERMINATION = 35           # 終止線
    THRESHOLD_STRONG_WARNING = 45        # 強烈警告線
    THRESHOLD_WARNING = 50               # 警告線
    THRESHOLD_CONTACT_ALLOWED = 55       # 可交換聯絡方式
    THRESHOLD_GOOD_MATCH = 60            # 良好婚配 (從70降低到60)
    THRESHOLD_EXCELLENT_MATCH = 70       # 上等婚配 (從75降低到70)
    THRESHOLD_PERFECT_MATCH = 85         # 極品婚配
    
    # 模組分數上限
    ENERGY_RESCUE_CAP = 25               # 能量救應上限
    PERSONALITY_RISK_CAP = -25           # 人格風險上限 (從-25調整)
    PRESSURE_PENALTY_CAP = -20           # 刑沖壓力上限 (從-30調整到-20)
    SHEN_SHA_BONUS_CAP = 12              # 神煞加持上限
    SHEN_SHA_FLOOR = 7                   # 神煞保底分
    RESOLUTION_BONUS_CAP = 10            # 專業化解上限
    TOTAL_PENALTY_CAP = -25              # 總扣分上限 (新增)
    
    # 能量救應配置
    WEAK_THRESHOLD = 10                  # 極弱閾值
    EXTREME_WEAK_BONUS = 15              # 極弱救應加分 (從12提升到15)
    DEMAND_MATCH_BONUS = 12              # 需求對接加分 (從8提升到12)
    RESCUE_DEDUCTION_RATIO = 0.3         # 救應抵銷比例
    
    # 結構核心配置 - 加強正向加分
    STEM_COMBINATION_FIVE_HARMONY = 15   # 五合 (從12提升到15)
    STEM_COMBINATION_GENERATION = 4      # 相生
    STEM_COMBINATION_SAME = 2            # 比和
    BRANCH_COMBINATION_SIX_HARMONY = 12  # 六合 (從10提升到12)
    BRANCH_COMBINATION_THREE_HARMONY = 10 # 三合加分
    
    # 刑沖壓力配置 - 修正為合理扣分
    BRANCH_CLASH_PENALTY = -12           # 六沖扣分 (從-18調整到-12)
    BRANCH_HARM_PENALTY = -10            # 六害扣分 (調整)
    DAY_CLASH_PENALTY = -15              # 日支六沖特別扣分 (從-20調整到-15)
    DAY_HARM_PENALTY = -12               # 日支六害特別扣分 (從-18調整到-12)
    
    PALACE_STABLE_BONUS = 4              # 穩定無沖
    PALACE_SLIGHT_BONUS = 1              # 輕微受壓
    PALACE_SEVERE_PENALTY = -8           # 嚴重受沖
    
    # 人格風險配置
    PERSONALITY_RISK_PATTERNS = {
        "傷官見官": -6,
        "羊刃坐財": -6,
        "半三刑": -6,
        "財星遇劫": -5,
        "官殺混雜": -5
    }
    PERSONALITY_STACKED_PENALTY = -12    # 疊加風險額外扣分
    
    HEXAGRAM_RESOLUTION_RATIO = 0.0      # 六合解沖係數
    TRIAD_RESOLUTION_RATIO = 0.5         # 三合化解係數 (新增: 50%化解)
    PASS_THROUGH_RESOLUTION_RATIO = 0.0  # 通關五行係數
    
    # 神煞系統配置
    SHEN_SHA_POSITIVE = {
        "hong_luan": 4,                  # 紅鸞
        "tian_xi": 3,                    # 天喜
        "tian_yi": 5,                    # 天乙貴人
        "tian_de": 2,                    # 天德
        "yue_de": 1,                     # 月德
        "wen_chang": 1,                  # 文昌
        "jiang_xing": 1                  # 將星
    }
    
    SHEN_SHA_NEGATIVE = {
        "yang_ren": -4,                  # 羊刃
        "jie_sha": -3,                   # 劫煞
        "wang_shen": -3,                 # 亡神
        "gu_chen": -3,                   # 孤辰
        "gua_su": -3,                    # 寡宿
        "yin_cha_yang_cuo": -4           # 陰差陽錯
    }
    
    # 專業化解配置
    RESOLUTION_PATTERNS = {
        "七殺+正印": 8,                  # 殺印相生
        "傷官+正財": 7,                  # 傷官生財
        "偏財+正官": 6,                  # 財官相生
        "食傷+正印": 5,                  # 食傷配印
        "財官+相生": 5                   # 財官組合
    }
    
    # 現實校準配置
    NO_HARD_PROBLEM_FLOOR = 45           # 無硬傷保底分
    DAY_CLASH_CAP = 45                   # 日支六沖上限
    AGE_GAP_PENALTY_11_15 = -5           # 11-15歲年齡差距扣分
    AGE_GAP_PENALTY_16_PLUS = -8         # 16歲以上年齡差距扣分
    FATAL_RISK_CAP = 35                  # 致命風險上限
    
    # 關係模型判定閾值
    BALANCED_MAX_DIFF = 12               # 平衡型最大差異
    SUPPLY_MIN_DIFF = 12                 # 供求型最小差異
    DEBT_MIN_DIFF = 20                   # 相欠型最小差異
    DEBT_MAX_AVG = 60                    # 相欠型最大平均分
    
    # 時間信心度映射
    TIME_CONFIDENCE_LEVELS = {
        'high': 0.95,                    # 精確到分鐘
        'medium': 0.90,                  # 精確到小時
        'low': 0.85,                     # 模糊描述
        'estimated': 0.80                # 系統估算
    }
    
    # 信心度文字映射
    CONFIDENCE_TEXT_MAP = {
        'high': '高',
        'medium': '中', 
        'low': '低',
        'estimated': '估算',
        '高': '高',
        '中': '中',
        '低': '低',
        '估算': '估算'
    }
    
    # 評級標準
    RATING_SCALE = [
        (THRESHOLD_PERFECT_MATCH, "🌟 萬中無一", "極品組合，互相成就"),
        (THRESHOLD_EXCELLENT_MATCH, "✨ 上等婚配", "明顯互補，幸福率高"),
        (THRESHOLD_GOOD_MATCH, "✅ 主流成功", "現實高成功率，可經營"),
        (THRESHOLD_CONTACT_ALLOWED, "🤝 普通可行", "有缺點但可努力經營"),
        (THRESHOLD_WARNING, "⚠️ 需要努力", "問題較多，需謹慎考慮"),
        (THRESHOLD_STRONG_WARNING, "🔴 不建議", "沖剋嚴重，難長久"),
        (THRESHOLD_TERMINATION, "🔴 不建議（接近終止）", "嚴重沖剋，極難長久"),
        (0, "❌ 強烈不建議", "硬傷明顯，易生變")
    ]
    
    @classmethod
    def get_rating(cls, score: float) -> str:
        """根據分數獲取評級"""
        for threshold, name, _ in cls.RATING_SCALE:
            if score >= threshold:
                return name
        return "❌ 強烈不建議"
    
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
        return cls.CONFIDENCE_TEXT_MAP.get(confidence, confidence)
    
    # 八字大師配置
    @classmethod
    def get_master_bazi_config(cls):
        """獲取大師配置"""
        return {
            "SCORING_SYSTEM": {
                "THRESHOLDS": {
                    "contact_allowed": cls.THRESHOLD_CONTACT_ALLOWED,
                    "good_match": cls.THRESHOLD_GOOD_MATCH,
                    "excellent_match": cls.THRESHOLD_EXCELLENT_MATCH,
                    "perfect_match": cls.THRESHOLD_PERFECT_MATCH
                },
                "BASE_SCORE": cls.BASE_SCORE,
                "REALITY_FLOOR": cls.REALITY_FLOOR
            },
            "MATCH_LOGIC": {
                "MIN_CANDIDATES": 3,
                "MAX_CANDIDATES": 10,
                "SCORE_GAP_THRESHOLD": 5,
                "EXCLUDE_PREVIOUS_DAYS": 30
            }
        }

    @classmethod
    def get_confidence_factor(cls, confidence_str: str) -> float:
        """獲取信心度因子"""
        confidence_map = {
            'high': '高', '高': 'high',
            'medium': '中', '中': 'medium',
            'low': '低', '低': 'low',
            'estimated': '估算', '估算': 'estimated'
        }
        
        # 轉換為英文
        english_confidence = confidence_map.get(confidence_str, confidence_str)
        if english_confidence in ['高', 'high']:
            return cls.TIME_CONFIDENCE_LEVELS['high']
        elif english_confidence in ['中', 'medium']:
            return cls.TIME_CONFIDENCE_LEVELS['medium']
        elif english_confidence in ['低', 'low']:
            return cls.TIME_CONFIDENCE_LEVELS['low']
        else:
            return cls.TIME_CONFIDENCE_LEVELS['estimated']

# 創建配置實例方便使用
C = Config
# 🔖 1.2 配置常量類結束

# 🔖 1.3 時間處理引擎開始 [行: 610-850]
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
        """計算均時差 (Equation of Time) - 高階算法"""
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
            jd = day_obj.jd + (hour + minute/60.0)/24.0
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
            new_confidence = "medium" if confidence == "high" else "low"
            audit_log.append(f"置信度調整: {confidence} → {new_confidence}")
        else:
            new_confidence = confidence
        
        return {
            'hour': true_hour,
            'minute': true_minute,
            'confidence': new_confidence,
            'adjusted': abs(total_adjust) > 1,
            'day_adjusted': day_adjusted,
            'total_adjust_minutes': total_adjust,
            'dst_adjust': dst_adjust,
            'longitude_adjust': longitude_adjust,
            'eot_adjust': eot_adjust,
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
                new_confidence = "medium" if confidence == "high" else confidence
                audit_log.append(f"日界調整: {year}-{month}-{day} {hour}:{minute} → {next_date.year}-{next_date.month}-{next_date.day} 00:00")
                return (next_date.year, next_date.month, next_date.day, new_confidence)
        
        return (year, month, day, confidence)
    
    @staticmethod
    def handle_missing_minute(hour: int, minute: Optional[int], confidence: str) -> Tuple[int, str]:
        """處理分鐘缺失"""
        if minute is None:
            use_minute = C.MISSING_MINUTE_HANDLING
            confidence_map = {
                "high": "medium",
                "medium": "low", 
                "low": "estimated",
                "unknown": "estimated",
                "estimated": "estimated"
            }
            new_confidence = confidence_map.get(confidence, "estimated")
            audit_log.append(f"分鐘缺失處理: 使用{use_minute}分，置信度{confidence}→{new_confidence}")
            return use_minute, new_confidence
        return minute, confidence
    
    @staticmethod
    def estimate_hour_from_description(description: str) -> Tuple[int, str]:
        """從描述估算時辰"""
        description = description.lower()
        
        time_map = [
            (['深夜', '半夜', '子夜', '凌晨前', '0點', '24點'], 0, 'medium'),
            (['凌晨', '丑時', '雞鳴', '1點', '2點'], 2, 'medium'),
            (['清晨', '黎明', '寅時', '平旦', '3點', '4點'], 4, 'medium'),
            (['早晨', '日出', '卯時', '早上', '5點', '6點'], 6, 'medium'),
            (['上午', '辰時', '食時', '7點', '8點'], 8, 'medium'),
            (['上午', '巳時', '隅中', '9點', '10點'], 10, 'medium'),
            (['中午', '正午', '午時', '日中', '11點', '12點'], 12, 'high'),
            (['下午', '未時', '日昳', '13點', '14點'], 14, 'medium'),
            (['下午', '申時', '晡時', '15點', '16點'], 16, 'medium'),
            (['傍晚', '酉時', '日入', '黃昏', '17點', '18點'], 18, 'medium'),
            (['晚上', '戌時', '黃昏', '日暮', '19點', '20點'], 20, 'medium'),
            (['晚上', '亥時', '人定', '夜晚', '21點', '22點'], 22, 'medium')
        ]
        
        for keywords, hour, confidence in time_map:
            if any(keyword in description for keyword in keywords):
                return hour, confidence
        
        return 12, 'low'
# 🔖 1.3 時間處理引擎結束

# 🔖 1.4 八字核心引擎開始 [行: 860-1700]
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
                  hour_confidence: str = "high",
                  minute: Optional[int] = None,
                  longitude: float = C.DEFAULT_LONGITUDE,
                  latitude: float = C.DEFAULT_LATITUDE) -> Dict:
        """
        八字計算主函數 - 唯一對外接口
        返回完整的八字數據
        """
        audit_log = []
        
        try:
            # 1. 處理分鐘缺失
            processed_minute, processed_confidence = TimeProcessor.handle_missing_minute(
                hour, minute, hour_confidence
            )
            audit_log.append(f"分鐘處理: {hour}:{minute} → {hour}:{processed_minute}")
            audit_log.append(f"初始置信度: {hour_confidence} → {processed_confidence}")
            
            # 2. 計算真太陽時
            true_solar_time = TimeProcessor.calculate_true_solar_time(
                year, month, day, hour, processed_minute, longitude, processed_confidence
            )
            audit_log.extend(true_solar_time.get('audit_log', []))
            
            # 3. 應用日界規則
            adjusted_date = TimeProcessor.apply_day_boundary(
                year, month, day, 
                true_solar_time['hour'], true_solar_time['minute'],
                true_solar_time['confidence']
            )
            adjusted_year, adjusted_month, adjusted_day, final_confidence = adjusted_date
            audit_log.append(f"日界調整: {year}-{month}-{day} → {adjusted_year}-{adjusted_month}-{adjusted_day}")
            audit_log.append(f"最終置信度: {final_confidence}")
            
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
                "birth_longitude": longitude,
                "birth_latitude": latitude,
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
            raise BaziCalculatorError(f"八字計算失敗: {str(e)}")
    
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
        audit_log.append(f"五行分佈: 木{bazi_data['elements'].get('木',0):.1f}% "
                        f"火{bazi_data['elements'].get('火',0):.1f}% "
                        f"土{bazi_data['elements'].get('土',0):.1f}% "
                        f"金{bazi_data['elements'].get('金',0):.1f}% "
                        f"水{bazi_data['elements'].get('水',0):.1f}%")
        
        # 2. 計算身強弱（含司令進氣）
        strength_score = BaziCalculator._calculate_strength_score(bazi_data, audit_log)
        bazi_data["strength_score"] = strength_score
        bazi_data["day_stem_strength"] = BaziCalculator._determine_strength(strength_score)
        audit_log.append(f"身強弱分數: {strength_score:.1f} ({bazi_data['day_stem_strength']})")
        
        # 3. 判斷格局（從格/專旺/正格）
        bazi_data["pattern_type"] = BaziCalculator._determine_pattern(bazi_data, audit_log)
        audit_log.append(f"格局類型: {bazi_data['pattern_type']}")
        
        # 4. 計算喜用神
        bazi_data["useful_elements"] = BaziCalculator._calculate_useful_elements(bazi_data, gender, audit_log)
        bazi_data["harmful_elements"] = BaziCalculator._calculate_harmful_elements(bazi_data, gender)
        audit_log.append(f"喜用神: {','.join(bazi_data['useful_elements'])}")
        audit_log.append(f"忌神: {','.join(bazi_data['harmful_elements'])}")
        
        # 5. 分析夫妻星
        spouse_status, spouse_effective = BaziCalculator._analyze_spouse_star(bazi_data, gender)
        bazi_data["spouse_star_status"] = spouse_status
        bazi_data["spouse_star_effective"] = spouse_effective
        audit_log.append(f"夫妻星: {spouse_status} ({spouse_effective})")
        
        # 6. 分析夫妻宮
        palace_status, pressure_score = BaziCalculator._analyze_spouse_palace(bazi_data)
        bazi_data["spouse_palace_status"] = palace_status
        bazi_data["pressure_score"] = pressure_score
        audit_log.append(f"夫妻宮: {palace_status} (壓力分: {pressure_score:.1f})")
        
        # 7. 計算神煞
        shen_sha_names, shen_sha_bonus = BaziCalculator._calculate_shen_sha(bazi_data)
        bazi_data["shen_sha_names"] = shen_sha_names
        bazi_data["shen_sha_bonus"] = shen_sha_bonus
        audit_log.append(f"神煞: {shen_sha_names} (加分: {shen_sha_bonus:.1f})")
        
        # 8. 計算十神結構
        bazi_data["shi_shen_structure"] = BaziCalculator._calculate_shi_shen(bazi_data, gender)
        audit_log.append(f"十神結構: {bazi_data['shi_shen_structure']}")
        
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
        """計算身強弱分數（含司令進氣動態）"""
        day_stem = bazi_data.get('day_stem', '')
        day_element = BaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        
        if not day_element:
            return C.DEFAULT_STRENGTH_SCORE
        
        score = 0
        strength_details = []
        
        # 1. 月令氣勢（司令進氣）
        month_strength = BaziCalculator._get_month_qi_strength(bazi_data, day_element)
        score += month_strength
        strength_details.append(f"月令氣勢: {month_strength:.1f}分")
        
        # 2. 通根力量
        tong_gen_score = BaziCalculator._calculate_tong_gen(bazi_data, day_element)
        score += tong_gen_score
        strength_details.append(f"通根力量: {tong_gen_score:.1f}分")
        
        # 3. 生扶力量
        support_score = BaziCalculator._calculate_support(bazi_data, day_element)
        score += support_score
        strength_details.append(f"生扶力量: {support_score:.1f}分")
        
        # 4. 調候影響
        tiao_hou_score = BaziCalculator._calculate_tiao_hou(bazi_data, day_element)
        score += tiao_hou_score
        strength_details.append(f"調候影響: {tiao_hou_score:.1f}分")
        
        # 5. 空亡影響
        kong_wang_score = BaziCalculator._calculate_kong_wang(bazi_data)
        score += kong_wang_score
        strength_details.append(f"空亡影響: {kong_wang_score:.1f}分")
        
        final_score = min(100, max(0, score))
        audit_log.append(f"身強弱計算詳情: {'; '.join(strength_details)}")
        
        return final_score
    
    @staticmethod
    def _get_month_qi_strength(bazi_data: Dict, day_element: str) -> float:
        """獲取月令氣勢（司令進氣動態）"""
        try:
            year = bazi_data.get('adjusted_year', bazi_data.get('birth_year', 2000))
            month = bazi_data.get('adjusted_month', bazi_data.get('birth_month', 1))
            day = bazi_data.get('adjusted_day', bazi_data.get('birth_day', 1))
            hour = bazi_data.get('true_solar_hour', 12)
            
            day_obj = sxtwl.fromSolar(year, month, day)
            
            jieqi_jd = day_obj.jq_jd
            birth_jd = day_obj.jd + hour / 24.0
            minutes_since_jieqi = (birth_jd - jieqi_jd) * 1440
            days_since_jieqi = minutes_since_jieqi / 1440.0
            
            # 分配權重（餘氣7天，中氣5天，本氣其餘）
            if days_since_jieqi <= 7.0:
                yuqi_weight, zhongqi_weight, zhengqi_weight = 1.0, 0.0, 0.0
            elif days_since_jieqi <= 12.0:
                yuqi_weight, zhongqi_weight, zhengqi_weight = 0.0, 1.0, 0.0
            else:
                yuqi_weight, zhongqi_weight, zhengqi_weight = 0.0, 0.0, 1.0
            
            month_branch_code = sxtwl.fromSolar(year, month, 1).getMonthGZ().dz
            month_branch = BaziCalculator.BRANCHES[month_branch_code]
            
            qi_info = C.MONTH_QI_MAP.get(month_branch, {})
            
            score = 0.0
            if BaziCalculator.STEM_ELEMENTS.get(qi_info.get('yuqi')) == day_element:
                score += yuqi_weight * C.MONTH_WEIGHT * 0.3
            if BaziCalculator.STEM_ELEMENTS.get(qi_info.get('zhongqi')) == day_element:
                score += zhongqi_weight * C.MONTH_WEIGHT * 0.4
            if BaziCalculator.STEM_ELEMENTS.get(qi_info.get('zhengqi')) == day_element:
                score += zhengqi_weight * C.MONTH_WEIGHT * 0.3
            
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
        
        # 印星生扶（生我者）
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
        
        # 比肩劫財（同類）
        for pillar in pillars:
            if len(pillar) >= 2:
                stem = pillar[0]
                if BaziCalculator.STEM_ELEMENTS.get(stem) == day_element:
                    score += C.SUPPORT_WEIGHT * 0.2
        
        return score
    
    @staticmethod
    def _calculate_tiao_hou(bazi_data: Dict, day_element: str) -> float:
        """計算調候影響"""
        month_branch = bazi_data.get('month_pillar', '  ')[1]
        
        cold_months = ['子', '丑', '亥']
        hot_months = ['巳', '午', '未']
        dry_months = ['辰', '戌']
        wet_months = ['申', '酉']
        
        score = 0
        
        if month_branch in cold_months:
            if day_element == '火':
                score += 5
            elif day_element == '水':
                score -= 3
        elif month_branch in hot_months:
            if day_element == '水':
                score += 5
            elif day_element == '火':
                score -= 3
        elif month_branch in dry_months:
            if day_element == '水':
                score += 3
        elif month_branch in wet_months:
            if day_element == '火':
                score += 3
        
        return score
    
    @staticmethod
    def _calculate_kong_wang(bazi_data: Dict) -> float:
        """計算空亡影響"""
        day_pillar = bazi_data.get('day_pillar', '')
        if len(day_pillar) < 2:
            return 0
        
        day_stem = day_pillar[0]
        day_branch = day_pillar[1]
        
        kong_wang_pairs = {
            '甲': ['申', '酉'], '乙': ['午', '未'], '丙': ['辰', '巳'],
            '丁': ['寅', '卯'], '戊': ['子', '丑'], '己': ['戌', '亥'],
            '庚': ['申', '酉'], '辛': ['午', '未'], '壬': ['辰', '巳'],
            '癸': ['寅', '卯']
        }
        
        kong_branches = kong_wang_pairs.get(day_stem, [])
        if day_branch in kong_branches:
            return -5
        
        return 0
    
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
        """判斷格局類型（從格/專旺/正格）"""
        strength_score = bazi_data.get('strength_score', 50)
        day_stem = bazi_data.get('day_stem', '')
        
        audit_details = []
        
        has_broken = BaziCalculator._has_broken_shi_shen(bazi_data)
        if has_broken:
            audit_details.append("有破格十神")
            audit_log.append("格局判斷: 有破格十神，不能從格")
            return '正格'
        
        has_momentum = BaziCalculator._has_momentum(bazi_data)
        if not has_momentum:
            audit_details.append("無成勢")
            audit_log.append("格局判斷: 無成勢，不能從格")
            return '正格'
        
        if day_stem in C.YANG_STEMS:
            if strength_score < 20:
                audit_details.append("陽干從氣")
                audit_log.append("格局判斷: 陽干從氣，判定為從格")
                return '從格'
        elif day_stem in C.YIN_STEMS:
            if strength_score < 20:
                audit_details.append("陰干從勢")
                audit_log.append("格局判斷: 陰干從勢，判定為從格")
                return '從格'
        
        if strength_score > 80 and BaziCalculator._is_special_wang(bazi_data):
            audit_details.append("專旺成格")
            audit_log.append("格局判斷: 專旺成格")
            return '專旺格'
        
        audit_log.append(f"格局判斷: 正格 (詳情: {'; '.join(audit_details)})")
        return '正格'
    
    @staticmethod
    def _has_broken_shi_shen(bazi_data: Dict) -> bool:
        """檢查是否有破格十神"""
        shi_shen = bazi_data.get('shi_shen_structure', '')
        broken_patterns = ['七殺混雜', '傷官見官', '財星遇劫']
        return any(pattern in shi_shen for pattern in broken_patterns)
    
    @staticmethod
    def _has_momentum(bazi_data: Dict) -> bool:
        """檢查是否成勢"""
        elements = bazi_data.get('elements', {})
        day_element = bazi_data.get('day_stem_element', '')
        
        same_element_percent = elements.get(day_element, 0)
        other_total = sum(v for k, v in elements.items() if k != day_element)
        
        return same_element_percent > 60 or same_element_percent > other_total * 2
    
    @staticmethod
    def _is_special_wang(bazi_data: Dict) -> bool:
        """檢查是否專旺格"""
        elements = bazi_data.get('elements', {})
        day_element = bazi_data.get('day_stem_element', '')
        
        same_element_percent = elements.get(day_element, 0)
        return same_element_percent > 80
    
    @staticmethod
    def _calculate_useful_elements(bazi_data: Dict, gender: str, audit_log: List[str]) -> List[str]:
        """計算喜用神 - 修正版"""
        pattern_type = bazi_data.get('pattern_type', '正格')
        strength_score = bazi_data.get('strength_score', 50)
        day_element = bazi_data.get('day_stem_element', '')
        day_stem = bazi_data.get('day_stem', '')
        
        useful_elements = []
        
        if pattern_type == '從格':
            elements = bazi_data.get('elements', {})
            other_elements = {k: v for k, v in elements.items() if k != day_element}
            if other_elements:
                max_element = max(other_elements.items(), key=lambda x: x[1])[0]
                useful_elements.append(max_element)
                audit_log.append(f"從格喜用: 順從最旺五行 {max_element}")
            else:
                useful_elements.append(day_element)
                audit_log.append(f"從格喜用: 無明顯從勢，用日主五行 {day_element}")
            
        elif pattern_type == '專旺格':
            useful_elements.append(day_element)
            audit_log.append(f"專旺格喜用: 同類五行 {day_element}")
            
        else:
            shi_shen = bazi_data.get('shi_shen_structure', '')
            
            if '殺印相生' in shi_shen:
                if day_element == '木':
                    useful_elements.extend(['水', '火'])
                    audit_log.append(f"殺印相生格喜用: 水、火")
                elif day_element == '火':
                    useful_elements.extend(['木', '土'])
                    audit_log.append(f"殺印相生格喜用: 木、土")
                elif day_element == '土':
                    useful_elements.extend(['火', '金'])
                    audit_log.append(f"殺印相生格喜用: 火、金")
                elif day_element == '金':
                    useful_elements.extend(['土', '水'])
                    audit_log.append(f"殺印相生格喜用: 土、水")
                elif day_element == '水':
                    useful_elements.extend(['金', '木'])
                    audit_log.append(f"殺印相生格喜用: 金、木")
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
                    audit_log.append(f"身強喜用: 克泄耗")
                    
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
                    audit_log.append(f"身弱喜用: 生扶")
                    
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
                    audit_log.append(f"中和喜用: 平衡")
        
        useful_elements = list(set([e for e in useful_elements if e]))
        
        if not useful_elements:
            useful_elements.append(day_element)
            audit_log.append(f"默認喜用: 日主五行 {day_element}")
        
        return useful_elements
    
    @staticmethod
    def _calculate_harmful_elements(bazi_data: Dict, gender: str) -> List[str]:
        """計算忌神 - 修正版"""
        useful_elements = bazi_data.get('useful_elements', [])
        day_element = bazi_data.get('day_stem_element', '')
        
        all_elements = ['木', '火', '土', '金', '水']
        
        harmful_elements = []
        for element in all_elements:
            if element not in useful_elements:
                harmful_elements.append(element)
        
        if day_element in harmful_elements:
            harmful_elements.remove(day_element)
            clash_map = {
                '木': '金', '金': '木',
                '火': '水', '水': '火',
                '土': '木', '木': '土'
            }
            if day_element in clash_map:
                harmful_elements.append(clash_map[day_element])
        
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
            return "未知", "unknown"
        
        spouse_element = SPOUSE_STARS[gender].get(day_element, '')
        if not spouse_element:
            return "無夫妻星", "none"
        
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
                
                hidden_stems = BaziCalculator.BRANCH_HIDDEN_STEMS.get(branch, [])
                for hidden_stem, _ in hidden_stems:
                    if BaziCalculator.STEM_ELEMENTS.get(hidden_stem) == spouse_element:
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
        
        clashes = {'子': '午', '午': '子', '丑': '未', '未': '丑',
                  '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
                  '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
        
        harms = {'子': '未', '未': '子', '丑': '午', '午': '丑',
                '寅': '巳', '巳': '寅', '卯': '辰', '辰': '卯',
                '申': '亥', '亥': '申', '酉': '戌', '戌': '酉'}
        
        pillars = [
            bazi_data.get('year_pillar', ''),
            bazi_data.get('month_pillar', ''),
            bazi_data.get('hour_pillar', '')
        ]
        
        for pillar in pillars:
            if len(pillar) >= 2:
                branch = pillar[1]
                
                if clashes.get(day_branch) == branch:
                    pressure_score += 15
                    status = "嚴重受沖"
                    break
                
                if harms.get(day_branch) == branch:
                    pressure_score += 10
                    status = "相害"
                    break
        
        # 新增藏干互補檢查
        hidden_stems = BaziCalculator.BRANCH_HIDDEN_STEMS.get(day_branch, [])
        for stem, _ in hidden_stems:
            if stem in ['乙', '癸']:  # 乙木為印星，癸水為官星，有助夫妻宮
                pressure_score += 5
                break
        
        return status, pressure_score
    
    @staticmethod
    def _calculate_shen_sha(bazi_data: Dict) -> Tuple[str, float]:
        """計算神煞"""
        shen_sha_list = []
        total_bonus = 0
        
        day_stem = bazi_data.get('day_stem', '')
        year_branch = bazi_data.get('year_pillar', '  ')[1]
        month_branch = bazi_data.get('month_pillar', '  ')[1]
        day_branch = bazi_data.get('day_pillar', '  ')[1]
        hour_branch = bazi_data.get('hour_pillar', '  ')[1]
        
        all_branches = [year_branch, month_branch, day_branch, hour_branch]
        
        hong_luan_map = {
            '子': '午', '丑': '巳', '寅': '辰', '卯': '卯',
            '辰': '寅', '巳': '丑', '午': '子', '未': '亥',
            '申': '戌', '酉': '酉', '戌': '申', '亥': '未'
        }
        
        hong_luan_branch = hong_luan_map.get(year_branch)
        if hong_luan_branch in all_branches:
            shen_sha_list.append("紅鸞")
            total_bonus += C.SHEN_SHA_POSITIVE.get("hong_luan", 0)
        
        tian_xi_map = {
            '子': '寅', '丑': '丑', '寅': '子', '卯': '亥',
            '辰': '戌', '巳': '酉', '午': '申', '未': '未',
            '申': '午', '酉': '巳', '戌': '辰', '亥': '卯'
        }
        
        tian_xi_branch = tian_xi_map.get(year_branch)
        if tian_xi_branch in all_branches:
            shen_sha_list.append("天喜")
            total_bonus += C.SHEN_SHA_POSITIVE.get("tian_xi", 0)
        
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
                total_bonus += C.SHEN_SHA_POSITIVE.get("tian_yi", 0)
                break
        
        if total_bonus > C.SHEN_SHA_BONUS_CAP:
            total_bonus = C.SHEN_SHA_BONUS_CAP
        
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
        
        if '傷官' in shi_shen_list and '正財' in shi_shen_list:
            structure_features.append("傷官生財")
        
        if structure_features:
            return "、".join(structure_features)
        else:
            return "普通結構"
    
    @staticmethod
    def calculate_dayun_flow(bazi_data: Dict, current_year: int, years: int = 5, audit_log: List[str] = None) -> float:
        """計算大運流年影響"""
        if audit_log is None:
            audit_log = []
        
        try:
            year = bazi_data.get('adjusted_year', bazi_data.get('birth_year', 2000))
            month = bazi_data.get('adjusted_month', bazi_data.get('birth_month', 1))
            day = bazi_data.get('adjusted_day', bazi_data.get('birth_day', 1))
            hour = bazi_data.get('true_solar_hour', 12)
            
            day_obj = sxtwl.fromSolar(year, month, day)
            
            start_age = day_obj.getStartAge()
            audit_log.append(f"起運歲數: {start_age}歲")
            
            risk = 0
            for y in range(current_year, current_year + years):
                year_gz = sxtwl.fromSolar(y, 1, 1).getYearGZ()
                year_stem = BaziCalculator._get_stem_name(year_gz.tg)
                year_branch = BaziCalculator._get_branch_name(year_gz.dz)
                
                day_branch = bazi_data.get('day_pillar', '  ')[1]
                clashes = {'子': '午', '午': '子', '丑': '未', '未': '丑',
                          '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
                          '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
                
                if clashes.get(day_branch) == year_branch:
                    risk -= 15
                    audit_log.append(f"{y}年沖夫妻宮: -15分")
            
            if risk < -30:
                audit_log.append("大運一票否決: 未來5年內有嚴重沖剋")
                return -100
            
            return risk
            
        except Exception as e:
            logger.warning(f"大運計算失敗: {e}")
            return 0
# 🔖 1.4 八字核心引擎結束

# 🔖 1.5 評分引擎開始 [行: 1700-2400]
class ScoringEngine:
    """評分引擎 - 負責命理評分，不計算最終D分"""
    
    @staticmethod
    def calculate_score_parts(bazi1: Dict, bazi2: Dict, gender1: str, gender2: str) -> Dict:
        """
        計算命理評分部分（不包含最終D分）
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
                "audit_log": audit_log
            }
            
            # 1. 能量救應 - 修正版（互為忌神打折）
            rescue_score, rescue_details = ScoringEngine._calculate_energy_rescue_corrected(bazi1, bazi2)
            score_parts["energy_rescue"] = rescue_score
            audit_log.append(f"能量救應: {rescue_score:.1f}分")
            audit_log.extend(rescue_details)
            
            # 2. 結構核心
            structure_score, structure_details = ScoringEngine._calculate_structure_core(bazi1, bazi2)
            score_parts["structure_core"] = structure_score
            audit_log.append(f"結構核心: {structure_score:.1f}分")
            audit_log.extend(structure_details)
            
            # 3. 人格風險
            personality_score, personality_details = ScoringEngine._calculate_personality_risk(bazi1, bazi2)
            score_parts["personality_risk"] = personality_score
            audit_log.append(f"人格風險: {personality_score:.1f}分")
            audit_log.extend(personality_details)
            
            # 4. 刑沖壓力 - 修正版（加強刑沖檢查）
            pressure_score, pressure_details = ScoringEngine._calculate_pressure_penalty_corrected(bazi1, bazi2)
            score_parts["pressure_penalty"] = pressure_score
            audit_log.append(f"刑沖壓力: {pressure_score:.1f}分")
            audit_log.extend(pressure_details)
            
            # 5. 神煞加持
            shen_sha_score, shen_sha_details = ScoringEngine._calculate_shen_sha_bonus(bazi1, bazi2)
            score_parts["shen_sha_bonus"] = shen_sha_score
            audit_log.append(f"神煞加持: {shen_sha_score:.1f}分")
            audit_log.extend(shen_sha_details)
            
            # 6. 專業化解
            resolution_score, resolution_details = ScoringEngine._calculate_resolution_bonus(bazi1, bazi2)
            score_parts["resolution_bonus"] = resolution_score
            audit_log.append(f"專業化解: {resolution_score:.1f}分")
            audit_log.extend(resolution_details)
            
            # 7. 雙向影響
            a_to_b, b_to_a, directional_details = ScoringEngine._calculate_asymmetric_scores(bazi1, bazi2, gender1, gender2)
            score_parts["a_to_b_influence"] = a_to_b
            score_parts["b_to_a_influence"] = b_to_a
            audit_log.append(f"雙向影響: 用戶A對用戶B={a_to_b:.1f}, 用戶B對用戶A={b_to_a:.1f}")
            audit_log.extend(directional_details)
            
            # 8. 大運風險
            current_year = datetime.now().year
            dayun_risk = ScoringEngine._calculate_dayun_risk_corrected(bazi1, bazi2, current_year, audit_log)
            score_parts["dayun_risk"] = dayun_risk
            audit_log.append(f"大運風險: {dayun_risk:.1f}分")
            
            # 9. 關係模型 - 修正為由分數推導
            relationship_model, model_details = ScoringEngine._determine_relationship_model_corrected(a_to_b, b_to_a, bazi1, bazi2)
            score_parts["relationship_model"] = relationship_model
            audit_log.append(f"關係模型: {relationship_model}")
            audit_log.extend(model_details)
            
            logger.info(f"命理評分計算完成: 總基礎分 {C.BASE_SCORE}")
            return score_parts
            
        except Exception as e:
            logger.error(f"評分計算錯誤: {e}", exc_info=True)
            raise ScoringEngineError(f"評分計算失敗: {str(e)}")
    
    # ========== 基礎工具方法開始 ==========
    @staticmethod
    def is_clash(branch1: str, branch2: str) -> bool:
        """檢查是否六沖 - 雙向檢查"""
        clashes = {'子': '午', '午': '子', '丑': '未', '未': '丑',
              '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
              '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
        return clashes.get(branch1) == branch2
    
    @staticmethod
    def is_harm(branch1: str, branch2: str) -> bool:
        """檢查是否六害 - 雙向檢查"""
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
    
    @staticmethod
    def is_branch_triad(branch1: str, branch2: str, branch3: str) -> bool:
        """檢查地支是否三合"""
        triad_groups = [
            {'寅', '卯', '辰'},  # 木局
            {'巳', '午', '未'},  # 火局
            {'申', '酉', '戌'},  # 金局
            {'亥', '子', '丑'}   # 水局
        ]
        for group in triad_groups:
            if branch1 in group and branch2 in group and branch3 in group:
                return True
        return False
    
    @staticmethod
    def _check_hard_problems(bazi1: Dict, bazi2: Dict) -> bool:
        """檢查硬傷問題（日支六沖）"""
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        return ScoringEngine.is_clash(day_branch1, day_branch2)
    
    @staticmethod
    def _check_day_branch_clash(bazi1: Dict, bazi2: Dict) -> bool:
        """檢查日支六沖（兼容別名）"""
        return ScoringEngine._check_hard_problems(bazi1, bazi2)
    # ========== 基礎工具方法結束 ==========
    
    @staticmethod
    def _calculate_energy_rescue_corrected(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算能量救應分數 - 修正版（加強互補）"""
        score = 0
        details = []
        
        elements1 = bazi1.get('elements', {})
        elements2 = bazi2.get('elements', {})
        
        # 檢查極弱救應
        for element, percent in elements1.items():
            if percent < C.WEAK_THRESHOLD:
                if elements2.get(element, 0) > 30:
                    # 檢查是否互為忌神
                    if element in bazi2.get('harmful_elements', []):
                        rescue_bonus = C.EXTREME_WEAK_BONUS * 0.5  # 互忌打5折
                        details.append(f"A方{element}極弱({percent}%)，B方強旺({elements2[element]}%)，但為B方忌神，打折後: +{rescue_bonus:.1f}分")
                    else:
                        rescue_bonus = C.EXTREME_WEAK_BONUS * 1.5  # 加強救應
                        details.append(f"A方{element}極弱({percent}%)，B方強旺({elements2[element]}%)，極弱救應+{rescue_bonus:.1f}分")
                    score += rescue_bonus
                    break
        
        # 檢查需求對接 - 第一階段緊急修正：添加濃度加成
        useful1 = bazi1.get('useful_elements', [])
        useful2 = bazi2.get('useful_elements', [])
        
        for element in useful1:
            if elements2.get(element, 0) > 20:
                # 檢查是否互為忌神
                if element in bazi2.get('harmful_elements', []):
                    demand_bonus = C.DEMAND_MATCH_BONUS * 0.5  # 互忌打5折
                    details.append(f"A喜{element}，B有{elements2[element]}%，但為B方忌神，打折後: +{demand_bonus:.1f}分")
                else:
                    # 根據濃度給予加成
                    target_percent = elements2.get(element, 0)
                    if target_percent > 30:
                        demand_bonus = C.DEMAND_MATCH_BONUS * 1.4  # 濃度>30%，加成1.4倍
                        details.append(f"A喜{element}，B有{elements2[element]}%（>30%），濃度加成+{demand_bonus:.1f}分")
                    elif target_percent > 15:
                        demand_bonus = C.DEMAND_MATCH_BONUS * 1.2  # 濃度>15%，加成1.2倍
                        details.append(f"A喜{element}，B有{elements2[element]}%（>15%），濃度加成+{demand_bonus:.1f}分")
                    else:
                        demand_bonus = C.DEMAND_MATCH_BONUS  # 正常加分
                        details.append(f"A喜{element}，B有{elements2[element]}%，需求對接+{demand_bonus:.1f}分")
                score += demand_bonus
                break
        
        for element in useful2:
            if elements1.get(element, 0) > 20:
                # 檢查是否互為忌神
                if element in bazi1.get('harmful_elements', []):
                    demand_bonus = C.DEMAND_MATCH_BONUS * 0.5  # 互忌打5折
                    details.append(f"B喜{element}，A有{elements1[element]}%，但為A方忌神，打折後: +{demand_bonus:.1f}分")
                else:
                    # 根據濃度給予加成
                    target_percent = elements1.get(element, 0)
                    if target_percent > 30:
                        demand_bonus = C.DEMAND_MATCH_BONUS * 1.4  # 濃度>30%，加成1.4倍
                        details.append(f"B喜{element}，A有{elements1[element]}%（>30%），濃度加成+{demand_bonus:.1f}分")
                    elif target_percent > 15:
                        demand_bonus = C.DEMAND_MATCH_BONUS * 1.2  # 濃度>15%，加成1.2倍
                        details.append(f"B喜{element}，A有{elements1[element]}%（>15%），濃度加成+{demand_bonus:.1f}分")
                    else:
                        demand_bonus = C.DEMAND_MATCH_BONUS  # 正常加分
                        details.append(f"B喜{element}，A有{elements1[element]}%，需求對接+{demand_bonus:.1f}分")
                score += demand_bonus
                break
        
        # 新增間接互補檢查
        day_element1 = bazi1.get('day_stem_element', '')
        day_element2 = bazi2.get('day_stem_element', '')
        
        # 水生木間接互補
        if day_element1 == '木' and elements2.get('水', 0) > 10:
            score += 5
            details.append(f"間接水生木互補: +5分")
        
        # 土生金間接互補
        if day_element1 == '金' and elements2.get('土', 0) > 15:
            score += 5
            details.append(f"間接土生金互補: +5分")
        
        # 反向檢查
        if day_element2 == '木' and elements1.get('水', 0) > 10:
            score += 5
            details.append(f"反向水生木互補: +5分")
        
        if day_element2 == '金' and elements1.get('土', 0) > 15:
            score += 5
            details.append(f"反向土生金互補: +5分")
        
        final_score = min(C.ENERGY_RESCUE_CAP, score)
        if final_score != score:
            details.append(f"能量救應上限控制: {score}→{final_score}分")
        
        return final_score, details
    
    @staticmethod
    def _calculate_structure_core(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算結構核心分數 - 修正版（加強正面加分）"""
        score = 0
        details = []
        
        # 日柱天干關係
        day_stem1 = bazi1.get('day_stem', '')
        day_stem2 = bazi2.get('day_stem', '')
        
        stem_pair = tuple(sorted([day_stem1, day_stem2]))
        
        # 天干五合配對
        five_harmony_pairs = [('甲', '己'), ('乙', '庚'), ('丙', '辛'), ('丁', '壬'), ('戊', '癸')]
        
        # 檢查日干五合
        if stem_pair in five_harmony_pairs:
            score += C.STEM_COMBINATION_FIVE_HARMONY
            details.append(f"日干五合 {stem_pair}: +{C.STEM_COMBINATION_FIVE_HARMONY}分")
        
        # 檢查所有柱的天干五合
        pillars1 = [bazi1.get('year_pillar', ''), bazi1.get('month_pillar', ''), bazi1.get('hour_pillar', '')]
        pillars2 = [bazi2.get('year_pillar', ''), bazi2.get('month_pillar', ''), bazi2.get('hour_pillar', '')]
        
        for p1 in pillars1:
            for p2 in pillars2:
                if len(p1) >= 1 and len(p2) >= 1:
                    if tuple(sorted([p1[0], p2[0]])) in five_harmony_pairs:
                        score += C.STEM_COMBINATION_FIVE_HARMONY * 0.6
                        details.append(f"他柱天干五合 {p1[0]}-{p2[0]}: +{C.STEM_COMBINATION_FIVE_HARMONY*0.6:.1f}分")
        
        # 日柱地支關係
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        
        branch_pair = tuple(sorted([day_branch1, day_branch2]))
        
        # 地支六合配對
        six_harmony_pairs = [('子', '丑'), ('寅', '亥'), ('卯', '戌'), 
                            ('辰', '酉'), ('巳', '申'), ('午', '未')]
        
        # 檢查日支六合
        if branch_pair in six_harmony_pairs:
            score += C.BRANCH_COMBINATION_SIX_HARMONY
            details.append(f"日支六合 {branch_pair}: +{C.BRANCH_COMBINATION_SIX_HARMONY}分")
        
        # 檢查所有柱的地支六合
        for p1 in pillars1:
            for p2 in pillars2:
                if len(p1) >= 2 and len(p2) >= 2:
                    branch_pair_other = tuple(sorted([p1[1], p2[1]]))
                    if branch_pair_other in six_harmony_pairs:
                        score += C.BRANCH_COMBINATION_SIX_HARMONY * 0.5
                        details.append(f"他柱地支六合 {p1[1]}-{p2[1]}: +{C.BRANCH_COMBINATION_SIX_HARMONY*0.5:.1f}分")
        
        # 檢查地支三合
        triad_groups = [
            {'寅', '卯', '辰'},  # 木局
            {'巳', '午', '未'},  # 火局
            {'申', '酉', '戌'},  # 金局
            {'亥', '子', '丑'}   # 水局
        ]
        
        # 收集所有地支
        all_branches1 = [bazi1.get('year_pillar', '  ')[1], bazi1.get('month_pillar', '  ')[1], 
                        bazi1.get('day_pillar', '  ')[1], bazi1.get('hour_pillar', '  ')[1]]
        all_branches2 = [bazi2.get('year_pillar', '  ')[1], bazi2.get('month_pillar', '  ')[1], 
                        bazi2.get('day_pillar', '  ')[1], bazi2.get('hour_pillar', '  ')[1]]
        
        all_branches = set(all_branches1 + all_branches2)
        
        for group in triad_groups:
            if group.issubset(all_branches):
                score += C.BRANCH_COMBINATION_THREE_HARMONY
                details.append(f"地支三合 {group}: +{C.BRANCH_COMBINATION_THREE_HARMONY}分")
                break
        
        # 檢查地支六沖 - 扣分
        if ScoringEngine.is_clash(day_branch1, day_branch2):
            score += C.BRANCH_CLASH_PENALTY
            details.append(f"日支六沖 {day_branch1}↔{day_branch2}: {C.BRANCH_CLASH_PENALTY}分")
    
        # 檢查地支六害
        if ScoringEngine.is_harm(day_branch1, day_branch2):
            score += C.BRANCH_HARM_PENALTY
            details.append(f"日支六害 {day_branch1}↔{day_branch2}: {C.BRANCH_HARM_PENALTY}分")
        
        # 正向因素乘法因子 - 第一階段修正：降低乘數
        if score > 15:
            score = score * 1.1  # 多正向加權10% (從1.2降)
            details.append(f"多正向因素加權10%: → {score:.1f}分")
        
        return score, details
    
    @staticmethod
    def _calculate_personality_risk(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算人格風險分數"""
        score = 0
        details = []
        
        structure1 = bazi1.get('shi_shen_structure', '')
        structure2 = bazi2.get('shi_shen_structure', '')
        
        for pattern, penalty in C.PERSONALITY_RISK_PATTERNS.items():
            if pattern in structure1:
                score += penalty
                details.append(f"A方{pattern}: {penalty}分")
            
            if pattern in structure2:
                score += penalty
                details.append(f"B方{pattern}: {penalty}分")
        
        # 檢查疊加風險
        risk_count = 0
        for pattern in C.PERSONALITY_RISK_PATTERNS:
            if pattern in structure1:
                risk_count += 1
            if pattern in structure2:
                risk_count += 1
        
        if risk_count >= 2:
            score += C.PERSONALITY_STACKED_PENALTY
            details.append(f"疊加風險({risk_count}個): {C.PERSONALITY_STACKED_PENALTY}分")
        
        # 確保至少有一定負分
        if score > 0:
            score = -5  # 確保有基本負分
            details.append(f"人格風險基礎負分: -5分")
        
        return score, details
    
    @staticmethod
    def _calculate_pressure_penalty_corrected(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算刑沖壓力分數 - 修正版（確保刑沖檢查生效）"""
        score = 0
        details = []
        
        # 收集所有地支
        branches1 = []
        branches2 = []
        
        # 正確收集所有地支
        for pillar in [bazi1.get('year_pillar', ''), bazi1.get('month_pillar', ''), 
                      bazi1.get('day_pillar', ''), bazi1.get('hour_pillar', '')]:
            if len(pillar) >= 2:
                branches1.append(pillar[1])
        
        for pillar in [bazi2.get('year_pillar', ''), bazi2.get('month_pillar', ''), 
                      bazi2.get('day_pillar', ''), bazi2.get('hour_pillar', '')]:
            if len(pillar) >= 2:
                branches2.append(pillar[1])
        
        # 防None檢查
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
                        details.append(f"日支六沖 {b1}↔{b2}: {penalty}分")
                    else:
                        penalty = C.BRANCH_CLASH_PENALTY
                        details.append(f"六沖 {b1}↔{b2}: {penalty}分")
                    
                    score += penalty
                    clash_count += 1
                
                # 檢查六害
                if ScoringEngine.is_harm(b1, b2):
                    # 日支六害特別重扣
                    if b1 == bazi1.get('day_pillar', '  ')[1] and b2 == bazi2.get('day_pillar', '  ')[1]:
                        penalty = C.DAY_HARM_PENALTY
                        details.append(f"日支六害 {b1}↔{b2}: {penalty}分")
                    else:
                        penalty = C.BRANCH_HARM_PENALTY
                        details.append(f"六害 {b1}↔{b2}: {penalty}分")
                    
                    score += penalty
                    harm_count += 1
        
        if clash_count > 0 or harm_count > 0:
            details.append(f"總計: 六沖{clash_count}個, 六害{harm_count}個")
        else:
            details.append("無刑沖")
        
        # 三合解刑邏輯
        resolution_ratio = 0.0
        triad_groups = [
            {'寅', '卯', '辰'},  # 木局
            {'巳', '午', '未'},  # 火局
            {'申', '酉', '戌'},  # 金局
            {'亥', '子', '丑'}   # 水局
        ]
        
        all_branches = set(branches1 + branches2)
        for group in triad_groups:
            if len(all_branches & group) >= 3:  # 完全三合
                resolution_ratio += C.TRIAD_RESOLUTION_RATIO
                details.append(f"完全三合{group}解刑: 化解{resolution_ratio*100}%")
        
        if resolution_ratio > 0:
            score *= (1 - resolution_ratio)
            details.append(f"刑沖分數化解後: {score:.1f}分")
        
        # 刑沖壓力上限控制
        final_score = max(score, C.PRESSURE_PENALTY_CAP)
        if final_score != score:
            details.append(f"刑沖壓力上限控制: {score}→{final_score}分")
        
        return final_score, details
    
    @staticmethod
    def _calculate_shen_sha_bonus(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算神煞加持分數"""
        details = []
        
        bonus1 = bazi1.get('shen_sha_bonus', 0)
        bonus2 = bazi2.get('shen_sha_bonus', 0)
        
        total_bonus = bonus1 + bonus2
        
        details.append(f"A方神煞: {bazi1.get('shen_sha_names', '無')} ({bonus1}分)")
        details.append(f"B方神煞: {bazi2.get('shen_sha_names', '無')} ({bonus2}分)")
        
        # 互動加成
        shen_sha1 = bazi1.get('shen_sha_names', '')
        shen_sha2 = bazi2.get('shen_sha_names', '')
        
        if '紅鸞' in shen_sha1 and '天喜' in shen_sha2:
            total_bonus += 6
            details.append(f"紅鸞天喜組合: +6分")
        elif '天喜' in shen_sha1 and '紅鸞' in shen_sha2:
            total_bonus += 6
            details.append(f"天喜紅鸞組合: +6分")
        
        if '天乙貴人' in shen_sha1 and '天乙貴人' in shen_sha2:
            total_bonus += 5
            details.append(f"雙天乙貴人: +5分")
        
        if total_bonus > C.SHEN_SHA_BONUS_CAP:
            details.append(f"神煞上限控制: {total_bonus}→{C.SHEN_SHA_BONUS_CAP}分")
            total_bonus = C.SHEN_SHA_BONUS_CAP
        
        return total_bonus, details
    
    @staticmethod
    def _calculate_resolution_bonus(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """計算專業化解分數"""
        score = 0
        details = []
        
        structure1 = bazi1.get('shi_shen_structure', '')
        structure2 = bazi2.get('shi_shen_structure', '')
        
        for pattern, bonus in C.RESOLUTION_PATTERNS.items():
            pattern1, pattern2 = pattern.split("+")
            
            if (pattern1 in structure1 and pattern2 in structure2) or \
               (pattern2 in structure1 and pattern1 in structure2):
                score += bonus
                details.append(f"化解組合 {pattern}: +{bonus}分")
        
        final_score = min(C.RESOLUTION_BONUS_CAP, score)
        if final_score != score:
            details.append(f"專業化解上限控制: {score}→{final_score}分")
        
        return final_score, details
    
    @staticmethod
    def _calculate_asymmetric_scores(bazi1: Dict, bazi2: Dict, 
                                   gender1: str, gender2: str) -> Tuple[float, float, List[str]]:
        """計算雙向不對稱分數"""
        details = []
        
        a_to_b, a_to_b_details = ScoringEngine._calculate_directional_score(
            bazi1, bazi2, gender1, gender2, "用戶A對用戶B"
        )
        details.extend(a_to_b_details)
        
        b_to_a, b_to_a_details = ScoringEngine._calculate_directional_score(
            bazi2, bazi1, gender2, gender1, "用戶B對用戶A"
        )
        details.extend(b_to_a_details)
        
        return a_to_b, b_to_a, details
    
    @staticmethod
    def _calculate_directional_score(source_bazi: Dict, target_bazi: Dict,
                                   source_gender: str, target_gender: str,
                                   direction: str) -> Tuple[float, List[str]]:
        """計算單向影響分數"""
        score = 50
        details = []
        
        source_useful = source_bazi.get('useful_elements', [])
        target_elements = target_bazi.get('elements', {})
        
        useful_match_score = 0
        for element in source_useful:
            if target_elements.get(element, 0) > 15:
                useful_match_score += 10
                details.append(f"{direction} {element}匹配強: +10分")
            elif target_elements.get(element, 0) > 5:
                useful_match_score += 5
                details.append(f"{direction} {element}匹配中: +5分")
        
        score += useful_match_score
        
        target_spouse_effective = target_bazi.get('spouse_star_effective', 'unknown')
        if target_spouse_effective == '強':
            score += 8
            details.append(f"{direction} 配偶星旺盛: +8分")
        elif target_spouse_effective == '中':
            score += 5
            details.append(f"{direction} 配偶星明顯: +5分")
        elif target_spouse_effective == '弱':
            score += 2
            details.append(f"{direction} 配偶星單一: +2分")
        
        final_score = max(0, min(100, round(score, 1)))
        details.append(f"{direction} 最終分數: {final_score:.1f}")
        
        return final_score, details
    
    @staticmethod
    def _calculate_dayun_risk_corrected(bazi1: Dict, bazi2: Dict, current_year: int, audit_log: List[str]) -> float:
        """計算大運風險 - 修正版"""
        try:
            risk = 0
            details = []
            
            # 計算大運同步率
            sync_score = ScoringEngine._calculate_dayun_sync(bazi1, bazi2, 10)
            details.append(f"大運同步率: {sync_score}%")
            
            # 不同步扣分
            if sync_score < 50:
                penalty = - (100 - sync_score) * 0.25
                risk += penalty
                details.append(f"大運同步率 {sync_score}% < 50%: 扣{penalty:.1f}分")
            
            # 原有的大運風險計算
            dayun_risk1 = BaziCalculator.calculate_dayun_flow(bazi1, current_year, 5, details)
            dayun_risk2 = BaziCalculator.calculate_dayun_flow(bazi2, current_year, 5, details)
            
            risk += dayun_risk1 + dayun_risk2
            
            audit_log.extend(details)
            return risk
            
        except Exception as e:
            logger.warning(f"大運風險計算失敗: {e}")
            return 0
    
    @staticmethod
    def _calculate_dayun_sync(bazi1: Dict, bazi2: Dict, years: int = 10) -> float:
        """計算大運同步率（0-100%）"""
        try:
            year1 = bazi1.get('adjusted_year', bazi1.get('birth_year', 2000))
            year2 = bazi2.get('adjusted_year', bazi2.get('birth_year', 2000))
            
            # 計算年齡差
            age_diff = abs(year1 - year2)
            
            # 年齡差越大，大運同步率越低
            if age_diff <= 5:
                return 85.0
            elif age_diff <= 10:
                return 65.0
            elif age_diff <= 15:
                return 45.0
            else:
                return 30.0
                
        except Exception as e:
            logger.warning(f"大運同步率計算失敗: {e}")
            return 50.0
    
    @staticmethod
    def _determine_relationship_model_corrected(a_to_b: float, b_to_a: float, 
                                            bazi1: Dict, bazi2: Dict) -> Tuple[str, List[str]]:
        """確定關係模型 - 修正版（由分數推導）"""
        details = []
        
        diff = abs(a_to_b - b_to_a)
        avg = (a_to_b + b_to_a) / 2
        
        details.append(f"雙向差異: {diff:.1f}分，平均: {avg:.1f}分")
        
        # 相同八字檢測
        pillars_same = all(bazi1.get(k) == bazi2.get(k) for k in ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar'])
        if pillars_same:
            details.append("相同八字，關係模型為混合型（伏吟）")
            return "混合型", details
        
        # 基於雙向分數決定關係模型
        if avg >= 70 and diff < C.BALANCED_MAX_DIFF:
            model = "平衡型"
            details.append(f"平均分≥70且差異<{C.BALANCED_MAX_DIFF}，判定為平衡型")
        elif avg >= 60 and diff >= C.SUPPLY_MIN_DIFF:
            if a_to_b > b_to_a:
                model = "供求型 (用戶A供應用戶B)"
                details.append(f"平均分≥60且差異≥{C.SUPPLY_MIN_DIFF}，用戶A>用戶B，判定為供求型(用戶A供應用戶B)")
            else:
                model = "供求型 (用戶B供應用戶A)"
                details.append(f"平均分≥60且差異≥{C.SUPPLY_MIN_DIFF}，用戶B>用戶A，判定為供求型(用戶B供應用戶A)")
        elif avg < 50:
            model = "相欠型"
            details.append(f"平均分<50，判定為相欠型")
        else:
            model = "混合型"
            details.append("不符合其他條件，判定為混合型")
        
        return model, details
    
    # 兼容舊方法
    @staticmethod
    def _determine_relationship_model(a_to_b: float, b_to_a: float, 
                                    bazi1: Dict, bazi2: Dict) -> Tuple[str, List[str]]:
        return ScoringEngine._determine_relationship_model_corrected(a_to_b, b_to_a, bazi1, bazi2)
    
    @staticmethod
    def get_rating(score: float) -> str:
        """獲取評級 - 使用Config的評級系統"""
        return C.get_rating(score)
    
    @staticmethod
    def get_rating_with_description(score: float) -> Dict[str, str]:
        """獲取評級和描述"""
        return {
            "name": C.get_rating(score),
            "description": C.get_rating_description(score)
        }
# 🔖 1.5 評分引擎結束

# 🔖 1.6 主入口函數開始 [行: 2410-2550]
def calculate_match(bazi1: Dict, bazi2: Dict, gender1: str, gender2: str, is_testpair: bool = False) -> Dict:
    """
    八字配對主入口函數 - 第一階段緊急止血修改
    核心修正：1. 刑沖硬上限 2. 正向加分飽和 3. 能量救應濃度加成 4. 相同八字懲罰
    """
    try:
        audit_log = []
        audit_log.append("=" * 50)
        audit_log.append("八字配對計算開始 (第一階段緊急止血)")
        
        # 增加詳細的DEBUG信息
        audit_log.append(f"=== DEBUG START ===")
        audit_log.append(f"A八字: {bazi1.get('year_pillar','')}{bazi1.get('month_pillar','')}{bazi1.get('day_pillar','')}{bazi1.get('hour_pillar','')}")
        audit_log.append(f"B八字: {bazi2.get('year_pillar','')}{bazi2.get('month_pillar','')}{bazi2.get('day_pillar','')}{bazi2.get('hour_pillar','')}")
        
        # 檢查日支六沖
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        has_day_clash = ScoringEngine.is_clash(day_branch1, day_branch2)
        has_day_harm = ScoringEngine.is_harm(day_branch1, day_branch2)
        
        audit_log.append(f"日支檢測: A日支={day_branch1}, B日支={day_branch2}")
        audit_log.append(f"是否日支六沖: {has_day_clash}")
        audit_log.append(f"是否日支六害: {has_day_harm}")
        
        audit_log.append(f"用戶A: {bazi1.get('year_pillar', '')} {bazi1.get('month_pillar', '')} "
                        f"{bazi1.get('day_pillar', '')} {bazi1.get('hour_pillar', '')}")
        audit_log.append(f"用戶B: {bazi2.get('year_pillar', '')} {bazi2.get('month_pillar', '')} "
                        f"{bazi2.get('day_pillar', '')} {bazi2.get('hour_pillar', '')}")
        
        audit_log.append(f"用戶A基本資料: {bazi1.get('birth_year', '')}年{bazi1.get('birth_month', '')}月{bazi1.get('birth_day', '')}日 "
                        f"{bazi1.get('birth_hour', '')}時 {gender1}")
        audit_log.append(f"用戶B基本資料: {bazi2.get('birth_year', '')}年{bazi2.get('birth_month', '')}月{bazi2.get('birth_day', '')}日 "
                        f"{bazi2.get('birth_hour', '')}時 {gender2}")
        
        # 防None檢查
        if not bazi1.get('day_pillar') or not bazi2.get('day_pillar'):
            audit_log.append("八字計算失敗，返回默認分數")
            return {
                "score": 50.0,
                "rating": "未知",
                "a_to_b_score": 50.0,
                "b_to_a_score": 50.0,
                "relationship_model": "未知",
                "module_scores": {
                    "energy_rescue": 0,
                    "structure_core": 0,
                    "personality_risk": 0,
                    "pressure_penalty": 0,
                    "shen_sha_bonus": 0,
                    "resolution_bonus": 0,
                    "dayun_risk": 0
                },
                "confidence_adjust_applied": False,
                "audit_log": audit_log,
                "details": audit_log[-10:],
                "debug_info": {
                    "day_branch1": day_branch1,
                    "day_branch2": day_branch2,
                    "has_day_clash": has_day_clash,
                    "has_day_harm": has_day_harm
                }
            }
        
        # ========== 第一階段核心修正開始 ==========
        
        # 1. 計算命理評分部分
        score_parts = ScoringEngine.calculate_score_parts(bazi1, bazi2, gender1, gender2)
        audit_log.extend(score_parts.get("audit_log", []))
        
        # 2. 檢測相同八字（伏吟）並應用懲罰
        pillars_same = all(bazi1.get(k) == bazi2.get(k) for k in ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar'])
        if pillars_same:
            # 伏吟懲罰：結構核心減20分，刑沖壓力乘0.7
            original_structure = score_parts["structure_core"]
            original_pressure = score_parts["pressure_penalty"]
            
            score_parts["structure_core"] = max(0, original_structure - 20)
            score_parts["pressure_penalty"] = original_pressure * 0.7
            
            audit_log.append(f"加強相同八字(伏吟)懲罰: 結構-20({original_structure:.1f}→{score_parts['structure_core']:.1f}), "
                           f"刑沖×0.7({original_pressure:.1f}→{score_parts['pressure_penalty']:.1f})")
        
        # 3. 正向加分飽和處理（防止爆100分）
        raw_bonus = (
            score_parts["energy_rescue"] + 
            score_parts["structure_core"] + 
            score_parts["shen_sha_bonus"] + 
            score_parts["resolution_bonus"]
        )
        
        # 更嚴格的飽和機制
        if raw_bonus > 25:
            # 超過25分後，每分只值0.2分
            adjusted_bonus = 25 + (raw_bonus - 25) * 0.2
            audit_log.append(f"嚴格正向加分飽和: {raw_bonus:.1f} → {adjusted_bonus:.1f}分 (超過25分部分×0.2)")
        elif raw_bonus > 15:
            # 15-25分，每分只值0.5分
            adjusted_bonus = 15 + (raw_bonus - 15) * 0.5
            audit_log.append(f"中度正向加分飽和: {raw_bonus:.1f} → {adjusted_bonus:.1f}分 (15-25分部分×0.5)")
        else:
            adjusted_bonus = raw_bonus
        
        # 4. 計算基礎總分（應用飽和後的加分）
        adjusted_score = C.BASE_SCORE + adjusted_bonus
        audit_log.append(f"基礎總分計算: {C.BASE_SCORE} + {adjusted_bonus:.1f} = {adjusted_score:.1f}")
        
        # 5. 應用負向扣分（刑沖、人格風險、大運風險）
        # 確保人格風險為負分
        personality_score = score_parts["personality_risk"]
        if personality_score > 0:
            personality_score = -personality_score
        if personality_score < C.PERSONALITY_RISK_CAP:
            personality_score = C.PERSONALITY_RISK_CAP
        
        # 確保刑沖壓力為負分
        pressure_score = score_parts["pressure_penalty"]
        if pressure_score > 0:
            pressure_score = -pressure_score
        if pressure_score < C.PRESSURE_PENALTY_CAP:
            pressure_score = C.PRESSURE_PENALTY_CAP
        
        # 總扣分
        total_penalty = personality_score + pressure_score + score_parts["dayun_risk"]
        audit_log.append(f"負向扣分: 人格{personality_score:.1f} + 刑沖{pressure_score:.1f} + 大運{score_parts['dayun_risk']:.1f} = {total_penalty:.1f}")
        
        # 6. 刑沖硬上限機制 - 修正為更嚴格的邏輯
        if has_day_clash:
            # 日支六沖：直接封頂40分，且不能有任何正向加分
            adjusted_score = min(40.0, C.BASE_SCORE - abs(total_penalty))
            audit_log.append(f"日支六沖硬上限激活: 最高40分，當前{adjusted_score:.1f}分")
        elif has_day_harm:
            # 日支六害：直接封頂45分
            adjusted_score = min(45.0, C.BASE_SCORE - abs(total_penalty) + 5)
            audit_log.append(f"日支六害硬上限激活: 最高45分，當前{adjusted_score:.1f}分")
        else:
            # 沒有刑沖才應用正常計分
            adjusted_score += total_penalty
            audit_log.append(f"無日支刑沖: 應用正常扣分後分數: {adjusted_score:.1f}")
        
        # 7. 總扣分上限保護
        if total_penalty < C.TOTAL_PENALTY_CAP:
            # 補償性調整，防止扣分過重
            penalty_diff = total_penalty - C.TOTAL_PENALTY_CAP
            adjusted_score -= penalty_diff
            audit_log.append(f"總扣分上限保護: {total_penalty:.1f} → {C.TOTAL_PENALTY_CAP:.1f}，補償{penalty_diff:.1f}分")
        
        # 8. 應用現實校準
        calibrated_score = adjusted_score

        # 年齡差距調整
        age_diff = abs(bazi1.get('birth_year', 0) - bazi2.get('birth_year', 0))
        if age_diff > 15:
            calibrated_score += C.AGE_GAP_PENALTY_16_PLUS
            audit_log.append(f"年齡差距>15歲: {C.AGE_GAP_PENALTY_16_PLUS}分")
        elif age_diff > 10:
            calibrated_score += C.AGE_GAP_PENALTY_11_15
            audit_log.append(f"年齡差距11-15歲: {C.AGE_GAP_PENALTY_11_15}分")
        
        # 9. 應用置信度調整
        confidence_adjust_applied = False
        
        if not is_testpair:
            confidence1 = bazi1.get('hour_confidence', 'high')
            confidence2 = bazi2.get('hour_confidence', 'high')
            
            adjusted1 = bazi1.get('time_adjusted', False) or bazi1.get('day_adjusted', 0) != 0
            adjusted2 = bazi2.get('time_adjusted', False) or bazi2.get('day_adjusted', 0) != 0
            
            if adjusted1 or adjusted2:
                confidence_factor = C.TIME_CONFIDENCE_LEVELS.get(confidence1, 0.85) * C.TIME_CONFIDENCE_LEVELS.get(confidence2, 0.85)
                calibrated_score = calibrated_score * confidence_factor
                confidence_adjust_applied = True
                audit_log.append(f"置信度調整: {confidence1}×{confidence2}={confidence_factor:.3f}, "
                                f"{adjusted_score:.1f} → {calibrated_score:.1f}")
            else:
                audit_log.append(f"無時間調整，不使用置信度折扣")
        else:
            audit_log.append(f"testpair命令，不使用置信度調整")
        
        # 10. 最終分數範圍限制（10-95分）
        final_score = max(10.0, min(95.0, round(calibrated_score, 1)))
        
        # 極品組合不應超過90分
        if final_score > 90:
            final_score = min(final_score, 90)
            audit_log.append(f"極品組合上限: 最高90分 → {final_score:.1f}")
        
        # 確保相同八字不會超過50分
        if pillars_same and final_score > 50:
            final_score = min(final_score, 50)
            audit_log.append(f"相同八字上限: 最高50分 → {final_score:.1f}")
        
        audit_log.append(f"最終分數範圍限制: {calibrated_score:.1f} → {final_score:.1f}")
        
        # 11. 獲取評級
        rating_info = ScoringEngine.get_rating_with_description(final_score)
        rating = rating_info["name"]
        rating_description = rating_info["description"]

        # 12. 基於最終分數重新確定關係模型
        relationship_model = score_parts["relationship_model"]
        
        # 根據最終分數調整關係模型
        if final_score >= 70 and abs(score_parts["a_to_b_influence"] - score_parts["b_to_a_influence"]) < 12:
            relationship_model = "平衡型"
        elif final_score >= 60 and abs(score_parts["a_to_b_influence"] - score_parts["b_to_a_influence"]) >= 12:
            if score_parts["a_to_b_influence"] > score_parts["b_to_a_influence"]:
                relationship_model = "供求型 (用戶A供應用戶B)"
            else:
                relationship_model = "供求型 (用戶B供應用戶A)"
        elif final_score < 50:
            relationship_model = "相欠型"
        
        # 13. 組裝結果
        result = {
            "score": final_score,
            "rating": rating,
            "a_to_b_score": score_parts["a_to_b_influence"],
            "b_to_a_score": score_parts["b_to_a_influence"],
            "relationship_model": relationship_model,
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
            "details": audit_log[-20:],  # 最後20條記錄作為摘要
            "debug_info": {
                "day_branch1": day_branch1,
                "day_branch2": day_branch2,
                "has_day_clash": has_day_clash,
                "has_day_harm": has_day_harm,
                "adjusted_score_before_limit": adjusted_score,
                "total_penalty": total_penalty,
                "raw_bonus": raw_bonus,
                "adjusted_bonus": adjusted_bonus,
                "pillars_same": pillars_same
            }
        }
        
        audit_log.append(f"最終結果: {final_score:.1f}分 ({rating})")
        audit_log.append("第一階段緊急止血完成")
        audit_log.append("=" * 50)
        
        logger.info(f"八字配對完成: 最終分數 {final_score:.1f}分, 評級: {rating}")
        
        return result
        
    except Exception as e:
        logger.error(f"配對計算錯誤: {e}", exc_info=True)
        raise ScoringEngineError(f"配對計算失敗: {str(e)}")

def calculate_bazi(year: int, month: int, day: int, hour: int, 
                  gender: str = "未知", 
                  hour_confidence: str = "high",
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

# 🔖 1.7 統一格式化工具類開始 [行: 2560-2800]
class BaziFormatters:
    """八字格式化工具類 - 統一個人資料和配對結果格式"""
    
    @staticmethod
    def format_personal_data(bazi_data: Dict, username: str = "用戶") -> str:
        """統一個人資料格式化"""
        # 提取性別
        gender = bazi_data.get('gender', '')

        # 提取基本資料
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
        shi_shen_structure = bazi_data.get('shi_shen_structure', '正格')

        # 喜用神和忌神
        useful_elements_list = bazi_data.get('useful_elements', [])
        harmful_elements_list = bazi_data.get('harmful_elements', [])
    
        useful_elements = ','.join(useful_elements_list) if useful_elements_list else '平衡'
        harmful_elements = ','.join(harmful_elements_list) if harmful_elements_list else '無'
        
        # 夫妻星和夫妻宮
        spouse_star_status = bazi_data.get('spouse_star_status', '未知')
        spouse_palace_status = bazi_data.get('spouse_palace_status', '未知')
        spouse_star_effective = bazi_data.get('spouse_star_effective', '未知')
        pressure_score = bazi_data.get('pressure_score', 0)

        # 神煞
        shen_sha_names = bazi_data.get('shen_sha_names', '無')
        shen_sha_bonus = bazi_data.get('shen_sha_bonus', 0)
        
        # 五行分佈
        elements = bazi_data.get('elements', {})
        wood = elements.get('木', 0)
        fire = elements.get('火', 0)
        earth = elements.get('土', 0)
        metal = elements.get('金', 0)
        water = elements.get('水', 0)
        
        # 構建個人資料文本
        personal_text = f"📊 @{username} 的八字分析\n{'='*40}\n\n"

        # 第一行：性別
        personal_text += f"性別:{gender}，\n"
        
        # 第二行：出生時間和信心度
        personal_text += f"{birth_year}年{birth_month}月{birth_day}日{birth_hour}時出生（時間信心度{confidence_text}），\n"
        
        # 第三行：八字四柱
        personal_text += f"八字：{year_pillar} {month_pillar} {day_pillar} {hour_pillar}，\n"
        
        # 第四行：生肖和日主
        personal_text += f"生肖{zodiac}，日主{day_stem}{day_stem_element}（身強弱:{day_stem_strength}，{strength_score:.1f}分）。\n\n"
        
        # 第五行：格局
        personal_text += f"格局：{pattern_type}\n"

        # 第六行：十神結構
        personal_text += f"十神結構：{shi_shen_structure}\n"
        
        # 第七行：喜用神和忌神
        if isinstance(useful_elements, str):
            useful_elements = useful_elements.split(',') if useful_elements else []
        personal_text += f"喜用神：{', '.join(useful_elements) if useful_elements else '無'}\n"
        personal_text += f"忌神：{', '.join(harmful_elements) if harmful_elements else '無'}\n"
        
        # 第八行：夫妻星和夫妻宮
        personal_text += f"夫妻星：{spouse_star_status},{spouse_star_effective},{pressure_score}分\n"
        personal_text += f"夫妻宮：{spouse_palace_status}\n"

        # 第九行：神煞
        personal_text += f"神煞：{shen_sha_names},{shen_sha_bonus}分\n"
        
        # 第十行：五行分佈
        personal_text += f"五行分佈：木{wood:.1f}%、火{fire:.1f}%、土{earth:.1f}%、金{metal:.1f}%、水{water:.1f}%\n"
        
        # ========== 2.5 配對建議生成 ==========
        personal_text += "\n💡 配對建議:\n"
        match_suggestions = BaziFormatters.generate_match_suggestions(bazi_data, gender)
        personal_text += match_suggestions
        
        return personal_text
    
    @staticmethod
    def generate_match_suggestions(bazi_data: Dict, gender: str) -> str:
        """生成配對建議"""
        day_stem_element = bazi_data.get('day_stem_element', '')
        useful_elements = bazi_data.get('useful_elements', [])
        harmful_elements = bazi_data.get('harmful_elements', [])
        
        suggestions = []
        
        # 根據日主五行給建議
        if day_stem_element == '木':
            suggestions.append("適合火、土、金型人（相生或制衡）")
        elif day_stem_element == '火':
            suggestions.append("適合土、金、水型人（相生或制衡）")
        elif day_stem_element == '土':
            suggestions.append("適合金、水、木型人（相生或制衡）")
        elif day_stem_element == '金':
            suggestions.append("適合水、木、火型人（相生或制衡）")
        elif day_stem_element == '水':
            suggestions.append("適合木、火、土型人（相生或制衡）")
        
        # 根據喜用神給建議
        if useful_elements:
            suggestions.append(f"喜用神為 {', '.join(useful_elements)}，可找此五行較旺的對象")
        
        # 根據忌神給避開建議
        if harmful_elements:
            suggestions.append(f"忌神為 {', '.join(harmful_elements)}，應避開此五行過旺的對象")
        
        # 根據性別給建議
        if gender == '男':
            suggestions.append("男性日主適合尋找五行相生的女性")
        else:
            suggestions.append("女性日主適合尋找五行相合的男性")
        
        return "\n".join([f"• {s}" for s in suggestions])
    
    @staticmethod
    def format_match_result(match_result: Dict, bazi1: Dict, bazi2: Dict, 
                          user_a_name: str = "用戶A", user_b_name: str = "用戶B") -> str:
        """統一配對結果格式化"""
        score = match_result.get('score', 0)
        rating = match_result.get('rating', '未知')
        model = match_result.get('relationship_model', '')
        
        # 模組分數
        module_scores = match_result.get('module_scores', {})
        
        # 雙向影響分數
        a_to_b = match_result.get('a_to_b_score', 0)
        b_to_a = match_result.get('b_to_a_score', 0)
        
        # 構建配對結果文本
        result_text = f"🎯 核心分析結果\n{'='*40}\n\n"
        
        # 核心分數和評級
        result_text += f"📊 配對分數：{score:.1f}分\n"
        result_text += f"✨ 評級：{rating}\n"
        result_text += f"🎭 關係模型：{model}\n\n"
        
        # 模組分數
        result_text += "📈 模組分數：\n"
        result_text += f"  💫 能量救應：{module_scores.get('energy_rescue', 0):.1f}分\n"
        result_text += f"  🏗️ 結構核心：{module_scores.get('structure_core', 0):.1f}分\n"
        result_text += f"  ⚠️ 人格風險：{module_scores.get('personality_risk', 0):.1f}分\n"
        result_text += f"  💢 刑沖壓力：{module_scores.get('pressure_penalty', 0):.1f}分\n"
        result_text += f"  ✨ 神煞加持：{module_scores.get('shen_sha_bonus', 0):.1f}分\n"
        result_text += f"  🔧 專業化解：{module_scores.get('resolution_bonus', 0):.1f}分\n\n"
        
        # 雙方個人資訊
        result_text += f"🤝 雙方個人資訊\n{'='*40}\n\n"
        
        # 用戶A個人資料
        a_personal = BaziFormatters.format_personal_data(bazi1, user_a_name)
        result_text += a_personal + "\n"
        
        result_text += f"{'-'*40}\n\n"
        
        # 用戶B個人資料
        b_personal = BaziFormatters.format_personal_data(bazi2, user_b_name)
        result_text += b_personal + "\n"
        
        # 雙向影響分析
        result_text += f"📊 雙向影響分析\n{'='*40}\n\n"
        result_text += f"{user_a_name} 對 {user_b_name} 的影響：{a_to_b:.1f}分\n"
        result_text += f"{user_b_name} 對 {user_a_name} 的影響：{b_to_a:.1f}分\n\n"
        
        # 關係解讀
        result_text += "💡 關係解讀："
        if abs(a_to_b - b_to_a) < 10:
            result_text += "• 雙方影響力相近，屬於平衡型關係\n• 互動平等，互相支持"
        elif a_to_b > b_to_a + 15:
            result_text += f"• {user_a_name}對{user_b_name}影響較強\n• {user_a_name}可能扮演供應者角色"
        elif b_to_a > a_to_b + 15:
            result_text += f"• {user_b_name}對{user_a_name}影響較強\n• {user_b_name}可能扮演供應者角色"
        else:
            result_text += "• 雙方有明顯的供需關係\n• 需要留意平衡點"
        
        result_text += "\n\n"
        
        # 優點與挑戰
        result_text += f"🌟 優點與挑戰\n{'='*40}\n\n"
        
        # 優勢
        result_text += "✅ 優勢：\n"
        if score >= C.THRESHOLD_EXCELLENT_MATCH:
            result_text += "• 五行能量高度互補\n• 結構穩定無硬傷\n• 有明顯的救應機制\n"
        elif score >= C.THRESHOLD_GOOD_MATCH:
            result_text += "• 核心需求能夠對接\n• 主要結構無大沖\n• 有化解機制\n"
        elif score >= C.THRESHOLD_CONTACT_ALLOWED:
            result_text += "• 基本能量可以互補\n• 需要努力經營關係\n"
        else:
            result_text += "• 優勢不明顯，需謹慎考慮\n"
        
        result_text += "\n⚠️ 挑戰：\n"
        
        # 挑戰
        challenges = []
        if module_scores.get('personality_risk', 0) < -10:
            challenges.append("• 人格風險較高，可能性格衝突")
        if module_scores.get('pressure_penalty', 0) < -15:
            challenges.append("• 刑沖壓力較大，容易產生矛盾")
        if module_scores.get('dayun_risk', 0) < -10:
            challenges.append("• 未來大運有挑戰，需要提前準備")
        
        if challenges:
            result_text += "\n".join(challenges) + "\n"
        else:
            result_text += "• 無明顯重大挑戰\n"
        
        result_text += "\n"
        
        # 建議與提醒
        result_text += f"💡 建議與提醒\n{'='*40}\n\n"
        result_text += "💭 建議：\n"
        
        if score >= C.THRESHOLD_EXCELLENT_MATCH:
            result_text += "• 這是極佳的組合，可以深入發展\n• 保持良好溝通，互相支持\n• 珍惜這段緣分，互相成就\n"
        elif score >= C.THRESHOLD_GOOD_MATCH:
            result_text += "• 良好的婚配組合，現實成功率較高\n• 需要互相理解和包容\n• 定期溝通，解決小問題\n"
        elif score >= C.THRESHOLD_CONTACT_ALLOWED:
            result_text += "• 可以嘗試交往，但需謹慎經營\n• 注意溝通方式，避免衝突\n• 需要更多時間了解彼此\n"
        elif score >= C.THRESHOLD_WARNING:
            result_text += "• 關係存在明顯挑戰，需謹慎考慮\n• 建議深入了解後再做決定\n• 不宜匆忙進入長期關係\n"
        else:
            result_text += "• 不建議發展長期關係\n• 建議尋找更合適的配對\n• 避免投入過多情感和資源\n"
        
        return result_text
    
    @staticmethod
    def generate_ai_prompt(match_result: Dict, bazi1: Dict, bazi2: Dict) -> str:
        """AI分析提示格式化"""
        # 先獲取完整的配對結果
        match_text = BaziFormatters.format_match_result(match_result, bazi1, bazi2, "用戶A", "用戶B")
        
        # 添加AI分析問題
        ai_prompt = match_text + f"\n🤖 AI分析提示（請分析以下7個問題）：\n\n"
        
        ai_prompt += """一、能量互補性：
   1. 雙方五行能量如何互補？
   2. 喜用神是否能夠對接？

二、結構穩定性：
   3. 日柱關係（天干五合、地支六合/六沖）如何？
   4. 夫妻宮和夫妻星的狀態如何？

三、潛在挑戰：
   5. 主要的刑沖壓力在哪些方面？
   6. 人格風險和十神結構的影響？

四、發展建議：
   7. 根據關係模型和時間線，給出具體發展建議。

請提供專業、深入的分析，每個問題不少於100字。"""
        
        return ai_prompt
# 🔖 1.7 統一格式化工具類結束

# ========== 修正紀錄開始 ==========
"""
修正內容：
2026-02-02 第二階段調試修正 - 針對測試成功率25%問題的修復

核心問題與修正：
1. 刑沖失效 → 新增詳細DEBUG信息和更嚴格刑沖硬上限
   - 添加詳細日支檢測DEBUG信息
   - 日支六沖：直接封頂40分
   - 日支六害：直接封頂45分

2. 加分失控 → 更嚴格的正向加分飽和機制
   - raw_bonus > 25 後，每分只值0.2分
   - raw_bonus > 15 後，每分只值0.5分
   - 極品組合不超過90分

3. 能量救應不足 → 在下一步修正中加強

4. 相同八字懲罰不足 → 加強懲罰
   - 結構核心減20分（原15）
   - 刑沖壓力乘0.7（原0.8）

5. 最終分數上限調整
   - 最高95分（原98.5）
   - 極品組合不超過90分

預期效果：
- 案例6（強烈沖剋）：75.9 → 預計38分
- 案例15（刑沖嚴重）：83.9 → 預計42分  
- 案例5（喜用互補）：45 → 預計68分（需後續加強能量救應）
- 案例10（極品組合）：98.5 → 預計85分
- 案例11-13（高分案例）：86.9+ → 預計75-82分
- 案例14、18（天干五合）：98.5 → 預計80-85分
- 案例9（相同八字）：63 → 預計48分

下一步：
1. 跑測試看audit log，確認刑沖檢測是否正確
2. 根據結果調整能量救應加成
3. 可能調整刑沖壓力模組的扣分力度
"""
# ========== 修正紀錄結束 ==========