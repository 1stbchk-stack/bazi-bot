# ========== 真太陽時配置 ==========
TRUE_SOLAR_TIME_ENABLED = True       # 啟用真太陽時校正
DEFAULT_LONGITUDE = 114.17           # 香港經度 (度)
LONGITUDE_CORRECTION = 4             # 經度差1度 = 4分鐘
DAY_BOUNDARY_HOUR = 23               # 日界線 (23點換日)
DAY_BOUNDARY_MINUTE = 0
MISSING_MINUTE_HANDLING = 0          # 分鐘缺失時使用0分鐘

# ========== 評分系統配置 ==========
# 起始與保底分數
BASE_SCORE = 72                      # 起始基準分
REALITY_FLOOR = 68                   # 現實保底分（無硬傷）
TERMINATION_SCORE = 45               # 終止評級分
STRONG_WARNING_FLOOR = 55            # 強烈警告下限

# 模組分數上限
ENERGY_RESCUE_CAP = 35               # 能量救應上限
PERSONALITY_RISK_CAP = -25           # 人格風險上限（扣分）
PRESSURE_PENALTY_CAP = -20           # 刑沖壓力上限（扣分）
SHEN_SHA_BONUS_CAP = 12              # 神煞加持上限
SHEN_SHA_FLOOR = 7                   # 神煞保底分
RESOLUTION_BONUS_CAP = 15            # 專業化解上限
TIME_CORRECTION_CAP = 10             # 時間校正上限
TOTAL_PENALTY_CAP = -50              # 總扣分上限

# 分數閾值
THRESHOLD_TERMINATION = 45           # 終止線
THRESHOLD_STRONG_WARNING = 55        # 強烈警告線
THRESHOLD_WARNING = 60               # 警告線
THRESHOLD_CONTACT_ALLOWED = 68       # 可交換聯絡方式
THRESHOLD_GOOD_MATCH = 75            # 良好婚配
THRESHOLD_EXCELLENT_MATCH = 85       # 上等婚配
THRESHOLD_PERFECT_MATCH = 93         # 極品婚配

# ========== 能量救應配置 ==========
WEAK_THRESHOLD = 10                  # 極弱閾值（百分比）
STRONG_THRESHOLD = 50                # 強旺閾值
EXTREME_WEAK_BONUS = 12              # 極弱救應加分
DEMAND_MATCH_BONUS = 6               # 需求對接加分
PASS_THROUGH_BONUS = 8               # 通關五行加分
RESCUE_DEDUCTION_RATIO = 0.3         # 救應抵銷後續扣分的比例

# ========== 身強弱計算配置 ==========
DEFAULT_STRENGTH_SCORE = 50          # 身強弱默認分數
MONTH_WEIGHT = 35                    # 月令權重
TONG_GEN_WEIGHT = 25                 # 通根權重
SUPPORT_WEIGHT = 15                  # 生扶權重
STRENGTH_THRESHOLD_STRONG = 65       # 身強閾值
STRENGTH_THRESHOLD_MEDIUM = 35       # 身中閾值

# ========== 結構核心配置 ==========
# 天干組合分數
STEM_COMBINATION_FIVE_HARMONY = 6    # 五合
STEM_COMBINATION_GENERATION = 4      # 相生
STEM_COMBINATION_SAME = 2            # 比和

# 地支組合分數
BRANCH_COMBINATION_SIX_HARMONY = 5   # 六合
BRANCH_CLASH_PENALTY = -12           # 六沖扣分
BRANCH_HARM_PENALTY = -8             # 六害扣分

# 夫妻宮分數
PALACE_STABLE_BONUS = 4              # 穩定無沖
PALACE_SLIGHT_BONUS = 1              # 輕微受壓
PALACE_SEVERE_PENALTY = -8           # 嚴重受沖

# ========== 人格風險配置 ==========
PERSONALITY_RISK_PATTERNS = {
    "傷官見官": -4,
    "羊刃坐財": -4,
    "半三刑": -4,
    "財星遇劫": -3,
    "官殺混雜": -3
}
PERSONALITY_STACKED_PENALTY = -8     # 疊加風險額外扣分

# ========== 刑沖壓力配置 ==========
CLASH_PENALTY = -10                  # 六沖扣分
HARM_PENALTY = -6                    # 六害扣分
HEXAGRAM_RESOLUTION_RATIO = 0.5      # 六合解沖係數
TRIAD_RESOLUTION_RATIO = 0.6         # 三合化解係數
PASS_THROUGH_RESOLUTION_RATIO = 0.7  # 通關五行係數
SEAL_RESOLUTION_RATIO = 0.6          # 正印化殺係數

# ========== 神煞系統配置 ==========
SHEN_SHA_POSITIVE = {
    "hong_luan": 3,                  # 紅鸞
    "tian_xi": 2,                    # 天喜
    "tian_yi": 4,                    # 天乙貴人
    "tian_de": 2,                    # 天德
    "yue_de": 1,                     # 月德
    "wen_chang": 1,                  # 文昌
    "jiang_xing": 1                  # 將星
}

SHEN_SHA_NEGATIVE = {
    "yang_ren": -3,                  # 羊刃
    "jie_sha": -2,                   # 劫煞
    "wang_shen": -2,                 # 亡神
    "gu_chen": -2,                   # 孤辰
    "gua_su": -2,                    # 寡宿
    "yin_cha_yang_cuo": -3           # 陰差陽錯
}

SHEN_SHA_INTERACTION_BONUS = {
    "hongluan_tianxi": 3,            # 紅鸞+天喜
    "tianyi_tiande": 2,              # 天乙+天德
    "wenchang_jiangxing": 1          # 文昌+將星
}

SHEN_SHA_RELATIONSHIP_WEIGHT = 0.10  # 關係模型判定權重
SHEN_SHA_NEGATIVE_OVERRIDE_LIMIT = 3 # 最多3個負向神煞仍適用保底

# ========== 專業化解配置 ==========
RESOLUTION_PATTERNS = {
    "七殺+正印": 6,                  # 殺印相生
    "傷官+正財": 5,                  # 傷官生財
    "偏財+正官": 4,                  # 財官相生
    "食傷+正印": 3,                  # 食傷配印
    "財官+相生": 3                   # 財官組合
}

# ========== 現實校準配置 ==========
NO_HARD_PROBLEM_FLOOR = 68           # 無硬傷保底分
DAY_CLASH_CAP = 75                   # 日支六沖上限
AGE_GAP_PENALTY_11_15 = -3           # 11-15歲年齡差距扣分
AGE_GAP_PENALTY_16_PLUS = -5         # 16歲以上年齡差距扣分
FATAL_RISK_CAP = 45                  # 致命風險上限（強制終止）

# ========== 關係模型判定閾值 ==========
BALANCED_MAX_DIFF = 10               # 平衡型最大差異
SUPPLY_MIN_DIFF = 15                 # 供求型最小差異
DEBT_MIN_DIFF = 20                   # 相欠型最小差異
DEBT_MAX_AVG = 60                    # 相欠型最大平均分

# ========== 性能配置 ==========
CACHE_TTL_HOURS = 24                 # 緩存有效期
MAX_SEARCH_YEARS = 10                # 最大搜尋年份範圍
SEARCH_BATCH_SIZE = 50               # 搜尋批次大小
PARALLEL_WORKERS = 4                 # 並行工作線程數
QUERY_TIMEOUT_SECONDS = 30           # 查詢超時時間
SOULMATE_CANDIDATES = 500            # 真命天子搜索候選數量

# ========== 時間信心度映射 ==========
TIME_CONFIDENCE_LEVELS = {
    'high': 0.95,                    # 精確到分鐘
    'medium': 0.90,                  # 精確到小時
    'low': 0.85,                     # 模糊描述
    'estimated': 0.80                # 系統估算
}

# ========== 解釋性報告配置 ==========
EXPLANATORY_REPORT_ENABLED = True
MAX_KEY_POINTS = 3                   # 每個部分最大關鍵點數
INCLUDE_SCORE_BREAKDOWN = True       # 包含分數細分
SHOW_CONFIDENCE_LEVEL = True         # 顯示置信度
SHOW_OPENING_TOPICS = True           # 顯示開場話題

# ========== 八字大師配置 ==========
MASTER_BAZI_CONFIG = {
    "SCORING_SYSTEM": {
        "THRESHOLDS": {
            "contact_allowed": THRESHOLD_CONTACT_ALLOWED,  # 68分
            "good_match": THRESHOLD_GOOD_MATCH,            # 75分
            "excellent_match": THRESHOLD_EXCELLENT_MATCH,  # 85分
            "perfect_match": THRESHOLD_PERFECT_MATCH       # 93分
        },
        "BASE_SCORE": BASE_SCORE,                          # 72分
        "REALITY_FLOOR": REALITY_FLOOR                     # 68分
    },
    "MATCH_LOGIC": {
        "MIN_CANDIDATES": 3,                               # 最少候選人數
        "MAX_CANDIDATES": 10,                              # 最多候選人數
        "SCORE_GAP_THRESHOLD": 5,                          # 分數差距閾值
        "EXCLUDE_PREVIOUS_DAYS": 30                        # 排除近期配對天數
    }
}

# ========== 評分閾值配置 ==========
SCORING_THRESHOLDS = {
    "TERMINATION_SCORE": THRESHOLD_TERMINATION,      # 終止線45分
    "STRONG_WARNING": THRESHOLD_STRONG_WARNING,      # 強烈警告線55分
    "WARNING": THRESHOLD_WARNING,                    # 警告線60分
    "contact_allowed": THRESHOLD_CONTACT_ALLOWED,    # 可交換聯絡方式68分
    "good_match": THRESHOLD_GOOD_MATCH,              # 良好婚配75分
    "excellent_match": THRESHOLD_EXCELLENT_MATCH,    # 上等婚配85分
    "perfect_match": THRESHOLD_PERFECT_MATCH,        # 極品婚配93分
    "MINIMUM_ACCEPTABLE": THRESHOLD_CONTACT_ALLOWED  # 最低接受分數68分
}

# ========== 真命天子精英閾值 ==========
ELITE_BAZI_CONFIG = {
    "ELITE_THRESHOLD": 75,                     # 精英庫底分閾值
    "PREMIUM_THRESHOLD": 85,                   # 高級精英閾值
    "MIN_DAYS_SAMPLES": 100,                   # 最小樣本天數
    "MAX_HOURS_PER_DAY": 12,                   # 每天最大時辰數
    "RANDOM_SEED_SALT": "bazi_soulmate_2026"   # 隨機種子鹽值
}

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
業務模型定義 - 所有數據模型的唯一來源
最後更新: 2026年1月30日
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# ========== 關係模型定義 ==========
RELATIONSHIP_MODELS = {
    "平衡型": {
        "description": "雙方影響力均衡，關係穩定和諧",
        "characteristics": ["互相尊重", "平等互動", "長期穩定", "溝通順暢"],
        "suggestions": ["保持溝通頻率", "共同制定目標", "定期檢視關係進度"],
        "opening_topics": ["分享日常", "共同興趣", "未來規劃", "價值觀討論"]
    },
    "供求型": {
        "description": "一方付出較多，另一方接收較多",
        "characteristics": ["互補性強", "有主導方", "需要平衡", "各取所需"],
        "suggestions": ["注意回饋機制", "避免單方面付出", "明確各自期望", "定期調整角色"],
        "opening_topics": ["互補優勢", "角色分工", "支持方式", "回饋機制"]
    },
    "相欠型": {
        "description": "有互相虧欠的緣分，需用心經營化解",
        "characteristics": ["緣分特殊", "需要化解", "挑戰較多", "成長機會"],
        "suggestions": ["耐心經營關係", "理解包容差異", "尋求專業指導", "設定合理期望"],
        "opening_topics": ["理解包容", "溝通方式", "成長空間", "化解方法"]
    },
    "混合型": {
        "description": "關係複雜多元，需靈活應對",
        "characteristics": ["多面性", "變化多", "需要智慧", "適應性強"],
        "suggestions": ["靈活應對變化", "多角度思考問題", "保持開放心態", "學習溝通技巧"],
        "opening_topics": ["多樣話題", "靈活應對", "學習交流", "探索發現"]
    }
}

# ========== 評級標準 ==========
RATING_SCALE = {
    93: {"name": "🌟 萬中無一", "description": "極品組合，互相成就", "percentage": "約3%"},
    85: {"name": "✨ 上等婚配", "description": "明顯互補，幸福率高", "percentage": "約15%"},
    75: {"name": "✅ 主流成功", "description": "現實高成功率，可經營", "percentage": "約55%"},
    68: {"name": "🤝 普通可行", "description": "有缺點但可努力經營", "percentage": "約20%"},
    60: {"name": "⚠️ 需要努力", "description": "問題較多，需謹慎考慮", "percentage": "約5%"},
    55: {"name": "🔴 不建議", "description": "沖剋嚴重，難長久", "percentage": "約2%"},
    0: {"name": "❌ 強烈不建議", "description": "硬傷明顯，易生變", "percentage": "<1%"}
}

# ========== 開場白建議 ==========
OPENING_LINES = {
    "GENERAL": [
        "👋 你好！系統話我哋八字幾有緣分，想認識下你。",
        "💫 八字配對系統介紹嘅朋友，打個招呼先！",
        "🌱 緣分開始，先簡單介紹下自己？",
        "✨ 覺得我哋應該幾啱傾，不如傾下偈了解下？",
        "🎯 配對到嘅朋友，你好！有興趣交流下嗎？"
    ],
    
    "BY_ELEMENT": {
        "木": "💚 我哋都係充滿生命力嘅木型人，可以傾下大自然、成長話題。",
        "火": "🔥 熱情嘅火型組合！分享下最近令你興奮嘅事？",
        "土": "🌍 務實穩重嘅土型人，傾下生活規劃、美食應該幾啱傾。",
        "金": "⚔️ 理性清晰嘅金型人，討論專業技能、理財投資有共鳴。",
        "水": "💧 感性流動嘅水型組合，音樂、藝術、心靈話題可能啱你。"
    },
    
    "BY_SCORE": {
        "high": "🌟 系統畀我哋好高分 ({score}分)，覺得應該幾有默契！",
        "medium": "✅ 系統話我哋基本配合 ({score}分)，有興趣互相了解下嗎？",
        "low": "🤝 雖然分數唔算高 ({score}分)，但都值得認識下，你點睇？"
    },
    
    "BY_MODEL": {
        "平衡型": "⚖️ 系統顯示我哋關係平衡，溝通應該好順暢。",
        "供求型": "🔄 系統話我哋幾互補，各自有可以學習嘅地方。",
        "相欠型": "💞 系統顯示我哋有特別緣分，值得用心了解。",
        "混合型": "🎭 系統話我哋關係多元化，應該幾有趣味。"
    },
    
    "TOPIC_STARTERS": {
        "興趣愛好": "你平時有咩興趣愛好？",
        "工作學習": "你做緊咩工作或者學緊咩？",
        "旅行經歷": "有冇去過邊度旅行覺得好難忘？",
        "音樂電影": "最近有冇睇到好睇嘅戲或者聽到好聽嘅歌？",
        "美食分享": "有冇咩特別鍾意食嘅嘢？",
        "未來規劃": "對未來有咩計劃或者想法？",
        "價值觀念": "你覺得一段好嘅關係最重要係咩？"
    }
}

# ========== 開場話題配置 ==========
OPENING_TOPICS = {
    "by_element": {
        "木": ["🌳 大自然與環保", "📈 成長與發展", "🎨 創意與藝術", "💚 健康與養生"],
        "火": ["🔥 熱情與動力", "🎭 娛樂與表演", "💡 創新與科技", "🎯 目標與成就"],
        "土": ["🏠 家庭與穩定", "💰 投資與理財", "🍜 美食與旅遊", "📅 規劃與執行"],
        "金": ["⚖️ 正義與原則", "💼 事業與專業", "📊 分析與邏輯", "🔧 技能與工具"],
        "水": ["🎵 音樂與藝術", "💭 思考與哲學", "🌊 變化與適應", "💧 情感與直覺"]
    },
    "by_relationship": {
        "平衡型": ["分享日常", "共同興趣", "未來規劃", "價值觀討論"],
        "供求型": ["互補優勢", "角色分工", "支持方式", "回饋機制"],
        "相欠型": ["理解包容", "溝通方式", "成長空間", "化解方法"],
        "混合型": ["多樣話題", "靈活應對", "學習交流", "探索發現"]
    },
    "by_score": {
        "high": ["深度話題", "人生規劃", "價值共鳴", "共同成長"],
        "medium": ["興趣愛好", "生活分享", "互相了解", "慢慢建立"],
        "low": ["簡單問候", "輕鬆話題", "觀察了解", "保持開放"]
    }
}

# ========== 五行元素定義 ==========
ELEMENTS = {
    "木": {
        "color": "💚",
        "traits": ["成長", "創造", "仁慈", "適應"],
        "strengths": ["有遠見", "有創意", "有韌性"],
        "weaknesses": ["理想主義", "易妥協", "不夠現實"]
    },
    "火": {
        "color": "🔥",
        "traits": ["熱情", "行動", "領導", "表現"],
        "strengths": ["有動力", "有魅力", "果斷"],
        "weaknesses": ["衝動", "急躁", "缺乏耐心"]
    },
    "土": {
        "color": "🌍",
        "traits": ["穩定", "務實", "責任", "耐心"],
        "strengths": ["可靠", "實際", "有條理"],
        "weaknesses": ["保守", "固執", "缺乏彈性"]
    },
    "金": {
        "color": "⚔️",
        "traits": ["原則", "紀律", "分析", "果斷"],
        "strengths": ["有原則", "理性", "有組織"],
        "weaknesses": ["嚴苛", "冷漠", "不夠靈活"]
    },
    "水": {
        "color": "💧",
        "traits": ["智慧", "適應", "情感", "直覺"],
        "strengths": ["有智慧", "有同理心", "適應力強"],
        "weaknesses": ["情緒化", "猶豫不決", "不夠果斷"]
    }
}

# ========== 神煞定義 ==========
SHEN_SHA_DEFINITIONS = {
    "紅鸞": {"type": "positive", "effect": "增強感情緣分，利婚戀"},
    "天喜": {"type": "positive", "effect": "喜慶之事，利婚姻感情"},
    "天乙貴人": {"type": "positive", "effect": "最吉之神，遇難有助"},
    "天德": {"type": "positive", "effect": "仁慈之德，化解凶煞"},
    "月德": {"type": "positive", "effect": "祥和之氣，逢凶化吉"},
    "文昌": {"type": "positive", "effect": "文采才華，聰明智慧"},
    "將星": {"type": "positive", "effect": "領導才能，組織能力"},
    
    "羊刃": {"type": "negative", "effect": "剛烈急躁，易有爭執"},
    "劫煞": {"type": "negative", "effect": "損失破財，人際不順"},
    "亡神": {"type": "negative", "effect": "是非口舌，心神不寧"},
    "孤辰": {"type": "negative", "effect": "孤獨傾向，人際疏離"},
    "寡宿": {"type": "negative", "effect": "孤獨傾向，婚姻不順"},
    "陰差陽錯": {"type": "negative", "effect": "時機不對，錯失良緣"}
}

# ========== 八字數據模型 ==========
@dataclass
class BaziData:
    """八字數據模型"""
    year_pillar: str
    month_pillar: str
    day_pillar: str
    hour_pillar: str
    day_stem: str
    day_stem_element: str
    day_stem_strength: str
    strength_score: float
    useful_elements: List[str]
    harmful_elements: List[str]
    spouse_star_status: str
    spouse_palace_status: str
    shen_sha_names: List[str]
    zodiac: str
    elements_balance: Dict[str, float]

# ========== 配對結果模型 ==========
@dataclass
class MatchResult:
    """配對結果模型"""
    overall_score: float
    a_to_b_score: float
    b_to_a_score: float
    relationship_model: str
    step_details: List[Dict]
    opening_suggestions: List[str]
    opening_topics: List[str]
    confidence_level: str
    time_warning: Optional[str]
    sickness_penalty: float
    sickness_reasons: List[Tuple[str, float, str]]
    calibrated_score: float
    raw_score: float

# ========== 用戶數據模型 ==========
@dataclass
class UserData:
    """用戶數據模型"""
    telegram_id: int
    username: str
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    hour_confidence: str
    hour_description: str
    gender: str
    bazi_data: BaziData
    registered_at: str
    last_active: str
    match_count_today: int
    soulmate_search_count_today: int



# ========== AI提示模板 ==========
AI_PROMPT_TEMPLATE = """請幫我分析以下八字配對：

【配對信息】
配對ID: {match_id}
整體分數: {score:.1f}分
關係模型: {model}

【用戶A】
八字: {bazi_a}
神煞: {shen_sha_a}
五行: {element_a}

【用戶B】
八字: {bazi_b}
神煞: {shen_sha_b}
五行: {element_b}

【分數詳情】
用戶A對用戶B影響: {a_to_b_score:.1f}分
用戶B對用戶A影響: {b_to_a_score:.1f}分

請從以下幾個方面分析：
1. 八字實際相處優缺點？
2. 最容易有摩擦嘅地方？
3. 長期發展要注意咩？
4. 如何化解八字中的沖剋？
5. 感情發展建議？
6. 基於分數差異，邊一方可能付出較多？
7. 神煞組合對關係嘅影響？

請用粵語回答，詳細分析。"""

# ========== 評分解釋文本 ==========
SCORE_EXPLANATIONS = {
    "ENERGY_RESCUE": "能量救應：評估雙方五行需求匹配度，可補足對方命局弱點。",
    "STRUCTURE_CORE": "結構核心：評估日柱配合和地支關係，是八字配對的基礎。",
    "PERSONALITY_RISK": "人格風險：評估十神人格衝突風險，反映性格相處難易度。",
    "PRESSURE_PENALTY": "刑沖壓力：評估地支刑沖害的壓力，反映現實相處的摩擦點。",
    "SHEN_SHA": "神煞影響：評估吉凶神煞對關係的加持或影響。",
    "RESOLUTION": "專業化解：評估特殊組合的化解能力，可減輕其他問題的影響。",
    "REALITY_CALIBRATION": "現實校準：根據現實婚姻比例調整分數，更貼近實際情況。"
}


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字排盤計算器 - 從年月日時計算八字四柱
最後更新: 2026年1月30日
"""

import logging
import json
import hashlib
import math
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import sxtwl

from config.constants import (
    TRUE_SOLAR_TIME_ENABLED, DEFAULT_LONGITUDE, LONGITUDE_CORRECTION,
    DAY_BOUNDARY_HOUR, DAY_BOUNDARY_MINUTE, MISSING_MINUTE_HANDLING,
    DEFAULT_STRENGTH_SCORE, MONTH_WEIGHT, STRENGTH_THRESHOLD_STRONG, 
    STRENGTH_THRESHOLD_MEDIUM
)
from config.models import BaziData

logger = logging.getLogger(__name__)


# ========== 時間處理工具函數 ==========
def calculate_true_solar_time(local_hour: int, local_minute: int, 
                             longitude: float, confidence: str = "high") -> Dict:
    """
    計算真太陽時
    返回: {'hour': int, 'minute': int, 'confidence': str, 'adjusted': bool}
    """
    if not TRUE_SOLAR_TIME_ENABLED:
        return {
            'hour': local_hour,
            'minute': local_minute,
            'confidence': confidence,
            'adjusted': False
        }
    
    # 計算經度差（相對於120°E）
    longitude_diff = longitude - DEFAULT_LONGITUDE
    
    # 計算時間差（每度4分鐘）
    time_diff_minutes = longitude_diff * LONGITUDE_CORRECTION
    
    # 計算真太陽時
    total_minutes = local_hour * 60 + local_minute + time_diff_minutes
    
    # 處理跨日
    if total_minutes < 0:
        total_minutes += 24 * 60
        day_adjusted = -1  # 前一日
    elif total_minutes >= 24 * 60:
        total_minutes -= 24 * 60
        day_adjusted = 1   # 後一日
    else:
        day_adjusted = 0
    
    true_hour = int(total_minutes // 60)
    true_minute = int(total_minutes % 60)
    
    # 調整置信度
    if abs(time_diff_minutes) > 10:  # 調整超過10分鐘
        new_confidence = "medium" if confidence == "high" else confidence
    else:
        new_confidence = confidence
    
    return {
        'hour': true_hour,
        'minute': true_minute,
        'confidence': new_confidence,
        'adjusted': abs(time_diff_minutes) > 1,
        'day_adjusted': day_adjusted,
        'time_diff_minutes': time_diff_minutes
    }

def apply_day_boundary(year: int, month: int, day: int, hour: int, minute: int) -> Tuple[int, int, int]:
    """
    應用23:00換日規則
    返回: (year, month, day) 調整後的日期
    """
    if hour >= DAY_BOUNDARY_HOUR and minute >= DAY_BOUNDARY_MINUTE:
        # 23:00後算翌日
        current_date = datetime(year, month, day)
        next_date = current_date + timedelta(days=1)
        return (next_date.year, next_date.month, next_date.day)
    
    return (year, month, day)

def handle_missing_minute(hour: int, minute: Optional[int], 
                         confidence: str) -> Tuple[int, str]:
    """
    處理分鐘缺失
    規則: 分鐘缺失時使用0分鐘，置信度降級
    """
    if minute is None:
        use_minute = MISSING_MINUTE_HANDLING
        # 降級置信度
        confidence_map = {
            "high": "medium",
            "medium": "low", 
            "low": "estimated",
            "unknown": "estimated",
            "estimated": "estimated"
        }
        new_confidence = confidence_map.get(confidence, "estimated")
        logger.debug(f"分鐘缺失處理: {hour}時→{hour}:{use_minute}, 置信度{confidence}→{new_confidence}")
        return use_minute, new_confidence
    
    return minute, confidence

# ========== 八字計算器類 ==========
class BaziCalculator:
    """專業八字計算器"""
    
    # 天干地支定義
    STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 五行對應
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
    
    # 藏干系統
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
    
    # 月令強度
    MONTH_STRENGTH = {
        '木': {'寅': 1.0, '卯': 1.0, '辰': 0.7, '巳': 0.3, '午': 0.0, '未': 0.0, '申': 0.0, '酉': 0.0, '戌': 0.0, '亥': 0.8, '子': 0.6, '丑': 0.3},
        '火': {'寅': 0.8, '卯': 0.6, '辰': 0.3, '巳': 1.0, '午': 1.0, '未': 0.7, '申': 0.0, '酉': 0.0, '戌': 0.3, '亥': 0.0, '子': 0.0, '丑': 0.0},
        '土': {'寅': 0.3, '卯': 0.0, '辰': 1.0, '巳': 0.7, '午': 0.7, '未': 1.0, '申': 0.3, '酉': 0.0, '戌': 1.0, '亥': 0.0, '子': 0.0, '丑': 1.0},
        '金': {'寅': 0.0, '卯': 0.0, '辰': 0.3, '巳': 0.6, '午': 0.0, '未': 0.0, '申': 1.0, '酉': 1.0, '戌': 0.7, '亥': 0.0, '子': 0.0, '丑': 0.8},
        '水': {'寅': 0.0, '卯': 0.0, '辰': 0.0, '巳': 0.0, '午': 0.0, '未': 0.0, '申': 0.8, '酉': 0.6, '戌': 0.0, '亥': 1.0, '子': 1.0, '丑': 0.7}
    }
    
    # 五行生剋
    ELEMENT_GENERATE = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    ELEMENT_OVERCOME = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}
    ELEMENT_OVERCOME_BY = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
    
    @staticmethod
    def calculate(year: int, month: int, day: int, hour: int, 
                  gender: str = "未知", 
                  hour_confidence: str = "high",
                  minute: Optional[int] = None,
                  longitude: float = DEFAULT_LONGITUDE) -> Dict:
        """
        計算八字主函數
        模組目的: 八字排盤核心計算，包含真太陽時校正
        """
        try:
            # 處理分鐘缺失
            processed_minute, processed_confidence = handle_missing_minute(
                hour, minute, hour_confidence
            )
            
            # 計算真太陽時
            true_solar_time = calculate_true_solar_time(
                hour, processed_minute, longitude, processed_confidence
            )
            
            # 應用23:00換日規則
            adjusted_date = apply_day_boundary(
                year, month, day, true_solar_time['hour'], true_solar_time['minute']
            )
            
            # 使用調整後的日期和時間
            adjusted_year, adjusted_month, adjusted_day = adjusted_date
            adjusted_hour = true_solar_time['hour']
            
            logger.info(f"時間處理: 本地{year}-{month}-{day} {hour}:{processed_minute} "
                       f"→ 真太陽時{adjusted_year}-{adjusted_month}-{adjusted_day} {adjusted_hour}:{true_solar_time['minute']} "
                       f"(置信度:{processed_confidence}→{true_solar_time['confidence']})")
            
            # 使用sxtwl計算四柱
            day_obj = sxtwl.fromSolar(adjusted_year, adjusted_month, adjusted_day)
            
            # 獲取四柱
            y_gz = day_obj.getYearGZ()
            m_gz = day_obj.getMonthGZ()
            d_gz = day_obj.getDayGZ()
            
            # 計算時柱
            hour_pillar = BaziCalculator._calculate_hour_pillar(
                adjusted_year, adjusted_month, adjusted_day, adjusted_hour
            )
            
            # 組裝八字數據
            bazi_data = {
                "year_pillar": f"{BaziCalculator._get_stem_name(y_gz.tg)}"
                              f"{BaziCalculator._get_branch_name(y_gz.dz)}",
                "month_pillar": f"{BaziCalculator._get_stem_name(m_gz.tg)}"
                               f"{BaziCalculator._get_branch_name(m_gz.dz)}",
                "day_pillar": f"{BaziCalculator._get_stem_name(d_gz.tg)}"
                             f"{BaziCalculator._get_branch_name(d_gz.dz)}",
                "hour_pillar": hour_pillar,
                "zodiac": BaziCalculator._get_zodiac(y_gz.dz),
                "day_stem": BaziCalculator._get_stem_name(d_gz.tg),
                "day_stem_element": BaziCalculator.STEM_ELEMENTS.get(
                    BaziCalculator._get_stem_name(d_gz.tg), ""
                ),
                "hour_confidence": true_solar_time['confidence'],
                "gender": gender,
                "birth_year": year,
                "birth_month": month,
                "birth_day": day,
                "birth_hour": hour,
                "birth_minute": processed_minute,
                "birth_longitude": longitude,
                "true_solar_hour": adjusted_hour,
                "true_solar_minute": true_solar_time['minute'],
                "adjusted_year": adjusted_year,
                "adjusted_month": adjusted_month,
                "adjusted_day": adjusted_day,
                "time_adjusted": true_solar_time['adjusted'],
                "day_adjusted": true_solar_time.get('day_adjusted', 0)
            }
            
            # 計算詳細分析
            bazi_data = BaziCalculator._analyze_details(bazi_data, gender)
            
            logger.info(f"✅ 八字計算完成: {bazi_data['year_pillar']} "
                       f"{bazi_data['month_pillar']} {bazi_data['day_pillar']} "
                       f"{bazi_data['hour_pillar']}")
            
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
        
        # 轉換小時為地支時辰
        hour_branch = BaziCalculator._hour_to_branch(hour)
        
        # 五鼠遁日起時法
        day_stem_mod = day_stem % 5
        start_stem_map = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8}
        start_stem = start_stem_map.get(day_stem_mod, 0)
        
        hour_stem = (start_stem + hour_branch) % 10
        
        return (f"{BaziCalculator.STEMS[hour_stem]}"
                f"{BaziCalculator.BRANCHES[hour_branch]}")
    
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
    def _analyze_details(bazi_data: Dict, gender: str) -> Dict:
        """分析八字詳細信息"""
        # 計算五行分佈
        bazi_data["elements"] = BaziCalculator._calculate_elements(bazi_data)
        
        # 計算身強弱
        strength_score = BaziCalculator._calculate_strength_score(bazi_data)
        bazi_data["strength_score"] = strength_score
        bazi_data["day_stem_strength"] = BaziCalculator._determine_strength(strength_score)
        
        # 計算從格類型
        bazi_data["cong_ge_type"] = BaziCalculator._determine_cong_ge(bazi_data, gender)
        
        # 計算喜用神
        bazi_data["useful_elements"] = BaziCalculator._calculate_useful_elements(bazi_data, gender)
        bazi_data["harmful_elements"] = BaziCalculator._calculate_harmful_elements(bazi_data, gender)
        
        # 分析夫妻星
        spouse_status, spouse_effective = BaziCalculator._analyze_spouse_star(bazi_data, gender)
        bazi_data["spouse_star_status"] = spouse_status
        bazi_data["spouse_star_effective"] = spouse_effective
        
        # 分析夫妻宮
        palace_status, pressure_score = BaziCalculator._analyze_spouse_palace(bazi_data)
        bazi_data["spouse_palace_status"] = palace_status
        bazi_data["pressure_score"] = pressure_score
        
        # 計算神煞
        shen_sha_names, shen_sha_bonus = BaziCalculator._calculate_shen_sha(bazi_data)
        bazi_data["shen_sha_names"] = shen_sha_names
        bazi_data["shen_sha_bonus"] = shen_sha_bonus
        
        # 計算十神結構
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
        
        weights = [1.0, 1.8, 1.5, 1.2]  # 年月日時權重
        
        for pillar, weight in zip(pillars, weights):
            if len(pillar) >= 2:
                stem = pillar[0]
                branch = pillar[1]
                
                # 天干五行
                stem_element = BaziCalculator.STEM_ELEMENTS.get(stem)
                if stem_element:
                    elements[stem_element] += weight
                
                # 地支五行
                branch_element = BaziCalculator.BRANCH_ELEMENTS.get(branch)
                if branch_element:
                    elements[branch_element] += weight * 0.5
                
                # 藏干五行
                hidden_stems = BaziCalculator.BRANCH_HIDDEN_STEMS.get(branch, [])
                for hidden_stem, hidden_weight in hidden_stems:
                    hidden_element = BaziCalculator.STEM_ELEMENTS.get(hidden_stem)
                    if hidden_element:
                        elements[hidden_element] += weight * hidden_weight
        
        # 標準化為百分比
        total = sum(elements.values())
        if total > 0:
            for element in elements:
                elements[element] = round(elements[element] * 100 / total, 1)
        
        return elements
    
    @staticmethod
    def _calculate_strength_score(bazi_data: Dict) -> float:
        """計算身強弱分數"""
        day_stem = bazi_data.get('day_stem', '')
        day_element = BaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        
        if not day_element:
            return DEFAULT_STRENGTH_SCORE
        
        score = 0
        
        # 月令強度
        month_branch = bazi_data.get('month_pillar', '  ')[1] if len(bazi_data.get('month_pillar', '  ')) >= 2 else ''
        month_strength = BaziCalculator.MONTH_STRENGTH.get(day_element, {}).get(month_branch, 0)
        score += month_strength * MONTH_WEIGHT
        
        # 通根力量
        tong_gen_score = BaziCalculator._calculate_tong_gen(bazi_data, day_element)
        score += tong_gen_score
        
        # 生扶力量
        support_score = BaziCalculator._calculate_support(bazi_data, day_element)
        score += support_score
        
        return min(100, max(0, score))
    
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
                        score += weight * 15  # 通根權重
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
                
                # 檢查是否為印星（生我者）
                for base, gen in BaziCalculator.ELEMENT_GENERATE.items():
                    if gen == day_element and base == stem_element:
                        score += 8  # 印星權重
                        break
        
        return score
    
    @staticmethod
    def _determine_strength(score: float) -> str:
        """判斷身強弱"""
        if score >= STRENGTH_THRESHOLD_STRONG:
            return '強'
        elif score >= STRENGTH_THRESHOLD_MEDIUM:
            return '中'
        else:
            return '弱'
    
    @staticmethod
    def _determine_cong_ge(bazi_data: Dict, gender: str) -> str:
        """判斷從格類型"""
        strength = bazi_data.get('day_stem_strength', '中')
        strength_score = bazi_data.get('strength_score', 50)
        
        if strength == '弱' and strength_score < 20:
            return "從格"
        elif strength == '強' and strength_score > 80:
            return "專旺格"
        else:
            return "正格"
    
    @staticmethod
    def _calculate_useful_elements(bazi_data: Dict, gender: str) -> List[str]:
        """計算喜用神"""
        day_stem = bazi_data.get('day_stem', '')
        day_element = BaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        strength = bazi_data.get('day_stem_strength', '中')
        cong_ge = bazi_data.get('cong_ge_type', '正格')
        
        useful_elements = []
        
        if cong_ge == "從格":
            # 從格喜順從
            elements = bazi_data.get('elements', {})
            max_element = max(elements.items(), key=lambda x: x[1])[0]
            useful_elements.append(max_element)
        elif cong_ge == "專旺格":
            # 專旺格喜同類
            useful_elements.append(day_element)
        else:
            # 正格喜用計算
            if strength == '強':
                # 身強喜克泄耗
                if day_element in BaziCalculator.ELEMENT_OVERCOME_BY:
                    useful_elements.append(BaziCalculator.ELEMENT_OVERCOME_BY[day_element])
                if day_element in BaziCalculator.ELEMENT_GENERATE:
                    useful_elements.append(BaziCalculator.ELEMENT_GENERATE[day_element])
            elif strength == '弱':
                # 身弱喜生扶
                for base, gen in BaziCalculator.ELEMENT_GENERATE.items():
                    if gen == day_element:
                        useful_elements.append(base)
                useful_elements.append(day_element)
            else:
                # 中和喜平衡
                month_branch = bazi_data.get('month_pillar', '  ')[1]
                month_element = BaziCalculator.BRANCH_ELEMENTS.get(month_branch, '')
                
                if month_element in ['子', '丑', '亥']:
                    useful_elements.append('火')
                elif month_element in ['巳', '午', '未']:
                    useful_elements.append('水')
                elif month_element in ['寅', '卯']:
                    useful_elements.append('金')
                elif month_element in ['申', '酉']:
                    useful_elements.append('木')
        
        return list(set(useful_elements))
    
    @staticmethod
    def _calculate_harmful_elements(bazi_data: Dict, gender: str) -> List[str]:
        """計算忌神"""
        useful_elements = bazi_data.get('useful_elements', [])
        day_stem = bazi_data.get('day_stem', '')
        day_element = BaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        
        harmful_elements = []
        all_elements = ['木', '火', '土', '金', '水']
        
        # 忌神為非喜用神
        for element in all_elements:
            if element not in useful_elements:
                harmful_elements.append(element)
        
        return harmful_elements
    
    @staticmethod
    def _analyze_spouse_star(bazi_data: Dict, gender: str) -> Tuple[str, str]:
        """分析夫妻星"""
        # 配偶星映射
        SPOUSE_STARS = {
            '男': {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'},
            '女': {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
        }
        
        day_stem = bazi_data.get('day_stem', '')
        day_element = BaziCalculator.STEM_ELEMENTS.get(day_stem, '')
        
        if gender not in ['男', '女'] or not day_element:
            return "未知", "unknown"
        
        # 獲取配偶星元素
        spouse_element = SPOUSE_STARS[gender].get(day_element, '')
        if not spouse_element:
            return "無夫妻星", "none"
        
        # 檢查夫妻星存在性
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
                
                # 檢查天干
                if BaziCalculator.STEM_ELEMENTS.get(stem) == spouse_element:
                    spouse_count += 1
                
                # 檢查地支
                if BaziCalculator.BRANCH_ELEMENTS.get(branch) == spouse_element:
                    spouse_count += 1
                
                # 檢查藏干
                hidden_stems = BaziCalculator.BRANCH_HIDDEN_STEMS.get(branch, [])
                for hidden_stem, _ in hidden_stems:
                    if BaziCalculator.STEM_ELEMENTS.get(hidden_stem) == spouse_element:
                        spouse_count += 1
        
        # 判斷有效性
        if spouse_count == 0:
            return "無夫妻星", "none"
        elif spouse_count == 1:
            return "夫妻星單一", "weak"
        elif spouse_count == 2:
            return "夫妻星明顯", "medium"
        else:
            return "夫妻星旺盛", "strong"
    
    @staticmethod
    def _analyze_spouse_palace(bazi_data: Dict) -> Tuple[str, float]:
        """分析夫妻宮"""
        day_pillar = bazi_data.get('day_pillar', '')
        if len(day_pillar) < 2:
            return "未知", 0
        
        day_branch = day_pillar[1]
        
        # 檢查刑沖害
        pressure_score = 0
        status = "穩定"
        
        # 地支六沖
        clashes = {'子': '午', '午': '子', '丑': '未', '未': '丑',
                  '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
                  '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
        
        # 地支六害
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
                
                # 檢查六沖
                if clashes.get(day_branch) == branch:
                    pressure_score += 15
                    status = "嚴重受沖"
                    break
                
                # 檢查六害
                if harms.get(day_branch) == branch:
                    pressure_score += 10
                    status = "相害"
                    break
        
        return status, pressure_score
    
    @staticmethod
    def _calculate_shen_sha(bazi_data: Dict) -> Tuple[str, float]:
        """計算神煞"""
        from config.constants import (
            SHEN_SHA_POSITIVE, SHEN_SHA_NEGATIVE, SHEN_SHA_INTERACTION_BONUS,
            SHEN_SHA_BONUS_CAP, SHEN_SHA_FLOOR
        )
        
        shen_sha_list = []
        total_bonus = 0
        
        # 獲取八字信息
        day_stem = bazi_data.get('day_stem', '')
        year_branch = bazi_data.get('year_pillar', '  ')[1]
        month_branch = bazi_data.get('month_pillar', '  ')[1]
        day_branch = bazi_data.get('day_pillar', '  ')[1]
        hour_branch = bazi_data.get('hour_pillar', '  ')[1]
        
        all_branches = [year_branch, month_branch, day_branch, hour_branch]
        
        # 紅鸞計算
        hong_luan_map = {
            '子': '午', '丑': '巳', '寅': '辰', '卯': '卯',
            '辰': '寅', '巳': '丑', '午': '子', '未': '亥',
            '申': '戌', '酉': '酉', '戌': '申', '亥': '未'
        }
        
        hong_luan_branch = hong_luan_map.get(year_branch)
        if hong_luan_branch in all_branches:
            shen_sha_list.append("紅鸞")
            total_bonus += SHEN_SHA_POSITIVE.get("hong_luan", 0)
        
        # 天喜計算
        tian_xi_map = {
            '子': '寅', '丑': '丑', '寅': '子', '卯': '亥',
            '辰': '戌', '巳': '酉', '午': '申', '未': '未',
            '申': '午', '酉': '巳', '戌': '辰', '亥': '卯'
        }
        
        tian_xi_branch = tian_xi_map.get(year_branch)
        if tian_xi_branch in all_branches:
            shen_sha_list.append("天喜")
            total_bonus += SHEN_SHA_POSITIVE.get("tian_xi", 0)
        
        # 天乙貴人
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
                total_bonus += SHEN_SHA_POSITIVE.get("tian_yi", 0)
                break
        
        # 其他神煞計算...
        # 這裡簡化處理，實際需要完整實現
        
        # 上限控制
        if total_bonus > SHEN_SHA_BONUS_CAP:
            logger.debug(f"神煞上限控制: {total_bonus}→{SHEN_SHA_BONUS_CAP}分")
            total_bonus = SHEN_SHA_BONUS_CAP
        
        shen_sha_names = "、".join(shen_sha_list) if shen_sha_list else "無"
        return shen_sha_names, total_bonus
    
    @staticmethod
    def _calculate_shi_shen(bazi_data: Dict, gender: str) -> str:
        """計算十神結構"""
        day_stem = bazi_data.get('day_stem', '')
        
        if not day_stem:
            return "普通結構"
        
        # 十神映射表（簡化版本）
        shi_shen_map = {
            '甲': {'甲': '比肩', '乙': '劫財', '丙': '食神', '丁': '傷官', '戊': '偏財',
                  '己': '正財', '庚': '七殺', '辛': '正官', '壬': '偏印', '癸': '正印'},
            # 其他天干映射...
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
        
        # 分析結構特點
        structure_features = []
        
        if '正官' in shi_shen_list and '正財' in shi_shen_list:
            structure_features.append("財官相生")
        
        if '七殺' in shi_shen_list and '正印' in shi_shen_list:
            structure_features.append("殺印相生")
        
        if '傷官' in shi_shen_list and '正財' in shi_shen_list:
            structure_features.append("傷官生財")
        
        if structure_features:
            return "、".join(structure_features)
        else:
            return "普通結構"
    
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
        
        # 默認中午，置信度低
        return 12, 'low'


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
關係分析器 - 分析八字配對的關係特點
最後更新: 2026年1月30日
"""

import logging
from typing import Dict, List, Tuple, Any, Optional

from config.constants import (
    THRESHOLD_PERFECT_MATCH, THRESHOLD_EXCELLENT_MATCH, 
    THRESHOLD_GOOD_MATCH, THRESHOLD_CONTACT_ALLOWED,
    THRESHOLD_WARNING, THRESHOLD_STRONG_WARNING,
    THRESHOLD_TERMINATION
)

logger = logging.getLogger(__name__)

class RelationshipAnalyzer:
    """關係分析器"""
    
    @staticmethod
    def analyze(match_result: Dict, bazi1: Dict, bazi2: Dict) -> Dict:
        """
        分析關係特點
        模組目的: 提供關係深度分析
        """
        analysis = {
            "model": match_result.get("relationship_model", ""),
            "description": "",
            "strengths": [],
            "challenges": [],
            "suggestions": [],
            "opening_topics": []
        }
        
        # 生成關係描述
        analysis["description"] = RelationshipAnalyzer._generate_description(match_result)
        
        # 分析優勢
        analysis["strengths"] = RelationshipAnalyzer._identify_strengths(bazi1, bazi2, match_result)
        
        # 分析挑戰
        analysis["challenges"] = RelationshipAnalyzer._identify_challenges(bazi1, bazi2, match_result)
        
        # 生成建議
        analysis["suggestions"] = RelationshipAnalyzer._generate_suggestions(match_result)
        
        # 生成開場話題
        analysis["opening_topics"] = RelationshipAnalyzer._generate_opening_topics(match_result, bazi1, bazi2)
        
        return analysis
    
    @staticmethod
    def _generate_description(match_result: Dict) -> str:
        """生成關係描述"""
        score = match_result.get("score", 0)
        
        if score >= THRESHOLD_PERFECT_MATCH:
            return "這是萬中無一的極品組合，雙方能夠深度互相成就，共同創造美好未來。"
        elif score >= THRESHOLD_EXCELLENT_MATCH:
            return "高質量的上等婚配，有明顯的互補性和成長潛力，幸福指數很高。"
        elif score >= THRESHOLD_GOOD_MATCH:
            return "良好的婚配組合，屬於現實中成功率高的類型，只要用心經營就會很美滿。"
        elif score >= THRESHOLD_CONTACT_ALLOWED:
            return "現實中可經營的關係，有一定挑戰但可以通過努力克服，需要雙方投入。"
        elif score >= THRESHOLD_WARNING:
            return "關係存在明顯挑戰，需要謹慎考慮和充分溝通，不適合急進發展。"
        else:
            return "關係中存在較多沖剋，建議尋找更合適的對象，或需要專業指導才能開始。"
    
    @staticmethod
    def _identify_strengths(bazi1: Dict, bazi2: Dict, match_result: Dict) -> List[str]:
        """識別關係優勢"""
        strengths = []
        
        # 檢查能量救應
        module_scores = match_result.get("module_scores", {})
        if module_scores.get('energy_rescue', 0) > 20:
            strengths.append("能量救應強烈，五行互補明顯")
        
        if module_scores.get('shen_sha_bonus', 0) >= 7:
            strengths.append("神煞加持有力，緣分標記明顯")
        
        if module_scores.get('resolution_bonus', 0) > 8:
            strengths.append("專業化解有效，衝突可轉化")
        
        # 檢查喜用神匹配
        useful1 = bazi1.get('useful_elements', [])
        useful2 = bazi2.get('useful_elements', [])
        
        common_useful = set(useful1) & set(useful2)
        if common_useful:
            strengths.append(f"喜用神共通: {', '.join(common_useful)}")
        
        return strengths
    
    @staticmethod
    def _identify_challenges(bazi1: Dict, bazi2: Dict, match_result: Dict) -> List[str]:
        """識別關係挑戰"""
        challenges = []
        
        # 檢查模組分數
        module_scores = match_result.get("module_scores", {})
        
        if module_scores.get('personality_risk', 0) < -15:
            challenges.append("人格衝突風險較高")
        
        if module_scores.get('pressure_penalty', 0) < -10:
            challenges.append("地支刑沖壓力較大")
        
        # 檢查日支相沖
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        
        six_clash_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'),
                          ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        pair = tuple(sorted([day_branch1, day_branch2]))
        
        if pair in six_clash_pairs:
            challenges.append(f"日支相沖 ({day_branch1}↔{day_branch2})，容易有價值觀和生活習慣衝突")
        
        # 檢查時間信心度
        confidence1 = bazi1.get('hour_confidence', 'high')
        confidence2 = bazi2.get('hour_confidence', 'high')
        if confidence1 in ['low', 'estimated'] or confidence2 in ['low', 'estimated']:
            challenges.append("出生時間較模糊，結果可能浮動")
        
        return challenges
    
    @staticmethod
    def _generate_suggestions(match_result: Dict) -> List[str]:
        """生成具體建議"""
        suggestions = []
        score = match_result.get("score", 0)
        model = match_result.get("relationship_model", "")
        
        if score >= THRESHOLD_PERFECT_MATCH:
            suggestions.append("珍惜這段難得緣分，互相扶持成長")
            suggestions.append("定期進行深度溝通，保持心靈連接")
            suggestions.append("共同設定人生目標，實現共贏發展")
        elif score >= THRESHOLD_EXCELLENT_MATCH:
            suggestions.append("用心經營關係，互相包容理解")
            suggestions.append("注意溝通方式，避免誤會積累")
            suggestions.append("培養共同興趣，增強情感連接")
        elif score >= THRESHOLD_GOOD_MATCH:
            suggestions.append("需要更多耐心，慢慢建立信任")
            suggestions.append("明確各自底線，避免衝突升級")
            suggestions.append("學習解決問題，增強關係韌性")
        elif score >= THRESHOLD_CONTACT_ALLOWED:
            suggestions.append("謹慎考慮開始，充分了解對方")
            suggestions.append("設定合理期望，避免失望")
            suggestions.append("如有衝突，及時溝通化解")
        else:
            suggestions.append("建議尋找更合適的對象")
            suggestions.append("如堅持開始，需要專業指導")
            suggestions.append("保護自己情感，避免傷害")
        
        # 根據模型添加建議
        if "供求型" in model:
            suggestions.append("注意關係平衡，避免單方面付出耗盡")
        elif "相欠型" in model:
            suggestions.append("理解緣分特點，用耐心化解挑戰")
        elif "混合型" in model:
            suggestions.append("需要靈活應對關係中的各種情況")
        
        return suggestions
    
    @staticmethod
    def _generate_opening_topics(match_result: Dict, bazi1: Dict, bazi2: Dict) -> List[str]:
        """生成開場話題"""
        topics = []
        score = match_result.get("score", 0)
        model = match_result.get("relationship_model", "")
        
        # 根據分數選擇話題類型
        if score >= THRESHOLD_EXCELLENT_MATCH:
            topics.append("分享人生重要經歷")
            topics.append("討論共同價值觀")
            topics.append("規劃未來藍圖")
        elif score >= THRESHOLD_GOOD_MATCH:
            topics.append("談談興趣愛好")
            topics.append("分享生活趣事")
            topics.append("討論旅行計劃")
        else:
            topics.append("簡單自我介紹")
            topics.append("聊聊日常小事")
            topics.append("分享最近看的電影")
        
        # 根據模型添加話題
        if "平衡型" in model:
            topics.append("討論平等相處方式")
        elif "供求型" in model:
            topics.append("談談互相支持的方式")
        elif "相欠型" in model:
            topics.append("分享學習成長的經驗")
        
        return topics[:3]  # 返回前3個話題


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
評分引擎 - 八字配對的唯一評分入口
最後更新: 2026年1月30日
"""

import logging
from typing import Dict, List, Tuple, Any, Optional
from core.bazi_calculator import BaziCalculator

from config.constants import (
    BASE_SCORE, REALITY_FLOOR, TERMINATION_SCORE, STRONG_WARNING_FLOOR,
    ENERGY_RESCUE_CAP, PERSONALITY_RISK_CAP, PRESSURE_PENALTY_CAP,
    SHEN_SHA_BONUS_CAP, RESOLUTION_BONUS_CAP, TOTAL_PENALTY_CAP,
    WEAK_THRESHOLD, EXTREME_WEAK_BONUS, DEMAND_MATCH_BONUS, PASS_THROUGH_BONUS,
    STEM_COMBINATION_FIVE_HARMONY, STEM_COMBINATION_GENERATION, STEM_COMBINATION_SAME,
    BRANCH_COMBINATION_SIX_HARMONY, BRANCH_CLASH_PENALTY, BRANCH_HARM_PENALTY,
    PALACE_STABLE_BONUS, PALACE_SLIGHT_BONUS, PALACE_SEVERE_PENALTY,
    PERSONALITY_RISK_PATTERNS, PERSONALITY_STACKED_PENALTY,
    CLASH_PENALTY, HARM_PENALTY, HEXAGRAM_RESOLUTION_RATIO,
    TRIAD_RESOLUTION_RATIO, PASS_THROUGH_RESOLUTION_RATIO,
    SHEN_SHA_POSITIVE, SHEN_SHA_NEGATIVE, SHEN_SHA_INTERACTION_BONUS,
    RESOLUTION_PATTERNS, NO_HARD_PROBLEM_FLOOR, DAY_CLASH_CAP,
    AGE_GAP_PENALTY_11_15, AGE_GAP_PENALTY_16_PLUS, FATAL_RISK_CAP,
    BALANCED_MAX_DIFF, SUPPLY_MIN_DIFF, DEBT_MIN_DIFF, DEBT_MAX_AVG
)
from config.models import MatchResult, RATING_SCALE
from config.texts import TIME_CONFIDENCE_TEXTS

logger = logging.getLogger(__name__)

class ScoringEngineError(Exception):
    """評分引擎錯誤"""
    pass

class ScoringEngine:
    """八字配對評分引擎 - 唯一評分入口"""
    
    @staticmethod
    def get_rating(score: float) -> str:
        """
        統一評級函數
        所有模塊必須調用此函數獲取評級，確保一致性
        """
        thresholds = sorted(RATING_SCALE.keys(), reverse=True)
        for threshold in thresholds:
            if score >= threshold:
                return RATING_SCALE[threshold]["name"]
        return "❌ 強烈不建議"
    
    @staticmethod
    def calculate(bazi1: Dict, bazi2: Dict, gender1: str, gender2: str) -> Dict:
        """
        八字配對主函數 - 唯一評分入口
        嚴格遵循評分模組順序與救應優先原則
        返回: 包含所有評分信息的字典
        """
        try:
            logger.info("開始八字配對評分計算")
            
            # 初始化結果
            result = {
                "score": 0,
                "a_to_b_score": 0,
                "b_to_a_score": 0,
                "relationship_model": "",
                "details": [],
                "step_details": [],
                "module_scores": {},
                "bazi1": bazi1,
                "bazi2": bazi2
            }
            
            # 第1步: 計算基礎分數
            base_score = BASE_SCORE
            result["score"] = base_score
            result["step_details"].append({"step": "起始分", "score": base_score})
            result["details"].append(f"起始基準分: {base_score}分")
            
            # 第2步: 計算能量救應 (優先計算)
            rescue_score, rescue_details = ScoringEngine._calculate_energy_rescue(bazi1, bazi2)
            result["score"] += rescue_score
            result["step_details"].append({"step": "能量救應", "score": rescue_score, "details": rescue_details})
            result["module_scores"]["energy_rescue"] = rescue_score
            result["details"].append(f"能量救應: +{rescue_score:.1f}分")
            
            # 第3步: 計算結構核心
            structure_score, structure_details = ScoringEngine._calculate_structure_core(bazi1, bazi2)
            # 應用救應抵銷
            structure_score = ScoringEngine._apply_rescue_deduction(structure_score, rescue_score)
            result["score"] += structure_score
            result["step_details"].append({"step": "結構核心", "score": structure_score, "details": structure_details})
            result["module_scores"]["structure_core"] = structure_score
            result["details"].append(f"結構核心: {structure_score:+.1f}分")
            
            # 第4步: 計算人格風險
            raw_personality_score, personality_details = ScoringEngine._calculate_personality_risk(bazi1, bazi2)
            # 應用救應抵銷
            personality_score = ScoringEngine._apply_rescue_deduction(raw_personality_score, rescue_score)
            personality_score = max(personality_score, PERSONALITY_RISK_CAP)
            result["score"] += personality_score
            result["step_details"].append({"step": "人格風險", "score": personality_score, "details": personality_details})
            result["module_scores"]["personality_risk"] = personality_score
            result["details"].append(f"人格風險: {personality_score:+.1f}分 (原始: {raw_personality_score:+.1f})")
            
            # 第5步: 計算刑沖壓力
            raw_pressure_score, pressure_details = ScoringEngine._calculate_pressure_penalty(bazi1, bazi2)
            # 應用化解機制
            pressure_score = ScoringEngine._apply_resolution_mechanism(raw_pressure_score, bazi1, bazi2)
            # 應用救應抵銷
            pressure_score = ScoringEngine._apply_rescue_deduction(pressure_score, rescue_score)
            pressure_score = max(pressure_score, PRESSURE_PENALTY_CAP)
            result["score"] += pressure_score
            result["step_details"].append({"step": "刑沖壓力", "score": pressure_score, "details": pressure_details})
            result["module_scores"]["pressure_penalty"] = pressure_score
            result["details"].append(f"刑沖壓力: {pressure_score:+.1f}分 (原始: {raw_pressure_score:+.1f})")
            
            # 第6步: 計算神煞加持
            shen_sha_score, shen_sha_details = ScoringEngine._calculate_shen_sha_bonus(bazi1, bazi2)
            result["score"] += shen_sha_score
            result["step_details"].append({"step": "神煞加持", "score": shen_sha_score, "details": shen_sha_details})
            result["module_scores"]["shen_sha_bonus"] = shen_sha_score
            result["details"].append(f"神煞加持: +{shen_sha_score:.1f}分")
            
            # 第7步: 計算專業化解
            resolution_score, resolution_details = ScoringEngine._calculate_resolution_bonus(bazi1, bazi2)
            result["score"] += resolution_score
            result["step_details"].append({"step": "專業化解", "score": resolution_score, "details": resolution_details})
            result["module_scores"]["resolution_bonus"] = resolution_score
            result["details"].append(f"專業化解: +{resolution_score:.1f}分")
            
            # 第8步: 計算雙向影響分數
            a_to_b, b_to_a, directional_details = ScoringEngine._calculate_asymmetric_scores(bazi1, bazi2, gender1, gender2)
            result["a_to_b_score"] = a_to_b
            result["b_to_a_score"] = b_to_a
            result["step_details"].append({"step": "雙向影響", "a_to_b": a_to_b, "b_to_a": b_to_a, "details": directional_details})
            
            # 第9步: 確定關係模型
            relationship_model, model_details = ScoringEngine._determine_relationship_model(a_to_b, b_to_a, bazi1, bazi2)
            result["relationship_model"] = relationship_model
            result["step_details"].append({"step": "關係模型", "model": relationship_model, "details": model_details})
            
            # 第10步: 檢查致命風險
            has_fatal_risk = ScoringEngine._check_hard_problems(bazi1, bazi2)
            
            # 第11步: 應用現實校準
            calibrated_score = ScoringEngine._apply_reality_calibration(
                result["score"], bazi1, bazi2, has_fatal_risk
            )
            result["score"] = calibrated_score
            
            # 第12步: 限制分數範圍
            result["score"] = max(0, min(100, round(result["score"], 1)))
            
            # 第13步: 生成評級
            result["rating"] = ScoringEngine.get_rating(result["score"])
            
            logger.info(f"評分計算完成: 總分 {result['score']}分, 評級: {result['rating']}")
            
            return result
            
        except Exception as e:
            logger.error(f"評分計算錯誤: {e}", exc_info=True)
            raise ScoringEngineError(f"評分計算失敗: {str(e)}")
    
    @staticmethod
    def _calculate_energy_rescue(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """
        計算能量救應分數
        加分理由: 雙方五行互補，能補足對方命局弱點
        """
        score = 0
        details = []
        rescued_elements = set()
        
        # 獲取雙方五行分佈
        elements1 = bazi1.get('elements', {})
        elements2 = bazi2.get('elements', {})
        
        # 檢查極弱救應
        for element, percent in elements1.items():
            if percent < WEAK_THRESHOLD and element not in rescued_elements:
                if elements2.get(element, 0) > 30:
                    score += EXTREME_WEAK_BONUS
                    rescued_elements.add(element)
                    details.append(f"A方{element}極弱({percent}%)，B方強旺({elements2[element]}%)，極弱救應+{EXTREME_WEAK_BONUS}分")
                    break
        
        # 檢查需求對接
        useful1 = bazi1.get('useful_elements', [])
        useful2 = bazi2.get('useful_elements', [])
        
        # A的需求在B處得到滿足
        for element in useful1:
            if element not in rescued_elements and elements2.get(element, 0) > 20:
                score += DEMAND_MATCH_BONUS
                rescued_elements.add(element)
                details.append(f"A喜{element}，B有{elements2[element]}%，需求對接+{DEMAND_MATCH_BONUS}分")
                break
        
        # B的需求在A處得到滿足
        for element in useful2:
            if element not in rescued_elements and elements1.get(element, 0) > 20:
                score += DEMAND_MATCH_BONUS
                rescued_elements.add(element)
                details.append(f"B喜{element}，A有{elements1[element]}%，需求對接+{DEMAND_MATCH_BONUS}分")
                break
        
        # 上限控制
        final_score = min(ENERGY_RESCUE_CAP, score)
        
        if final_score != score:
            details.append(f"能量救應上限控制: {score}→{final_score}分")
        
        logger.debug(f"能量救應分數: {final_score:.1f}")
        return final_score, details
    
    @staticmethod
    def _calculate_structure_core(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """
        計算結構核心分數
        加分理由: 天干地支配合良好，關係基礎穩固
        減分理由: 地支刑沖害，容易產生摩擦
        """
        score = 0
        details = []
        
        # 日柱天干關係
        day_stem1 = bazi1.get('day_stem', '')
        day_stem2 = bazi2.get('day_stem', '')
        
        stem_pair = tuple(sorted([day_stem1, day_stem2]))
        
        # 檢查天干五合
        five_harmony_pairs = [('甲', '己'), ('乙', '庚'), ('丙', '辛'), ('丁', '壬'), ('戊', '癸')]
        if stem_pair in five_harmony_pairs:
            score += STEM_COMBINATION_FIVE_HARMONY
            details.append(f"天干五合 {stem_pair}: +{STEM_COMBINATION_FIVE_HARMONY}分")
        elif BaziCalculator.ELEMENT_GENERATE.get(
            BaziCalculator.STEM_ELEMENTS.get(day_stem1, '')
        ) == BaziCalculator.STEM_ELEMENTS.get(day_stem2, ''):
            score += STEM_COMBINATION_GENERATION
            details.append(f"天干相生 {day_stem1}→{day_stem2}: +{STEM_COMBINATION_GENERATION}分")
        elif BaziCalculator.STEM_ELEMENTS.get(day_stem1, '') == \
             BaziCalculator.STEM_ELEMENTS.get(day_stem2, ''):
            score += STEM_COMBINATION_SAME
            details.append(f"天干比和 {day_stem1}≡{day_stem2}: +{STEM_COMBINATION_SAME}分")
        
        # 日柱地支關係
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        
        branch_pair = tuple(sorted([day_branch1, day_branch2]))
        
        # 檢查地支六合
        six_harmony_pairs = [('子', '丑'), ('寅', '亥'), ('卯', '戌'), 
                            ('辰', '酉'), ('巳', '申'), ('午', '未')]
        if branch_pair in six_harmony_pairs:
            score += BRANCH_COMBINATION_SIX_HARMONY
            details.append(f"地支六合 {branch_pair}: +{BRANCH_COMBINATION_SIX_HARMONY}分")
        
        # 檢查地支六沖
        six_clash_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'),
                          ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        if branch_pair in six_clash_pairs:
            score += BRANCH_CLASH_PENALTY
            details.append(f"地支六沖 {branch_pair}: {BRANCH_CLASH_PENALTY}分")
        
        # 檢查地支六害
        six_harm_pairs = [('子', '未'), ('丑', '午'), ('寅', '巳'),
                         ('卯', '辰'), ('申', '亥'), ('酉', '戌')]
        if branch_pair in six_harm_pairs:
            score += BRANCH_HARM_PENALTY
            details.append(f"地支六害 {branch_pair}: {BRANCH_HARM_PENALTY}分")
        
        # 夫妻宮互動
        palace_score1 = bazi1.get('pressure_score', 0)
        palace_score2 = bazi2.get('pressure_score', 0)
        
        if palace_score1 == 0 and palace_score2 == 0:
            score += PALACE_STABLE_BONUS
            details.append(f"夫妻宮穩定: +{PALACE_STABLE_BONUS}分")
        elif palace_score1 > 20 or palace_score2 > 20:
            # 檢查是否已在日柱地支關係中計算過
            if not (branch_pair in six_clash_pairs or branch_pair in six_harm_pairs):
                score += PALACE_SEVERE_PENALTY
                details.append(f"夫妻宮嚴重受沖: {PALACE_SEVERE_PENALTY}分")
        elif palace_score1 < 10 and palace_score2 < 10:
            score += PALACE_SLIGHT_BONUS
            details.append(f"夫妻宮輕微壓力: +{PALACE_SLIGHT_BONUS}分")
        
        logger.debug(f"結構核心分數: {score:.1f}分")
        return score, details
    
    @staticmethod
    def _calculate_personality_risk(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """
        計算人格風險分數
        減分理由: 十神人格衝突，性格難以協調
        """
        score = 0
        details = []
        
        # 獲取十神結構
        structure1 = bazi1.get('shi_shen_structure', '')
        structure2 = bazi2.get('shi_shen_structure', '')
        
        # 檢查風險組合
        for pattern, penalty in PERSONALITY_RISK_PATTERNS.items():
            if pattern in structure1:
                score += penalty
                details.append(f"A方{pattern}: {penalty}分")
            
            if pattern in structure2:
                score += penalty
                details.append(f"B方{pattern}: {penalty}分")
        
        # 檢查疊加風險
        risk_count = 0
        for pattern in PERSONALITY_RISK_PATTERNS:
            if pattern in structure1:
                risk_count += 1
            if pattern in structure2:
                risk_count += 1
        
        if risk_count >= 2:
            score += PERSONALITY_STACKED_PENALTY
            details.append(f"疊加風險({risk_count}個): {PERSONALITY_STACKED_PENALTY}分")
        
        logger.debug(f"人格風險分數: {score:.1f}分")
        return score, details
    
    @staticmethod
    def _calculate_pressure_penalty(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """
        計算刑沖壓力分數
        減分理由: 地支刑沖害過多，現實相處壓力大
        """
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
        
        # 檢查六沖
        six_clash_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'),
                          ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        
        # 檢查六害
        six_harm_pairs = [('子', '未'), ('丑', '午'), ('寅', '巳'),
                         ('卯', '辰'), ('申', '亥'), ('酉', '戌')]
        
        clash_count = 0
        harm_count = 0
        
        for b1 in branches1:
            for b2 in branches2:
                pair = tuple(sorted([b1, b2]))
                
                if pair in six_clash_pairs:
                    penalty = CLASH_PENALTY
                    score += penalty
                    clash_count += 1
                    details.append(f"六沖 {b1}↔{b2}: {penalty}分")
                
                if pair in six_harm_pairs:
                    penalty = HARM_PENALTY
                    score += penalty
                    harm_count += 1
                    details.append(f"六害 {b1}↔{b2}: {penalty}分")
        
        if clash_count > 0 or harm_count > 0:
            details.append(f"總計: 六沖{clash_count}個, 六害{harm_count}個")
        
        logger.debug(f"刑沖壓力分數: {score:.1f}分")
        return score, details
    
    @staticmethod
    def _calculate_shen_sha_bonus(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """
        計算神煞加持分數
        加分理由: 吉神增強緣分，凶神增加困難
        """
        details = []
        
        # 獲取雙方神煞分數
        bonus1 = bazi1.get('shen_sha_bonus', 0)
        bonus2 = bazi2.get('shen_sha_bonus', 0)
        
        total_bonus = bonus1 + bonus2
        
        # 記錄基礎分數
        details.append(f"A方神煞: {bazi1.get('shen_sha_names', '無')} ({bonus1}分)")
        details.append(f"B方神煞: {bazi2.get('shen_sha_names', '無')} ({bonus2}分)")
        
        # 互動加成
        shen_sha1 = bazi1.get('shen_sha_names', '')
        shen_sha2 = bazi2.get('shen_sha_names', '')
        
        # 檢查紅鸞天喜組合
        if '紅鸞' in shen_sha1 and '天喜' in shen_sha2:
            total_bonus += SHEN_SHA_INTERACTION_BONUS.get("hongluan_tianxi", 0)
            details.append(f"紅鸞天喜組合: +{SHEN_SHA_INTERACTION_BONUS.get('hongluan_tianxi', 0)}分")
        elif '天喜' in shen_sha1 and '紅鸞' in shen_sha2:
            total_bonus += SHEN_SHA_INTERACTION_BONUS.get("hongluan_tianxi", 0)
            details.append(f"天喜紅鸞組合: +{SHEN_SHA_INTERACTION_BONUS.get('hongluan_tianxi', 0)}分")
        
        # 上限控制
        if total_bonus > SHEN_SHA_BONUS_CAP:
            details.append(f"神煞上限控制: {total_bonus}→{SHEN_SHA_BONUS_CAP}分")
            total_bonus = SHEN_SHA_BONUS_CAP
        
        logger.debug(f"神煞加持分數: {total_bonus:.1f}分")
        return total_bonus, details
    
    @staticmethod
    def _calculate_resolution_bonus(bazi1: Dict, bazi2: Dict) -> Tuple[float, List[str]]:
        """
        計算專業化解分數
        加分理由: 特殊組合能化解其他問題
        """
        score = 0
        details = []
        
        # 獲取十神結構
        structure1 = bazi1.get('shi_shen_structure', '')
        structure2 = bazi2.get('shi_shen_structure', '')
        
        # 檢查化解組合
        for pattern, bonus in RESOLUTION_PATTERNS.items():
            pattern1, pattern2 = pattern.split("+")
            
            if (pattern1 in structure1 and pattern2 in structure2) or \
               (pattern2 in structure1 and pattern1 in structure2):
                score += bonus
                details.append(f"化解組合 {pattern}: +{bonus}分")
        
        # 上限控制
        final_score = min(RESOLUTION_BONUS_CAP, score)
        
        if final_score != score:
            details.append(f"專業化解上限控制: {score}→{final_score}分")
        
        logger.debug(f"專業化解分數: {final_score:.1f}分")
        return final_score, details
    
    @staticmethod
    def _calculate_asymmetric_scores(bazi1: Dict, bazi2: Dict, 
                                   gender1: str, gender2: str) -> Tuple[float, float, List[str]]:
        """
        計算雙向不對稱分數
        計算理由: 關係中雙方影響力不同
        """
        details = []
        
        # A對B的影響分數
        a_to_b, a_to_b_details = ScoringEngine._calculate_directional_score(
            bazi1, bazi2, gender1, gender2, "A→B"
        )
        details.extend(a_to_b_details)
        
        # B對A的影響分數
        b_to_a, b_to_a_details = ScoringEngine._calculate_directional_score(
            bazi2, bazi1, gender2, gender1, "B→A"
        )
        details.extend(b_to_a_details)
        
        logger.debug(f"雙向分數: A→B={a_to_b:.1f}, B→A={b_to_a:.1f}")
        return a_to_b, b_to_a, details
    
    @staticmethod
    def _calculate_directional_score(source_bazi: Dict, target_bazi: Dict,
                                   source_gender: str, target_gender: str,
                                   direction: str) -> Tuple[float, List[str]]:
        """計算單向影響分數"""
        score = 50  # 起始分
        details = []
        
        # 喜用神匹配
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
        
        # 配偶星影響
        target_spouse_effective = target_bazi.get('spouse_star_effective', 'unknown')
        if target_spouse_effective == 'strong':
            score += 8
            details.append(f"{direction} 配偶星旺盛: +8分")
        elif target_spouse_effective == 'medium':
            score += 5
            details.append(f"{direction} 配偶星明顯: +5分")
        elif target_spouse_effective == 'weak':
            score += 2
            details.append(f"{direction} 配偶星單一: +2分")
        
        # 夫妻宮影響
        target_pressure = target_bazi.get('pressure_score', 0)
        if target_pressure < 5:
            score += 5
            details.append(f"{direction} 夫妻宮穩定: +5分")
        elif target_pressure > 15:
            score -= 5
            details.append(f"{direction} 夫妻宮受沖: -5分")
        
        # 神煞影響
        target_shen_sha = target_bazi.get('shen_sha_names', '')
        if '紅鸞' in target_shen_sha or '天喜' in target_shen_sha:
            score += 3
            details.append(f"{direction} 紅鸞/天喜: +3分")
        if '天乙貴人' in target_shen_sha:
            score += 2
            details.append(f"{direction} 天乙貴人: +2分")
        
        final_score = max(0, min(100, round(score, 1)))
        details.append(f"{direction} 最終分數: {final_score:.1f}")
        
        logger.debug(f"單向分數: {direction}={final_score:.1f}")
        return final_score, details
    
    @staticmethod
    def _determine_relationship_model(a_to_b: float, b_to_a: float, 
                                    bazi1: Dict, bazi2: Dict) -> Tuple[str, List[str]]:
        """
        確定關係模型
        判定理由: 根據雙向分數差異判斷關係類型
        """
        details = []
        
        diff = abs(a_to_b - b_to_a)
        avg = (a_to_b + b_to_a) / 2
        
        details.append(f"雙向差異: {diff:.1f}分，平均: {avg:.1f}分")
        
        # 獲取神煞信息
        shen_sha1 = bazi1.get('shen_sha_names', '')
        shen_sha2 = bazi2.get('shen_sha_names', '')
        
        # 神煞權重因子
        shen_sha_weight = 0
        if '紅鸞' in shen_sha1 and '天喜' in shen_sha2:
            shen_sha_weight += 0.10
            details.append("紅鸞天喜組合: +0.10權重")
        if '天喜' in shen_sha1 and '紅鸞' in shen_sha2:
            shen_sha_weight += 0.10
            details.append("天喜紅鸞組合: +0.10權重")
        if '天乙貴人' in shen_sha1 or '天乙貴人' in shen_sha2:
            shen_sha_weight += 0.05
            details.append("天乙貴人: +0.05權重")
        
        # 調整後的差異
        adjusted_diff = diff * (1 - shen_sha_weight)
        details.append(f"調整後差異: {adjusted_diff:.1f} (神煞權重: {shen_sha_weight:.2f})")
        
        # 判定關係模型
        model = ""
        
        if adjusted_diff < BALANCED_MAX_DIFF:
            model = "平衡型"
            details.append(f"差異<{BALANCED_MAX_DIFF}，判定為平衡型")
        elif a_to_b > b_to_a + SUPPLY_MIN_DIFF:
            model = "供求型 (A供應B)"
            details.append(f"A→B > B→A + {SUPPLY_MIN_DIFF}，判定為供求型(A供應B)")
        elif b_to_a > a_to_b + SUPPLY_MIN_DIFF:
            model = "供求型 (B供應A)"
            details.append(f"B→A > A→B + {SUPPLY_MIN_DIFF}，判定為供求型(B供應A)")
        elif adjusted_diff > DEBT_MIN_DIFF and avg < DEBT_MAX_AVG:
            model = "相欠型"
            details.append(f"差異>{DEBT_MIN_DIFF}且平均<{DEBT_MAX_AVG}，判定為相欠型")
        else:
            model = "混合型"
            details.append("不符合其他條件，判定為混合型")
        
        logger.debug(f"關係模型: {model}")
        return model, details
    
    @staticmethod
    def _apply_reality_calibration(score: float, bazi1: Dict, bazi2: Dict, 
                                  has_fatal_risk: bool) -> float:
        """
        應用現實校準
        校準理由: 使分數分佈更符合現實婚姻比例
        """
        original_score = score
        
        # 致命風險強制終止
        if has_fatal_risk:
            score = min(score, FATAL_RISK_CAP)
        
        # 無硬傷保底
        if not has_fatal_risk:
            score = max(score, NO_HARD_PROBLEM_FLOOR)
        
        # 日支六沖上限
        has_day_clash = ScoringEngine._check_day_branch_clash(bazi1, bazi2)
        if has_day_clash:
            score = min(score, DAY_CLASH_CAP)
        
        # 年齡差距調整
        age_diff = abs(bazi1.get('birth_year', 0) - bazi2.get('birth_year', 0))
        if age_diff > 15:
            score += AGE_GAP_PENALTY_16_PLUS
        elif age_diff > 10:
            score += AGE_GAP_PENALTY_11_15
        
        # 總扣分上限控制
        base_score = BASE_SCORE
        minimum_score = base_score + TOTAL_PENALTY_CAP
        
        if score < minimum_score:
            score = minimum_score
        
        logger.debug(f"現實校準: {original_score}→{score}分")
        return score
    
    @staticmethod
    def _apply_rescue_deduction(raw_penalty: float, rescue_score: float) -> float:
        """
        應用救應抵銷機制
        抵銷理由: 能量救應可以部分抵銷後續扣分
        """
        if raw_penalty >= 0:
            return raw_penalty
        
        # 抵銷比例
        deduction_ratio = 0.3
        
        # 可抵銷的懲罰量
        deductible_amount = rescue_score * deduction_ratio
        
        # 應用抵銷
        adjusted_penalty = raw_penalty + deductible_amount
        
        # 確保不會變成加分
        final_penalty = min(0, adjusted_penalty)
        
        logger.debug(f"救應抵銷: 懲罰{raw_penalty:.1f}→{final_penalty:.1f}")
        return final_penalty
    
    @staticmethod
    def _apply_resolution_mechanism(raw_penalty: float, bazi1: Dict, bazi2: Dict) -> float:
        """
        應用化解機制
        化解理由: 特殊組合能減輕刑沖壓力
        """
        if raw_penalty >= 0:
            return raw_penalty
        
        # 檢查是否有化解因素
        has_resolution, resolution_factor = ScoringEngine._check_resolution_exists(bazi1, bazi2)
        
        if not has_resolution:
            return raw_penalty
        
        # 應用化解係數
        adjusted_penalty = raw_penalty * resolution_factor
        
        logger.debug(f"化解機制: 壓力{raw_penalty:.1f}→{adjusted_penalty:.1f}")
        return adjusted_penalty
    
    @staticmethod
    def _check_resolution_exists(bazi1: Dict, bazi2: Dict) -> Tuple[bool, float]:
        """檢查是否存在化解因素"""
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
        
        # 檢查六合解沖
        six_harmony_pairs = [('子', '丑'), ('寅', '亥'), ('卯', '戌'), 
                            ('辰', '酉'), ('巳', '申'), ('午', '未')]
        for b1 in branches1:
            for b2 in branches2:
                if (b1, b2) in six_harmony_pairs or (b2, b1) in six_harmony_pairs:
                    logger.debug(f"六合化解存在: {b1}↔{b2}")
                    return True, HEXAGRAM_RESOLUTION_RATIO
        
        # 檢查三合化解
        triads = [
            ('寅', '午', '戌'),
            ('亥', '卯', '未'),
            ('申', '子', '辰'),
            ('巳', '酉', '丑')
        ]
        
        all_branches = branches1 + branches2
        for triad in triads:
            count = sum(1 for branch in triad if branch in all_branches)
            if count >= 2:
                logger.debug(f"三合化解存在: {triad}")
                return True, TRIAD_RESOLUTION_RATIO
        
        # 檢查通關五行
        day_element1 = bazi1.get('day_stem_element', '')
        day_element2 = bazi2.get('day_stem_element', '')
        
        all_elements = ['木', '火', '土', '金', '水']
        for middle in all_elements:
            if (BaziCalculator.ELEMENT_GENERATE.get(day_element1) == middle and
                BaziCalculator.ELEMENT_GENERATE.get(middle) == day_element2):
                logger.debug(f"通關五行化解: {day_element1}→{middle}→{day_element2}")
                return True, PASS_THROUGH_RESOLUTION_RATIO
        
        return False, 1.0
    
    @staticmethod
    def _check_hard_problems(bazi1: Dict, bazi2: Dict) -> bool:
        """檢查是否有硬傷問題"""
        # 檢查多重嚴重沖煞
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
        
        six_clash_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'),
                          ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        
        clash_count = 0
        for b1 in branches1:
            for b2 in branches2:
                pair = tuple(sorted([b1, b2]))
                if pair in six_clash_pairs:
                    clash_count += 1
        
        if clash_count >= 3:
            logger.warning(f"多重嚴重沖煞: {clash_count}個六沖")
            return True
        
        return False
    
    @staticmethod
    def _check_day_branch_clash(bazi1: Dict, bazi2: Dict) -> bool:
        """檢查日支是否六沖"""
        day_branch1 = bazi1.get('day_pillar', '  ')[1]
        day_branch2 = bazi2.get('day_pillar', '  ')[1]
        
        six_clash_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'),
                          ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        pair = tuple(sorted([day_branch1, day_branch2]))
        
        has_clash = pair in six_clash_pairs
        if has_clash:
            logger.debug(f"日支六沖: {day_branch1}↔{day_branch2}")
        
        return has_clash

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時間處理器 - 處理真太陽時、23:00換日規則
最後更新: 2026年1月30日
"""

import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta

from config.constants import (
    TRUE_SOLAR_TIME_ENABLED, DEFAULT_LONGITUDE, LONGITUDE_CORRECTION,
    DAY_BOUNDARY_HOUR, DAY_BOUNDARY_MINUTE, MISSING_MINUTE_HANDLING
)

logger = logging.getLogger(__name__)

class TimeProcessor:
    """時間處理器"""
    
    @staticmethod
    def calculate_true_solar_time(local_hour: int, local_minute: int, 
                                  longitude: float, confidence: str = "high") -> Dict:
        """
        計算真太陽時
        返回: {'hour': int, 'minute': int, 'confidence': str, 'adjusted': bool}
        """
        if not TRUE_SOLAR_TIME_ENABLED:
            return {
                'hour': local_hour,
                'minute': local_minute,
                'confidence': confidence,
                'adjusted': False
            }
        
        # 計算經度差
        longitude_diff = longitude - DEFAULT_LONGITUDE
        
        # 計算時間差
        time_diff_minutes = longitude_diff * LONGITUDE_CORRECTION
        
        # 計算真太陽時
        total_minutes = local_hour * 60 + local_minute + time_diff_minutes
        
        # 處理跨日
        if total_minutes < 0:
            total_minutes += 24 * 60
            day_adjusted = -1
        elif total_minutes >= 24 * 60:
            total_minutes -= 24 * 60
            day_adjusted = 1
        else:
            day_adjusted = 0
        
        true_hour = int(total_minutes // 60)
        true_minute = int(total_minutes % 60)
        
        # 調整置信度
        if abs(time_diff_minutes) > 10:
            new_confidence = "medium" if confidence == "high" else confidence
        else:
            new_confidence = confidence
        
        return {
            'hour': true_hour,
            'minute': true_minute,
            'confidence': new_confidence,
            'adjusted': abs(time_diff_minutes) > 1,
            'day_adjusted': day_adjusted,
            'time_diff_minutes': time_diff_minutes
        }
    
    @staticmethod
    def apply_day_boundary(year: int, month: int, day: int, hour: int, minute: int) -> Tuple[int, int, int]:
        """
        應用23:00換日規則
        返回: (year, month, day) 調整後的日期
        """
        if hour >= DAY_BOUNDARY_HOUR and minute >= DAY_BOUNDARY_MINUTE:
            current_date = datetime(year, month, day)
            next_date = current_date + timedelta(days=1)
            return (next_date.year, next_date.month, next_date.day)
        
        return (year, month, day)
    
    @staticmethod
    def handle_missing_minute(hour: int, minute: Optional[int], 
                             confidence: str) -> Tuple[int, str]:
        """
        處理分鐘缺失
        規則: 分鐘缺失時使用0分鐘，置信度降級
        """
        if minute is None:
            use_minute = MISSING_MINUTE_HANDLING
            confidence_map = {
                "high": "medium",
                "medium": "low", 
                "low": "estimated",
                "unknown": "estimated",
                "estimated": "estimated"
            }
            new_confidence = confidence_map.get(confidence, "estimated")
            logger.debug(f"分鐘缺失處理: {hour}時→{hour}:{use_minute}, 置信度{confidence}→{new_confidence}")
            return use_minute, new_confidence
        
        return minute, confidence
    
    @staticmethod
    def estimate_hour_from_description(description: str) -> Tuple[int, str]:
        """從描述估算時辰 (返回小時和置信度)"""
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
        
        # 默認中午，置信度低
        return 12, 'low'



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
1.1 配置常量
1.2 數據模型定義
1.3 八字計算器類
1.4 評分引擎類
1.5 關係分析器類
1.6 時間處理器類
1.7 格式化函數
1.8 AI提示函數
"""
# ========目錄結束 ========#
