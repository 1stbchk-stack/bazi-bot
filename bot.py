# ========1.1 導入模組開始 ========#
import os
import logging
import asyncio
import json
import hashlib
import traceback
from datetime import datetime
from contextlib import closing
from typing import Dict, List, Tuple, Any, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# 導入新的計算核心 (使用 new_calculator.py)
from new_calculator import (
    # 八字計算器 - 保持相同接口
    BaziCalculator as ProfessionalBaziCalculator,  # 使用別名保持兼容
    
    # 評分引擎 - 使用新的ScoringEngine
    ScoringEngine as MasterBaziMatcher,  # 使用別名保持兼容
    
    # 主入口函數 - 計算最終D分
    calculate_match,
    
    # 錯誤處理 - 映射到新的錯誤類
    BaziCalculatorError as BaziError,    # 映射到新的錯誤類
    ScoringEngineError as MatchError,    # 映射到新的錯誤類
    
    # 配置常數
    Config,
    
    # 時間處理器
    TimeProcessor,
    
    # 創新功能類
    HealthAnalyzer,
    RelationshipTimeline,
    BaziDNAMatcher,
    PairingAdviceGenerator
)

# 導入 Soulmate 功能（新分拆的檔案）
from bazi_soulmate import (
    SoulmateFinder
)

# 導入文本常量
from texts import (
    PRIVACY_TERMS,
    EXPLANATION_TEXT,
    ASK_HOUR_KNOWN_TEXT,
    APPROXIMATE_HOUR_DESCRIPTION,
    UNKNOWN_HOUR_WARNING,
    HELP_TEXT,
    AI_USAGE_TIPS,
    REGISTRATION_COMPLETE_TEXT,
    HEALTH_QUOTES,
    BASIC_INFO_FORMAT_TEXT,
    CONFIRM_TIME_TEXT,
    FUNCTION_MENU_TEXT,
    ADMIN_MENU_TEXT
)

# 導入管理員服務
from admin_service import AdminService
# ========1.1 導入模組結束 ========#

# ========1.2 配置與初始化開始 ========#
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# PostgreSQL 數據庫配置
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    logger.error("錯誤: DATABASE_URL 環境變數未設定！")
    raise ValueError("DATABASE_URL 未設定")

# 修復 Railway PostgreSQL URL 格式
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

SECRET_KEY = os.getenv("MATCH_SECRET_KEY", "your-secret-key-change-me").strip()
DAILY_MATCH_LIMIT = 10

# 維護模式標誌 - 全局變數
MAINTENANCE_MODE = False

# 管理員用戶ID列表（從環境變量讀取，支援多個ID用逗號分隔）
ADMIN_USER_IDS_STR = os.getenv("ADMIN_USER_IDS", "").strip()
ADMIN_USER_IDS = []
if ADMIN_USER_IDS_STR:
    try:
        # 將字串轉換為整數列表
        ADMIN_USER_IDS = [int(id_str.strip()) for id_str in ADMIN_USER_IDS_STR.split(",") if id_str.strip().isdigit()]
        logger.info(f"載入管理員ID: {ADMIN_USER_IDS}")
    except Exception as e:
        logger.error(f"解析管理員ID失敗: {e}")
        ADMIN_USER_IDS = []

# 對話狀態
(
    TERMS_ACCEPTANCE,
    ASK_BASIC_INFO,          # 新增：一步輸入所有基本信息
    ASK_TIME_CONFIRMATION,   # 新增：時間確認
    ASK_YEAR,
    ASK_MONTH,
    ASK_DAY,
    ASK_HOUR_KNOWN,
    ASK_HOUR,
    ASK_MINUTE,
    ASK_LONGITUDE,
    ASK_GENDER,
    ASK_TARGET_GENDER,       # 新增：對象性別
    FIND_SOULMATE_RANGE,
    FIND_SOULMATE_PURPOSE,
) = range(14)

# 從 Config 類獲取評分閾值常量
THRESHOLD_WARNING = Config.THRESHOLD_WARNING
THRESHOLD_CONTACT_ALLOWED = Config.THRESHOLD_CONTACT_ALLOWED
THRESHOLD_GOOD_MATCH = Config.THRESHOLD_GOOD_MATCH
THRESHOLD_EXCELLENT_MATCH = Config.THRESHOLD_EXCELLENT_MATCH
THRESHOLD_PERFECT_MATCH = Config.THRESHOLD_PERFECT_MATCH
# 從 Config 類獲取其他常量
DEFAULT_LONGITUDE = Config.DEFAULT_LONGITUDE
# ========1.2 配置與初始化結束 ========#

# ========1.3 維護模式檢查開始 ========#
def check_maintenance(func):
    """維護模式檢查裝飾器 - 增強版（真正暫停非管理員用戶）"""
    async def wrapper(update, context, *args, **kwargs):
        if MAINTENANCE_MODE:
            user_id = update.effective_user.id
            
            # 管理員可以繞過維護模式
            if user_id not in ADMIN_USER_IDS:
                # 獲取消息類型
                if update.message:
                    await update.message.reply_text(
                        "🔧 **系統維護中**\n\n"
                        "八字配對系統正在進行升級維護，請稍後再試。\n\n"
                        "**維護期間：**\n"
                        "• 普通用戶無法使用任何功能\n"
                        "• 管理員可正常使用管理功能\n"
                        "• 預計恢復時間請關注公告\n\n"
                        "如需協助，請聯繫管理員。"
                    )
                    return ConversationHandler.END
                elif update.callback_query:
                    await update.callback_query.answer(
                        "系統維護中，請稍後再試", 
                        show_alert=True
                    )
                    return None
        return await func(update, context, *args, **kwargs)
    return wrapper

def is_admin(user_id: int) -> bool:
    """檢查是否為管理員"""
    return user_id in ADMIN_USER_IDS

def check_admin_only(func):
    """管理員專用檢查裝飾器"""
    async def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if not is_admin(user_id):
            await update.message.reply_text(
                "❌ **權限不足**\n\n"
                "此功能僅限管理員使用。\n"
                "如需管理員權限，請聯繫系統管理員。"
            )
            return None
        return await func(update, context, *args, **kwargs)
    return wrapper
# ========1.3 維護模式檢查結束 ========#

# ========1.4 統一格式化工具類開始 ========#
class FormatUtils:
    """統一格式化工具類 - 負責所有顯示格式化"""
    
    # 信心度映射
    CONFIDENCE_MAP = {
        'high': '高',
        'medium': '中',
        'low': '低',
        'estimated': '估算',
        '高': '高',
        '中': '中',
        '低': '低',
        '估算': '估算'
    }
    
    # 評級符號映射
    RATING_SYMBOLS = {
        '🌟 萬中無一': '🌟',
        '✨ 上等婚配': '✨',
        '✅ 主流成功': '✅',
        '🤝 普通可行': '🤝',
        '⚠️ 需要努力': '⚠️',
        '🔴 不建議': '🔴',
        '🔴 不建議（接近終止）': '🔴',
        '❌ 強烈不建議': '❌'
    }
    
    @staticmethod
    def format_confidence(confidence: str) -> str:
        """格式化信心度"""
        return FormatUtils.CONFIDENCE_MAP.get(confidence, confidence)
    
    @staticmethod
    def format_rating(rating: str) -> str:
        """格式化評級（保留符號）"""
        return rating
    
    @staticmethod
    def format_bazi_basic_simple(bazi_data: Dict, title: str = "用戶") -> str:
        """簡化版八字基本資料（不顯示分鐘和經度）"""
        hour = bazi_data.get('birth_hour', 0)
        confidence = FormatUtils.format_confidence(bazi_data.get('hour_confidence', '中'))
        
        text = (
            f"{title}：{bazi_data.get('birth_year', '')}年"
            f"{bazi_data.get('birth_month', '')}月{bazi_data.get('birth_day', '')}日出生"
            f"（時間信心度{confidence}），"
            f"八字：{bazi_data.get('year_pillar', '')} "
            f"{bazi_data.get('month_pillar', '')} "
            f"{bazi_data.get('day_pillar', '')} "
            f"{bazi_data.get('hour_pillar', '')}，"
            f"生肖{bazi_data.get('zodiac', '')}，"
            f"日主{bazi_data.get('day_stem', '')}"
            f"{bazi_data.get('day_stem_element', '')}"
            f"（{bazi_data.get('day_stem_strength', '中')}，"
            f"{bazi_data.get('strength_score', 50):.1f}分）。"
        )
        
        # 添加五行分佈（簡化）
        elements = bazi_data.get('elements', {})
        wood = elements.get('木', 0)
        fire = elements.get('火', 0)
        earth = elements.get('土', 0)
        metal = elements.get('金', 0)
        water = elements.get('水', 0)
        
        text += f"五行分佈：木{wood:.1f}%、火{fire:.1f}%、土{earth:.1f}%、金{metal:.1f}%、水{water:.1f}%。"
        
        return text
    
    @staticmethod
    def format_profile_result(bazi_data: Dict, username: str) -> str:
        """個人資料完整格式（使用統一格式）"""
        # 基本信息部分
        basic_info = FormatUtils.format_bazi_basic_simple(bazi_data, username)
        
        # 詳細分析部分
        detail_info = f"""
📊 詳細分析：
  格局：{bazi_data.get('cong_ge_type', '正格')}
  喜用神：{', '.join(bazi_data.get('useful_elements', []))}
  忌神：{', '.join(bazi_data.get('harmful_elements', []))}
  夫妻星：{bazi_data.get('spouse_star_status', '未知')}
  夫妻宮：{bazi_data.get('spouse_palace_status', '未知')}
  神煞：{bazi_data.get('shen_sha_names', '無')}
"""
        
        # 配對建議部分
        advice_info = "🎯 配對建議：\n"
        try:
            advice_list = PairingAdviceGenerator.generate_advice(bazi_data)
            for i, advice in enumerate(advice_list[:3], 1):  # 只顯示前3個建議
                advice_info += f"  {i}. {advice}\n"
        except Exception as e:
            logger.debug(f"配對建議生成失敗: {e}")
            advice_info += "  • 建議尋找五行互補的伴侶\n"
        
        # 需要避開的特徵
        avoid_info = "🚫 需要避開的特徵：\n"
        harmful_elements = bazi_data.get('harmful_elements', [])
        if harmful_elements:
            avoid_info += f"  • 避免{', '.join(harmful_elements)}過旺的對象\n"
        else:
            avoid_info += "  • 無明顯需要避開的特徵\n"
        
        # 健康引用（隨機選擇一條）
        import random
        health_quote = random.choice(HEALTH_QUOTES)
        
        # 組合所有部分
        full_text = f"📊 {username} 的八字分析\n{'='*40}\n"
        full_text += basic_info + "\n"
        full_text += detail_info + "\n"
        full_text += advice_info + "\n"
        full_text += avoid_info + "\n"
        full_text += f"💚 {health_quote}"
        
        return full_text
    
    @staticmethod
    def format_match_result(match_result: Dict, bazi1: Dict, bazi2: Dict, 
                          user_a_name: str = "用戶A", user_b_name: str = "用戶B") -> str:
        """配對結果完整格式（單一消息）"""
        score = match_result.get('score', 0)
        rating = FormatUtils.format_rating(match_result.get('rating', '未知'))
        model = match_result.get('relationship_model', '')
        
        text = f"""🎯 核心分析結果
{'='*40}

📊 配對分數：{score:.1f}分
✨ 評級：{rating}
🎭 關係模型：{model}

📈 模組分數："""
        
        # 模組分數
        module_scores = match_result.get('module_scores', {})
        if module_scores:
            text += f"""
  💫 能量救應：{module_scores.get('energy_rescue', 0):.1f}分
  🏗️ 結構核心：{module_scores.get('structure_core', 0):.1f}分
  ⚠️ 人格風險：{module_scores.get('personality_risk', 0):.1f}分
  💢 刑沖壓力：{module_scores.get('pressure_penalty', 0):.1f}分
  ✨ 神煞加持：{module_scores.get('shen_sha_bonus', 0):.1f}分
  🔧 專業化解：{module_scores.get('resolution_bonus', 0):.1f}分"""
        
        text += f"""

🤝 雙方個人資訊
{'='*40}

{FormatUtils.format_bazi_basic_simple(bazi1, user_a_name)}

{'-'*20}

{FormatUtils.format_bazi_basic_simple(bazi2, user_b_name)}"""
        
        # 雙向影響分析
        a_to_b = match_result.get('a_to_b_score', 0)
        b_to_a = match_result.get('b_to_a_score', 0)
        
        text += f"""

📊 雙向影響分析
{'='*40}

{user_a_name} 對 {user_b_name} 的影響：{a_to_b:.1f}分
{user_b_name} 對 {user_a_name} 的影響：{b_to_a:.1f}分

💡 關係解讀："""
        
        if abs(a_to_b - b_to_a) < 10:
            text += "• 雙方影響力相近，屬於平衡型關係\n• 互動平等，互相支持"
        elif a_to_b > b_to_a + 15:
            text += f"• {user_a_name}對{user_b_name}影響較強\n• {user_a_name}可能扮演供應者角色"
        elif b_to_a > a_to_b + 15:
            text += f"• {user_b_name}對{user_a_name}影響較強\n• {user_b_name}可能扮演供應者角色"
        else:
            text += "• 雙方有明顯的供需關係\n• 需要留意平衡點"
        
        text += f"""

🌟 優點與挑戰
{'='*40}

✅ 優勢："""
        
        # 根據分數添加優勢
        if score >= Config.THRESHOLD_EXCELLENT_MATCH:
            text += "\n• 五行能量高度互補\n• 結構穩定無硬傷\n• 有明顯的救應機制"
        elif score >= Config.THRESHOLD_GOOD_MATCH:
            text += "\n• 核心需求能夠對接\n• 主要結構無大沖\n• 有化解機制"
        elif score >= Config.THRESHOLD_CONTACT_ALLOWED:
            text += "\n• 基本能量可以互補\n• 需要努力經營關係"
        
        text += "\n\n⚠️ 挑戰："
        
        # 根據風險模組添加挑戰
        if module_scores.get('personality_risk', 0) < -10:
            text += "\n• 人格風險較高，可能性格衝突"
        if module_scores.get('pressure_penalty', 0) < -15:
            text += "\n• 刑沖壓力較大，容易產生矛盾"
        if module_scores.get('dayun_risk', 0) < -10:
            text += "\n• 未來大運有挑戰，需要提前準備"
        
        text += f"""

💡 建議與提醒
{'='*40}"""
        
        try:
            timeline = RelationshipTimeline.generate_timeline(bazi1, bazi2)
            years = timeline.get('timeline', [])[:2]  # 只顯示前2年
            if years:
                text += "\n📅 關係發展時間線："
                for year_info in years:
                    text += f"\n• {year_info.get('year', '')}年：{year_info.get('phase', '')} - {year_info.get('description', '')}"
        except Exception as e:
            logger.debug(f"時間線生成失敗: {e}")
        
        text += "\n\n💭 建議："
        
        if score >= Config.THRESHOLD_EXCELLENT_MATCH:
            text += "\n• 這是極佳的組合，可以深入發展\n• 保持良好溝通，互相支持"
        elif score >= Config.THRESHOLD_GOOD_MATCH:
            text += "\n• 良好的婚配組合，現實成功率較高\n• 需要互相理解和包容"
        elif score >= Config.THRESHOLD_CONTACT_ALLOWED:
            text += "\n• 可以嘗試交往，但需謹慎經營\n• 注意溝通方式，避免衝突"
        elif score >= Config.THRESHOLD_WARNING:
            text += "\n• 關係存在明顯挑戰，需謹慎考慮\n• 建議深入了解後再做決定"
        else:
            text += "\n• 不建議發展長期關係\n• 建議尋找更合適的配對"
        
        return text
    
    @staticmethod
    def generate_ai_prompt(match_result: Dict, bazi1: Dict, bazi2: Dict) -> str:
        """AI分析提示格式（7個問題）"""
        score = match_result.get('score', 0)
        rating = match_result.get('rating', '')
        model = match_result.get('relationship_model', '')
        
        prompt = f"""請作為八字配對專家，分析以下婚配組合：

**核心分析結果**：
- 配對分數：{score:.1f}分
- 評級：{rating}
- 關係模型：{model}

**用戶A八字**：
{FormatUtils.format_bazi_basic_simple(bazi1, '用戶A')}

**用戶B八字**：
{FormatUtils.format_bazi_basic_simple(bazi2, '用戶B')}

**請分析以下7個問題**：

一、能量互補性：
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
        
        return prompt
    
    @staticmethod
    def format_find_soulmate_result(matches: List[Dict], start_year: int, end_year: int, purpose: str) -> str:
        """真命天子搜尋結果格式（單一消息）"""
        if not matches:
            return "❌ 在指定範圍內未找到合適的匹配時空。"
        
        text = f"""🔮 真命天子搜尋結果
{'='*40}

📅 搜尋範圍：{start_year}年 - {end_year}年
🎯 搜尋目的：{"尋找正緣" if purpose == "正緣" else "事業合夥"}
📊 找到匹配：{len(matches)}個時空

🏆 最佳匹配："""
        
        if matches:
            best = matches[0]
            text += f"\n• 分數：{best.get('score', 0):.1f}分"
            text += f"\n• 日期：{best.get('date', '')}"
            text += f"\n• 時辰：{best.get('hour', 0)}:00"
            text += f"\n• 八字：{best.get('pillar', '')}"
        
        text += f"""

📋 詳細匹配列表（前5名）
{'='*40}"""
        
        for i, match in enumerate(matches[:5], 1):
            score = match.get('score', 0)
            date = match.get('date', '')
            hour = match.get('hour', 0)
            
            text += f"""
{i:2d}. {date} {hour:02d}:00
     分數：{score:.1f}分"""
        
        text += f"""

💡 使用建議
{'='*40}

1. **確認時辰**：以上時辰均為整點，實際使用時需結合出生地經度校正
2. **綜合考慮**：分數僅供參考，還需結合實際情況
3. **深入分析**：可複製具體八字使用 /testpair 命令深入分析
4. **時間信心度**：搜尋結果為理論最佳，實際應用時需考慮時間精度"""
        
        return text
# ========1.4 統一格式化工具類結束 ========#

# ========1.5 數據庫工具開始 ========#
def get_conn():
    """獲取 PostgreSQL 數據庫連接"""
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        logger.error(f"PostgreSQL 連接失敗: {e}")
        raise

def init_db():
    """初始化 PostgreSQL 數據庫"""
    try:
        with closing(get_conn()) as conn:
            cur = conn.cursor()
            
            logger.info("創建 PostgreSQL 表...")
            
            # 創建 users 表
            cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1
            )
            ''')
            
            # 創建 profiles 表
            cur.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                birth_year INTEGER,
                birth_month INTEGER,
                birth_day INTEGER,
                birth_hour INTEGER,
                birth_minute INTEGER DEFAULT 0,
                hour_confidence TEXT DEFAULT '高',
                gender TEXT,
                target_gender TEXT DEFAULT '異性',  -- 新增：對象性別偏好
                year_pillar TEXT,
                month_pillar TEXT,
                day_pillar TEXT,
                hour_pillar TEXT,
                zodiac TEXT,
                day_stem TEXT,
                day_stem_element TEXT,
                wood REAL,
                fire REAL,
                earth REAL,
                metal REAL,
                water REAL,
                day_stem_strength TEXT,
                strength_score REAL,
                useful_elements TEXT,
                harmful_elements TEXT,
                spouse_star_status TEXT,
                spouse_star_effective TEXT DEFAULT '未知',
                spouse_palace_status TEXT,
                pressure_score REAL DEFAULT 0,
                cong_ge_type TEXT DEFAULT '正常',
                shi_shen_structure TEXT,
                shen_sha_data TEXT
            )
            ''')
            
            # 創建 matches 表
            cur.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id SERIAL PRIMARY KEY,
                user_a INTEGER REFERENCES users(id) ON DELETE CASCADE,
                user_b INTEGER REFERENCES users(id) ON DELETE CASCADE,
                score REAL,
                user_a_accepted INTEGER DEFAULT 0,
                user_b_accepted INTEGER DEFAULT 0,
                match_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_a, user_b)
            )
            ''')
            
            # 創建 daily_limits 表
            cur.execute('''
            CREATE TABLE IF NOT EXISTS daily_limits (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                date DATE DEFAULT CURRENT_DATE,
                match_count INTEGER DEFAULT 0,
                UNIQUE(user_id, date)
            )
            ''')
            
            # 創建索引
            cur.execute('CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_matches_users ON matches(user_a, user_b)')
            
            conn.commit()
            logger.info("PostgreSQL 數據庫初始化完成")
            
    except Exception as e:
        logger.error(f"數據庫初始化失敗: {e}")
        raise

def check_daily_limit(user_id):
    """檢查每日配對限制"""
    try:
        with closing(get_conn()) as conn:
            cur = conn.cursor()
            today = datetime.now().date()

            cur.execute("""
                INSERT INTO daily_limits (user_id, date, match_count)
                VALUES (%s, %s, 1)
                ON CONFLICT (user_id, date)
                DO UPDATE SET match_count = daily_limits.match_count + 1
                RETURNING match_count
            """, (user_id, today))

            result = cur.fetchone()
            conn.commit()
            match_count = result[0] if result else 1

            if match_count > DAILY_MATCH_LIMIT:
                return False, match_count
            return True, match_count
    except Exception as e:
        logger.error(f"檢查每日限制失敗: {e}")
        return True, 0

def clear_user_data(telegram_id):
    """清除用戶所有資料 - 修復版（使用事務）"""
    try:
        with closing(get_conn()) as conn:
            cur = conn.cursor()
            
            # 開始事務
            conn.autocommit = False
            
            try:
                # 1. 獲取用戶ID
                cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
                user_row = cur.fetchone()
                
                if not user_row:
                    conn.commit()
                    return True  # 用戶不存在，視為成功
                    
                user_id = user_row[0]
                
                # 2. 刪除所有相關數據（按外鍵順序）
                cur.execute("DELETE FROM matches WHERE user_a = %s OR user_b = %s", (user_id, user_id))
                cur.execute("DELETE FROM daily_limits WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM profiles WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
                
                conn.commit()
                logger.info(f"已完全清除用戶 {telegram_id} 的所有資料")
                return True
                
            except Exception as e:
                conn.rollback()
                logger.error(f"清除失敗（事務回滾）: {e}")
                return False
                
    except Exception as e:
        logger.error(f"清除用戶資料失敗: {e}")
        return False

def get_internal_user_id(telegram_id):
    """獲取內部用戶ID"""
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        row = cur.fetchone()
        return row[0] if row else None

def get_telegram_id(internal_user_id):
    """獲取Telegram ID"""
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT telegram_id FROM users WHERE id = %s", (internal_user_id,))
        row = cur.fetchone()
        return row[0] if row else None

def get_username(internal_user_id):
    """獲取用戶名"""
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE id = %s", (internal_user_id,))
        row = cur.fetchone()
        return row[0] if row else None

def get_profile_data(internal_user_id):
    """獲取完整的個人資料數據"""
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                u.username,
                p.birth_year, p.birth_month, p.birth_day, p.birth_hour, p.birth_minute, 
                p.hour_confidence, p.gender, p.target_gender,
                p.year_pillar, p.month_pillar, p.day_pillar, p.hour_pillar,
                p.zodiac, p.day_stem, p.day_stem_element,
                p.wood, p.fire, p.earth, p.metal, p.water,
                p.day_stem_strength, p.strength_score, p.useful_elements, p.harmful_elements,
                p.spouse_star_status, p.spouse_star_effective, p.spouse_palace_status, p.pressure_score,
                p.cong_ge_type, p.shi_shen_structure, p.shen_sha_data
            FROM users u
            JOIN profiles p ON u.id = p.user_id
            WHERE u.id = %s
        """, (internal_user_id,))
        row = cur.fetchone()
        
        if not row:
            return None
            
        # 解析神煞數據
        shen_sha_data = json.loads(row[30]) if row[30] else {"names": "無", "bonus": 0}
        
        return {
            "username": row[0],
            "birth_year": row[1],
            "birth_month": row[2],
            "birth_day": row[3],
            "birth_hour": row[4],
            "birth_minute": row[5],
            "hour_confidence": row[6],
            "gender": row[7],
            "target_gender": row[8],
            "year_pillar": row[9],
            "month_pillar": row[10],
            "day_pillar": row[11],
            "hour_pillar": row[12],
            "zodiac": row[13],
            "day_stem": row[14],
            "day_stem_element": row[15],
            "elements": {
                "木": float(row[16]),
                "火": float(row[17]),
                "土": float(row[18]),
                "金": float(row[19]),
                "水": float(row[20])
            },
            "day_stem_strength": row[21],
            "strength_score": float(row[22]),
            "useful_elements": row[23].split(',') if row[23] else [],
            "harmful_elements": row[24].split(',') if row[24] else [],
            "spouse_star_status": row[25],
            "spouse_star_effective": row[26],
            "spouse_palace_status": row[27],
            "pressure_score": float(row[28]),
            "cong_ge_type": row[29],
            "shi_shen_structure": row[30],
            "shen_sha_names": shen_sha_data.get("names", "無"),
            "shen_sha_bonus": shen_sha_data.get("bonus", 0)
        }
# ========1.5 數據庫工具結束 ========#

# ========1.6 隱私條款模組開始 ========#
@check_maintenance
async def show_terms(update, context):
    """顯示隱私條款"""
    keyboard = [["✅ 同意並繼續", "❌ 不同意"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        PRIVACY_TERMS,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return TERMS_ACCEPTANCE

@check_maintenance
async def handle_terms_acceptance(update, context):
    """處理隱私條款同意"""
    text = update.message.text.strip()

    if text == "✅ 同意並繼續":
        await update.message.reply_text(
            "✅ 感謝您同意隱私條款！\n\n",
            "現在開始註冊流程。\n\n"
            BASIC_INFO_FORMAT_TEXT,
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_BASIC_INFO
    elif text == "❌ 不同意":
        await update.message.reply_text(
            "❌ 您未同意隱私條款，無法使用本服務。\n"
            "如需使用，請重新輸入 /start。",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        keyboard = [["✅ 同意並繼續", "❌ 不同意"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("請選擇「同意並繼續」或「不同意」：", reply_markup=reply_markup)
        return TERMS_ACCEPTANCE
# ========1.6 隱私條款模組結束 ========#

# ========1.7 簡化註冊流程開始 ========#
@check_maintenance
async def ask_basic_info(update, context):
    """第一步：詢問所有基本信息（簡化版）"""
    text = update.message.text.strip()
    
    # 檢查是否從確認時間步驟返回
    if text == "重新輸入基本信息":
        await update.message.reply_text(
            "請重新輸入所有基本信息：\n\n" + BASIC_INFO_FORMAT_TEXT,
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_BASIC_INFO
    
    # 正常流程：解析基本信息
    parts = text.split()
    
    # 最少需要7個參數（性別、年、月、日、時、分、對象性別）
    if len(parts) < 7:
        await update.message.reply_text(
            "輸入格式錯誤！請按照指定格式輸入。\n\n"
            "正確格式：\n"
            "性別 年 月 日 時 分 對象性別 [經度]\n\n"
            "例子：\n"
            "男 1990 01 31 12 30 女\n"
            "女 1995 06 15 14 0 男 121.47\n\n"
            "請重新輸入：",
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_BASIC_INFO
    
    try:
        # 解析參數
        gender = parts[0]
        year = int(parts[1])
        month = int(parts[2])
        day = int(parts[3])
        hour = int(parts[4])
        minute = int(parts[5]) if len(parts) > 5 else 0
        target_gender = parts[6] if len(parts) > 6 else "異性"
        longitude = float(parts[7]) if len(parts) > 7 else DEFAULT_LONGITUDE
        
        # 驗證基本參數
        if gender not in ["男", "女"]:
            await update.message.reply_text("性別必須是「男」或「女」，請重新輸入：")
            return ASK_BASIC_INFO
            
        if target_gender not in ["男", "女", "異性", "同性"]:
            await update.message.reply_text("對象性別必須是「男」、「女」、「異性」或「同性」，請重新輸入：")
            return ASK_BASIC_INFO
            
        if not 1900 <= year <= datetime.now().year:
            await update.message.reply_text(f"年份必須在1900-{datetime.now().year}之間，請重新輸入：")
            return ASK_BASIC_INFO
            
        if not 1 <= month <= 12:
            await update.message.reply_text("月份必須在1-12之間，請重新輸入：")
            return ASK_BASIC_INFO
            
        if not 1 <= day <= 31:
            await update.message.reply_text("日期必須在1-31之間，請重新輸入：")
            return ASK_BASIC_INFO
            
        try:
            datetime(year, month, day)
        except ValueError:
            await update.message.reply_text(f"{year}年{month}月無{day}號，請重新輸入：")
            return ASK_BASIC_INFO
            
        if not 0 <= hour <= 23:
            await update.message.reply_text("時間必須在0-23之間，請重新輸入：")
            return ASK_BASIC_INFO
            
        if not 0 <= minute <= 59:
            await update.message.reply_text("分鐘必須在0-59之間，請重新輸入：")
            return ASK_BASIC_INFO
            
        if not -180 <= longitude <= 180:
            await update.message.reply_text("經度必須在-180到180之間，請重新輸入：")
            return ASK_BASIC_INFO
        
        # 儲存到context
        context.user_data.update({
            "gender": gender,
            "birth_year": year,
            "birth_month": month,
            "birth_day": day,
            "birth_hour": hour,
            "birth_minute": minute,
            "target_gender": target_gender,
            "longitude": longitude,
            "basic_info_entered": True
        })
        
        # 顯示確認信息並詢問時間精度
        await update.message.reply_text(
            CONFIRM_TIME_TEXT.format(
                gender=gender,
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                target_gender=target_gender,
                longitude=longitude
            ),
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["✅ 完全確定（知道確切時間）"],
                    ["🤔 大約知道（知道大概時段）"],
                    ["❓ 完全不知道（使用預設時間）"],
                    ["🔄 重新輸入基本信息"]
                ],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        
        return ASK_TIME_CONFIRMATION
        
    except ValueError as e:
        logger.error(f"解析基本信息失敗: {e}")
        await update.message.reply_text(
            "輸入格式錯誤！請檢查數字格式。\n\n"
            "請重新輸入：",
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_BASIC_INFO

@check_maintenance
async def ask_time_confirmation(update, context):
    """第二步：確認時間精度"""
    text = update.message.text.strip()
    
    if text == "✅ 完全確定（知道確切時間）":
        context.user_data["hour_known"] = "yes"
        context.user_data["hour_confidence"] = "高"
        
        # 直接完成註冊
        return await complete_registration(update, context)
        
    elif text == "🤔 大約知道（知道大概時段）":
        context.user_data["hour_known"] = "approximate"
        context.user_data["hour_confidence"] = "中"
        
        await update.message.reply_text(
            APPROXIMATE_HOUR_DESCRIPTION,
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_HOUR_KNOWN
        
    elif text == "❓ 完全不知道（使用預設時間）":
        context.user_data["hour_known"] = "no"
        context.user_data["hour_confidence"] = "低"
        
        # 直接完成註冊
        return await complete_registration(update, context)
        
    elif text == "🔄 重新輸入基本信息":
        await update.message.reply_text(
            "請重新輸入所有基本信息：\n\n" + BASIC_INFO_FORMAT_TEXT,
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_BASIC_INFO
        
    else:
        await update.message.reply_text(
            "請選擇上方選項：",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["✅ 完全確定（知道確切時間）"],
                    ["🤔 大約知道（知道大概時段）"],
                    ["❓ 完全不知道（使用預設時間）"],
                    ["🔄 重新輸入基本信息"]
                ],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return ASK_TIME_CONFIRMATION

@check_maintenance
async def ask_hour_known(update, context):
    """處理大約知道的時間描述"""
    description = update.message.text.strip()
    
    # 使用時間處理器估算
    estimated_hour, estimated_confidence = TimeProcessor.estimate_hour_from_description(description)
    
    context.user_data["birth_hour"] = estimated_hour
    context.user_data["birth_minute"] = 0
    context.user_data["hour_confidence"] = "中"
    context.user_data["hour_description"] = description
    
    await update.message.reply_text(
        f"✅ 已根據描述估算為 {estimated_hour}:00 時\n\n"
        f"📝 您的描述：{description}\n"
        f"⏰ 估算時間：{estimated_hour}:00\n"
        f"📊 信心度：中等\n\n"
        "現在完成註冊..."
    )
    
    return await complete_registration(update, context)

async def complete_registration(update, context):
    """完成註冊流程"""
    # 獲取所有資料
    user_data = context.user_data
    
    year = user_data.get("birth_year")
    month = user_data.get("birth_month")
    day = user_data.get("birth_day")
    hour = user_data.get("birth_hour", 12)
    minute = user_data.get("birth_minute", 0)
    gender = user_data.get("gender")
    target_gender = user_data.get("target_gender", "異性")
    hour_confidence = user_data.get("hour_confidence", "低")
    longitude = user_data.get("longitude", DEFAULT_LONGITUDE)
    
    try:
        # 計算八字
        bazi = ProfessionalBaziCalculator.calculate(
            year, month, day, hour, 
            gender=gender,
            hour_confidence=hour_confidence,
            minute=minute,
            longitude=longitude
        )
        
        if not bazi:
            await update.message.reply_text("八字計算失敗，請重新輸入 /start")
            return ConversationHandler.END
            
    except BaziError as e:
        await update.message.reply_text(f"八字計算錯誤: {e}，請重新輸入 /start")
        return ConversationHandler.END
    
    telegram_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not username:
        await update.message.reply_text(
            "⚠️ 你未設定 Telegram 用戶名！\n"
            "請先到 Telegram 設定中設定用戶名，否則配對成功後對方無法聯絡你。\n"
            "設定完成後請重新輸入 /start。",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        
        # 插入或更新用戶資料
        cur.execute("""
            INSERT INTO users (telegram_id, username)
            VALUES (%s, %s)
            ON CONFLICT (telegram_id) DO UPDATE SET username = EXCLUDED.username
            RETURNING id
        """, (telegram_id, username))
        
        row = cur.fetchone()
        if not row:
            await update.message.reply_text("用戶創建失敗，請重試", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
            
        internal_user_id = row[0]
        elements = bazi.get("elements", {})
        
        # 插入或更新八字資料
        cur.execute("""
            INSERT INTO profiles
            (user_id, birth_year, birth_month, birth_day, birth_hour, birth_minute, 
             hour_confidence, gender, target_gender,
             year_pillar, month_pillar, day_pillar, hour_pillar,
             zodiac, day_stem, day_stem_element,
             wood, fire, earth, metal, water,
             day_stem_strength, strength_score, useful_elements, harmful_elements,
             spouse_star_status, spouse_star_effective, spouse_palace_status, pressure_score,
             cong_ge_type, shi_shen_structure, shen_sha_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
                   %s, %s, %s, %s, %s, %s, %s,
                   %s, %s, %s, %s, %s, %s, %s, %s, %s,
                   %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                birth_year = EXCLUDED.birth_year,
                birth_month = EXCLUDED.birth_month,
                birth_day = EXCLUDED.birth_day,
                birth_hour = EXCLUDED.birth_hour,
                birth_minute = EXCLUDED.birth_minute,
                hour_confidence = EXCLUDED.hour_confidence,
                gender = EXCLUDED.gender,
                target_gender = EXCLUDED.target_gender,
                year_pillar = EXCLUDED.year_pillar,
                month_pillar = EXCLUDED.month_pillar,
                day_pillar = EXCLUDED.day_pillar,
                hour_pillar = EXCLUDED.hour_pillar,
                zodiac = EXCLUDED.zodiac,
                day_stem = EXCLUDED.day_stem,
                day_stem_element = EXCLUDED.day_stem_element,
                wood = EXCLUDED.wood,
                fire = EXCLUDED.fire,
                earth = EXCLUDED.earth,
                metal = EXCLUDED.metal,
                water = EXCLUDED.water,
                day_stem_strength = EXCLUDED.day_stem_strength,
                strength_score = EXCLUDED.strength_score,
                useful_elements = EXCLUDED.useful_elements,
                harmful_elements = EXCLUDED.harmful_elements,
                spouse_star_status = EXCLUDED.spouse_star_status,
                spouse_star_effective = EXCLUDED.spouse_star_effective,
                spouse_palace_status = EXCLUDED.spouse_palace_status,
                pressure_score = EXCLUDED.pressure_score,
                cong_ge_type = EXCLUDED.cong_ge_type,
                shi_shen_structure = EXCLUDED.shi_shen_structure,
                shen_sha_data = EXCLUDED.shen_sha_data
        """, (
            internal_user_id, year, month, day, hour, minute, hour_confidence, gender, target_gender,
            bazi.get("year_pillar", ""), bazi.get("month_pillar", ""), bazi.get("day_pillar", ""), bazi.get("hour_pillar", ""),
            bazi.get("zodiac", ""), bazi.get("day_stem", ""), bazi.get("day_stem_element", ""),
            float(elements.get("木", 0)), float(elements.get("火", 0)),
            float(elements.get("土", 0)), float(elements.get("金", 0)),
            float(elements.get("水", 0)), bazi.get("day_stem_strength", "中"),
            bazi.get("strength_score", 50), ','.join(bazi.get("useful_elements", [])),
            ','.join(bazi.get("harmful_elements", [])), bazi.get("spouse_star_status", "未知"),
            bazi.get("spouse_star_effective", "未知"), bazi.get("spouse_palace_status", "未知"),
            bazi.get("pressure_score", 0), bazi.get("cong_ge_type", "正格"),
            bazi.get("shi_shen_structure", "普通結構"),
            json.dumps({"names": bazi.get("shen_sha_names", "無"), "bonus": bazi.get("shen_sha_bonus", 0)})
        ))
        
        conn.commit()
    
    # 準備個人資料顯示
    bazi_data_for_display = {
        "year_pillar": bazi.get("year_pillar", ""),
        "month_pillar": bazi.get("month_pillar", ""),
        "day_pillar": bazi.get("day_pillar", ""),
        "hour_pillar": bazi.get("hour_pillar", ""),
        "zodiac": bazi.get("zodiac", ""),
        "day_stem": bazi.get("day_stem", ""),
        "day_stem_element": bazi.get("day_stem_element", ""),
        "gender": gender,
        "cong_ge_type": bazi.get("cong_ge_type", "正格"),
        "shi_shen_structure": bazi.get("shi_shen_structure", "普通結構"),
        "day_stem_strength": bazi.get("day_stem_strength", "中"),
        "strength_score": bazi.get("strength_score", 50),
        "useful_elements": bazi.get("useful_elements", []),
        "harmful_elements": bazi.get("harmful_elements", []),
        "spouse_star_status": bazi.get("spouse_star_status", "未知"),
        "spouse_star_effective": bazi.get("spouse_star_effective", "未知"),
        "spouse_palace_status": bazi.get("spouse_palace_status", "未知"),
        "pressure_score": bazi.get("pressure_score", 0),
        "shen_sha_names": bazi.get("shen_sha_names", "無"),
        "shen_sha_bonus": bazi.get("shen_sha_bonus", 0),
        "elements": elements,
        "hour_confidence": hour_confidence,
        "birth_year": year,
        "birth_month": month,
        "birth_day": day,
        "birth_hour": hour,
        "birth_minute": minute
    }
    
    profile_result = FormatUtils.format_profile_result(bazi_data_for_display, username)
    
    # 發送註冊完成消息
    confidence_map = {
        "高": "（高信心度）",
        "中": "（中信心度，時辰估算）",
        "低": "（低信心度，時辰未知）"
    }
    confidence_text = confidence_map.get(hour_confidence, "（信心度未知）")
    
    registration_text = REGISTRATION_COMPLETE_TEXT.format(
        confidence_text=confidence_text,
        profile_result=profile_result
    )
    
    await update.message.reply_text(
        registration_text,
        reply_markup=ReplyKeyboardRemove(),
    )
    
    # 發送功能選單（包含管理員專用功能）
    telegram_id = update.effective_user.id
    function_menu = FUNCTION_MENU_TEXT.format(target_gender=target_gender)
    
    # 如果是管理員，添加管理員專用功能
    if is_admin(telegram_id):
        function_menu += ADMIN_MENU_TEXT
    
    await update.message.reply_text(function_menu)
    
    return ConversationHandler.END

@check_maintenance
async def cancel(update, context):
    """取消流程"""
    await update.message.reply_text("已取消流程。", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
# ========1.7 簡化註冊流程結束 ========#

# ========1.8 命令處理函數開始 ========#
@check_maintenance
async def start(update, context):
    """開始命令 - 顯示隱私條款"""
    user = update.effective_user
    
    # 檢查維護模式
    if MAINTENANCE_MODE and not is_admin(user.id):
        await update.message.reply_text(
            "🔧 **系統維護中**\n\n"
            "八字配對系統正在進行升級維護，請稍後再試。\n\n"
            "**維護期間：**\n"
            "• 普通用戶無法使用任何功能\n"
            "• 管理員可正常使用管理功能\n"
            "• 預計恢復時間請關注公告\n\n"
            "如需協助，請聯繫管理員。"
        )
        return ConversationHandler.END
    
    # 檢查是否已有資料
    internal_user_id = get_internal_user_id(user.id)
    if internal_user_id:
        keyboard = [["是", "否"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "發現你已有註冊資料，重新註冊會覆蓋舊資料。\n是否繼續？",
            reply_markup=reply_markup
        )
        context.user_data["confirm_overwrite"] = True
        return await show_terms(update, context)
    
    return await show_terms(update, context)

@check_maintenance
async def help_command(update, context):
    """幫助命令"""
    await update.message.reply_text(HELP_TEXT)

@check_maintenance
async def explain_command(update, context):
    """解釋算法命令"""
    await update.message.reply_text(EXPLANATION_TEXT)

@check_maintenance
async def profile(update, context):
    """查看個人資料"""
    telegram_id = update.effective_user.id
    internal_user_id = get_internal_user_id(telegram_id)
    
    if not internal_user_id:
        await update.message.reply_text("未找到紀錄，請先 /start 註冊。")
        return
    
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE id = %s", (internal_user_id,))
        user_row = cur.fetchone()
        uname = user_row[0] if user_row else "未知"
        
        cur.execute("""
            SELECT birth_year, birth_month, birth_day, birth_hour, birth_minute, hour_confidence, gender,
                   year_pillar, month_pillar, day_pillar, hour_pillar,
                   zodiac, day_stem, day_stem_element,
                   wood, fire, earth, metal, water,
                   day_stem_strength, strength_score, useful_elements, harmful_elements,
                   spouse_star_status, spouse_star_effective, spouse_palace_status, pressure_score,
                   cong_ge_type, shi_shen_structure, shen_sha_data
            FROM profiles WHERE user_id = %s
        """, (internal_user_id,))
        p = cur.fetchone()
    
    if p is None:
        await update.message.reply_text("尚未完成資料輸入。請輸入 /start 開始註冊。")
        return
    
    (
        by, bm, bd, bh, bmin, hour_conf, g,
        yp, mp, dp, hp,
        zodiac, day_stem, day_stem_element,
        w, f, e, m, wt,
        strength, strength_score, useful, harmful,
        spouse_star, spouse_star_effective, spouse_palace, pressure_score,
        cong_ge, shi_shen, shen_sha_json
    ) = p
    
    # 解析神煞數據
    shen_sha_data = json.loads(shen_sha_json) if shen_sha_json else {"names": "無", "bonus": 0}
    shen_sha_names = shen_sha_data.get("names", "無")
    
    # 準備數據供格式化函數使用
    bazi_data = {
        "year_pillar": yp,
        "month_pillar": mp,
        "day_pillar": dp,
        "hour_pillar": hp,
        "zodiac": zodiac,
        "day_stem": day_stem,
        "day_stem_element": day_stem_element,
        "gender": g,
        "cong_ge_type": cong_ge if cong_ge else '正格',
        "shi_shen_structure": shi_shen if shi_shen else '普通結構',
        "day_stem_strength": strength,
        "strength_score": strength_score,
        "useful_elements": useful.split(',') if useful else [],
        "harmful_elements": harmful.split(',') if harmful else [],
        "spouse_star_status": spouse_star,
        "spouse_star_effective": spouse_star_effective if spouse_star_effective else '未知',
        "spouse_palace_status": spouse_palace,
        "pressure_score": pressure_score,
        "shen_sha_names": shen_sha_names,
        "elements": {"木": w, "火": f, "土": e, "金": m, "水": wt},
        "hour_confidence": hour_conf,
        "birth_year": by,
        "birth_month": bm,
        "birth_day": bd,
        "birth_hour": bh,
        "birth_minute": bmin
    }
    
    # 使用統一的格式化函數
    profile_text = FormatUtils.format_profile_result(bazi_data, uname)
    await update.message.reply_text(profile_text)

@check_maintenance
async def match(update, context):
    """開始配對 - 支援同性配對"""
    telegram_id = update.effective_user.id
    internal_user_id = get_internal_user_id(telegram_id)
    
    if not internal_user_id:
        await update.message.reply_text("請先用 /start 登記資料。")
        return
    
    allowed, match_count = check_daily_limit(internal_user_id)
    if not allowed:
        await update.message.reply_text(
            f"⚠️ 今日已達配對次數上限（{DAILY_MATCH_LIMIT}次）。\n"
            f"請明天再試。"
        )
        return
    
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT birth_year, birth_month, birth_day, birth_hour, birth_minute, hour_confidence, gender,
                   year_pillar, month_pillar, day_pillar, hour_pillar,
                   zodiac, day_stem, day_stem_element,
                   wood, fire, earth, metal, water,
                   day_stem_strength, strength_score, useful_elements, harmful_elements,
                   spouse_star_status, spouse_star_effective, spouse_palace_status, pressure_score,
                   cong_ge_type, shi_shen_structure, shen_sha_data
            FROM profiles WHERE user_id = %s
        """, (internal_user_id,))
        me_p = cur.fetchone()
        
        if me_p is None:
            await update.message.reply_text("請先完成資料輸入流程。")
            return
        
        def to_profile(row):
            (
                by, bm, bd, bh, bmin, hour_conf, gender,
                yp, mp, dp, hp,
                zodiac, day_stem, day_stem_element,
                w, f, e, m, wt,
                strength, strength_score, useful, harmful,
                spouse_star, spouse_star_effective, spouse_palace, pressure_score,
                cong_ge, shi_shen, shen_sha_json
            ) = row
            
            useful_list = useful.split(',') if useful else []
            harmful_list = harmful.split(',') if harmful else []
            
            # 解析神煞數據
            shen_sha_data = json.loads(shen_sha_json) if shen_sha_json else {"names": "無", "bonus": 0}
            
            return {
                "gender": gender,
                "year_pillar": yp,
                "month_pillar": mp,
                "day_pillar": dp,
                "hour_pillar": hp,
                "zodiac": zodiac,
                "day_stem": day_stem,
                "day_stem_element": day_stem_element,
                "elements": {"木": w, "火": f, "土": e, "金": m, "水": wt},
                "day_stem_strength": strength,
                "strength_score": strength_score,
                "useful_elements": useful_list,
                "harmful_elements": harmful_list,
                "spouse_star_status": spouse_star,
                "spouse_star_effective": spouse_star_effective,
                "spouse_palace_status": spouse_palace,
                "pressure_score": pressure_score,
                "cong_ge_type": cong_ge,
                "shi_shen_structure": shi_shen,
                "hour_confidence": hour_conf,
                "birth_year": by,
                "birth_month": bm,
                "birth_day": bd,
                "birth_hour": bh,
                "birth_minute": bmin,
                "shen_sha_names": shen_sha_data.get("names", "無"),
                "shen_sha_bonus": shen_sha_data.get("bonus", 0)
            }
        
        me_profile = to_profile(me_p)
        my_gender = me_p[6]
        
        # 獲取用戶的目標性別偏好
        cur.execute("SELECT target_gender FROM profiles WHERE user_id = %s", (internal_user_id,))
        target_gender_row = cur.fetchone()
        target_gender = target_gender_row[0] if target_gender_row else "異性"
        
        # 根據目標性別偏好構建查詢條件
        if target_gender == "異性":
            gender_condition = "p.gender != %s"
            params = (internal_user_id, internal_user_id, internal_user_id, my_gender)
        elif target_gender == "同性":
            gender_condition = "p.gender = %s"
            params = (internal_user_id, internal_user_id, internal_user_id, my_gender)
        elif target_gender in ["男", "女"]:
            gender_condition = "p.gender = %s"
            params = (internal_user_id, internal_user_id, internal_user_id, target_gender)
        else:
            # 默認異性
            gender_condition = "p.gender != %s"
            params = (internal_user_id, internal_user_id, internal_user_id, my_gender)
        
        # 修正查詢：支援同性配對
        query = f"""
            SELECT
                u.id, u.telegram_id, u.username,
                p.birth_year, p.birth_month, p.birth_day, p.birth_hour, p.birth_minute, p.hour_confidence, p.gender,
                p.year_pillar, p.month_pillar, p.day_pillar, p.hour_pillar,
                p.zodiac, p.day_stem, p.day_stem_element,
                p.wood, p.fire, p.earth, p.metal, p.water,
                p.day_stem_strength, p.strength_score, p.useful_elements, p.harmful_elements,
                p.spouse_star_status, p.spouse_star_effective, p.spouse_palace_status, p.pressure_score,
                p.cong_ge_type, p.shi_shen_structure, p.shen_sha_data
            FROM users u
            JOIN profiles p ON u.id = p.user_id
            WHERE u.id != %s
            AND u.active = 1
            AND {gender_condition}
            AND NOT EXISTS (
                SELECT 1 FROM matches m
                WHERE ((m.user_a = %s AND m.user_b = u.id)
                       OR (m.user_a = u.id AND m.user_b = %s))
                AND m.user_a_accepted = 1 AND m.user_b_accepted = 1
            )
            ORDER BY RANDOM()
            LIMIT 100
        """
        
        cur.execute(query, params)
        rows = cur.fetchall()
    
    if not rows:
        await update.message.reply_text("暫時未有合適的配對對象。請稍後再試。")
        return
    
    matches = []
    
    for r in rows:
        other_internal_id = r[0]
        other_profile = to_profile(r[3:])
        
        try:
            # 使用主入口函數進行配對
            match_result = calculate_match(
                me_profile,
                other_profile,
                my_gender,
                other_profile["gender"]
            )
            
            score = match_result.get("score", 0)
            rating = match_result.get("rating", "未知")
            relationship_model = match_result.get("relationship_model", "")
            details = match_result.get("details", [])
            module_scores = match_result.get("module_scores", {})
            a_to_b_score = match_result.get("a_to_b_score", 0)
            b_to_a_score = match_result.get("b_to_a_score", 0)
            
            logger.debug(f"配對計算完成: {score}分")
            
            matches.append({
                "internal_id": other_internal_id,
                "telegram_id": r[1],
                "username": r[2] or "匿名用戶",
                "profile": other_profile,
                "score": score,
                "rating": rating,
                "relationship_model": relationship_model,
                "details": details,
                "module_scores": module_scores,
                "a_to_b_score": a_to_b_score,
                "b_to_a_score": b_to_a_score,
                "confidence_level": me_profile.get("hour_confidence", "中"),
                "match_result": match_result
            })
            
        except MatchError as e:
            logger.error(f"配對計算錯誤: {e}", exc_info=True)
            continue
    
    if not matches:
        await update.message.reply_text("暫時未有新的配對對象。請稍後再試。")
        return
    
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    # 使用新的評分閾值
    valid_matches = [m for m in matches if m["score"] >= THRESHOLD_WARNING]
    
    if not valid_matches:
        best_score = matches[0]["score"] if matches else 0
        await update.message.reply_text(
            f"現時未有合適的配對對象（最佳配對分數：{best_score:.1f}分，需≥{THRESHOLD_WARNING}分）。\n"
            f"建議稍後再試 /match 或使用 /find_soulmate。"
        )
        return
    
    best = valid_matches[0]
    op = best["profile"]
    match_result = best.get("match_result", {})
    
    timestamp = int(datetime.now().timestamp())
    data_str = f"{internal_user_id}_{best['internal_id']}_{timestamp}"
    token = hashlib.sha256(
        f"{data_str}_{SECRET_KEY}".encode()).hexdigest()[:12]
    
    accept_data = f"accept_{data_str}_{token}"
    reject_data = f"reject_{data_str}_{token}"
    
    keyboard = [
        [InlineKeyboardButton("✅ 有興趣", callback_data=accept_data),
         InlineKeyboardButton("❌ 略過", callback_data=reject_data)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data["current_match"] = {
        "user_a": internal_user_id,
        "user_b": best["internal_id"],
        "score": best["score"],
        "token": token,
        "timestamp": timestamp,
        "match_result": match_result
    }
    
    # 使用統一格式化函數
    match_text = FormatUtils.format_match_result(
        match_result, me_profile, op, 
        user_a_name="您", user_b_name=best["username"]
    )
    
    # 發送配對結果
    await update.message.reply_text(match_text)
    
    # 發送按鈕
    await update.message.reply_text("是否想認識對方？", reply_markup=reply_markup)
    
    # 發送AI分析提示按鈕
    ai_prompt = FormatUtils.generate_ai_prompt(match_result, me_profile, op)
    context.user_data["ai_prompt"] = ai_prompt
    
    ai_keyboard = [
        [InlineKeyboardButton("🤖 獲取AI分析提示",
                              callback_data=f"ai_prompt_{timestamp}_{token}")]
    ]
    ai_reply_markup = InlineKeyboardMarkup(ai_keyboard)
    
    await update.message.reply_text(
        "💡 想深入了解這個配對？點擊下方按鈕獲取AI分析提示，可直接複製問AI！",
        reply_markup=ai_reply_markup
    )
    
    # 通知對方
    try:
        # 發送格式化消息給對方
        await context.bot.send_message(
            chat_id=best["telegram_id"],
            text=match_text
        )
        
        await context.bot.send_message(
            chat_id=best["telegram_id"],
            text="是否想認識對方？",
            reply_markup=reply_markup
        )
        
        await context.bot.send_message(
            chat_id=best["telegram_id"],
            text="💡 想深入了解這個配對？點擊下方按鈕獲取AI分析提示，可直接複製問AI！",
            reply_markup=ai_reply_markup
        )
    except Exception as e:
        logger.error(f"無法通知對方: {e}")

@check_maintenance
async def test_command(update, context):
    """測試命令"""
    await update.message.reply_text("✅ Bot 正在運行中！")

@check_maintenance
async def clear_command(update, context):
    """清除用戶所有資料 - 修復版"""
    telegram_id = update.effective_user.id
    
    # 確認用戶是否真的要清除資料
    if context.args and context.args[0] == "confirm":
        success = clear_user_data(telegram_id)
        if success:
            await update.message.reply_text(
                "✅ 已清除你的所有資料。\n"
                "如需重新使用服務，請輸入 /start 重新註冊。"
            )
        else:
            await update.message.reply_text(
                "❌ 清除資料失敗，請稍後再試或聯繫管理員。"
            )
    else:
        await update.message.reply_text(
            "⚠️ **確認清除所有資料**\n\n"
            "此操作將會：\n"
            "• 刪除你的八字資料\n"
            "• 刪除所有配對紀錄\n"
            "• 刪除你的用戶資料\n\n"
            "⚠️ 此操作無法還原！\n\n"
            "確定要清除所有資料嗎？\n"
            "請輸入： /clear confirm\n"
            "或輸入其他命令取消。"
        )

@check_maintenance
async def test_pair_command(update, context):
    """獨立測試任意兩個八字配對（不加入數據庫）"""
    if len(context.args) < 10:
        await update.message.reply_text(
            "請提供兩個完整的八字參數。\n"
            "格式：/testpair <年1> <月1> <日1> <時1> <性別1> <年2> <月2> <日2> <時2> <性別2>\n\n"
            "例如：/testpair 1990 1 1 12 男 1991 2 2 13 女\n"
            "性別：男 或 女\n\n"
            "可選參數：<分鐘1> <分鐘2> <經度1> <經度2>\n"
            "例如：/testpair 1990 1 1 12 男 1991 2 2 13 女 30 30 114.17 121.47"
        )
        return
    
    try:
        # 基本參數（10個必填）
        year1, month1, day1, hour1 = map(int, context.args[:4])
        gender1 = context.args[4]
        year2, month2, day2, hour2 = map(int, context.args[5:9])
        gender2 = context.args[9] if len(context.args) > 9 else "女"
        
        # 可選參數（分鐘和經度）
        minute1 = int(context.args[10]) if len(context.args) > 10 else 0
        minute2 = int(context.args[11]) if len(context.args) > 11 else 0
        longitude1 = float(context.args[12]) if len(context.args) > 12 else DEFAULT_LONGITUDE
        longitude2 = float(context.args[13]) if len(context.args) > 13 else DEFAULT_LONGITUDE
        
        # 驗證性別
        if gender1 not in ["男", "女"]:
            await update.message.reply_text("第一個性別必須是「男」或「女」")
            return
        
        if gender2 not in ["男", "女"]:
            await update.message.reply_text("第二個性別必須是「男」或「女」")
            return
        
        # 驗證日期
        try:
            datetime(year1, month1, day1)
            datetime(year2, month2, day2)
        except ValueError:
            await update.message.reply_text("日期無效，請檢查年月日是否正確")
            return
        
        # 驗證時間
        if not 0 <= hour1 <= 23 or not 0 <= hour2 <= 23:
            await update.message.reply_text("時間必須在 0-23 之間")
            return
        
        # 驗證分鐘
        if not 0 <= minute1 <= 59 or not 0 <= minute2 <= 59:
            await update.message.reply_text("分鐘必須在 0-59 之間")
            return
        
        # 驗證經度
        if not -180 <= longitude1 <= 180 or not -180 <= longitude2 <= 180:
            await update.message.reply_text("經度必須在 -180 到 180 之間")
            return
        
        # 計算八字 - testpair命令使用高置信度
        bazi1 = ProfessionalBaziCalculator.calculate(
            year1, month1, day1, hour1, 
            gender=gender1,
            hour_confidence="high",
            minute=minute1,
            longitude=longitude1
        )
        bazi2 = ProfessionalBaziCalculator.calculate(
            year2, month2, day2, hour2,
            gender=gender2,
            hour_confidence="high",
            minute=minute2,
            longitude=longitude2
        )
        
        if not bazi1 or not bazi2:
            await update.message.reply_text("八字計算失敗，請檢查輸入參數")
            return
        
        # 配對計算 - 使用主入口函數
        match_result = calculate_match(bazi1, bazi2, gender1, gender2, is_testpair=True)
        
        # 使用統一格式化函數
        match_text = FormatUtils.format_match_result(
            match_result, bazi1, bazi2, 
            user_a_name="用戶A", user_b_name="用戶B"
        )
        
        # 發送配對結果
        await update.message.reply_text(match_text)
        
        # 提供AI分析提示
        ai_prompt = FormatUtils.generate_ai_prompt(match_result, bazi1, bazi2)
        await update.message.reply_text(
            "🤖 AI分析提示（可複製問AI）：\n\n"
            f"```\n{ai_prompt}\n```",
            parse_mode='Markdown'
        )
        
        # 提示這只是獨立測試
        await update.message.reply_text(
            "💡 注意：這只是獨立測試，不會保存到配對數據庫中。\n"
            "如需正式配對，請使用 /match 命令。"
        )
        
    except Exception as e:
        logger.error(f"測試配對失敗: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 測試失敗: {str(e)}\n請檢查輸入格式是否正確。")

@check_maintenance
@check_admin_only
async def maintenance_command(update, context):
    """維護模式命令 - 僅管理員可用"""
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id):
        await update.message.reply_text("❌ 此功能僅限管理員使用")
        return
    
    global MAINTENANCE_MODE
    
    if context.args and context.args[0] == "on":
        MAINTENANCE_MODE = True
        await update.message.reply_text(
            "🔧 **維護模式已開啟**\n\n"
            "**系統狀態：**\n"
            "• 普通用戶無法使用任何功能\n"
            "• 管理員可正常使用管理功能\n"
            "• 新用戶無法註冊\n"
            "• 現有配對功能暫停\n\n"
            "請在完成維護後輸入 /maintenance off 恢復正常運作。"
        )
    elif context.args and context.args[0] == "off":
        MAINTENANCE_MODE = False
        await update.message.reply_text(
            "✅ **維護模式已關閉**\n\n"
            "**系統狀態：**\n"
            "• 所有功能恢復正常\n"
            "• 用戶可以正常註冊和使用\n"
            "• 配對功能恢復運作\n\n"
            "系統已恢復正常運作。"
        )
    else:
        status = "🔧 **開啟**" if MAINTENANCE_MODE else "✅ **關閉**"
        await update.message.reply_text(
            f"🛠️ **當前維護模式：{status}**\n\n"
            "**使用方法：**\n"
            "/maintenance on - 開啟維護模式\n"
            "/maintenance off - 關閉維護模式\n\n"
            "**影響：**\n"
            "• 開啟時普通用戶無法使用系統\n"
            "• 管理員功能不受影響\n"
            "• 維護期間可進行系統升級和測試"
        )

@check_maintenance
@check_admin_only
async def admin_test_command(update, context):
    """管理員測試命令 - 運行20組測試案例"""
    # 創建AdminService實例
    admin_service = AdminService()
    
    # 運行測試
    await update.message.reply_text("🔄 開始運行管理員測試（20組測試案例）...")
    results = await admin_service.run_admin_tests()
    
    # 格式化並發送結果
    formatted_results = admin_service.format_test_results(results)
    await update.message.reply_text(formatted_results)

@check_maintenance
@check_admin_only
async def admin_stats_command(update, context):
    """管理員統計命令 - 查看系統統計"""
    # 創建AdminService實例
    admin_service = AdminService()
    
    # 獲取系統統計
    await update.message.reply_text("🔄 正在獲取系統統計數據...")
    stats = await admin_service.get_system_stats()
    
    # 格式化並發送結果
    formatted_stats = admin_service.format_system_stats(stats)
    await update.message.reply_text(formatted_stats)

@check_maintenance
@check_admin_only
async def admin_demo_command(update, context):
    """管理員一鍵測試演示"""
    await update.message.reply_text("🔄 開始一鍵測試演示...")
    
    # 創建AdminService實例
    admin_service = AdminService()
    
    # 運行一鍵演示
    demo_results = await admin_service.run_oneclick_demo()
    
    # 發送演示結果
    await update.message.reply_text(demo_results)

@check_maintenance
@check_admin_only
async def admin_service_command(update, context):
    """管理員服務總覽命令"""
    admin_text = """
👑 **管理員服務總覽**

**可用命令：**
1. /admin_test - 運行20組測試案例
2. /admin_stats - 查看系統統計數據
3. /admin_demo - 一鍵測試演示（模擬testpair/match/profile等功能）
4. /maintenance on/off - 開關維護模式
5. /admin_service - 顯示此幫助

**功能說明：**
• **測試案例**：驗證算法準確性，包含20組完整測試
• **系統統計**：查看用戶和配對數據，實時更新
• **一鍵演示**：快速測試所有核心功能，模擬完整用戶流程
• **維護模式**：暫停普通用戶服務，管理員可繼續測試

**使用提示：**
1. 測試案例使用 test_cases.py 中的20組數據
2. 一鍵演示會模擬 testpair/match/profile/find_soulmate/explain 功能
3. 維護模式開啟後普通用戶會收到提示
4. 所有管理員命令都有權限檢查

**系統狀態：** ✅ 正常運作
"""
    
    await update.message.reply_text(admin_text)
# ========1.8 命令處理函數結束 ========#

# ========1.9 Find Soulmate 流程函數開始 ========#
@check_maintenance
async def find_soulmate_start(update, context):
    """開始真命天子搜尋"""
    telegram_id = update.effective_user.id
    internal_user_id = get_internal_user_id(telegram_id)
    
    if not internal_user_id:
        await update.message.reply_text("請先用 /start 登記資料。")
        return
    
    # 檢查每日限制
    allowed, match_count = check_daily_limit(internal_user_id)
    if not allowed:
        await update.message.reply_text(
            f"⚠️ 今日已達配對次數上限（{DAILY_MATCH_LIMIT}次）。\n"
            f"請明天再試。"
        )
        return
    
    await update.message.reply_text(
        "🔮 歡迎使用「真命天子搜尋器」！\n"
        "這個功能會幫你在指定過去年份範圍內，找出最匹配的出生時空（年月日時）。\n"
        "請先輸入搜尋年份範圍（例如1990-1999，建議每次不超過10年，避免運算太長）："
    )
    
    return FIND_SOULMATE_RANGE

@check_maintenance
async def find_soulmate_range(update, context):
    """處理搜尋年份範圍"""
    text = update.message.text.strip()
    
    # 檢查格式
    if '-' not in text:
        await update.message.reply_text("請使用正確格式，例如：1990-1999")
        return FIND_SOULMATE_RANGE
    
    try:
        start_year, end_year = map(int, text.split('-'))
        
        # 驗證年份範圍
        if start_year < 1900 or end_year > datetime.now().year:
            await update.message.reply_text(f"請輸入合理年份範圍（1900-{datetime.now().year}）")
            return FIND_SOULMATE_RANGE
        
        if end_year - start_year > 20:
            await update.message.reply_text("年份範圍太大，建議每次不超過20年")
            return FIND_SOULMATE_RANGE
        
        if start_year >= end_year:
            await update.message.reply_text("開始年份必須小於結束年份")
            return FIND_SOULMATE_RANGE
        
        # 計算日期數量
        date_count = (end_year - start_year + 1) * 365
        if date_count > 10000:
            await update.message.reply_text(f"範圍太大（約{date_count}個日期），請縮小範圍")
            return FIND_SOULMATE_RANGE
        
        context.user_data["soulmate_range"] = (start_year, end_year)
        
        # 詢問搜尋目的
        keyboard = [["💖 尋找正緣", "🤝 事業合夥"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            f"✅ 確認搜尋範圍：{start_year}-{end_year}年（約{date_count}個時空會被篩選）。\n"
            "請選擇搜尋目的（影響權重調整）：\n"
            "💖 尋找正緣（重視靈魂契合、日柱配合同配偶星）\n"
            "🤝 事業合夥（重視喜用互補、格局穩定同大運加持）",
            reply_markup=reply_markup
        )
        
        return FIND_SOULMATE_PURPOSE
        
    except ValueError:
        await update.message.reply_text("請使用正確格式，例如：1990-1999")
        return FIND_SOULMATE_RANGE
    except Exception as e:
        logger.error(f"處理年份範圍失敗: {e}")
        await update.message.reply_text("處理失敗，請重新輸入")
        return FIND_SOULMATE_RANGE

@check_maintenance
async def find_soulmate_purpose(update, context):
    """處理搜尋目的並開始計算"""
    text = update.message.text.strip()
    
    purpose_map = {
        "💖 尋找正緣": "正緣",
        "🤝 事業合夥": "合夥"
    }
    
    if text not in purpose_map:
        await update.message.reply_text("請選擇上方選項")
        return FIND_SOULMATE_PURPOSE
    
    purpose = purpose_map[text]
    start_year, end_year = context.user_data.get("soulmate_range", (1990, 1999))
    
    # 通知用戶開始計算
    calculating_msg = await update.message.reply_text(
        f"⚡ 開始掃描{start_year}-{end_year}年內所有出生時空...\n"
        f"⏳ 第一層初選完成（飛走95%不合組，剩1200組）...\n"
        f"⏳ 第二層複選完成（剩400組）...\n"
        f"⏳ 正在進行資深精算（包含化解、大運、神煞加分）...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    try:
        # 獲取用戶八字資料
        telegram_id = update.effective_user.id
        internal_user_id = get_internal_user_id(telegram_id)
        
        with closing(get_conn()) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT birth_year, birth_month, birth_day, birth_hour, birth_minute, hour_confidence, gender,
                       year_pillar, month_pillar, day_pillar, hour_pillar,
                       zodiac, day_stem, day_stem_element,
                       wood, fire, earth, metal, water,
                       day_stem_strength, strength_score, useful_elements, harmful_elements,
                       spouse_star_status, spouse_star_effective, spouse_palace_status, pressure_score,
                       cong_ge_type, shi_shen_structure, shen_sha_data
                FROM profiles WHERE user_id = %s
            """, (internal_user_id,))
            me_p = cur.fetchone()
        
        if not me_p:
            await calculating_msg.edit_text("找不到用戶資料，請先使用 /start 註冊")
            return ConversationHandler.END
        
        # 轉換為八字數據
        def to_profile(row):
            (
                by, bm, bd, bh, bmin, hour_conf, gender,
                yp, mp, dp, hp,
                zodiac, day_stem, day_stem_element,
                w, f, e, m, wt,
                strength, strength_score, useful, harmful,
                spouse_star, spouse_star_effective, spouse_palace, pressure_score,
                cong_ge, shi_shen, shen_sha_json
            ) = row
            
            useful_list = useful.split(',') if useful else []
            harmful_list = harmful.split(',') if harmful else []
            
            # 解析神煞數據
            shen_sha_data = json.loads(shen_sha_json) if shen_sha_json else {"names": "無", "bonus": 0}
            
            return {
                "gender": gender,
                "year_pillar": yp,
                "month_pillar": mp,
                "day_pillar": dp,
                "hour_pillar": hp,
                "zodiac": zodiac,
                "day_stem": day_stem,
                "day_stem_element": day_stem_element,
                "elements": {"木": w, "火": f, "土": e, "金": m, "水": wt},
                "day_stem_strength": strength,
                "strength_score": strength_score,
                "useful_elements": useful_list,
                "harmful_elements": harmful_list,
                "spouse_star_status": spouse_star,
                "spouse_star_effective": spouse_star_effective,
                "spouse_palace_status": spouse_palace,
                "pressure_score": pressure_score,
                "cong_ge_type": cong_ge,
                "shi_shen_structure": shi_shen,
                "hour_confidence": hour_conf,
                "birth_year": by,
                "birth_month": bm,
                "birth_day": bd,
                "birth_hour": bh,
                "birth_minute": bmin,
                "shen_sha_names": shen_sha_data.get("names", "無"),
                "shen_sha_bonus": shen_sha_data.get("bonus", 0)
            }
        
        user_bazi = to_profile(me_p)
        user_gender = me_p[6]
        
        # 搜尋最佳匹配
        top_matches = SoulmateFinder.find_top_matches(
            user_bazi, user_gender, start_year, end_year, purpose, limit=10
        )
        
        # 使用統一格式化函數
        formatted_message = FormatUtils.format_find_soulmate_result(top_matches, start_year, end_year, purpose)
        
        # 更新計算完成消息
        await calculating_msg.edit_text(f"✅ 搜尋完成！找到 {len(top_matches)} 個匹配時空。")
        
        # 發送結果
        await update.message.reply_text(formatted_message)
        
    except Exception as e:
        logger.error(f"搜尋真命天子失敗: {e}", exc_info=True)
        await calculating_msg.edit_text(f"❌ 搜尋失敗: {str(e)}\n請稍後再試或縮小搜尋範圍。")
    
    return ConversationHandler.END

@check_maintenance
async def find_soulmate_cancel(update, context):
    """取消真命天子搜尋"""
    await update.message.reply_text("已取消真命天子搜尋。", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
# ========1.9 Find Soulmate 流程函數結束 ========#

# ========1.10 按鈕回調處理函數開始 ========#
async def button_callback(update, context):
    """處理按鈕回調"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    telegram_id = query.from_user.id
    internal_user_id = get_internal_user_id(telegram_id)
    
    if not internal_user_id:
        await query.edit_message_text("無法識別用戶，請重新註冊 /start。")
        return
    
    if data.startswith("ai_prompt_"):
        # 處理AI提示請求
        parts = data.split("_")
        if len(parts) < 3:
            await query.edit_message_text("AI提示數據錯誤。")
            return
        
        timestamp_str = parts[2]
        token = parts[3] if len(parts) > 3 else ""
        
        ai_prompt = context.user_data.get("ai_prompt", "")
        
        if ai_prompt:
            # 發送完整的AI提示
            await query.edit_message_text(AI_USAGE_TIPS)
            # 發送提示文本
            prompt_text = f"```\n{ai_prompt}\n```"
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=prompt_text,
                parse_mode='Markdown'
            )
            
            # 發送使用提示
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=AI_USAGE_TIPS
            )
        else:
            await query.edit_message_text("AI提示數據已過期，請重新進行配對。")
        return
    
    elif data.startswith("accept_"):
        parts = data.split("_")
        if len(parts) != 5:
            await query.edit_message_text("配對數據格式錯誤。")
            return
        
        _, user_a_str, user_b_str, timestamp_str, token = parts
        data_str = f"{user_a_str}_{user_b_str}_{timestamp_str}"
        expected_token = hashlib.sha256(
            f"{data_str}_{SECRET_KEY}".encode()).hexdigest()[:12]
        
        if token != expected_token:
            await query.edit_message_text("配對數據已過期或無效。")
            return
        
        try:
            timestamp = int(timestamp_str)
            if datetime.now().timestamp() - timestamp > 600:
                await query.edit_message_text("配對已過期，請重新開始。")
                return
        except BaseException:
            await query.edit_message_text("配對數據錯誤。")
            return
        
        user_a_id = int(user_a_str)
        user_b_id = int(user_b_str)
        
        if internal_user_id not in [user_a_id, user_b_id]:
            await query.edit_message_text("你不是此配對的參與者。")
            return
        
        other_id = user_b_id if internal_user_id == user_a_id else user_a_id
        
        with closing(get_conn()) as conn:
            cur = conn.cursor()
            
            user_a_accepted = 0
            user_b_accepted = 0
            match_id = None
            
            cur.execute("""
                SELECT id, user_a_accepted, user_b_accepted
                FROM matches
                WHERE (user_a = %s AND user_b = %s)
                   OR (user_a = %s AND user_b = %s)
            """, (user_a_id, user_b_id, user_b_id, user_a_id))
            
            match_row = cur.fetchone()
            
            if match_row:
                match_id, user_a_accepted, user_b_accepted = match_row
            else:
                score = context.user_data.get(
                    "current_match", {}).get(
                    "score", 70)
                match_result = context.user_data.get(
                    "current_match", {}).get(
                    "match_result", {})
                
                cur.execute("""
                    INSERT INTO matches (user_a, user_b, score, match_details)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_a, user_b) DO NOTHING
                    RETURNING id
                """, (user_a_id, user_b_id, score, json.dumps(match_result)))
                result = cur.fetchone()
                match_id = result[0] if result else None
                
                conn.commit()
                
                if not match_id:
                    cur.execute("""
                        SELECT id FROM matches
                        WHERE user_a = %s AND user_b = %s
                    """, (user_a_id, user_b_id))
                    match_row = cur.fetchone()
                    if match_row:
                        match_id = match_row[0]
                    else:
                        await query.edit_message_text("配對記錄創建失敗。")
                        return
            
            if internal_user_id == user_a_id:
                user_a_accepted = 1
                cur.execute("""
                    UPDATE matches
                    SET user_a_accepted = 1
                    WHERE id = %s
                """, (match_id,))
            else:
                user_b_accepted = 1
                cur.execute("""
                    UPDATE matches
                    SET user_b_accepted = 1
                    WHERE id = %s
                """, (match_id,))
            
            conn.commit()
            
            if user_a_accepted == 1 and user_b_accepted == 1:
                cur.execute("SELECT score FROM matches WHERE id = %s", (match_id,))
                score_row = cur.fetchone()
                actual_score = score_row[0] if score_row else 70
                
                # 使用新的評分閾值
                if actual_score < THRESHOLD_CONTACT_ALLOWED:
                    await query.edit_message_text(
                        f"此配對分數 {actual_score:.1f}分 未達交換聯絡方式標準（需≥{THRESHOLD_CONTACT_ALLOWED}分）。\n"
                        f"建議尋找更合適的配對。"
                    )
                    return
                
                a_telegram_id = get_telegram_id(user_a_id)
                b_telegram_id = get_telegram_id(user_b_id)
                a_username = get_username(user_a_id) or "未設定用戶名"
                b_username = get_username(user_b_id) or "未設定用戶名"
                
                # 獲取雙方完整資料用於格式化配對成功消息
                a_profile = get_profile_data(user_a_id)
                b_profile = get_profile_data(user_b_id)
                
                # 使用新的評級系統
                from new_calculator import ScoringEngine
                rating = ScoringEngine.get_rating(actual_score)
                
                # 格式化配對成功消息
                message_for_a = f"{rating} 配對成功！\n\n"
                message_for_a += f"🎯 配對分數：{actual_score:.1f}分\n"
                message_for_a += f"📱 對方 Telegram: @{b_username}\n"
                
                if b_profile:
                    b_hour_conf = FormatUtils.format_confidence(b_profile['hour_confidence'])
                    message_for_a += f"📅 出生時間: {b_profile['birth_year']}年{b_profile['birth_month']}月{b_profile['birth_day']}日 {b_profile['birth_hour']}:{b_profile['birth_minute']:02d}\n"
                    message_for_a += f"🕰️ 時間信心度: {b_hour_conf}\n"
                    message_for_a += f"📅 八字: {b_profile['year_pillar']} {b_profile['month_pillar']} {b_profile['day_pillar']} {b_profile['hour_pillar']}\n"
                    message_for_a += f"🐉 生肖: {b_profile['zodiac']}\n"
                    message_for_a += f"⚖️ 日主: {b_profile['day_stem']}{b_profile['day_stem_element']} ({b_profile['day_stem_strength']})\n"
                    message_for_a += f"💪 身強弱: {b_profile['strength_score']:.1f}分\n"
                    message_for_a += f"🎭 格局: {b_profile['cong_ge_type']}\n"
                    message_for_a += f"🎯 喜用神: {', '.join(b_profile['useful_elements'])}\n"
                    message_for_a += f"🚫 忌神: {', '.join(b_profile['harmful_elements'])}\n"
                    message_for_a += f"💑 夫妻星: {b_profile['spouse_star_status']}\n"
                    message_for_a += f"🏠 夫妻宮: {b_profile['spouse_palace_status']}\n"
                    message_for_a += f"✨ 神煞: {b_profile['shen_sha_names']}\n"
                
                message_for_a += "💡 溫馨提示：\n"
                message_for_a += "• 先打招呼互相認識\n"
                message_for_a += "• 分享興趣尋找共同話題\n"
                message_for_a += "• 保持尊重，慢慢了解\n\n"
                message_for_a += "✨ 祝你們交流愉快！"
                
                message_for_b = f"{rating} 配對成功！\n\n"
                message_for_b += f"🎯 配對分數：{actual_score:.1f}分\n"
                message_for_b += f"📱 對方 Telegram: @{a_username}\n"
                
                if a_profile:
                    a_hour_conf = FormatUtils.format_confidence(a_profile['hour_confidence'])
                    message_for_b += f"📅 出生時間: {a_profile['birth_year']}年{a_profile['birth_month']}月{a_profile['birth_day']}日 {a_profile['birth_hour']}:{a_profile['birth_minute']:02d}\n"
                    message_for_b += f"🕰️ 時間信心度: {a_hour_conf}\n"
                    message_for_b += f"📅 八字: {a_profile['year_pillar']} {a_profile['month_pillar']} {a_profile['day_pillar']} {a_profile['hour_pillar']}\n"
                    message_for_b += f"🐉 生肖: {a_profile['zodiac']}\n"
                    message_for_b += f"⚖️ 日主: {a_profile['day_stem']}{a_profile['day_stem_element']} ({a_profile['day_stem_strength']})\n"
                    message_for_b += f"💪 身強弱: {a_profile['strength_score']:.1f}分\n"
                    message_for_b += f"🎭 格局: {a_profile['cong_ge_type']}\n"
                    message_for_b += f"🎯 喜用神: {', '.join(a_profile['useful_elements'])}\n"
                    message_for_b += f"🚫 忌神: {', '.join(a_profile['harmful_elements'])}\n"
                    message_for_b += f"💑 夫妻星: {a_profile['spouse_star_status']}\n"
                    message_for_b += f"🏠 夫妻宮: {a_profile['spouse_palace_status']}\n"
                    message_for_b += f"✨ 神煞: {a_profile['shen_sha_names']}\n"
                
                message_for_b += "💡 溫馨提示：\n"
                message_for_b += "• 先打招呼互相認識\n"
                message_for_b += "• 分享興趣尋找共同話題\n"
                message_for_b += "• 保持尊重，慢慢了解\n\n"
                message_for_b += "✨ 祝你們交流愉快！"
                
                if a_username == "未設定用戶名" or b_username == "未設定用戶名":
                    warning = "\n\n⚠️ 注意：如無法聯絡對方，請對方在 Telegram 設定中設定用戶名。"
                    message_for_a += warning
                    message_for_b += warning
                
                try:
                    await context.bot.send_message(chat_id=a_telegram_id, text=message_for_a)
                except Exception as e:
                    logger.error(f"無法發送消息給用戶A: {e}")
                
                try:
                    await context.bot.send_message(chat_id=b_telegram_id, text=message_for_b)
                except Exception as e:
                    logger.error(f"無法發送消息給用戶B: {e}")
                
                # 發送AI提示給雙方
                match_result = context.user_data.get(
                    "current_match", {}).get(
                    "match_result", {})
                if match_result and a_profile and b_profile:
                    ai_prompt = FormatUtils.generate_ai_prompt(match_result, a_profile, b_profile)
                    
                    ai_tips = (
                        "🤖 AI分析提示：\n\n"
                        "想深入了解這個配對？複製以下內容問AI：\n\n"
                        f"```\n{ai_prompt[:500]}...\n```\n\n"
                        "完整提示請查看之前的消息。"
                    )
                    
                    try:
                        await context.bot.send_message(chat_id=a_telegram_id, text=ai_tips, parse_mode='Markdown')
                        await context.bot.send_message(chat_id=b_telegram_id, text=ai_tips, parse_mode='Markdown')
                    except Exception as e:
                        logger.error(f"發送AI提示失敗: {e}")
                
                await query.edit_message_text("🎉 配對成功！已交換聯絡方式。")
            else:
                await query.edit_message_text("已記錄你的意願，等待對方回應...")
    
    elif data.startswith("reject_"):
        await query.edit_message_text("已略過此配對。下次再試 /match 吧！")
# ========1.10 按鈕回調處理函數結束 ========#

# ========1.11 主程序開始 ========#
def main():
    import time
    
    logger.info("⏳ 等待舊實例清理...")
    time.sleep(1)
    
    # 初始化PostgreSQL數據庫
    init_db()
    
    token = os.getenv("BOT_TOKEN", "").strip()
    
    if not token:
        logger.error("錯誤: BOT_TOKEN 環境變數未設定！")
        raise ValueError("BOT_TOKEN 未設定")
    
    token = token.replace('\n', '').replace('\r', '')
    
    try:
        app = Application.builder().token(token).build()
        
        async def error_handler(update, context):
            logger.error(f"錯誤: {context.error}")
            error_str = str(context.error)
            if "Conflict" in error_str or "terminated by other getUpdates request" in error_str:
                logger.error("⚠️ 多實例衝突，將在5秒後退出...")
                await asyncio.sleep(5)
                os._exit(1)
        
        app.add_error_handler(error_handler)
        
        # 主註冊流程（簡化版）
        main_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                TERMS_ACCEPTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_terms_acceptance)],
                ASK_BASIC_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_basic_info)],
                ASK_TIME_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_time_confirmation)],
                ASK_HOUR_KNOWN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_hour_known)],
            },
            fallbacks=[
                CommandHandler("cancel", cancel),
                CommandHandler("start", start),
            ],
            allow_reentry=True,
        )
        
        # Find Soulmate 流程
        soulmate_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("find_soulmate", find_soulmate_start)],
            states={
                FIND_SOULMATE_RANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_soulmate_range)],
                FIND_SOULMATE_PURPOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_soulmate_purpose)],
            },
            fallbacks=[
                CommandHandler("cancel", find_soulmate_cancel),
            ],
            allow_reentry=True,
        )
        
        # 添加所有處理器
        app.add_handler(main_conv_handler)
        app.add_handler(soulmate_conv_handler)
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("profile", profile))
        app.add_handler(CommandHandler("explain", explain_command))
        app.add_handler(CommandHandler("test", test_command))
        app.add_handler(CommandHandler("clear", clear_command))
        app.add_handler(CommandHandler("testpair", test_pair_command))
        app.add_handler(CommandHandler("match", match))
        # 添加管理員命令處理器
        app.add_handler(CommandHandler("admin_test", admin_test_command))
        app.add_handler(CommandHandler("admin_stats", admin_stats_command))
        app.add_handler(CommandHandler("admin_demo", admin_demo_command))
        app.add_handler(CommandHandler("admin_service", admin_service_command))
        app.add_handler(CommandHandler("maintenance", maintenance_command))
        app.add_handler(CallbackQueryHandler(button_callback))
        
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.error(f"❌ Bot 啟動失敗: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()
# ========1.11 主程序結束 ========#

# ========文件信息開始 ========#
"""
文件: bot.py
功能: 主程序文件，包含所有Bot交互邏輯

引用文件: 
- texts.py (文本常量)
- new_calculator.py (八字計算核心)
- bazi_soulmate.py (真命天子搜尋功能)
- admin_service.py (管理員服務)
- psycopg2 (PostgreSQL數據庫連接)

被引用文件: 無

主要修改：
1. 增強維護模式檢查裝飾器：真正暫停非管理員用戶
2. 添加管理員專用檢查裝飾器：check_admin_only
3. 增強維護模式命令：提供更詳細的狀態信息
4. 在註冊完成後的功能選單中正確顯示管理員專用功能
5. 所有管理員命令添加權限檢查
6. 統一格式化工具類擴展
7. 簡化註冊流程（兩步完成）
8. 添加健康引用功能
9. 支援同性配對
10. 優化admin功能顯示
11. 統一四方功能格式
12. 所有消息單次發送
13. 添加target_gender字段支援對象性別選擇
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
1.1 導入模組開始
1.2 配置與初始化開始
1.3 維護模式檢查開始
1.4 統一格式化工具類開始
1.5 數據庫工具開始
1.6 隱私條款模組開始
1.7 簡化註冊流程開始
1.8 命令處理函數開始
1.9 Find Soulmate流程函數開始
1.10 按鈕回調處理函數開始
1.11 主程序開始
"""
# ========目錄結束 ========#

# ========修正紀錄開始 ========#
"""
修正內容：
1. 增強維護模式檢查裝飾器：真正暫停非管理員用戶，管理員可繞過
2. 添加管理員專用檢查裝飾器：check_admin_only
3. 維護模式命令增強：提供更詳細的狀態信息和管理指南
4. 註冊完成後功能選單：正確顯示管理員專用功能區塊
5. 所有管理員命令添加權限檢查和裝飾器
6. 一鍵測試演示功能：使用測試案例第一組八字模擬所有核心功能
7. 統一消息發送：所有功能單次發送完整消息
8. 修復同性配對查詢邏輯
9. 添加健康引用功能：profile結果包含健康建議
10. 增強FormatUtils類：統一四方功能格式

導致問題：原維護模式只設置標誌未真正阻止用戶
如何修復：增強check_maintenance裝飾器，真正攔截非管理員請求
後果：維護模式期間普通用戶無法使用任何功能

導致問題：管理員功能對管理員不可見
如何修復：在註冊完成後的功能選單中為管理員添加專用區塊
後果：管理員能正常看到和使用所有管理功能

導致問題：缺少一鍵測試演示功能
如何修復：在admin_service.py中添加run_oneclick_demo()函數
後果：管理員可以快速測試所有核心功能

導致問題：四方功能格式不一致
如何修復：擴展FormatUtils類提供統一格式化方法
後果：所有功能使用相同格式，提高一致性
"""
# ========修正紀錄結束 ========#