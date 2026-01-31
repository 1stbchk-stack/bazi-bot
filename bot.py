# ========1.1 導入模組開始 ========#
import os
import logging
import sqlite3
import asyncio
import json
import hashlib
import traceback
from datetime import datetime
from contextlib import closing
from typing import Dict, List, Tuple, Any, Optional

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
from new_calculator import (
    # 格式化函數 - 從 new_calculator 導入
    format_match_result,
    format_profile_result,
    generate_ai_prompt,
    
    # 評分閾值 - 從 new_calculator 導入
    THRESHOLD_WARNING,
    THRESHOLD_CONTACT_ALLOWED,
    THRESHOLD_GOOD_MATCH,
    THRESHOLD_EXCELLENT_MATCH,
    THRESHOLD_PERFECT_MATCH
)


# 導入新的計算核心 (使用 new_calculator.py)
from new_calculator import (
    # 八字計算器 - 保持相同接口
    BaziCalculator as ProfessionalBaziCalculator,  # 使用別名保持兼容
    
    # 評分引擎 - 使用新的ScoringEngine
    ScoringEngine as MasterBaziMatcher,  # 使用別名保持兼容
    
    # 格式化函數 - 從 new_calculator 導入
    format_match_result,
    format_profile_result,
    generate_ai_prompt,
    
    # 錯誤處理 - 映射到新的錯誤類
    BaziCalculatorError as BaziError,    # 映射到新的錯誤類
    ScoringEngineError as MatchError,    # 映射到新的錯誤類
    
    # 配置常數
    MASTER_BAZI_CONFIG,
    
    # 關係分析器
    RelationshipAnalyzer,
    
    # 時間處理器
    TimeProcessor,
    
    # 審計日誌函數
    audit_log_match,
    audit_log_calculation
)

# 導入 Soulmate 功能（新分拆的檔案）
from bazi_soulmate import (
    SoulmateFinder,
    format_find_soulmate_result
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
    REGISTRATION_COMPLETE_TEXT
)
# ========1.1 導入模組結束 ========#

# ========1.2 配置與初始化開始 ========#
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

def get_db_path():
    railway_data = "/data/bazi_match.db"
    current_dir = "bazi_match.db"

    try:
        if os.path.exists("/data"):
            test_file = "/data/.write_test"
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                logger.info("/data 目錄可寫，使用持久化儲存")
                return railway_data
            except BaseException:
                logger.warning("/data 目錄不可寫，使用當前目錄")
                return current_dir
        else:
            logger.info("/data 目錄不存在，使用當前目錄")
            return current_dir
    except Exception as e:
        logger.error(f"檢查目錄權限失敗: {e}")
        return current_dir

DB_PATH = get_db_path()
logger.info(f"使用數據庫路徑: {DB_PATH}")

SECRET_KEY = os.getenv("MATCH_SECRET_KEY", "your-secret-key-change-me").strip()
DAILY_MATCH_LIMIT = 10

# 對話狀態
(
    TERMS_ACCEPTANCE,
    ASK_YEAR,
    ASK_MONTH,
    ASK_DAY,
    ASK_HOUR_KNOWN,
    ASK_HOUR,
    ASK_GENDER,
    FIND_SOULMATE_RANGE,
    FIND_SOULMATE_PURPOSE,
) = range(9)

USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql://")
# ========1.2 配置與初始化結束 ========#

# ========1.3 數據庫工具開始 ========#
def get_conn():
    if USE_POSTGRES:
        try:
            import psycopg2
            conn_url = DATABASE_URL.replace("postgres://", "postgresql://")
            return psycopg2.connect(conn_url)
        except ImportError:
            logger.warning("未安裝 psycopg2，將使用 SQLite")
            return sqlite3.connect(DB_PATH)
        except Exception as e:
            logger.error(f"PostgreSQL 連接失敗: {e}，使用 SQLite")
            return sqlite3.connect(DB_PATH)
    else:
        return sqlite3.connect(DB_PATH)

def get_placeholder():
    return "%s" if USE_POSTGRES else "?"

def init_db():
    try:
        with closing(get_conn()) as conn:
            cur = conn.cursor()

            if USE_POSTGRES:
                logger.info("創建 PostgreSQL 表...")
                cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active INTEGER DEFAULT 1
                )
                ''')
                cur.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    birth_year INTEGER,
                    birth_month INTEGER,
                    birth_day INTEGER,
                    birth_hour INTEGER,
                    hour_confidence TEXT DEFAULT '高',
                    gender TEXT,
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
                cur.execute('''
                CREATE TABLE IF NOT EXISTS daily_limits (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    date DATE DEFAULT CURRENT_DATE,
                    match_count INTEGER DEFAULT 0,
                    UNIQUE(user_id, date)
                )
                ''')
                cur.execute('CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)')
                cur.execute('CREATE INDEX IF NOT EXISTS idx_matches_users ON matches(user_a, user_b)')
            else:
                logger.info("創建 SQLite 表...")
                try:
                    cur.execute('PRAGMA foreign_keys = ON')
                except BaseException:
                    pass
                cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active INTEGER DEFAULT 1
                )
                ''')
                cur.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id INTEGER PRIMARY KEY,
                    birth_year INTEGER,
                    birth_month INTEGER,
                    birth_day INTEGER,
                    birth_hour INTEGER,
                    hour_confidence TEXT DEFAULT '高',
                    gender TEXT,
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
                    shen_sha_data TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                ''')
                cur.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_a INTEGER,
                    user_b INTEGER,
                    score REAL,
                    user_a_accepted INTEGER DEFAULT 0,
                    user_b_accepted INTEGER DEFAULT 0,
                    match_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_a) REFERENCES users(id),
                    FOREIGN KEY (user_b) REFERENCES users(id),
                    UNIQUE(user_a, user_b)
                )
                ''')
                cur.execute('''
                CREATE TABLE IF NOT EXISTS daily_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE DEFAULT CURRENT_DATE,
                    match_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, date)
                )
                ''')
                cur.execute('CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)')
                cur.execute('CREATE INDEX IF NOT EXISTS idx_matches_users ON matches(user_a, user_b)')

            conn.commit()
            logger.info(f"數據庫初始化完成")
    except Exception as e:
        logger.error(f"數據庫初始化失敗: {e}")
        raise

def check_daily_limit(user_id):
    try:
        with closing(get_conn()) as conn:
            cur = conn.cursor()
            today = datetime.now().date()

            if USE_POSTGRES:
                cur.execute("""
                    INSERT INTO daily_limits (user_id, date, match_count)
                    VALUES (%s, %s, 1)
                    ON CONFLICT (user_id, date)
                    DO UPDATE SET match_count = daily_limits.match_count + 1
                    RETURNING match_count
                """, (user_id, today))
            else:
                cur.execute("""
                    INSERT OR IGNORE INTO daily_limits (user_id, date, match_count)
                    VALUES (?, DATE('now'), 0)
                """, (user_id,))
                cur.execute("""
                    UPDATE daily_limits
                    SET match_count = match_count + 1
                    WHERE user_id = ? AND date = DATE('now')
                """, (user_id,))
                cur.execute("""
                    SELECT match_count FROM daily_limits
                    WHERE user_id = ? AND date = DATE('now')
                """, (user_id,))

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
    try:
        with closing(get_conn()) as conn:
            cur = conn.cursor()
            placeholder = get_placeholder()
            cur.execute(f"""
                DELETE FROM matches
                WHERE user_a = (SELECT id FROM users WHERE telegram_id = {placeholder})
                   OR user_b = (SELECT id FROM users WHERE telegram_id = {placeholder})
            """, (telegram_id, telegram_id))
            cur.execute(f"""
                DELETE FROM daily_limits
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = {placeholder})
            """, (telegram_id,))
            cur.execute(f"""
                DELETE FROM profiles
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = {placeholder})
            """, (telegram_id,))
            cur.execute(f"""
                DELETE FROM users
                WHERE telegram_id = {placeholder}
            """, (telegram_id,))
            conn.commit()
            logger.info(f"已清除用戶 {telegram_id} 的資料")
    except Exception as e:
        logger.error(f"清除用戶資料失敗: {e}")

def get_internal_user_id(telegram_id):
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM users WHERE telegram_id = {get_placeholder()}", (telegram_id,))
        row = cur.fetchone()
        return row[0] if row else None

def get_telegram_id(internal_user_id):
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT telegram_id FROM users WHERE id = {get_placeholder()}", (internal_user_id,))
        row = cur.fetchone()
        return row[0] if row else None

def get_username(internal_user_id):
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT username FROM users WHERE id = {get_placeholder()}", (internal_user_id,))
        row = cur.fetchone()
        return row[0] if row else None
# ========1.3 數據庫工具結束 ========#

# ========1.4 隱私條款模組開始 ========#
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

async def handle_terms_acceptance(update, context):
    """處理隱私條款同意"""
    text = update.message.text.strip()

    if text == "✅ 同意並繼續":
        await update.message.reply_text(
            "✅ 感謝您同意隱私條款！\n\n"
            "現在開始註冊流程。\n"
            "請輸入出生年份（西元年份，例如 1990）：",
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_YEAR
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
# ========1.4 隱私條款模組結束 ========#

# ========1.5 Bot 註冊流程函數開始 ========#
async def start(update, context):
    """開始命令 - 顯示隱私條款"""
    user = update.effective_user
    
    # 僅在用戶有資料且需要覆蓋時才清除
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

async def ask_year(update, context):
    """詢問年份"""
    text = update.message.text.strip()

    if context.user_data.get("confirm_overwrite"):
        if text == "否":
            await update.message.reply_text("已取消重新註冊。", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        elif text != "是":
            keyboard = [["是", "否"]]
            reply_markup = ReplyKeyboardMarkup(
                keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("請選擇「是」或「否」：", reply_markup=reply_markup)
            return ASK_YEAR

        context.user_data.pop("confirm_overwrite", None)
        await update.message.reply_text(
            "請輸入出生年份（西元年份，例如 1990）：",
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_YEAR

    if not text.isdigit():
        await update.message.reply_text("請輸入數字年份，例如 1990：")
        return ASK_YEAR

    year = int(text)
    current_year = datetime.now().year
    if year < 1900 or year > current_year:
        await update.message.reply_text(f"請輸入合理年份（1900-{current_year}）：")
        return ASK_YEAR

    context.user_data["birth_year"] = year
    await update.message.reply_text("請輸入出生月份（1-12）：")
    return ASK_MONTH

async def ask_month(update, context):
    """詢問月份"""
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("請輸入數字月份（1-12）：")
        return ASK_MONTH

    month = int(text)
    if not 1 <= month <= 12:
        await update.message.reply_text("月份必須 1-12，請重新輸入：")
        return ASK_MONTH

    context.user_data["birth_month"] = month
    await update.message.reply_text("請輸入出生日（1-31）：")
    return ASK_DAY

async def ask_day(update, context):
    """詢問日期"""
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("請輸入數字日期（1-31）：")
        return ASK_DAY

    day = int(text)
    if not 1 <= day <= 31:
        await update.message.reply_text("日期必須 1-31，請重新輸入：")
        return ASK_DAY

    year = context.user_data.get("birth_year", 2000)
    month = context.user_data.get("birth_month", 1)

    try:
        datetime(year, month, day)
    except ValueError:
        await update.message.reply_text(f"{year}年{month}月無{day}號，請重新輸入：")
        return ASK_DAY

    context.user_data["birth_day"] = day

    keyboard = [["✅ 知道確切時間", "🤔 大約知道", "❓ 完全不知道"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        ASK_HOUR_KNOWN_TEXT,
        reply_markup=reply_markup
    )
    return ASK_HOUR_KNOWN

async def ask_hour_known(update, context):
    """處理是否知道出生時間"""
    text = update.message.text.strip()

    if text == "✅ 知道確切時間":
        context.user_data["hour_known"] = "yes"
        await update.message.reply_text(
            "請輸入出生時間（0-23 點，例如 14 代表下午2點）：",
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_HOUR

    elif text == "🤔 大約知道":
        context.user_data["hour_known"] = "approximate"
        await update.message.reply_text(
            APPROXIMATE_HOUR_DESCRIPTION,
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_HOUR

    elif text == "❓ 完全不知道":
        context.user_data["hour_known"] = "no"
        context.user_data["birth_hour"] = 12
        context.user_data["hour_confidence"] = "低"

        keyboard = [["男", "女"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            UNKNOWN_HOUR_WARNING,
            reply_markup=reply_markup
        )
        return ASK_GENDER

    else:
        keyboard = [["✅ 知道確切時間", "🤔 大約知道", "❓ 完全不知道"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("請選擇上方選項：", reply_markup=reply_markup)
        return ASK_HOUR_KNOWN

async def ask_hour(update, context):
    """詢問出生時間"""
    hour_known = context.user_data.get("hour_known", "yes")

    if hour_known == "yes":
        text = update.message.text.strip()
        if not text.isdigit():
            await update.message.reply_text("請輸入 0-23 整點，例如 14：")
            return ASK_HOUR

        hour = int(text)
        if not 0 <= hour <= 23:
            await update.message.reply_text("時間必須 0-23，請重新輸入：")
            return ASK_HOUR

        context.user_data["birth_hour"] = hour
        context.user_data["hour_confidence"] = "高"

    elif hour_known == "approximate":
        description = update.message.text.strip()
        estimated_hour, estimated_confidence = TimeProcessor.estimate_hour_from_description(description)

        context.user_data["birth_hour"] = estimated_hour
        context.user_data["hour_confidence"] = "中"
        context.user_data["hour_description"] = description

        await update.message.reply_text(
            f"✅ 已根據描述估算為 {estimated_hour}:00 時\n\n"
            f"📝 您的描述：{description}\n"
            f"⏰ 估算時間：{estimated_hour}:00\n"
            f"📊 信心度：中等\n\n"
            "💡 如需更準確，請查詢確切出生時間。"
        )

    keyboard = [["男", "女"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("請選擇性別：", reply_markup=reply_markup)
    return ASK_GENDER

async def ask_gender(update, context):
    """詢問性別並完成註冊"""
    gender = update.message.text.strip()

    if gender not in ["男", "女"]:
        keyboard = [["男", "女"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("請使用下方鍵盤選擇「男」或「女」：", reply_markup=reply_markup)
        return ASK_GENDER

    year = context.user_data["birth_year"]
    month = context.user_data["birth_month"]
    day = context.user_data["birth_day"]
    hour = context.user_data.get("birth_hour", 12)
    hour_confidence = context.user_data.get("hour_confidence", "高")

    try:
        datetime(year, month, day)
    except ValueError:
        await update.message.reply_text("日期無效，請重新輸入 /start")
        return ConversationHandler.END

    try:
        # 使用新的八字計算器
        bazi = ProfessionalBaziCalculator.calculate(
            year, month, day, hour, 
            gender=gender,
            hour_confidence=hour_confidence
        )
    except BaziError as e:
        await update.message.reply_text(f"八字計算錯誤: {e}，請重新輸入 /start")
        return ConversationHandler.END

    if not bazi:
        await update.message.reply_text("八字計算失敗，請重新輸入 /start")
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

        if USE_POSTGRES:
            cur.execute(f"""
                INSERT INTO users (telegram_id, username)
                VALUES ({get_placeholder()}, {get_placeholder()})
                ON CONFLICT (telegram_id) DO UPDATE SET username = EXCLUDED.username
                RETURNING id
            """, (telegram_id, username))
        else:
            cur.execute(f"""
                INSERT OR IGNORE INTO users (telegram_id, username)
                VALUES ({get_placeholder()}, {get_placeholder()})
            """, (telegram_id, username))
            cur.execute(f"""
                UPDATE users SET username = {get_placeholder()} WHERE telegram_id = {get_placeholder()}
            """, (username, telegram_id))
            cur.execute(
                f"SELECT id FROM users WHERE telegram_id = {
                    get_placeholder()}", (telegram_id,))

        row = cur.fetchone()
        if not row:
            await update.message.reply_text("用戶創建失敗，請重試", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

        internal_user_id = row[0]
        elements = bazi.get("elements", {})

        if USE_POSTGRES:
            cur.execute(f"""
                INSERT INTO profiles
                (user_id, birth_year, birth_month, birth_day, birth_hour, hour_confidence, gender,
                 year_pillar, month_pillar, day_pillar, hour_pillar,
                 zodiac, day_stem, day_stem_element,
                 wood, fire, earth, metal, water,
                 day_stem_strength, strength_score, useful_elements, harmful_elements,
                 spouse_star_status, spouse_star_effective, spouse_palace_status, pressure_score,
                 cong_ge_type, shi_shen_structure, shen_sha_data)
                VALUES ({get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()}, {get_placeholder()},{get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()}, {get_placeholder()})
                ON CONFLICT (user_id) DO UPDATE SET
                    birth_year = EXCLUDED.birth_year,
                    birth_month = EXCLUDED.birth_month,
                    birth_day = EXCLUDED.birth_day,
                    birth_hour = EXCLUDED.birth_hour,
                    hour_confidence = EXCLUDED.hour_confidence,
                    gender = EXCLUDED.gender,
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
                internal_user_id, year, month, day, hour, hour_confidence, gender,
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
        else:
            cur.execute(f"""
                INSERT OR REPLACE INTO profiles
                (user_id, birth_year, birth_month, birth_day, birth_hour, hour_confidence, gender,
                 year_pillar, month_pillar, day_pillar, hour_pillar,
                 zodiac, day_stem, day_stem_element,
                 wood, fire, earth, metal, water,
                 day_stem_strength, strength_score, useful_elements, harmful_elements,
                 spouse_star_status, spouse_star_effective, spouse_palace_status, pressure_score,
                 cong_ge_type, shi_shen_structure, shen_sha_data)
                VALUES ({get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()}, {get_placeholder()},{get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()},
                       {get_placeholder()}, {get_placeholder()}, {get_placeholder()}, {get_placeholder()})
            """, (
                internal_user_id, year, month, day, hour, hour_confidence, gender,
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

    # 準備顯示用的信心度文本
    confidence_map = {
        "高": "（高信心度）",
        "中": "（中信心度，時辰估算）",
        "低": "（低信心度，時辰未知）"
    }
    confidence_text = confidence_map.get(hour_confidence, "（信心度未知）")

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
        "hour_confidence": hour_confidence
    }

    profile_result = format_profile_result(bazi_data_for_display, username)
    
    # 使用文字常量
    registration_text = REGISTRATION_COMPLETE_TEXT.format(
        confidence_text=confidence_text,
        profile_result=profile_result
    )
    
    await update.message.reply_text(
        registration_text,
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END

async def cancel(update, context):
    """取消流程"""
    await update.message.reply_text("已取消流程。", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
# ========1.5 Bot 註冊流程函數結束 ========#

# ========1.6 命令處理函數開始 ========#
async def help_command(update, context):
    """幫助命令"""
    await update.message.reply_text(HELP_TEXT)

async def explain_command(update, context):
    """解釋算法命令"""
    await update.message.reply_text(EXPLANATION_TEXT)

async def profile(update, context):
    """查看個人資料"""
    telegram_id = update.effective_user.id
    internal_user_id = get_internal_user_id(telegram_id)

    if not internal_user_id:
        await update.message.reply_text("未找到紀錄，請先 /start 註冊。")
        return

    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT username FROM users WHERE id = {
                get_placeholder()}", (internal_user_id,))
        user_row = cur.fetchone()
        uname = user_row[0] if user_row else "未知"

        cur.execute(f"""
            SELECT birth_year, birth_month, birth_day, birth_hour, hour_confidence, gender,
                   year_pillar, month_pillar, day_pillar, hour_pillar,
                   zodiac, day_stem, day_stem_element,
                   wood, fire, earth, metal, water,
                   day_stem_strength, strength_score, useful_elements, harmful_elements,
                   spouse_star_status, spouse_star_effective, spouse_palace_status, pressure_score,
                   cong_ge_type, shi_shen_structure, shen_sha_data
            FROM profiles WHERE user_id = {get_placeholder()}
        """, (internal_user_id,))
        p = cur.fetchone()

    if p is None:
        await update.message.reply_text("尚未完成資料輸入。請輸入 /start 開始註冊。")
        return

    (
        by, bm, bd, bh, hour_conf, g,
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
    shen_sha_bonus = shen_sha_data.get("bonus", 0)

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
        "shen_sha_bonus": shen_sha_bonus,
        "elements": {"木": w, "火": f, "土": e, "金": m, "水": wt},
        "hour_confidence": hour_conf
    }

    # 使用計算核心的格式化函數
    profile_text = format_profile_result(bazi_data, uname)
    await update.message.reply_text(profile_text)

async def match(update, context):
    """開始配對"""
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

        cur.execute(f"""
            SELECT birth_year, birth_month, birth_day, birth_hour, hour_confidence, gender,
                   year_pillar, month_pillar, day_pillar, hour_pillar,
                   zodiac, day_stem, day_stem_element,
                   wood, fire, earth, metal, water,
                   day_stem_strength, strength_score, useful_elements, harmful_elements,
                   spouse_star_status, spouse_star_effective, spouse_palace_status, pressure_score,
                   cong_ge_type, shi_shen_structure, shen_sha_data
            FROM profiles WHERE user_id = {get_placeholder()}
        """, (internal_user_id,))
        me_p = cur.fetchone()

        if me_p is None:
            await update.message.reply_text("請先完成資料輸入流程。")
            return

        def to_profile(row):
            (
                by, bm, bd, bh, hour_conf, gender,
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
                "shi_shen_list": shi_shen.split(',')[0] if shi_shen else '',
                "hour_confidence": hour_conf,
                "birth_year": by,
                "shen_sha_names": shen_sha_data.get("names", "無"),
                "shen_sha_bonus": shen_sha_data.get("bonus", 0)
            }

        me_profile = to_profile(me_p)
        my_gender = me_p[5]

        cur.execute(f"""
            SELECT
                u.id, u.telegram_id, u.username,
                p.birth_year, p.birth_month, p.birth_day, p.birth_hour, p.hour_confidence, p.gender,
                p.year_pillar, p.month_pillar, p.day_pillar, p.hour_pillar,
                p.zodiac, p.day_stem, p.day_stem_element,
                p.wood, p.fire, p.earth, p.metal, p.water,
                p.day_stem_strength, p.strength_score, p.useful_elements, p.harmful_elements,
                p.spouse_star_status, p.spouse_star_effective, p.spouse_palace_status, p.pressure_score,
                p.cong_ge_type, p.shi_shen_structure, p.shen_sha_data
            FROM users u
            JOIN profiles p ON u.id = p.user_id
            WHERE u.id != {get_placeholder()}
            AND u.active = 1
            AND p.gender != {get_placeholder()}
            AND NOT EXISTS (
                SELECT 1 FROM matches m
                WHERE ((m.user_a = {get_placeholder()} AND m.user_b = u.id)
                       OR (m.user_a = u.id AND m.user_b = {get_placeholder()}))
                AND m.user_a_accepted = 1 AND m.user_b_accepted = 1
            )
            ORDER BY RANDOM()
            LIMIT 50
        """, (internal_user_id, my_gender, internal_user_id, internal_user_id))

        rows = cur.fetchall()

    if not rows:
        await update.message.reply_text("暫時未有合適的配對對象。請稍後再試。")
        return

    matches = []

    for r in rows:
        other_internal_id = r[0]
        other_profile = to_profile(r[3:])

        try:
            # 使用新的評分引擎進行配對

            match_result = MasterBaziMatcher.calculate(
                me_profile,
                other_profile,
                my_gender,
                other_profile["gender"]
            )
    
            # 檢查返回值結構
            score = match_result.get("score", 0)
            rating = match_result.get("rating", "未知")
            relationship_model = match_result.get("relationship_model", "")
            details = match_result.get("details", [])
            module_scores = match_result.get("module_scores", {})
            a_to_b_score = match_result.get("a_to_b_score", 0)
            b_to_a_score = match_result.get("b_to_a_score", 0)
            step_details = match_result.get("step_details", [])
    
            # 添加審計日誌（如果函數存在）
            try:
                audit_log_match(score, module_scores, telegram_id)
            except NameError:
                logger.debug("審計日誌功能未啟用")
            
            matches.append({
                "internal_id": other_internal_id,
                "telegram_id": r[1],
                "username": r[2] or "匿名用戶",
                "profile": other_profile,
                "score": score,
                "rating": rating,
                "relationship_model": relationship_model,
                "details": details,
                "step_details": step_details,
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
    from new_calculator import THRESHOLD_WARNING
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

    # 只發送【核心分析結果】和【配對資訊】
    formatted_messages = format_match_result(match_result)
    if len(formatted_messages) >= 2:
        core_analysis = formatted_messages[0]  # 第一條：核心分析結果
        pairing_info = formatted_messages[1]   # 第二條：分數詳情
    else:
        core_analysis = formatted_messages[0]
        pairing_info = ""

   
    # 發送前兩條消息
    await update.message.reply_text(core_analysis)
    await update.message.reply_text(pairing_info)
    
    # 發送按鈕
    await update.message.reply_text("是否想認識對方？", reply_markup=reply_markup)
    
    # 發送AI分析提示按鈕
    ai_prompt = generate_ai_prompt(match_result)
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

    # 通知對方（只發送【核心分析結果】和【配對資訊】）
    try:
        await context.bot.send_message(
            chat_id=best["telegram_id"],
            text=core_analysis
        )
        
        await context.bot.send_message(
            chat_id=best["telegram_id"],
            text=pairing_info
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

async def test_command(update, context):
    """測試命令"""
    await update.message.reply_text("✅ Bot 正在運行中！")

async def debug_command(update, context):
    """調試命令"""
    import platform

    info = f"""
🛠️ Debug 資訊：
Python 版本: {platform.python_version()}
系統: {platform.system()} {platform.release()}
數據庫路徑: {DB_PATH}
使用 PostgreSQL: {USE_POSTGRES}
八字算法版本: 師傅級婚配系統（新評分引擎）
評分模組: 能量救應、結構核心、人格風險、刑沖壓力、神煞加持、專業化解
聯絡交換門檻: {MASTER_BAZI_CONFIG['SCORING_SYSTEM']['THRESHOLDS']['contact_allowed']}分
關係模型系統: 已啟用（平衡型、供求型、相欠型、混合型）
救應優先原則: 能量救應可抵銷後續扣分
審計日誌: 已啟用
"""
    await update.message.reply_text(info)

async def test_pair_command(update, context):
    """獨立測試任意兩個八字配對（不加入數據庫）"""
    if len(context.args) < 10:
        await update.message.reply_text(
            "請提供兩個完整的八字參數。\n"
            "格式：/testpair <年1> <月1> <日1> <時1> <性別1> <年2> <月2> <日2> <時2> <性別2>\n\n"
            "例如：/testpair 1990 1 1 12 男 1991 2 2 13 女\n"
            "性別：男 或 女"
        )
        return

    try:
        # 解析參數
        year1, month1, day1, hour1 = map(int, context.args[:4])
        gender1 = context.args[4]
        year2, month2, day2, hour2 = map(int, context.args[5:9])
        gender2 = context.args[9] if len(context.args) > 9 else "女"

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

        # 計算八字 - 使用新的八字計算器
        bazi1 = ProfessionalBaziCalculator.calculate(
            year1, month1, day1, hour1, 
            gender=gender1,
            hour_confidence="高"
        )
        bazi2 = ProfessionalBaziCalculator.calculate(
            year2, month2, day2, hour2,
            gender=gender2,
            hour_confidence="高"
        )

        if not bazi1 or not bazi2:
            await update.message.reply_text("八字計算失敗，請檢查輸入參數")
            return

        # 配對計算 - 使用新的評分引擎
        match_result = MasterBaziMatcher.calculate(
            bazi1, bazi2, gender1, gender2)

        # 添加審計日誌
        audit_log_match(
            match_result["score"],
            match_result.get("module_scores", {}),
            "test_pair"
        )

        # 發送完整的格式化消息
        formatted_messages = format_match_result(match_result)
        for message in formatted_messages:
            await update.message.reply_text(message)

        # 提供AI分析提示
        ai_prompt = generate_ai_prompt(match_result)
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
# ========1.6 命令處理函數結束 ========#

# ========1.7 Find Soulmate 流程函數開始 ========#
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
        "呢個功能會幫你喺指定過去年份範圍內，搵出最匹配嘅10個出生時空（年月日時）。\n"
        "請先輸入搜尋年份範圍（例如1990-1999，建議每次唔超過10年，避免運算太長）："
    )
    
    return FIND_SOULMATE_RANGE

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
            await update.message.reply_text("年份範圍太大，建議每次唔超過20年")
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
            cur.execute(f"""
                SELECT birth_year, birth_month, birth_day, birth_hour, hour_confidence, gender,
                       year_pillar, month_pillar, day_pillar, hour_pillar,
                       zodiac, day_stem, day_stem_element,
                       wood, fire, earth, metal, water,
                       day_stem_strength, strength_score, useful_elements, harmful_elements,
                       spouse_star_status, spouse_star_effective, spouse_palace_status, pressure_score,
                       cong_ge_type, shi_shen_structure, shen_sha_data
                FROM profiles WHERE user_id = {get_placeholder()}
            """, (internal_user_id,))
            me_p = cur.fetchone()
        
        if not me_p:
            await calculating_msg.edit_text("找不到用戶資料，請先使用 /start 註冊")
            return ConversationHandler.END
        
        # 轉換為八字數據
        def to_profile(row):
            (
                by, bm, bd, bh, hour_conf, gender,
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
                "shi_shen_list": shi_shen.split(',')[0] if shi_shen else '',
                "hour_confidence": hour_conf,
                "birth_year": by,
                "birth_month": bm,
                "birth_day": bd,
                "birth_hour": bh,
                "shen_sha_names": shen_sha_data.get("names", "無"),
                "shen_sha_bonus": shen_sha_data.get("bonus", 0)
            }
        
        user_bazi = to_profile(me_p)
        user_gender = me_p[5]
        
        # 搜尋最佳匹配
        top_matches = SoulmateFinder.find_top_matches(
            user_bazi, user_gender, start_year, end_year, purpose, limit=10
        )
        
        # 使用計算核心的格式化函數
        formatted_messages = format_find_soulmate_result(top_matches, start_year, end_year, purpose)
        
        # 更新計算完成消息
        await calculating_msg.edit_text(f"✅ 搜尋完成！找到 {len(top_matches)} 個匹配時空。")
        
        # 發送所有格式化消息
        for message in formatted_messages:
            await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"搜尋真命天子失敗: {e}", exc_info=True)
        await calculating_msg.edit_text(f"❌ 搜尋失敗: {str(e)}\n請稍後再試或縮小搜尋範圍。")
    
    return ConversationHandler.END

async def find_soulmate_cancel(update, context):
    """取消真命天子搜尋"""
    await update.message.reply_text("已取消真命天子搜尋。", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
# ========1.7 Find Soulmate 流程函數結束 ========#

# ========1.8 按鈕回調處理函數開始 ========#
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

            cur.execute(f"""
                SELECT id, user_a_accepted, user_b_accepted
                FROM matches
                WHERE (user_a = {get_placeholder()} AND user_b = {get_placeholder()})
                   OR (user_a = {get_placeholder()} AND user_b = {get_placeholder()})
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

                if USE_POSTGRES:
                    cur.execute(f"""
                        INSERT INTO matches (user_a, user_b, score, match_details)
                        VALUES ({get_placeholder()}, {get_placeholder()}, {get_placeholder()}, {get_placeholder()})
                        ON CONFLICT (user_a, user_b) DO NOTHING
                        RETURNING id
                    """, (user_a_id, user_b_id, score, json.dumps(match_result)))
                    result = cur.fetchone()
                    match_id = result[0] if result else None
                else:
                    cur.execute(f"""
                        INSERT OR IGNORE INTO matches (user_a, user_b, score, match_details)
                        VALUES ({get_placeholder()}, {get_placeholder()}, {get_placeholder()}, {get_placeholder()})
                    """, (user_a_id, user_b_id, score, json.dumps(match_result)))
                    match_id = cur.lastrowid

                conn.commit()

                if not match_id:
                    cur.execute(f"""
                        SELECT id FROM matches
                        WHERE user_a = {get_placeholder()} AND user_b = {get_placeholder()}
                    """, (user_a_id, user_b_id))
                    match_row = cur.fetchone()
                    if match_row:
                        match_id = match_row[0]
                    else:
                        await query.edit_message_text("配對記錄創建失敗。")
                        return

            if internal_user_id == user_a_id:
                user_a_accepted = 1
                cur.execute(f"""
                    UPDATE matches
                    SET user_a_accepted = 1
                    WHERE id = {get_placeholder()}
                """, (match_id,))
            else:
                user_b_accepted = 1
                cur.execute(f"""
                    UPDATE matches
                    SET user_b_accepted = 1
                    WHERE id = {get_placeholder()}
                """, (match_id,))

            conn.commit()

            if user_a_accepted == 1 and user_b_accepted == 1:
                cur.execute(
                    f"SELECT score FROM matches WHERE id = {
                        get_placeholder()}", (match_id,))
                score_row = cur.fetchone()
                actual_score = score_row[0] if score_row else 70

                # 使用新的評分閾值
                from new_calculator import THRESHOLD_CONTACT_ALLOWED
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

                # 使用新的評級系統
                from new_calculator import ScoringEngine
                rating = ScoringEngine.get_rating(actual_score)

                message_for_a = (
                    f"{rating} 配對成功！\n\n"
                    f"🎯 配對分數：{actual_score:.1f}分\n"
                    f"📱 對方 Telegram: @{b_username}\n\n"
                    f"💡 溫馨提示：\n"
                    f"• 先打招呼互相認識\n"
                    f"• 分享興趣尋找共同話題\n"
                    f"• 保持尊重，慢慢了解\n\n"
                    f"✨ 祝你們交流愉快！"
                )

                message_for_b = (
                    f"{rating} 配對成功！\n\n"
                    f"🎯 配對分數：{actual_score:.1f}分\n"
                    f"📱 對方 Telegram: @{a_username}\n\n"
                    f"💡 溫馨提示：\n"
                    f"• 先打招呼互相認識\n"
                    f"• 分享興趣尋找共同話題\n"
                    f"• 保持尊重，慢慢了解\n\n"
                    f"✨ 祝你們交流愉快！"
                )

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
                if match_result:
                    ai_prompt = generate_ai_prompt(match_result)

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
# ========1.8 按鈕回調處理函數結束 ========#

# ========1.9 主程序開始 ========#
def main():
    import time

    logger.info("⏳ 等待舊實例清理...")
    time.sleep(1)

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

        # 主註冊流程
        main_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                TERMS_ACCEPTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_terms_acceptance)],
                ASK_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_year)],
                ASK_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_month)],
                ASK_DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_day)],
                ASK_HOUR_KNOWN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_hour_known)],
                ASK_HOUR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_hour)],
                ASK_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gender)],
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
        app.add_handler(CommandHandler("debug", debug_command))
        app.add_handler(CommandHandler("testpair", test_pair_command))
        app.add_handler(CommandHandler("match", match))
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
# ========1.9 主程序結束 ========#

# ========文件信息開始 ========#
"""
文件: bot.py
功能: 主程序文件，包含所有Bot交互邏輯

引用文件: texts.py, new_calculator.py, bazi_soulmate.py
被引用文件: 無
"""
# ========文件信息結束 ========#

# ========目錄開始 ========#
"""
1.1 導入模組 - 導入所有必要的庫和模組（已更新使用 new_calculator）
1.2 配置與初始化 - 日誌配置、路徑檢查、基礎配置
1.3 數據庫工具 - 數據庫連接、初始化、輔助函數
1.4 隱私條款模組 - 隱私條款相關函數
1.5 Bot 註冊流程函數 - 所有註冊流程處理函數（已對齊新接口）
1.6 命令處理函數 - 所有命令處理函數（已對齊新接口）
1.7 Find Soulmate 流程函數 - 真命天子搜尋流程
1.8 按鈕回調處理函數 - 所有按鈕回調處理（已對齊新評分閾值）
1.9 主程序 - Bot啟動和主循環
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
3. 將硬編碼文字替換為從 texts.py 導入的常量：
   - 詢問出生時間文字
   - 大約知道時間描述
   - 時辰未知提示
   - 幫助命令文字
   - AI使用提示
   - 註冊完成提示
4. 添加新的文字常量導入
5. 更新目錄和修正紀錄

錯誤修復：
- 修復了 ask_gender 函數中 json.dumps() 導致的 "name 'json' is not defined" 錯誤
- 該錯誤導致用戶輸入性別後程序崩潰，無法完成註冊

版本 1.2 (2024-02-01)
緊急修復：
1. 添加 import hashlib（解決match按鈕無反應問題）
   - 問題：button_callback函數中缺少hashlib導入，無法生成token驗證
   - 影響：用戶點擊"有興趣"後無反應，無法完成配對
   - 修復：在頂部導入部分添加import hashlib

2. 修復信心度顯示為英文問題
   - 問題：信心度顯示為high, medium, low等英文
   - 影響：用戶體驗不佳，顯示不統一
   - 修復：
     - 數據庫默認值改為"高"
     - ask_hour_known函數中改為"低"
     - ask_hour函數中改為"高"和"中"
     - ask_gender函數中添加信心度映射

3. 優化數據庫操作
   - 問題：start函數中過度使用clear_user_data()
   - 影響：每次start都清除用戶資料，不必要
   - 修復：僅在用戶需要覆蓋時才詢問是否清除

4. 刪除重複提示
   - 問題：註冊完成時顯示重複的操作指南
   - 影響：信息冗餘，用戶體驗差
   - 修復：使用format_profile_result返回的完整內容，不額外添加

版本 1.3 (2024-02-01)
問題修復：
1. 修復信心度數據庫初始化問題
   - 問題：init_db()中hour_confidence默認值仍為'high'
   - 影響：新用戶註冊時信心度可能顯示英文
   - 修復：將數據庫表中的hour_confidence默認值改為'高'

2. 優化start函數邏輯
   - 問題：clear_user_data在start函數中可能被過度調用
   - 修復：只在用戶確認覆蓋時才清除資料

3. 統一section header編號
   - 問題：section header編號不統一
   - 修復：統一使用小數後一位編號（如1.1, 1.2, 2.1）

版本 1.4 (2024-02-01)
重要修改：
1. 修復 testpair 顯示完整分析問題
   - 問題：testpair命令使用format_match_result顯示所有5條消息
   - 修改：保持testpair顯示完整分析，與match區分

2. 優化配對通知流程
   - 問題：match()函數發送完整5條分析給雙方，訊息冗餘
   - 修改：match()只發送【核心分析結果】和【配對資訊】兩條消息
   - 配對成功後不再重複發送詳細分析

3. 修復數據庫查詢錯誤
   - 問題：match()函數中的SQL查詢字段名錯誤（shi_shen_structure拼寫錯誤）
   - 修改：將"shis_shen_structure"改為"shi_shen_structure"

4. 簡化通知邏輯
   - match()函數中只使用format_core_analysis和format_pairing_info
   - 不再發送完整的format_match_result（5條消息）
   - 對方也只收到這兩條基本訊息

5. 數據庫默認值統一為中文
   - 修改init_db()中spouse_star_effective默認值為'未知'
   - 修改init_db()中cong_ge_type默認值為'正常'

影響：
- testpair命令保持顯示完整分析（5條消息）
- match命令只顯示基本分析（2條消息），避免訊息冗餘
- 配對成功後不會重複發送詳細分析
- 數據庫字段統一使用中文默認值

版本 1.5 (2024-02-01) - 本次修改
重要修改：
1. 對齊 new_calculator.py 接口
   - 修改導入語句：從 bazi_calculator 改為 new_calculator
   - 映射錯誤類別：BaziError -> BaziCalculatorError, MatchError -> ScoringEngineError
   - 保持別名兼容：ProfessionalBaziCalculator, MasterBaziMatcher

2. 更新函數調用
   - 八字計算：從 calculate_bazi() 改為 calculate()
   - 配對計算：從 match() 改為 calculate()
   - 使用新的參數格式：添加 gender, hour_confidence 參數

3. 整合審計日誌系統
   - 在 match() 和 test_pair_command() 中添加 audit_log_match()
   - 使用新的模組分數結構

4. 更新評分系統
   - 使用新的評分閾值（SCORING_THRESHOLDS）
   - 使用新的評級系統（ScoringEngine.get_rating()）
   - 更新 debug_command 顯示新評分模組信息

5. 保持向後兼容
   - 數據庫結構不變
   - 用戶界面不變
   - 三個核心功能（match/testpair/findsoulmate）保持正常

錯誤修復：
- 修復 ask_hour() 函數中 TimeProcessor 調用錯誤
- 修復 ask_gender() 函數中 calculate() 參數錯誤
- 修復 match() 函數中評分閾值引用錯誤

影響：
- 完全對齊 new_calculator.py 的新評分引擎
- 保持所有現有功能不變
- 添加審計日誌功能
- 使用更精確的評分系統
"""
# ========修正紀錄結束 ========#