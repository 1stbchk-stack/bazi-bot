# ========1.1 導入模組開始 ========#
import os
import logging
import hashlib
import random
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import sxtwl

# 導入配置常量（從原bot.py拆分）
MASTER_BAZI_CONFIG = {
    # 師傅級鐵律：只設一個主鎖 + 一個次鎖
    "LOCK_SYSTEM": {
        "primary_locks": {
            "broken_pattern": 45,          # 破格或被破格
            "no_carriage": 48,             # 空承載（雙方都無配偶星）
        },
        "secondary_locks": {
            "disordered_palace": 62,       # 夫妻宮失序
            "opposite_useful": 62,         # 喜用完全相反
        },
        "soft_adjustments": {
            "weak_spouse_star": -8,        # 配偶星弱
            "medium_pressure": -5,         # 中等壓力
            "cold_warm_mismatch": -3,      # 寒暖不調
        }
    },
    
    # 基礎分保障（避免20分地獄）
    "BASE_PROTECTION": {
        "non_broken_minimum": 45,          # 非破局最低分
        "base_score": 50,                  # 基礎分
    },
    
    # 模組權重（師傅級重新分配）
    "MODULE_WEIGHTS": {
        "spouse_carriage": 32,             # 配偶承載匹配（最重要）
        "day_pillar": 28,                  # 日柱基礎配合
        "personality": 22,                 # 十神性格互補
        "energy_flow": 18,                 # 氣勢平衡流通
    },
    
    # 分數對應關係
    "THRESHOLDS": {
        "display_match": 40,
        "contact_exchange": 60,
        "good_match": 70,
        "excellent_match": 80,
    },
    
    # 解局系統（只解對應病位）
    "RESOLUTION_SYSTEM": {
        "strong_resolution": 1.15,         # 強解：天地德合+通關用神
        "medium_resolution": 1.10,         # 中解：有三合/半三合
        "weak_resolution": 0.85,           # 弱解：只有六合
        "no_resolution": 1.0,              # 無解
    },
    
    # 神煞加分系統（師傅級互動計算）
    "SHEN_SHA_BONUS": {
        "hong_luan": 8,                    # 紅鸞（正緣）
        "tian_xi": 6,                      # 天喜（喜慶）
        "tian_yi": 8,                      # 天乙貴人
        "tian_de": 5,                      # 天德（化解）
        "tao_hua": 5,                      # 桃花（姻緣）
        "yang_ren": -3,                    # 羊刃（衝突）
        "max_bonus": 20,                   # 最大加分
    }
}

# 日誌配置
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# ========1.1 導入模組結束 ========#

# ========1.2 錯誤處理類開始 ========#
class BaziError(Exception):
    pass

class MatchError(Exception):
    pass

def safe_calculate(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} 錯誤: {e}")
            raise BaziError(f"八字計算失敗: {str(e)}")
    return wrapper
# ========1.2 錯誤處理類結束 ========#

# ========1.3 專業八字計算類開始 ========#
class ProfessionalBaziCalculator:
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

    MONTH_STRENGTH = {
        '木': {'寅': 1.0, '卯': 1.0, '辰': 0.7, '巳': 0.3, '午': 0.0, '未': 0.0, '申': 0.0, '酉': 0.0, '戌': 0.0, '亥': 0.8, '子': 0.6, '丑': 0.3},
        '火': {'寅': 0.8, '卯': 0.6, '辰': 0.3, '巳': 1.0, '午': 1.0, '未': 0.7, '申': 0.0, '酉': 0.0, '戌': 0.3, '亥': 0.0, '子': 0.0, '丑': 0.0},
        '土': {'寅': 0.3, '卯': 0.0, '辰': 1.0, '巳': 0.7, '午': 0.7, '未': 1.0, '申': 0.3, '酉': 0.0, '戌': 1.0, '亥': 0.0, '子': 0.0, '丑': 1.0},
        '金': {'寅': 0.0, '卯': 0.0, '辰': 0.3, '巳': 0.6, '午': 0.0, '未': 0.0, '申': 1.0, '酉': 1.0, '戌': 0.7, '亥': 0.0, '子': 0.0, '丑': 0.8},
        '水': {'寅': 0.0, '卯': 0.0, '辰': 0.0, '巳': 0.0, '午': 0.0, '未': 0.0, '申': 0.8, '酉': 0.6, '戌': 0.0, '亥': 1.0, '子': 1.0, '丑': 0.7}
    }

    SPOUSE_STARS = {
        '男': {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'},
        '女': {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
    }

    ELEMENT_GENERATE = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    ELEMENT_OVERCOME = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}
    ELEMENT_OVERCOME_BY = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}

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

    STEM_COMBINATIONS = [
        ('甲', '己'), ('乙', '庚'), ('丙', '辛'), ('丁', '壬'), ('戊', '癸')
    ]

    # 神煞對照表（師傅級完整版）
    SHEN_SHA_TABLES = {
        # 桃花（咸池桃花）
        'tao_hua': {
            ('子', '辰', '申'): '卯',
            ('丑', '巳', '酉'): '子',
            ('寅', '午', '戌'): '酉',
            ('卯', '未', '亥'): '午'
        },
        # 紅鸞
        'hong_luan': {
            '子': '午', '丑': '巳', '寅': '辰', '卯': '卯',
            '辰': '寅', '巳': '丑', '午': '子', '未': '亥',
            '申': '戌', '酉': '酉', '戌': '申', '亥': '未'
        },
        # 天喜（相對紅鸞）
        'tian_xi': {
            '子': '寅', '丑': '丑', '寅': '子', '卯': '亥',
            '辰': '戌', '巳': '酉', '午': '申', '未': '未',
            '申': '午', '酉': '巳', '戌': '辰', '亥': '卯'
        },
        # 羊刃（負煞）
        'yang_ren': {
            '甲': '卯', '乙': '辰', '丙': '午', '丁': '未',
            '戊': '午', '己': '未', '庚': '酉', '辛': '戌',
            '壬': '子', '癸': '丑'
        },
        # 天乙貴人
        'tian_yi': {
            '甲': ['丑', '未'], '乙': ['子', '申'], '丙': ['亥', '酉'],
            '丁': ['亥', '酉'], '戊': ['丑', '未'], '己': ['子', '申'],
            '庚': ['丑', '未'], '辛': ['寅', '午'], '壬': ['寅', '午'],
            '癸': ['寅', '午']
        },
        # 天德（月德）
        'tian_de': {
            '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
            '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
            '戌': '丙', '亥': '乙', '子': '己', '丑': '庚'
        }
    }

    @staticmethod
    def hour_to_branch_hour(hour):
        """將24小時制轉換為地支時辰"""
        if hour == 23 or hour == 0:
            return 0  # 子
        elif hour == 1 or hour == 2:
            return 1  # 丑
        elif hour == 3 or hour == 4:
            return 2  # 寅
        elif hour == 5 or hour == 6:
            return 3  # 卯
        elif hour == 7 or hour == 8:
            return 4  # 辰
        elif hour == 9 or hour == 10:
            return 5  # 巳
        elif hour == 11 or hour == 12:
            return 6  # 午
        elif hour == 13 or hour == 14:
            return 7  # 未
        elif hour == 15 or hour == 16:
            return 8  # 申
        elif hour == 17 or hour == 18:
            return 9  # 酉
        elif hour == 19 or hour == 20:
            return 10  # 戌
        else:
            return 11  # 亥

    @staticmethod
    def calculate_correct_hour_pillar(year, month, day, hour):
        """計算正確的時柱"""
        try:
            day_obj = sxtwl.fromSolar(year, month, day)
            d_gz = day_obj.getDayGZ()
            day_stem = d_gz.tg
            hour_branch = ProfessionalBaziCalculator.hour_to_branch_hour(hour)

            # 五鼠遁日起時法
            day_stem_mod = day_stem % 5
            if day_stem_mod == 0:  # 甲己
                start_stem = 0  # 甲
            elif day_stem_mod == 1:  # 乙庚
                start_stem = 2  # 丙
            elif day_stem_mod == 2:  # 丙辛
                start_stem = 4  # 戊
            elif day_stem_mod == 3:  # 丁壬
                start_stem = 6  # 庚
            else:  # 戊癸
                start_stem = 8  # 壬

            hour_stem = (start_stem + hour_branch) % 10
            return f"{ProfessionalBaziCalculator.STEMS[hour_stem]}{ProfessionalBaziCalculator.BRANCHES[hour_branch]}"
        except Exception as e:
            logger.error(f"計算時柱錯誤: {e}")
            return "甲子"

    @staticmethod
    def get_stem_name(code):
        return ProfessionalBaziCalculator.STEMS[code] if 0 <= code < 10 else ''

    @staticmethod
    def get_branch_name(code):
        return ProfessionalBaziCalculator.BRANCHES[code] if 0 <= code < 12 else ''

    @staticmethod
    def check_day_stem_root_and_print(bazi):
        """嚴格檢查日主是否有根或印（從格判斷基礎）"""
        day_stem = bazi.get('day_stem', '')
        day_stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        
        branches = [
            bazi.get('year_pillar', '  ')[1],
            bazi.get('month_pillar', '  ')[1],
            bazi.get('day_pillar', '  ')[1],
            bazi.get('hour_pillar', '  ')[1]
        ]
        
        has_root = False
        for branch in branches:
            hidden_stems = ProfessionalBaziCalculator.BRANCH_HIDDEN_STEMS.get(branch, [])
            for stem, weight in hidden_stems:
                if ProfessionalBaziCalculator.STEM_ELEMENTS.get(stem, '') == day_stem_element:
                    if weight >= 0.5:
                        has_root = True
                        break
            if has_root:
                break
        
        has_print = False
        print_elements = []
        for base_element, gen_element in ProfessionalBaziCalculator.ELEMENT_GENERATE.items():
            if gen_element == day_stem_element:
                print_elements.append(base_element)
        
        stems = [
            bazi.get('year_pillar', '  ')[0],
            bazi.get('month_pillar', '  ')[0],
            bazi.get('day_pillar', '  ')[0],
            bazi.get('hour_pillar', '  ')[0]
        ]
        
        for stem in stems:
            element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(stem, '')
            if element in print_elements:
                has_print = True
                break
        
        if not has_print:
            for branch in branches:
                element = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(branch, '')
                if element in print_elements:
                    has_print = True
                    break
        
        return has_root, has_print

    @staticmethod
    def calculate_strength_score(bazi):
        """改進的身強弱計算（物理意義明確）"""
        day_stem = bazi.get('day_stem', '')
        day_stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        if not day_stem_element:
            return 50

        score = 0
        month_branch = bazi.get('month_pillar', '  ')[1] if len(bazi.get('month_pillar', '  ')) >= 2 else ''
        
        month_strength = ProfessionalBaziCalculator.MONTH_STRENGTH.get(day_stem_element, {}).get(month_branch, 0)
        score += month_strength * 35
        
        month_element = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(month_branch, '')
        if month_element == ProfessionalBaziCalculator.ELEMENT_OVERCOME_BY.get(day_stem_element):
            score -= 15

        day_branch = bazi.get('day_pillar', '  ')[1] if len(bazi.get('day_pillar', '  ')) >= 2 else ''
        hidden_stems = ProfessionalBaziCalculator.BRANCH_HIDDEN_STEMS.get(day_branch, [])
        tong_gen_score = 0
        for stem, weight in hidden_stems:
            if ProfessionalBaziCalculator.STEM_ELEMENTS.get(stem, '') == day_stem_element:
                tong_gen_score = weight * 25
                break
        score += tong_gen_score

        other_branches = [
            bazi.get('year_pillar', '  ')[1],
            bazi.get('month_pillar', '  ')[1],
            bazi.get('hour_pillar', '  ')[1]
        ]

        for branch in other_branches:
            hidden_stems = ProfessionalBaziCalculator.BRANCH_HIDDEN_STEMS.get(branch, [])
            for stem, weight in hidden_stems:
                if ProfessionalBaziCalculator.STEM_ELEMENTS.get(stem, '') == day_stem_element:
                    score += min(10, weight * 10)

        other_stems = [
            bazi.get('year_pillar', '  ')[0],
            bazi.get('month_pillar', '  ')[0],
            bazi.get('hour_pillar', '  ')[0]
        ]

        for stem in other_stems:
            stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(stem, '')
            if stem_element == day_stem_element:
                score += 5
                break

        return min(100, max(0, score))

    @staticmethod
    def determine_strength(strength_score):
        """根據分數判斷身強弱"""
        if strength_score >= 65:
            return '強'
        elif strength_score >= 35:
            return '中'
        else:
            return '弱'

    @staticmethod
    def calculate_cong_ge_type(bazi, gender):
        """判斷從格類型（嚴格條件）"""
        day_stem = bazi.get('day_stem', '')
        day_stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        
        has_root, has_print = ProfessionalBaziCalculator.check_day_stem_root_and_print(bazi)
        
        if has_root or has_print:
            return 'normal'
        
        stems = [
            bazi.get('year_pillar', '  ')[0],
            bazi.get('month_pillar', '  ')[0],
            bazi.get('day_pillar', '  ')[0],
            bazi.get('hour_pillar', '  ')[0]
        ]
        
        for stem in stems:
            pair = tuple(sorted([day_stem, stem]))
            if pair in ProfessionalBaziCalculator.STEM_COMBINATIONS:
                return 'normal'
        
        strength_score = bazi.get('strength_score', 50)
        elements = bazi.get('elements', {})
        
        if strength_score < 20:
            element_scores = {}
            for element, percent in elements.items():
                if element != day_stem_element:
                    element_scores[element] = percent
            
            if element_scores:
                max_element = max(element_scores.items(), key=lambda x: x[1])[0]
                if ProfessionalBaziCalculator.ELEMENT_OVERCOME_BY.get(day_stem_element) == max_element:
                    return f'從{max_element}格'
                elif ProfessionalBaziCalculator.ELEMENT_GENERATE.get(day_stem_element) == max_element:
                    return f'從{max_element}格'
        
        elif strength_score > 85:
            day_element_percent = elements.get(day_stem_element, 0)
            if day_element_percent > 70:
                return f'專旺{day_stem_element}格'

        return 'normal'

    @staticmethod
    def calculate_useful_elements(bazi, gender):
        """改進的用神計算（由格局推導，禁止比例反推）"""
        day_stem = bazi.get('day_stem', '')
        day_stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        strength = bazi.get('day_stem_strength', '中')
        strength_score = bazi.get('strength_score', 50)
        cong_ge_type = bazi.get('cong_ge_type', 'normal')

        useful_elements = []

        if '從' in cong_ge_type:
            target_element = cong_ge_type.replace('從', '').replace('格', '')
            if target_element:
                useful_elements.append(target_element)
        elif '專旺' in cong_ge_type:
            target_element = cong_ge_type.replace('專旺', '').replace('格', '')
            if target_element:
                useful_elements.append(target_element)
                for base_element, gen_element in ProfessionalBaziCalculator.ELEMENT_GENERATE.items():
                    if gen_element == target_element:
                        useful_elements.append(base_element)
        else:
            if strength == '強':
                if day_stem_element in ProfessionalBaziCalculator.ELEMENT_OVERCOME_BY:
                    useful_elements.append(ProfessionalBaziCalculator.ELEMENT_OVERCOME_BY[day_stem_element])
                
                if day_stem_element in ProfessionalBaziCalculator.ELEMENT_GENERATE:
                    useful_elements.append(ProfessionalBaziCalculator.ELEMENT_GENERATE[day_stem_element])
                
                if day_stem_element in ProfessionalBaziCalculator.ELEMENT_OVERCOME:
                    useful_elements.append(ProfessionalBaziCalculator.ELEMENT_OVERCOME[day_stem_element])
            
            elif strength == '弱':
                for base_element, gen_element in ProfessionalBaziCalculator.ELEMENT_GENERATE.items():
                    if gen_element == day_stem_element:
                        useful_elements.append(base_element)
                
                useful_elements.append(day_stem_element)
            
            else:
                month_branch = bazi.get('month_pillar', '  ')[1] if len(bazi.get('month_pillar', '  ')) >= 2 else ''
                month_element = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(month_branch, '')
                
                if month_element in ['子', '丑', '亥']:
                    useful_elements.append('火')
                elif month_element in ['巳', '午', '未']:
                    useful_elements.append('水')
                elif month_element in ['寅', '卯']:
                    useful_elements.append('金')
                elif month_element in ['申', '酉']:
                    useful_elements.append('木')
        
        return list(set([e for e in useful_elements if e]))

    @staticmethod
    def calculate_harmful_elements(bazi, gender):
        """改進的忌神計算（根據格局和用神推導）"""
        day_stem = bazi.get('day_stem', '')
        day_stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        strength = bazi.get('day_stem_strength', '中')
        cong_ge_type = bazi.get('cong_ge_type', 'normal')
        useful_elements = bazi.get('useful_elements', [])

        harmful_elements = []

        if '從' in cong_ge_type:
            target_element = cong_ge_type.replace('從', '').replace('格', '')
            if target_element:
                if target_element in ProfessionalBaziCalculator.ELEMENT_OVERCOME_BY:
                    harmful_elements.append(ProfessionalBaziCalculator.ELEMENT_OVERCOME_BY[target_element])
                if target_element in ProfessionalBaziCalculator.ELEMENT_GENERATE:
                    harmful_elements.append(ProfessionalBaziCalculator.ELEMENT_GENERATE[target_element])
                if target_element in ProfessionalBaziCalculator.ELEMENT_OVERCOME:
                    harmful_elements.append(ProfessionalBaziCalculator.ELEMENT_OVERCOME[target_element])
        
        elif '專旺' in cong_ge_type:
            target_element = cong_ge_type.replace('專旺', '').replace('格', '')
            if target_element:
                if target_element in ProfessionalBaziCalculator.ELEMENT_OVERCOME_BY:
                    harmful_elements.append(ProfessionalBaziCalculator.ELEMENT_OVERCOME_BY[target_element])
                if target_element in ProfessionalBaziCalculator.ELEMENT_GENERATE:
                    harmful_elements.append(ProfessionalBaziCalculator.ELEMENT_GENERATE[target_element])
                if target_element in ProfessionalBaziCalculator.ELEMENT_OVERCOME:
                    harmful_elements.append(ProfessionalBaziCalculator.ELEMENT_OVERCOME[target_element])
        
        else:
            if strength == '強':
                for base_element, gen_element in ProfessionalBaziCalculator.ELEMENT_GENERATE.items():
                    if gen_element == day_stem_element:
                        harmful_elements.append(base_element)
                
                harmful_elements.append(day_stem_element)
            
            elif strength == '弱':
                if day_stem_element in ProfessionalBaziCalculator.ELEMENT_OVERCOME_BY:
                    harmful_elements.append(ProfessionalBaziCalculator.ELEMENT_OVERCOME_BY[day_stem_element])
                
                if day_stem_element in ProfessionalBaziCalculator.ELEMENT_GENERATE:
                    harmful_elements.append(ProfessionalBaziCalculator.ELEMENT_GENERATE[day_stem_element])
                
                if day_stem_element in ProfessionalBaziCalculator.ELEMENT_OVERCOME:
                    harmful_elements.append(ProfessionalBaziCalculator.ELEMENT_OVERCOME[day_stem_element])
            
            else:
                elements = bazi.get('elements', {})
                for element, percent in elements.items():
                    if percent > 30:
                        harmful_elements.append(element)
        
        harmful_elements = [e for e in harmful_elements if e not in useful_elements]
        
        return list(set([e for e in harmful_elements if e]))

    @staticmethod
    def analyze_spouse_star(bazi, gender):
        """分析夫妻星"""
        day_stem = bazi.get('day_stem', '')
        day_stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        if gender not in ['男', '女']:
            return '未知', '未知'

        spouse_element = ProfessionalBaziCalculator.SPOUSE_STARS[gender].get(day_stem_element, '')
        if not spouse_element:
            return '無夫妻星', '無'

        all_stems = [
            bazi.get('year_pillar', '  ')[0],
            bazi.get('month_pillar', '  ')[0],
            bazi.get('day_pillar', '  ')[0],
            bazi.get('hour_pillar', '  ')[0]
        ]

        all_branches = [
            bazi.get('year_pillar', '  ')[1],
            bazi.get('month_pillar', '  ')[1],
            bazi.get('day_pillar', '  ')[1],
            bazi.get('hour_pillar', '  ')[1]
        ]

        stem_count = sum(1 for stem in all_stems if ProfessionalBaziCalculator.STEM_ELEMENTS.get(stem, '') == spouse_element)
        branch_count = sum(1 for branch in all_branches if ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(branch, '') == spouse_element)

        hidden_count = 0
        for branch in all_branches:
            hidden_stems = ProfessionalBaziCalculator.BRANCH_HIDDEN_STEMS.get(branch, [])
            for stem, weight in hidden_stems:
                if ProfessionalBaziCalculator.STEM_ELEMENTS.get(stem, '') == spouse_element:
                    hidden_count += 1

        total_count = stem_count + branch_count + hidden_count

        effective = '未知'
        if total_count == 0:
            status = '無夫妻星'
            effective = '無'
        elif total_count == 1:
            month_branch = bazi.get('month_pillar', '  ')[1] if len(bazi.get('month_pillar', '  ')) >= 2 else ''
            month_element = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(month_branch, '')
            
            if month_element == spouse_element:
                status = '夫妻星得月令'
                effective = '中'
            else:
                has_root = False
                for branch in all_branches:
                    element = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(branch, '')
                    if element == spouse_element:
                        has_root = True
                        break
                
                if has_root:
                    status = '夫妻星有根'
                    effective = '中'
                else:
                    status = '夫妻星單一'
                    effective = '弱'
        elif total_count >= 2:
            month_branch = bazi.get('month_pillar', '  ')[1] if len(bazi.get('month_pillar', '  ')) >= 2 else ''
            month_element = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(month_branch, '')
            
            clashes = {'子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
                      '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
            
            is_clashed = False
            for branch in all_branches:
                clash_branch = clashes.get(branch)
                if clash_branch and clash_branch in all_branches:
                    is_clashed = True
                    break
            
            if month_element == spouse_element and not is_clashed:
                status = '夫妻星明顯且有效'
                effective = '強'
            elif is_clashed:
                status = '夫妻星被沖但仍有力'
                effective = '中'
            else:
                status = '夫妻星明顯'
                effective = '強'
        else:
            status = '夫妻星混雜'
            effective = '中'

        return status, effective

    @staticmethod
    def analyze_spouse_palace(bazi):
        """分析夫妻宮（計算壓力分數，考慮刑沖害疊加）"""
        day_branch = bazi.get('day_pillar', '  ')[1] if len(bazi.get('day_pillar', '  ')) >= 2 else ''
        if not day_branch:
            return '未知', 0

        year_branch = bazi.get('year_pillar', '  ')[1]
        month_branch = bazi.get('month_pillar', '  ')[1]
        hour_branch = bazi.get('hour_pillar', '  ')[1]

        other_branches = [year_branch, month_branch, hour_branch]

        clashes = {'子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
                  '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}

        harms = {'子': '未', '未': '子', '丑': '午', '午': '丑', '寅': '巳', '巳': '寅',
                '卯': '辰', '辰': '卯', '申': '亥', '亥': '申', '酉': '戌', '戌': '酉'}

        self_penalty = {'辰': '辰', '午': '午', '酉': '酉', '亥': '亥'}

        pressure_score = 0
        
        for other_branch in other_branches:
            if clashes.get(day_branch) == other_branch:
                pressure_score += 40
                break
        
        if pressure_score == 0:
            for other_branch in other_branches:
                if harms.get(day_branch) == other_branch:
                    pressure_score += 25
                    break
        
        if pressure_score == 0 and day_branch in self_penalty:
            pressure_score += 20
        
        other_pressure = 0
        for i in range(len(other_branches)):
            for j in range(i+1, len(other_branches)):
                b1, b2 = other_branches[i], other_branches[j]
                if (b1, b2) in clashes.items() or (b2, b1) in clashes.items():
                    other_pressure += 15
                elif (b1, b2) in harms.items() or (b2, b1) in harms.items():
                    other_pressure += 10
                elif b1 in self_penalty and b1 == b2:
                    other_pressure += 8
        
        pressure_score += min(20, other_pressure)
        
        if pressure_score >= 40:
            status = '日支嚴重受沖'
        elif pressure_score >= 25:
            status = '日支相害'
        elif pressure_score >= 20:
            status = '日支自刑'
        elif pressure_score >= 10:
            status = '日支輕微受壓'
        else:
            status = '日支穩定'

        return status, pressure_score

    @staticmethod
    def calculate_confidence_level(hour_known, approximate_hour=None):
        """計算信心度（返回中文）"""
        if hour_known == 'yes':
            return '高', '高（時辰準確）'
        elif hour_known == 'no':
            return '低', '低（時辰未知）'
        elif hour_known == 'approximate':
            if approximate_hour is not None:
                return '中', f'中（約{approximate_hour}時）'
            else:
                return '低', '低（時辰估算）'
        else:
            return '未知', '未知'

    @staticmethod
    def estimate_hour_from_description(description):
        """從描述估算時辰"""
        description = description.lower()

        if any(word in description for word in ['深夜', '半夜', '子夜', '凌晨前']):
            return 0
        elif any(word in description for word in ['凌晨', '丑時', '雞鳴']):
            return 2
        elif any(word in description for word in ['清晨', '黎明', '寅時', '平旦']):
            return 4
        elif any(word in description for word in ['早晨', '日出', '卯時', '早上']):
            return 6
        elif any(word in description for word in ['上午', '辰時', '食時', '早上']):
            return 8
        elif any(word in description for word in ['上午', '巳時', '隅中']):
            return 10
        elif any(word in description for word in ['中午', '正午', '午時', '日中']):
            return 12
        elif any(word in description for word in ['下午', '未時', '日昳']):
            return 14
        elif any(word in description for word in ['下午', '申時', '晡時']):
            return 16
        elif any(word in description for word in ['傍晚', '酉時', '日入', '黃昏']):
            return 18
        elif any(word in description for word in ['晚上', '戌時', '黃昏', '日暮']):
            return 20
        elif any(word in description for word in ['晚上', '亥時', '人定', '夜晚']):
            return 22
        else:
            return 12

    @staticmethod
    def calculate_shi_shen_structure(bazi, gender):
        """計算十神結構"""
        day_stem = bazi.get('day_stem', '')
        stems = [
            bazi.get('year_pillar', '  ')[0],
            bazi.get('month_pillar', '  ')[0],
            bazi.get('day_pillar', '  ')[0],
            bazi.get('hour_pillar', '  ')[0]
        ]

        shi_shen_list = []
        shi_shen_map = ProfessionalBaziCalculator.SHI_SHEN_MAP.get(day_stem, {})

        for stem in stems:
            if stem and stem in shi_shen_map:
                shi_shen_list.append(shi_shen_map[stem])

        has_zheng_cai = '正財' in shi_shen_list
        has_pian_cai = '偏財' in shi_shen_list
        has_zheng_guan = '正官' in shi_shen_list
        has_qi_sha = '七殺' in shi_shen_list
        has_shang_guan = '傷官' in shi_shen_list

        structure = []
        if has_zheng_cai and has_zheng_guan:
            structure.append('財官雙美')
        if has_shang_guan and (has_zheng_guan or has_qi_sha):
            structure.append('傷官見官')
        if has_zheng_guan and has_qi_sha:
            structure.append('官殺混雜')
        if has_pian_cai and '劫財' in shi_shen_list:
            structure.append('財星遇劫')

        return ','.join(shi_shen_list), ','.join(structure) if structure else '正常'

    @staticmethod
    def calculate_shen_sha_data(bazi):
        """計算神煞數據（師傅級完整版）"""
        shen_sha_list = []
        total_bonus = 0
        
        year_branch = bazi.get('year_pillar', '  ')[1]
        day_branch = bazi.get('day_pillar', '  ')[1]
        month_branch = bazi.get('month_pillar', '  ')[1]
        day_stem = bazi.get('day_stem', '')
        
        # 所有支柱
        all_branches = [
            bazi.get('year_pillar', '  ')[1],
            bazi.get('month_pillar', '  ')[1],
            bazi.get('day_pillar', '  ')[1],
            bazi.get('hour_pillar', '  ')[1]
        ]
        
        all_stems = [
            bazi.get('year_pillar', '  ')[0],
            bazi.get('month_pillar', '  ')[0],
            bazi.get('day_pillar', '  ')[0],
            bazi.get('hour_pillar', '  ')[0]
        ]
        
        # 1. 桃花計算
        tao_hua_table = ProfessionalBaziCalculator.SHEN_SHA_TABLES['tao_hua']
        for key, value in tao_hua_table.items():
            if year_branch in key:
                if value in all_branches:
                    shen_sha_list.append(f'桃花:{value}')
                    total_bonus += MASTER_BAZI_CONFIG['SHEN_SHA_BONUS']['tao_hua']
                break
        
        # 2. 紅鸞計算
        hong_luan_zhi = ProfessionalBaziCalculator.SHEN_SHA_TABLES['hong_luan'].get(year_branch)
        if hong_luan_zhi and hong_luan_zhi in all_branches:
            shen_sha_list.append(f'紅鸞:{hong_luan_zhi}')
            total_bonus += MASTER_BAZI_CONFIG['SHEN_SHA_BONUS']['hong_luan']
        
        # 3. 天喜計算
        tian_xi_zhi = ProfessionalBaziCalculator.SHEN_SHA_TABLES['tian_xi'].get(year_branch)
        if tian_xi_zhi and tian_xi_zhi in all_branches:
            shen_sha_list.append(f'天喜:{tian_xi_zhi}')
            total_bonus += MASTER_BAZI_CONFIG['SHEN_SHA_BONUS']['tian_xi']
        
        # 4. 羊刃計算（負煞）
        yang_ren_zhi = ProfessionalBaziCalculator.SHEN_SHA_TABLES['yang_ren'].get(day_stem)
        if yang_ren_zhi and yang_ren_zhi in all_branches:
            shen_sha_list.append(f'羊刃:{yang_ren_zhi}')
            total_bonus += MASTER_BAZI_CONFIG['SHEN_SHA_BONUS']['yang_ren']
        
        # 5. 天乙貴人計算
        tian_yi_zhis = ProfessionalBaziCalculator.SHEN_SHA_TABLES['tian_yi'].get(day_stem, [])
        for zhi in tian_yi_zhis:
            if zhi in all_branches:
                shen_sha_list.append(f'天乙貴人:{zhi}')
                total_bonus += MASTER_BAZI_CONFIG['SHEN_SHA_BONUS']['tian_yi']
                break
        
        # 6. 天德計算
        tian_de_gan = ProfessionalBaziCalculator.SHEN_SHA_TABLES['tian_de'].get(month_branch)
        if tian_de_gan and tian_de_gan in all_stems:
            shen_sha_list.append(f'天德:{tian_de_gan}')
            total_bonus += MASTER_BAZI_CONFIG['SHEN_SHA_BONUS']['tian_de']
        
        # 上限控制
        max_bonus = MASTER_BAZI_CONFIG['SHEN_SHA_BONUS']['max_bonus']
        total_bonus = min(max_bonus, total_bonus)
        
        return ','.join(shen_sha_list) if shen_sha_list else '無', total_bonus

    @safe_calculate
    @staticmethod
    def calculate_bazi(year, month, day, hour, gender='未知', hour_confidence='高'):
        try:
            day_obj = sxtwl.fromSolar(year, month, day)
            y_gz = day_obj.getYearGZ()
            m_gz = day_obj.getMonthGZ()
            d_gz = day_obj.getDayGZ()

            year_pillar = f"{ProfessionalBaziCalculator.get_stem_name(y_gz.tg)}{ProfessionalBaziCalculator.get_branch_name(y_gz.dz)}"
            month_pillar = f"{ProfessionalBaziCalculator.get_stem_name(m_gz.tg)}{ProfessionalBaziCalculator.get_branch_name(m_gz.dz)}"
            day_pillar = f"{ProfessionalBaziCalculator.get_stem_name(d_gz.tg)}{ProfessionalBaziCalculator.get_branch_name(d_gz.dz)}"
            hour_pillar = ProfessionalBaziCalculator.calculate_correct_hour_pillar(year, month, day, hour)

            day_stem = ProfessionalBaziCalculator.get_stem_name(d_gz.tg)
            day_stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem, '')

            zodiac_list = ['鼠', '牛', '虎', '兔', '龍', '蛇', '馬', '羊', '猴', '雞', '狗', '豬']
            zodiac = zodiac_list[y_gz.dz] if 0 <= y_gz.dz < 12 else '未知'

            elements = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}

            for pillar, weight in [(year_pillar, 1.0), (month_pillar, 1.8), (day_pillar, 1.5), (hour_pillar, 1.2)]:
                if len(pillar) >= 2:
                    stem = pillar[0]
                    branch = pillar[1]
                    
                    stem_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(stem, '')
                    if stem_element:
                        elements[stem_element] += weight
                    
                    branch_element = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(branch, '')
                    if branch_element:
                        elements[branch_element] += weight * 0.5
                    
                    hidden_stems = ProfessionalBaziCalculator.BRANCH_HIDDEN_STEMS.get(branch, [])
                    for hidden_stem, hidden_weight in hidden_stems:
                        hidden_element = ProfessionalBaziCalculator.STEM_ELEMENTS.get(hidden_stem, '')
                        if hidden_element:
                            elements[hidden_element] += weight * hidden_weight

            total = sum(elements.values())
            if total > 0:
                for element in elements:
                    elements[element] = round(elements[element] * 100 / total, 1)

            bazi_data = {
                "year_pillar": year_pillar,
                "month_pillar": month_pillar,
                "day_pillar": day_pillar,
                "hour_pillar": hour_pillar,
                "zodiac": zodiac,
                "day_stem": day_stem,
                "day_stem_element": day_stem_element,
                "elements": elements,
                "hour_confidence": hour_confidence
            }

            strength_score = ProfessionalBaziCalculator.calculate_strength_score(bazi_data)
            bazi_data["strength_score"] = strength_score
            strength = ProfessionalBaziCalculator.determine_strength(strength_score)
            bazi_data["day_stem_strength"] = strength

            cong_ge_type = ProfessionalBaziCalculator.calculate_cong_ge_type(bazi_data, gender)
            bazi_data["cong_ge_type"] = cong_ge_type

            shi_shen_list, shi_shen_structure = ProfessionalBaziCalculator.calculate_shi_shen_structure(bazi_data, gender)
            bazi_data["shi_shen_list"] = shi_shen_list
            bazi_data["shi_shen_structure"] = shi_shen_structure

            useful_elements = ProfessionalBaziCalculator.calculate_useful_elements(bazi_data, gender)
            bazi_data["useful_elements"] = useful_elements
            
            harmful_elements = ProfessionalBaziCalculator.calculate_harmful_elements(bazi_data, gender)
            bazi_data["harmful_elements"] = harmful_elements

            spouse_star_status, spouse_star_effective = ProfessionalBaziCalculator.analyze_spouse_star(bazi_data, gender)
            bazi_data["spouse_star_status"] = spouse_star_status
            bazi_data["spouse_star_effective"] = spouse_star_effective

            spouse_palace_status, pressure_score = ProfessionalBaziCalculator.analyze_spouse_palace(bazi_data)
            bazi_data["spouse_palace_status"] = spouse_palace_status
            bazi_data["pressure_score"] = pressure_score

            # 計算神煞數據
            shen_sha_names, shen_sha_bonus = ProfessionalBaziCalculator.calculate_shen_sha_data(bazi_data)
            bazi_data["shen_sha_names"] = shen_sha_names
            bazi_data["shen_sha_bonus"] = shen_sha_bonus

            logger.info(f"八字計算完成: {year_pillar} {month_pillar} {day_pillar} {hour_pillar}")
            logger.info(f"日主: {day_stem}({day_stem_element}), 身強弱: {strength}({strength_score}分)")
            logger.info(f"從格類型: {cong_ge_type}")
            logger.info(f"用神: {','.join(useful_elements)}, 忌神: {','.join(harmful_elements)}")
            logger.info(f"夫妻星: {spouse_star_status}({spouse_star_effective}), 夫妻宮: {spouse_palace_status}(壓力分數: {pressure_score})")
            logger.info(f"神煞: {shen_sha_names} (+{shen_sha_bonus}分)")

            return bazi_data

        except Exception as e:
            logger.error(f"八字計算錯誤: {e}", exc_info=True)
            raise BaziError(f"八字計算失敗: {str(e)}")
# ========1.3 專業八字計算類結束 ========#

# ========1.4 終極師傅級配對算法開始 ========#
class MasterBaziMatcher:
    """師傅級八字配對算法（整合所有改進）"""
    
    STEM_FIVE_COMBINATIONS = {
        ('甲', '己'): '土', ('乙', '庚'): '金', ('丙', '辛'): '水',
        ('丁', '壬'): '木', ('戊', '癸'): '火'
    }

    BRANCH_SIX_COMBINATIONS = {
        ('子', '丑'): '土', ('寅', '亥'): '木', ('卯', '戌'): '火',
        ('辰', '酉'): '金', ('巳', '申'): '水', ('午', '未'): '土'
    }

    BRANCH_THREE_COMBINATIONS = [
        {'申', '子', '辰'}, {'亥', '卯', '未'},
        {'寅', '午', '戌'}, {'巳', '酉', '丑'}
    ]

    BRANCH_SIX_CLASHES = {
        ('子', '午'), ('丑', '未'), ('寅', '申'),
        ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
    }

    BRANCH_HARMS = {
        ('子', '未'), ('丑', '午'), ('寅', '巳'),
        ('卯', '辰'), ('申', '亥'), ('酉', '戌')
    }

    @staticmethod
    def _evaluate_primary_lock(bazi1, bazi2, gender1, gender2):
        """
        師傅級第一步：檢查主鎖（破局/不承載）
        只允許一個主鎖
        """
        # 1. 檢查破格
        cong_ge1 = bazi1.get('cong_ge_type', '正常')
        cong_ge2 = bazi2.get('cong_ge_type', '正常')
        
        if '從' in cong_ge1 and '從' in cong_ge2:
            # 雙方都是從格，檢查是否互相破格
            # 簡化：如果喜用完全相反且無解，則視為破格
            useful1 = bazi1.get('useful_elements', [])
            harmful2 = bazi2.get('harmful_elements', [])
            
            opposite_count = sum(1 for e in useful1 if e in harmful2)
            if opposite_count >= len(useful1) and len(useful1) > 0:
                return True, "破格", MASTER_BAZI_CONFIG["LOCK_SYSTEM"]["primary_locks"]["broken_pattern"]
        
        # 2. 檢查不承載（空承載）
        spouse_effective1 = bazi1.get('spouse_star_effective', '未知')
        spouse_effective2 = bazi2.get('spouse_star_effective', '未知')
        
        if spouse_effective1 == '無' and spouse_effective2 == '無':
            return True, "雙方空承載", MASTER_BAZI_CONFIG["LOCK_SYSTEM"]["primary_locks"]["no_carriage"]
        
        return False, None, 100  # 無主鎖
    
    @staticmethod
    def _evaluate_secondary_lock(bazi1, bazi2, gender1, gender2):
        """
        師傅級第二步：檢查次鎖（夫妻宮失序/喜用相反）
        只允許一個次鎖，取較差者
        """
        secondary_locks = []
        
        # 1. 檢查夫妻宮失序
        pressure1 = bazi1.get('pressure_score', 0)
        pressure2 = bazi2.get('pressure_score', 0)
        total_pressure = pressure1 + pressure2
        
        if total_pressure >= 70 and pressure1 >= 30 and pressure2 >= 30:
            secondary_locks.append(("夫妻宮失序", MASTER_BAZI_CONFIG["LOCK_SYSTEM"]["secondary_locks"]["disordered_palace"]))
        
        # 2. 檢查喜用完全相反
        useful1 = bazi1.get('useful_elements', [])
        useful2 = bazi2.get('useful_elements', [])
        harmful1 = bazi1.get('harmful_elements', [])
        harmful2 = bazi2.get('harmful_elements', [])
        
        if useful1 and useful2:
            # 計算相反比例
            total_useful = len(useful1) + len(useful2)
            opposite_count = 0
            
            for element in useful1:
                if element in harmful2:
                    opposite_count += 1
            
            for element in useful2:
                if element in harmful1:
                    opposite_count += 1
            
            opposite_ratio = opposite_count / total_useful if total_useful > 0 else 0
            
            if opposite_ratio >= 0.8:  # 80%以上相反
                secondary_locks.append(("喜用相反", MASTER_BAZI_CONFIG["LOCK_SYSTEM"]["secondary_locks"]["opposite_useful"]))
        
        # 取最嚴重的次鎖
        if secondary_locks:
            secondary_locks.sort(key=lambda x: x[1])  # 按分數排序，越低越嚴重
            return True, secondary_locks[0][0], secondary_locks[0][1]
        
        return False, None, 100  # 無次鎖
    
    @staticmethod
    def _calculate_resolution_capacity(bazi1, bazi2, primary_lock, secondary_lock):
        """
        師傅級第三步：評估解局能力
        只解對應病位，無效則視為無解
        """
        # 檢查天干五合
        stems1 = [
            bazi1.get('year_pillar', '  ')[0],
            bazi1.get('month_pillar', '  ')[0],
            bazi1.get('day_pillar', '  ')[0],
            bazi1.get('hour_pillar', '  ')[0]
        ]
        stems2 = [
            bazi2.get('year_pillar', '  ')[0],
            bazi2.get('month_pillar', '  ')[0],
            bazi2.get('day_pillar', '  ')[0],
            bazi2.get('hour_pillar', '  ')[0]
        ]
        
        # 檢查地支六合
        branches1 = [
            bazi1.get('year_pillar', '  ')[1],
            bazi1.get('month_pillar', '  ')[1],
            bazi1.get('day_pillar', '  ')[1],
            bazi1.get('hour_pillar', '  ')[1]
        ]
        branches2 = [
            bazi2.get('year_pillar', '  ')[1],
            bazi2.get('month_pillar', '  ')[1],
            bazi2.get('day_pillar', '  ')[1],
            bazi2.get('hour_pillar', '  ')[1]
        ]
        
        # 檢查是否針對病位解局
        has_resolution = False
        resolution_level = "無解"
        resolution_factor = MASTER_BAZI_CONFIG["RESOLUTION_SYSTEM"]["no_resolution"]
        
        # 針對夫妻宮失序的解局
        if secondary_lock == "夫妻宮失序":
            day_branch1 = bazi1.get('day_pillar', '  ')[1]
            day_branch2 = bazi2.get('day_pillar', '  ')[1]
            
            # 檢查日支六合
            day_pair = tuple(sorted([day_branch1, day_branch2]))
            if day_pair in MasterBaziMatcher.BRANCH_SIX_COMBINATIONS:
                resolution_level = "弱解"
                resolution_factor = MASTER_BAZI_CONFIG["RESOLUTION_SYSTEM"]["weak_resolution"]
                has_resolution = True
            
            # 檢查日支三合
            all_branches = {day_branch1, day_branch2}
            for group in MasterBaziMatcher.BRANCH_THREE_COMBINATIONS:
                if all_branches.issubset(group):
                    resolution_level = "中解"
                    resolution_factor = MASTER_BAZI_CONFIG["RESOLUTION_SYSTEM"]["medium_resolution"]
                    has_resolution = True
                    break
        
        # 針對喜用相反的解局（通關五行）
        elif secondary_lock == "喜用相反":
            # 檢查通關五行
            useful1 = bazi1.get('useful_elements', [])
            useful2 = bazi2.get('useful_elements', [])
            harmful1 = bazi1.get('harmful_elements', [])
            harmful2 = bazi2.get('harmful_elements', [])
            
            # 找出衝突五行
            conflict_elements = []
            for element in useful1:
                if element in harmful2:
                    conflict_elements.append(element)
            
            for element in useful2:
                if element in harmful1:
                    conflict_elements.append(element)
            
            # 檢查是否有通關五行
            for element in conflict_elements:
                pass_through = None
                for base, gen in ProfessionalBaziCalculator.ELEMENT_GENERATE.items():
                    if gen == element:
                        pass_through = base
                        break
                
                if pass_through:
                    # 檢查通關五行是否為雙方喜用
                    if (pass_through in useful1 or pass_through not in harmful1) and \
                       (pass_through in useful2 or pass_through not in harmful2):
                        resolution_level = "強解"
                        resolution_factor = MASTER_BAZI_CONFIG["RESOLUTION_SYSTEM"]["strong_resolution"]
                        has_resolution = True
                        break
        
        # 無針對性解局，檢查一般合化
        if not has_resolution:
            # 檢查天干五合
            for s1 in stems1:
                for s2 in stems2:
                    if tuple(sorted([s1, s2])) in MasterBaziMatcher.STEM_FIVE_COMBINATIONS:
                        resolution_level = "中解"
                        resolution_factor = MASTER_BAZI_CONFIG["RESOLUTION_SYSTEM"]["medium_resolution"]
                        has_resolution = True
                        break
                if has_resolution:
                    break
        
        return resolution_level, resolution_factor
    
    @staticmethod
    def _calculate_spouse_carriage_score(bazi1, bazi2, gender1, gender2):
        """計算配偶承載匹配分數（32分）"""
        score = 0
        details = []
        
        # 基礎分
        base_score = 16
        score += base_score
        details.append(f"配偶承載基礎分 +{base_score}分")
        
        # 配偶星有效性
        spouse_effective1 = bazi1.get('spouse_star_effective', '未知')
        spouse_effective2 = bazi2.get('spouse_star_effective', '未知')
        
        effective_scores = {
            '強': 8, '中': 6, '弱': 3, '無': 0, '未知': 4
        }
        
        score1 = effective_scores.get(spouse_effective1, 4)
        score2 = effective_scores.get(spouse_effective2, 4)
        
        avg_effective = (score1 + score2) / 2
        score += avg_effective
        details.append(f"配偶星有效性平均 +{avg_effective:.1f}分")
        
        # 配偶星位置互動
        day_stem1 = bazi1.get('day_stem', '')
        day_stem2 = bazi2.get('day_stem', '')
        day_stem_element1 = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem1, '')
        day_stem_element2 = ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem2, '')
        
        # 對方配偶星元素
        spouse_element1 = ''
        spouse_element2 = ''
        
        if gender1 == '男':
            spouse_element1 = ProfessionalBaziCalculator.SPOUSE_STARS['男'].get(day_stem_element1, '')
        else:
            spouse_element1 = ProfessionalBaziCalculator.SPOUSE_STARS['女'].get(day_stem_element1, '')
            
        if gender2 == '男':
            spouse_element2 = ProfessionalBaziCalculator.SPOUSE_STARS['男'].get(day_stem_element2, '')
        else:
            spouse_element2 = ProfessionalBaziCalculator.SPOUSE_STARS['女'].get(day_stem_element2, '')
        
        # 檢查配偶星位置
        day_branch1 = bazi1.get('day_pillar', '  ')[1] if len(bazi1.get('day_pillar', '  ')) >= 2 else ''
        day_branch2 = bazi2.get('day_pillar', '  ')[1] if len(bazi2.get('day_pillar', '  ')) >= 2 else ''
        day_branch_element1 = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(day_branch1, '')
        day_branch_element2 = ProfessionalBaziCalculator.BRANCH_ELEMENTS.get(day_branch2, '')
        
        if day_branch_element1 == spouse_element2:
            score += 4
            details.append(f"你日支為對方配偶星 +4分")
        
        if day_branch_element2 == spouse_element1:
            score += 4
            details.append(f"對方日支為你配偶星 +4分")
        
        return min(32, max(0, score)), details
    
    @staticmethod
    def _calculate_day_pillar_score(bazi1, bazi2, gender1, gender2):
        """計算日柱基礎配合分數（28分）"""
        score = 0
        details = []
        
        day_stem1 = bazi1.get('day_stem', '')
        day_stem2 = bazi2.get('day_stem', '')
        day_branch1 = bazi1.get('day_pillar', '  ')[1] if len(bazi1.get('day_pillar', '  ')) >= 2 else ''
        day_branch2 = bazi2.get('day_pillar', '  ')[1] if len(bazi2.get('day_pillar', '  ')) >= 2 else ''
        
        # 基礎分
        base_score = 14
        score += base_score
        details.append(f"日柱基礎分 +{base_score}分")
        
        # 天干關係
        day_stem_pair = tuple(sorted([day_stem1, day_stem2]))
        
        if day_stem_pair in MasterBaziMatcher.STEM_FIVE_COMBINATIONS:
            score += 8
            details.append(f"天干五合 +8分")
        elif ProfessionalBaziCalculator.ELEMENT_GENERATE.get(
            ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem1, '')
        ) == ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem2, ''):
            score += 6
            details.append(f"天干相生 +6分")
        elif ProfessionalBaziCalculator.ELEMENT_GENERATE.get(
            ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem2, '')
        ) == ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem1, ''):
            score += 6
            details.append(f"天干相生 +6分")
        elif ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem1, '') == ProfessionalBaziCalculator.STEM_ELEMENTS.get(day_stem2, ''):
            score += 4
            details.append(f"天干比和 +4分")
        
        # 地支關係
        day_branch_pair = tuple(sorted([day_branch1, day_branch2]))
        
        # 地支六合
        if day_branch_pair in MasterBaziMatcher.BRANCH_SIX_COMBINATIONS:
            score += 6
            details.append(f"地支六合 +6分")
        
        # 地支三合局
        all_branches = {day_branch1, day_branch2}
        for group in MasterBaziMatcher.BRANCH_THREE_COMBINATIONS:
            if all_branches.issubset(group):
                score += 5
                details.append(f"地支三合 +5分")
                break
        
        # 地支相害
        if day_branch_pair in MasterBaziMatcher.BRANCH_HARMS:
            score = max(0, score - 4)
            details.append(f"地支相害 -4分")
        
        # 地支六沖（已在次鎖處理，這裡只提醒）
        if day_branch_pair in MasterBaziMatcher.BRANCH_SIX_CLASHES:
            details.append(f"地支六沖（已在次鎖處理）")
        
        return min(28, max(0, score)), details
    
    @staticmethod
    def _calculate_personality_score(bazi1, bazi2, gender1, gender2):
        """計算十神性格互補分數（22分）"""
        score = 11  # 基礎分
        details = ["十神性格基礎分 +11分"]
        
        # 獲取十神結構
        shi_shen_list1 = bazi1.get('shi_shen_list', '').split(',')
        shi_shen_list2 = bazi2.get('shi_shen_list', '').split(',')
        
        # 官印互補
        if ('正官' in shi_shen_list1 or '七殺' in shi_shen_list1) and \
           ('正印' in shi_shen_list2 or '偏印' in shi_shen_list2):
            score += 3
            details.append("官印互補 +3分")
        
        if ('正官' in shi_shen_list2 or '七殺' in shi_shen_list2) and \
           ('正印' in shi_shen_list1 or '偏印' in shi_shen_list1):
            score += 3
            details.append("官印互補 +3分")
        
        # 食傷生財
        if ('食神' in shi_shen_list1 or '傷官' in shi_shen_list1) and \
           ('正財' in shi_shen_list2 or '偏財' in shi_shen_list2):
            score += 2
            details.append("食傷生財 +2分")
        
        if ('食神' in shi_shen_list2 or '傷官' in shi_shen_list2) and \
           ('正財' in shi_shen_list1 or '偏財' in shi_shen_list1):
            score += 2
            details.append("食傷生財 +2分")
        
        # 比劫有制
        if ('比肩' in shi_shen_list1 or '劫財' in shi_shen_list1) and \
           ('正官' in shi_shen_list2 or '七殺' in shi_shen_list2):
            score += 2
            details.append("比劫有制 +2分")
        
        if ('比肩' in shi_shen_list2 or '劫財' in shi_shen_list2) and \
           ('正官' in shi_shen_list1 or '七殺' in shi_shen_list1):
            score += 2
            details.append("比劫有制 +2分")
        
        # 衝突組合
        # 傷官見官
        if ('傷官' in shi_shen_list1 and ('正官' in shi_shen_list2 or '七殺' in shi_shen_list2)) or \
           ('傷官' in shi_shen_list2 and ('正官' in shi_shen_list1 or '七殺' in shi_shen_list1)):
            score = max(0, score - 4)
            details.append("傷官見官 -4分")
        
        # 官殺混雜
        if ('正官' in shi_shen_list1 and '七殺' in shi_shen_list1) and \
           ('正官' in shi_shen_list2 and '七殺' in shi_shen_list2):
            score = max(0, score - 3)
            details.append("雙方官殺混雜 -3分")
        
        return min(22, max(0, score)), details
    
    @staticmethod
    def _calculate_energy_flow_score(bazi1, bazi2):
        """計算氣勢平衡流通分數（18分）"""
        score = 9  # 基礎分
        details = ["氣勢平衡基礎分 +9分"]
        
        # 寒暖調候分析
        month_branch1 = bazi1.get('month_pillar', '  ')[1]
        month_branch2 = bazi2.get('month_pillar', '  ')[1]
        
        cold_months = ['亥', '子', '丑']
        warm_months = ['巳', '午', '未']
        
        is_cold1 = month_branch1 in cold_months
        is_cold2 = month_branch2 in cold_months
        is_warm1 = month_branch1 in warm_months
        is_warm2 = month_branch2 in warm_months
        
        # 寒暖互補
        if is_cold1 and not is_cold2:
            elements2 = bazi2.get('elements', {})
            if elements2.get('火', 0) > 20:
                score += 2
                details.append("寒暖互補 +2分")
        
        if is_warm1 and not is_warm2:
            elements2 = bazi2.get('elements', {})
            if elements2.get('水', 0) > 20:
                score += 2
                details.append("寒暖互補 +2分")
        
        # 五行通關
        elements1 = bazi1.get('elements', {})
        elements2 = bazi2.get('elements', {})
        
        strongest1 = max(elements1.items(), key=lambda x: x[1])[0] if elements1 else ''
        strongest2 = max(elements2.items(), key=lambda x: x[1])[0] if elements2 else ''
        
        if strongest1 and strongest2:
            # 檢查是否需要通關
            if ProfessionalBaziCalculator.ELEMENT_OVERCOME.get(strongest1) == strongest2:
                pass_through_map = {'金': '水', '水': '木', '木': '火', '火': '土', '土': '金'}
                pass_element = pass_through_map.get(strongest1)
                if pass_element and (elements1.get(pass_element, 0) > 15 or elements2.get(pass_element, 0) > 15):
                    score += 2
                    details.append(f"五行通關 +2分")
        
        # 從格配正格調整
        cong_ge1 = bazi1.get('cong_ge_type', '正常')
        cong_ge2 = bazi2.get('cong_ge_type', '正常')
        
        if ('從' in cong_ge1 and cong_ge2 == '正常') or \
           ('從' in cong_ge2 and cong_ge1 == '正常'):
            score = max(0, score - 1)
            details.append("從格配正格 -1分")
        
        return min(18, max(0, score)), details
    
    @staticmethod
    def _calculate_shen_sha_bonus(bazi1, bazi2, purpose="正緣"):
        """計算神煞加分（師傅級互動計算）"""
        bonus = 0
        shen_sha_details = []
        
        # 獲取雙方神煞
        shen_sha1 = bazi1.get('shen_sha_names', '無')
        shen_sha2 = bazi2.get('shen_sha_names', '無')
        bonus1 = bazi1.get('shen_sha_bonus', 0)
        bonus2 = bazi2.get('shen_sha_bonus', 0)
        
        # 基礎加分
        total_bonus = bonus1 + bonus2
        
        # 神煞互動（疊加/抵銷）
        shen_sha_list1 = shen_sha1.split(',') if shen_sha1 != '無' else []
        shen_sha_list2 = shen_sha2.split(',') if shen_sha2 != '無' else []
        
        # 檢查紅鸞+天喜疊加
        has_hong_luan1 = any('紅鸞' in s for s in shen_sha_list1)
        has_hong_luan2 = any('紅鸞' in s for s in shen_sha_list2)
        has_tian_xi1 = any('天喜' in s for s in shen_sha_list1)
        has_tian_xi2 = any('天喜' in s for s in shen_sha_list2)
        
        if (has_hong_luan1 or has_hong_luan2) and (has_tian_xi1 or has_tian_xi2):
            bonus += 5  # 疊加獎勵
            shen_sha_details.append("紅鸞天喜疊加 +5分")
        
        # 檢查天乙貴人+天德疊加
        has_tian_yi1 = any('天乙貴人' in s for s in shen_sha_list1)
        has_tian_yi2 = any('天乙貴人' in s for s in shen_sha_list2)
        has_tian_de1 = any('天德' in s for s in shen_sha_list1)
        has_tian_de2 = any('天德' in s for s in shen_sha_list2)
        
        if (has_tian_yi1 or has_tian_yi2) and (has_tian_de1 or has_tian_de2):
            bonus += 4  # 疊加獎勵
            shen_sha_details.append("天乙天德疊加 +4分")
        
        # 檢查羊刃+天德抵銷
        has_yang_ren1 = any('羊刃' in s for s in shen_sha_list1)
        has_yang_ren2 = any('羊刃' in s for s in shen_sha_list2)
        
        if (has_yang_ren1 or has_yang_ren2) and (has_tian_de1 or has_tian_de2):
            # 抵銷部分負分
            bonus += 2  # 減輕負面影響
            shen_sha_details.append("羊刃天德抵銷 +2分")
        
        # 根據目的調整
        if purpose == "合夥":
            total_bonus = total_bonus * 0.7  # 合夥模式神煞影響減小
        
        total_bonus += bonus
        
        # 上限控制
        max_bonus = MASTER_BAZI_CONFIG['SHEN_SHA_BONUS']['max_bonus']
        total_bonus = min(max_bonus, total_bonus)
        
        if shen_sha_details:
            details_str = f"神煞加分: {total_bonus:.1f}分 (" + "; ".join(shen_sha_details) + ")"
        else:
            details_str = f"神煞加分: {total_bonus:.1f}分"
        
        return total_bonus, details_str
    
    @staticmethod
    def calculate_match_confidence(bazi1, bazi2):
        """計算配對信心度"""
        confidence1 = bazi1.get('hour_confidence', '高')
        confidence2 = bazi2.get('hour_confidence', '高')

        confidence_map = {
            '高': 0.95,
            '中': 0.90,
            '低': 0.85,
            '未知': 0.80
        }

        conf1 = confidence_map.get(confidence1, 0.85)
        conf2 = confidence_map.get(confidence2, 0.85)

        overall_confidence = (conf1 + conf2) / 2

        if overall_confidence >= 0.92:
            return "高", overall_confidence
        elif overall_confidence >= 0.87:
            return "中", overall_confidence
        else:
            return "低", overall_confidence
    
    @staticmethod
    def generate_master_analysis(bazi1, bazi2, gender1, gender2, final_score, 
                                raw_total, max_score, primary_lock, secondary_lock,
                                resolution_level, module_scores, shen_sha_bonus):
        """生成師傅級分析報告"""
        
        # 師傅一句話評論
        day_stem1 = bazi1.get('day_stem', '')
        day_stem2 = bazi2.get('day_stem', '')
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        
        stem_comment = ""
        stem_pair = tuple(sorted([day_stem1, day_stem2]))
        if stem_pair in MasterBaziMatcher.STEM_FIVE_COMBINATIONS:
            stem_comment = f"{day_stem1}{day_stem2}五合有情"
        else:
            stem_comment = f"{day_stem1}{day_stem2}配合"
        
        branch_comment = ""
        branch_pair = tuple(sorted([day_branch1, day_branch2]))
        if branch_pair in MasterBaziMatcher.BRANCH_SIX_COMBINATIONS:
            branch_comment = "地支六合根基穩"
        elif branch_pair in MasterBaziMatcher.BRANCH_SIX_CLASHES:
            branch_comment = "地支六沖心難安"
        elif branch_pair in MasterBaziMatcher.BRANCH_HARMS:
            branch_comment = "地支相害暗傷藏"
        else:
            branch_comment = "地支平和可經營"
        
        # 根據分數生成結論
        if final_score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["excellent_match"]:
            conclusion = "，可成佳偶互扶持。"
        elif final_score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["good_match"]:
            conclusion = "，用心經營可長久。"
        elif final_score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["contact_exchange"]:
            conclusion = "，有緣有份需努力。"
        elif final_score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["display_match"]:
            conclusion = "，波折較多考驗深。"
        else:
            conclusion = "，勉強結合多磨難。"
        
        master_comment = f"{stem_comment}，{branch_comment}{conclusion}"
        
        # 結構標籤解讀
        tags_interpretation = "【結構標籤】\n"
        if primary_lock:
            tags_interpretation += f"• 主鎖: {primary_lock}\n"
        if secondary_lock:
            tags_interpretation += f"• 次鎖: {secondary_lock}\n"
        tags_interpretation += f"• 解局能力: {resolution_level}\n"
        
        # 模組分數詳解
        module_details = "【模組分數】\n"
        for module, score in module_scores.items():
            module_name = {
                "spouse_carriage": "配偶承載",
                "day_pillar": "日柱配合",
                "personality": "性格互補",
                "energy_flow": "氣勢平衡"
            }.get(module, module)
            max_score_module = MASTER_BAZI_CONFIG["MODULE_WEIGHTS"][module]
            module_details += f"• {module_name}: {score:.1f}/{max_score_module}分\n"
        
        # 具體建議
        suggestions = "【師傅建議】\n"
        if final_score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["good_match"]:
            suggestions += "• 八字相合度良好，適合長期發展\n"
            suggestions += "• 互相包容理解，感情自然深厚\n"
        elif final_score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["contact_exchange"]:
            suggestions += "• 八字基本相合，但需更多溝通\n"
            suggestions += "• 注意化解沖剋，增強信任\n"
        else:
            suggestions += "• 八字沖剋較多，需謹慎考慮\n"
            suggestions += "• 建議多觀察了解，勿急於決定\n"
        
        # 神煞提示
        if shen_sha_bonus > 10:
            suggestions += "• 有吉神加持，姻緣助力強\n"
        
        full_analysis = f"""
【師傅級八字配對分析】

🔮 總評: {final_score:.1f}分
💬 師傅一句話: {master_comment}

{tags_interpretation}
{module_details}
✨ 神煞加持: {shen_sha_bonus:.1f}分
📊 原始總分: {raw_total:.1f}分
🔒 結構上限: {max_score:.1f}分

{suggestions}

💡 溫馨提示: 八字僅供參考，真心相待最重要！
"""
        
        return full_analysis
    
    @staticmethod
    def match(bazi1, bazi2, gender1, gender2, purpose="正緣"):
        """
        師傅級八字配對主算法
        按照「老師傅實戰判局」流程：
        1. 檢查主鎖（破局/不承載）
        2. 檢查次鎖（夫妻宮失序/喜用相反）
        3. 評估解局能力
        4. 計算四大模組分數
        5. 應用神煞加分
        6. 生成師傅級分析
        """
        try:
            # 修復數據：確保所有必要的字段都存在
            for bazi in [bazi1, bazi2]:
                if 'shi_shen_list' not in bazi:
                    bazi['shi_shen_list'] = bazi.get('shi_shen_structure', '正常')
                if 'cong_ge_type' not in bazi:
                    bazi['cong_ge_type'] = '正常'
                if 'spouse_star_effective' not in bazi:
                    bazi['spouse_star_effective'] = '未知'
                if 'pressure_score' not in bazi:
                    bazi['pressure_score'] = 0
            
            # 1. 檢查主鎖
            has_primary_lock, primary_lock_name, primary_max = MasterBaziMatcher._evaluate_primary_lock(
                bazi1, bazi2, gender1, gender2
            )
            
            # 2. 檢查次鎖
            has_secondary_lock, secondary_lock_name, secondary_max = MasterBaziMatcher._evaluate_secondary_lock(
                bazi1, bazi2, gender1, gender2
            )
            
            # 3. 確定上限（只取一個主鎖+一個次鎖）
            if has_primary_lock:
                max_score = primary_max
                lock_type = "主鎖"
                lock_name = primary_lock_name
            elif has_secondary_lock:
                max_score = secondary_max
                lock_type = "次鎖"
                lock_name = secondary_lock_name
            else:
                max_score = 100  # 無鎖定
                lock_type = None
                lock_name = None
            
            # 4. 評估解局能力
            resolution_level, resolution_factor = MasterBaziMatcher._calculate_resolution_capacity(
                bazi1, bazi2, lock_type, lock_name
            )
            
            # 5. 計算四大模組分數
            spouse_score, spouse_details = MasterBaziMatcher._calculate_spouse_carriage_score(
                bazi1, bazi2, gender1, gender2
            )
            
            day_score, day_details = MasterBaziMatcher._calculate_day_pillar_score(
                bazi1, bazi2, gender1, gender2
            )
            
            personality_score, personality_details = MasterBaziMatcher._calculate_personality_score(
                bazi1, bazi2, gender1, gender2
            )
            
            energy_score, energy_details = MasterBaziMatcher._calculate_energy_flow_score(
                bazi1, bazi2
            )
            
            module_scores = {
                "spouse_carriage": spouse_score,
                "day_pillar": day_score,
                "personality": personality_score,
                "energy_flow": energy_score
            }
            
            # 6. 計算原始總分
            raw_total = sum(module_scores.values())
            
            # 7. 應用解局系數（只作用於細項分，不作用於總分）
            adjusted_max = max_score * resolution_factor
            
            # 8. 計算神煞加分
            shen_sha_bonus, shen_sha_details = MasterBaziMatcher._calculate_shen_sha_bonus(
                bazi1, bazi2, purpose
            )
            
            # 9. 計算基礎分（非破局最低45分）
            base_score = MASTER_BAZI_CONFIG["BASE_PROTECTION"]["base_score"]
            if not has_primary_lock:  # 非破局
                base_score = max(base_score, MASTER_BAZI_CONFIG["BASE_PROTECTION"]["non_broken_minimum"])
            
            # 10. 計算最終分數
            final_raw = base_score + (raw_total - 50) + shen_sha_bonus  # 基礎分 + 模組調整 + 神煞
            final_score = min(adjusted_max, final_raw)
            
            # 11. 信心度調整
            confidence_level, confidence_value = MasterBaziMatcher.calculate_match_confidence(bazi1, bazi2)
            final_score = final_score * confidence_value
            
            # 12. 底線保護（非破局最低45分）
            if not has_primary_lock and final_score < MASTER_BAZI_CONFIG["BASE_PROTECTION"]["non_broken_minimum"]:
                final_score = MASTER_BAZI_CONFIG["BASE_PROTECTION"]["non_broken_minimum"]
            
            # 13. 生成師傅級分析
            master_analysis = MasterBaziMatcher.generate_master_analysis(
                bazi1, bazi2, gender1, gender2, final_score, raw_total,
                adjusted_max, lock_name, secondary_lock_name if has_secondary_lock else None,
                resolution_level, module_scores, shen_sha_bonus
            )
            
            # 14. 收集所有詳細信息
            all_details = []
            all_details.extend(spouse_details)
            all_details.extend(day_details)
            all_details.extend(personality_details)
            all_details.extend(energy_details)
            
            if lock_type:
                all_details.append(f"🔒 {lock_type}: {lock_name} (上限{max_score}分)")
            
            if resolution_level != "無解":
                all_details.append(f"✨ 解局能力: {resolution_level} (系數{resolution_factor})")
            
            all_details.append(shen_sha_details)
            
            # 15. 生成建議
            suggestions = []
            if final_score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["excellent_match"]:
                level = "🌟 上等婚配"
                advice = "結構良好，互相成就，適合長期發展"
            elif final_score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["good_match"]:
                level = "✨ 中上婚配"
                advice = "有緣有份，需用心經營，互相包容"
            elif final_score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["contact_exchange"]:
                level = "✅ 中等婚配"
                advice = "內耗較大，易生疲憊，需更多溝通"
            elif final_score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["display_match"]:
                level = "🤝 普通婚配"
                advice = "結構缺陷多，易生變數，需謹慎考慮"
            else:
                level = "❌ 不建議"
                advice = "破格或嚴重不承載，不建議發展"
            
            return {
                "score": round(final_score, 1),
                "level": level,
                "advice": advice,
                "master_analysis": master_analysis,
                "details": all_details,
                "module_scores": {
                    "spouse_carriage": round(spouse_score, 1),
                    "day_pillar": round(day_score, 1),
                    "personality": round(personality_score, 1),
                    "energy_flow": round(energy_score, 1)
                },
                "raw_total": round(raw_total, 1),
                "max_score": round(adjusted_max, 1),
                "shen_sha_bonus": round(shen_sha_bonus, 1),
                "confidence_level": confidence_level,
                "confidence_value": confidence_value,
                "lock_info": {
                    "has_lock": lock_type is not None,
                    "lock_type": lock_type,
                    "lock_name": lock_name,
                    "max_score": max_score
                },
                "resolution_info": {
                    "level": resolution_level,
                    "factor": resolution_factor
                },
                "bazi1": {
                    "pillars": f"{bazi1.get('year_pillar')} {bazi1.get('month_pillar')} {bazi1.get('day_pillar')} {bazi1.get('hour_pillar')}",
                    "zodiac": bazi1.get('zodiac'),
                    "day_stem": bazi1.get('day_stem'),
                    "gender": gender1,
                    "hour_confidence": bazi1.get('hour_confidence', '高'),
                    "cong_ge_type": bazi1.get('cong_ge_type', '正常'),
                    "shi_shen_structure": bazi1.get('shi_shen_structure', '正常'),
                    "pressure_score": bazi1.get('pressure_score', 0),
                    "spouse_star_effective": bazi1.get('spouse_star_effective', '未知'),
                    "shen_sha": bazi1.get('shen_sha_names', '無')
                },
                "bazi2": {
                    "pillars": f"{bazi2.get('year_pillar')} {bazi2.get('month_pillar')} {bazi2.get('day_pillar')} {bazi2.get('hour_pillar')}",
                    "zodiac": bazi2.get('zodiac'),
                    "day_stem": bazi2.get('day_stem'),
                    "gender": gender2,
                    "hour_confidence": bazi2.get('hour_confidence', '高'),
                    "cong_ge_type": bazi2.get('cong_ge_type', '正常'),
                    "shi_shen_structure": bazi2.get('shi_shen_structure', '正常'),
                    "pressure_score": bazi2.get('pressure_score', 0),
                    "spouse_star_effective": bazi2.get('spouse_star_effective', '未知'),
                    "shen_sha": bazi2.get('shen_sha_names', '無')
                }
            }
            
        except Exception as e:
            logger.error(f"師傅級配對計算錯誤: {e}", exc_info=True)
            # 嘗試修復數據並重新計算
            try:
                logger.info("嘗試修復數據並重新計算...")
                # 確保所有必要的字段都存在
                for bazi in [bazi1, bazi2]:
                    if 'shi_shen_list' not in bazi:
                        bazi['shi_shen_list'] = bazi.get('shi_shen_structure', '正常')
                    if 'cong_ge_type' not in bazi:
                        bazi['cong_ge_type'] = '正常'
                    if 'spouse_star_effective' not in bazi:
                        bazi['spouse_star_effective'] = '未知'
                    if 'pressure_score' not in bazi:
                        bazi['pressure_score'] = 0
                
                # 重新嘗試計算
                return MasterBaziMatcher.match(bazi1, bazi2, gender1, gender2, purpose)
            except Exception as e2:
                logger.error(f"修復後重新計算也失敗: {e2}")
                # 如果修復失敗，使用結構判局模式
                return MasterBaziMatcher._fallback_match(bazi1, bazi2, gender1, gender2)
    
    @staticmethod
    def _fallback_match(bazi1, bazi2, gender1, gender2):
        """結構判局模式（當主算法失敗時使用）"""
        try:
            # 簡單判斷
            day_stem1 = bazi1.get('day_stem', '')
            day_stem2 = bazi2.get('day_stem', '')
            day_branch1 = bazi1.get('day_pillar', '  ')[1]
            day_branch2 = bazi2.get('day_pillar', '  ')[1]
            
            # 檢查天干五合
            stem_pair = tuple(sorted([day_stem1, day_stem2]))
            has_five_combination = stem_pair in MasterBaziMatcher.STEM_FIVE_COMBINATIONS
            
            # 檢查地支六沖
            branch_pair = tuple(sorted([day_branch1, day_branch2]))
            has_six_clash = branch_pair in MasterBaziMatcher.BRANCH_SIX_CLASHES
            
            # 簡單評分
            if has_five_combination and not has_six_clash:
                score = 75
                level = "✨ 結構良好"
                advice = "天干有情，地支平和，適合發展"
            elif has_five_combination and has_six_clash:
                score = 58
                level = "⚠️ 有合有沖"
                advice = "天干有情但地支相沖，需努力化解"
            elif not has_five_combination and not has_six_clash:
                score = 62
                level = "✅ 普通配合"
                advice = "無明顯沖合，可慢慢培養"
            else:
                score = 45
                level = "🤝 需要努力"
                advice = "地支相沖較多，需謹慎考慮"
            
            # 確保 module_scores 存在
            module_scores = {
                "spouse_carriage": round(score * 0.32, 1),
                "day_pillar": round(score * 0.28, 1),
                "personality": round(score * 0.22, 1),
                "energy_flow": round(score * 0.18, 1)
            }
            
            return {
                "score": score,
                "level": level,
                "advice": advice,
                "master_analysis": f"【結構判局模式】\n{level}\n{advice}",
                "details": ["使用結構判局模式（主算法異常）"],
                "module_scores": module_scores,
                "raw_total": score,
                "max_score": 100,
                "shen_sha_bonus": 0,
                "confidence_level": "中",
                "confidence_value": 0.85,
                "lock_info": {"has_lock": False},
                "resolution_info": {"level": "無解", "factor": 1.0},
                "bazi1": {
                    "pillars": f"{bazi1.get('year_pillar')} {bazi1.get('month_pillar')} {bazi1.get('day_pillar')} {bazi1.get('hour_pillar')}",
                    "zodiac": bazi1.get('zodiac'),
                    "day_stem": day_stem1,
                    "gender": gender1
                },
                "bazi2": {
                    "pillars": f"{bazi2.get('year_pillar')} {bazi2.get('month_pillar')} {bazi2.get('day_pillar')} {bazi2.get('hour_pillar')}",
                    "zodiac": bazi2.get('zodiac'),
                    "day_stem": day_stem2,
                    "gender": gender2
                }
            }
        except Exception as e:
            logger.error(f"結構判局模式也失敗: {e}")
            raise MatchError("配對計算完全失敗")
# ========1.4 終極師傅級配對算法結束 ========#

# ========1.5 格式化顯示函數開始 ========#
def format_core_analysis(match_result: dict) -> str:
    """格式化【核心分析結果】"""
    bazi1 = match_result.get("bazi1", {})
    bazi2 = match_result.get("bazi2", {})
    
    text = f"""
🔮 【核心分析結果】

{match_result.get('level', '未知')}
🎯 配對分數: {match_result.get('score', 0):.1f}%
💡 建議: {match_result.get('advice', '')}

📊 詳細分數:
• 原始總分: {match_result.get('raw_total', 0):.1f}分
• 結構上限: {match_result.get('max_score', 0):.1f}分
• 神煞加持: {match_result.get('shen_sha_bonus', 0):.1f}分
• 信心度: {match_result.get('confidence_level', '中')} ({match_result.get('confidence_value', 1.0)*100:.0f}%)
"""
    return text.strip()

def format_pairing_info(match_result: dict) -> str:
    """格式化【配對資訊】"""
    bazi1 = match_result.get("bazi1", {})
    bazi2 = match_result.get("bazi2", {})
    
    text = f"""
👥 【配對資訊】

【八字1】{bazi1.get('gender', '未知')}
四柱: 年柱{bazi1.get('year_pillar', '未知')} 月柱{bazi1.get('month_pillar', '未知')} 日柱{bazi1.get('day_pillar', '未知')} 時柱{bazi1.get('hour_pillar', '未知')}
生肖: {bazi1.get('zodiac', '未知')}，日主: {bazi1.get('day_stem', '未知')}
從格類型: {bazi1.get('cong_ge_type', '正常')}
十神結構: {bazi1.get('shi_shen_structure', '正常')}
夫妻星有效性: {bazi1.get('spouse_star_effective', '未知')}
夫妻宮壓力: {bazi1.get('pressure_score', 0)}分
神煞: {bazi1.get('shen_sha', '無')}
時辰信心度: {bazi1.get('hour_confidence', '高')}

【八字2】{bazi2.get('gender', '未知')}
四柱: 年柱{bazi2.get('year_pillar', '未知')} 月柱{bazi2.get('month_pillar', '未知')} 日柱{bazi2.get('day_pillar', '未知')} 時柱{bazi2.get('hour_pillar', '未知')}
生肖: {bazi2.get('zodiac', '未知')}，日主: {bazi2.get('day_stem', '未知')}
從格類型: {bazi2.get('cong_ge_type', '正常')}
十神結構: {bazi2.get('shi_shen_structure', '正常')}
夫妻星有效性: {bazi2.get('spouse_star_effective', '未知')}
夫妻宮壓力: {bazi2.get('pressure_score', 0)}分
神煞: {bazi2.get('shen_sha', '無')}
時辰信心度: {bazi2.get('hour_confidence', '高')}
"""
    return text.strip()

def format_module_scores(match_result: dict) -> str:
    """格式化【模組分數詳解】"""
    module_scores = match_result.get("module_scores", {})
    
    if not module_scores:
        return "📊 【模組分數詳解】\n• 未計算模組分數"
    
    text = "📊 【模組分數詳解】\n"
    
    for module, score in module_scores.items():
        module_name = {
            "spouse_carriage": "配偶承載匹配",
            "day_pillar": "日柱基礎配合",
            "personality": "十神性格互補",
            "energy_flow": "氣勢平衡流通"
        }.get(module, module)
        
        max_score = MASTER_BAZI_CONFIG["MODULE_WEIGHTS"][module]
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        # 添加評級圖標
        if percentage >= 80:
            icon = "⭐"
        elif percentage >= 70:
            icon = "✨"
        elif percentage >= 60:
            icon = "✅"
        elif percentage >= 50:
            icon = "🤝"
        else:
            icon = "⚠️"
        
        text += f"• {icon} {module_name}: {score:.1f}/{max_score}分 ({percentage:.0f}%)\n"
    
    # 鎖定信息
    lock_info = match_result.get("lock_info", {})
    if lock_info.get("has_lock"):
        text += f"\n🔒 結構鎖定: {lock_info.get('lock_name')} (上限{lock_info.get('max_score')}分)\n"
    
    # 解局信息
    resolution_info = match_result.get("resolution_info", {})
    if resolution_info.get("level") != "無解":
        text += f"✨ 解局能力: {resolution_info.get('level')} (系數{resolution_info.get('factor')})\n"
    
    return text.strip()

def format_key_interactions(match_result: dict) -> str:
    """格式化【關鍵互動】"""
    details = match_result.get("details", [])
    
    if not details:
        return "🔍 【關鍵互動】\n• 無關鍵互動分析"
    
    text = "🔍 【關鍵互動】\n"
    for i, detail in enumerate(details[:8], 1):  # 限制顯示前8條
        text += f"• {detail}\n"
    
    if len(details) > 8:
        text += f"• ... 等{len(details)}條詳細分析\n"
    
    return text.strip()

def format_suggestions(match_result: dict) -> str:
    """格式化【建議】"""
    score = match_result.get("score", 0)
    lock_info = match_result.get("lock_info", {})
    
    text = "💡 【建議】\n"
    
    if lock_info.get("has_lock"):
        lock_type = lock_info.get("lock_type")
        lock_name = lock_info.get("lock_name")
        text += f"• 注意: 存在{lock_type}「{lock_name}」，發展需謹慎\n"
    
    if score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["excellent_match"]:
        text += """• 八字相合度極佳，適合長期發展
• 互相包容理解，感情自然深厚
• 有吉神加持，姻緣助力強
• 建議深入交往，建立穩定關係
"""
    elif score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["good_match"]:
        text += """• 八字相合度良好，適合發展
• 有緣有份，需用心經營
• 互相包容，增強信任
• 建議多溝通了解彼此
"""
    elif score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["contact_exchange"]:
        text += """• 八字基本相合，但需更多溝通
• 內耗較大，易生疲憊
• 注意化解沖剋
• 建議慢慢培養感情
"""
    elif score >= MASTER_BAZI_CONFIG["THRESHOLDS"]["display_match"]:
        text += """• 八字沖剋較多，需謹慎考慮
• 結構缺陷多，易生變數
• 需要更多耐心和理解
• 建議多觀察了解，勿急於決定
"""
    else:
        text += """• 八字沖剋嚴重，不建議發展
• 破格或嚴重不承載
• 勉強結合多磨難
• 建議尋找更合適的配對
"""
    
    text += "\n✨ 溫馨提示: 八字僅供參考，真心相待最重要！"
    
    return text.strip()

def format_personal_data(bazi_data: dict) -> str:
    """格式化【個人八字資料】"""
    elements = bazi_data.get("elements", {})
    
    text = f"""
📋 【個人八字資料】

四柱: 年柱{bazi_data.get('year_pillar', '未知')} 月柱{bazi_data.get('month_pillar', '未知')} 日柱{bazi_data.get('day_pillar', '未知')} 時柱{bazi_data.get('hour_pillar', '未知')}
生肖: {bazi_data.get('zodiac', '未知')}
日主: {bazi_data.get('day_stem', '未知')} ({bazi_data.get('day_stem_element', '未知')})
性別: {bazi_data.get('gender', '未知')}

📊 八字分析:
• 從格類型: {bazi_data.get('cong_ge_type', '正常')}
• 十神結構: {bazi_data.get('shi_shen_structure', '正常')}
• 身強弱: {bazi_data.get('day_stem_strength', '未知')} ({bazi_data.get('strength_score', 0)}分)
• 喜用神: {', '.join(bazi_data.get('useful_elements', [])) if bazi_data.get('useful_elements') else '平衡'}
• 忌神: {', '.join(bazi_data.get('harmful_elements', [])) if bazi_data.get('harmful_elements') else '無'}

💑 婚姻信息:
• 夫妻星: {bazi_data.get('spouse_star_status', '未知')}
• 夫妻星有效性: {bazi_data.get('spouse_star_effective', '未知')}
• 夫妻宮: {bazi_data.get('spouse_palace_status', '未知')}
• 夫妻宮壓力: {bazi_data.get('pressure_score', 0)}分

✨ 神煞信息:
• 神煞: {bazi_data.get('shen_sha_names', '無')}
• 神煞加分: {bazi_data.get('shen_sha_bonus', 0)}分

🌿 五行分佈:
• 木: {elements.get('木', 0):.1f}%
• 火: {elements.get('火', 0):.1f}%
• 土: {elements.get('土', 0):.1f}%
• 金: {elements.get('金', 0):.1f}%
• 水: {elements.get('水', 0):.1f}%

📈 信心度: {bazi_data.get('hour_confidence', '未知')}
"""
    return text.strip()

def format_match_result(match_result: dict) -> List[str]:
    """格式化配對結果（分為多個消息）"""
    messages = []
    
    # 1. 核心分析結果
    messages.append(format_core_analysis(match_result))
    
    # 2. 配對資訊
    messages.append(format_pairing_info(match_result))
    
    # 3. 模組分數詳解
    messages.append(format_module_scores(match_result))
    
    # 4. 關鍵互動（如果有）
    key_interactions = format_key_interactions(match_result)
    if key_interactions:
        messages.append(key_interactions)
    
    # 5. 建議
    messages.append(format_suggestions(match_result))
    
    return messages

def format_profile_result(bazi_data: dict, username: str = "") -> str:
    """格式化個人資料結果"""
    if username:
        header = f"👤 用戶名: @{username}\n"
    else:
        header = ""
    
    return f"""
{header}{format_personal_data(bazi_data)}

💡 提示:
• 輸入 /profile 查看個人資料
• 輸入 /match 開始八字配對
• 輸入 /find_soulmate 搜尋最佳出生時空
• 輸入 /testpair 測試任意兩個八字
• 輸入 /explain 查看算法說明
"""
# ========1.5 格式化顯示函數結束 ========#

# ========1.7 AI分析提示函數開始 ========#
def generate_ai_prompt(match_result):
    """生成AI分析提示"""
    bazi1 = match_result.get("bazi1", {})
    bazi2 = match_result.get("bazi2", {})

    # 模組分數
    module_scores = match_result.get("module_scores", {})
    module_text = "📊 各模組分數："
    for module, score in module_scores.items():
        module_name = {
            "spouse_carriage": "配偶承載",
            "day_pillar": "日柱配合",
            "personality": "性格互補",
            "energy_flow": "氣勢平衡"
        }.get(module, module)
        module_text += f"\n• {module_name}: {score}/" + {
            "spouse_carriage": "32",
            "day_pillar": "28",
            "personality": "22",
            "energy_flow": "18"
        }.get(module, "?") + "分"

    # 鎖定信息
    lock_text = ""
    lock_info = match_result.get("lock_info", {})
    if lock_info.get("has_lock"):
        lock_text = f"\n🔒 結構鎖定: {lock_info.get('lock_name')} (上限{lock_info.get('max_score')}分)"
    
    # 解局信息
    resolution_text = ""
    resolution_info = match_result.get("resolution_info", {})
    if resolution_info.get("level") != "無解":
        resolution_text = f"\n✨ 解局能力: {resolution_info.get('level')} (系數{resolution_info.get('factor')})"

    prompt = f"""請幫我分析以下八字配對（師傅級婚配系統）：

【八字1】
四柱：年柱{bazi1.get('year_pillar')} 月柱{bazi1.get('month_pillar')} 日柱{bazi1.get('day_pillar')} 時柱{bazi1.get('hour_pillar')}
生肖：{bazi1.get('zodiac')}
日主：{bazi1.get('day_stem')}
性別：{bazi1.get('gender')}
從格類型：{bazi1.get('cong_ge_type')}
十神結構：{bazi1.get('shi_shen_structure')}
配偶星有效性：{bazi1.get('spouse_star_effective')}
夫妻宮壓力：{bazi1.get('pressure_score')}
神煞：{bazi1.get('shen_sha')}

【八字2】
四柱：年柱{bazi2.get('year_pillar')} 月柱{bazi2.get('month_pillar')} 日柱{bazi2.get('day_pillar')} 時柱{bazi2.get('hour_pillar')}
生肖：{bazi2.get('zodiac')}
日主：{bazi2.get('day_stem')}
性別：{bazi2.get('gender')}
從格類型：{bazi2.get('cong_ge_type')}
十神結構：{bazi2.get('shi_shen_structure')}
配偶星有效性：{bazi2.get('spouse_star_effective')}
夫妻宮壓力：{bazi2.get('pressure_score')}
神煞：{bazi2.get('shen_sha')}

【配對結果】
分數: {match_result.get('score', 0)}%
等級: {match_result.get('level', '未知')}
原始總分: {match_result.get('raw_total', 0)}分
結構上限: {match_result.get('max_score', 0)}分
神煞加持: {match_result.get('shen_sha_bonus', 0)}分
信心度: {match_result.get('confidence_level')} ({match_result.get('confidence_value', 1.0)*100:.0f}%)
{module_text}{lock_text}{resolution_text}

請從以下幾個方面分析：
1. 八字實際相處優缺點？
2. 最容易有摩擦嘅地方？
3. 長期發展要注意咩？
4. 如何化解八字中的沖剋？
5. 感情發展建議？

請用粵語回答，詳細分析。"""

    return prompt
# ========1.7 AI分析提示函數結束 ========#

# ========文件信息開始 ========#
"""
文件: bazi_calculator.py
功能: 八字計算核心邏輯，包含所有計算和格式化函數

引用文件: 無
被引用文件: bot.py (主程序), bazi_soulmate.py
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
1.1 導入模組 - 導入必要的庫和配置常量
1.2 錯誤處理類 - 自定義錯誤類和裝飾器
1.3 專業八字計算類 - 完整的八字計算邏輯
1.4 終極師傅級配對算法 - 完整的配對算法
1.5 格式化顯示函數 - 所有格式化顯示模板
1.7 AI分析提示函數 - AI分析提示生成
"""
# ========目錄結束 ========#

# ========修正紀錄開始 ========#
"""
版本 1.0 (2024-01-31)
重構文件：
- 將所有計算邏輯遷移到 bazi_calculator.py
- 保留Bot交互邏輯在本文件
- 使用計算核心的格式化函數
- 刪除profile中的概率分析
- 統一match/testpair/profile的顯示格式

版本 1.1 (2024-01-31)
修改內容：
1. 添加 import json 模塊（解決 json 未定義錯誤）
2. 移除所有日誌中的 "✅ " 前綴
3. 將硬編碼文字替換為從 texts.py 導入的常量
4. 添加新的文字常量導入
5. 更新目錄和修正紀錄

版本 1.2 (2024-02-01)
緊急修復：
1. 添加 import hashlib（解決match按鈕無反應問題）
2. 修復信心度顯示為英文問題
3. 優化數據庫操作
4. 刪除重複提示

版本 1.3 (2024-02-01)
問題修復：
1. 修復信心度數據庫初始化問題
2. 優化start函數邏輯
3. 統一section header編號

版本 1.4 (2024-02-01)
重要修改：
1. 修復 testpair 顯示「主算法異常」問題：
   - 在 MasterBaziMatcher.match() 方法中添加數據修復邏輯
   - 當計算出現異常時，嘗試修復缺失字段並重新計算
   - 改進 _fallback_match() 方法，確保 module_scores 字段存在
   
2. 四柱顯示加前綴（年月日時）：
   - 修改 format_pairing_info() 函數：四柱: 年柱甲子 月柱乙丑 日柱丙寅 時柱丁卯
   - 修改 format_personal_data() 函數：四柱: 年柱甲子 月柱乙丑 日柱丙寅 時柱丁卯
   - 修改 generate_ai_prompt() 函數：四柱：年柱甲子 月柱乙丑 日柱丙寅 時柱丁卯

3. 英文顯示改回中文：
   - ProfessionalBaziCalculator.analyze_spouse_star()：將 'strong', 'medium', 'weak', 'none', 'unknown' 改為 '強', '中', '弱', '無', '未知'
   - MasterBaziMatcher._calculate_spouse_carriage_score()：更新 effective_scores 映射
   - MasterBaziMatcher._evaluate_primary_lock()：配偶星有效性比較改為中文
   - ProfessionalBaziCalculator.analyze_spouse_star()：返回中文有效性描述

4. 改進異常處理：
   - MasterBaziMatcher.match()：添加數據修復和重新計算機制
   - 避免直接回退到 fallback 模式

影響：
- testpair 命令現在可以正常顯示完整的師傅級分析
- 所有四柱顯示都清晰標註年月日時
- 用戶看到的都是中文描述，體驗更佳
- 配對計算更穩定，減少異常情況
"""
# ========修正紀錄結束 ========#