# ========1.1 導入模組開始 ========#
import os
import logging
import asyncio
import json
import hashlib
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool

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

# 導入計算核心
from new_calculator import (
    calculate_match,
    calculate_bazi,
    BaziError,
    MatchError,
    ProfessionalConfig as Config,
    BaziFormatters
)

# 導入 Soulmate 功能
from bazi_soulmate import (
    SoulmateFinder,
    format_find_soulmate_result
)
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

SECRET_KEY = os.getenv("MATCH_SECRET_KEY", "").strip()
DAILY_MATCH_LIMIT = 10

# 分數閾值常量 - 從new_calculator導入
THRESHOLD_WARNING = Config.THRESHOLD_WARNING
THRESHOLD_ACCEPTABLE = Config.THRESHOLD_ACCEPTABLE
THRESHOLD_GOOD_MATCH = Config.THRESHOLD_GOOD_MATCH
THRESHOLD_EXCELLENT_MATCH = Config.THRESHOLD_EXCELLENT_MATCH
THRESHOLD_PERFECT_MATCH = Config.THRESHOLD_PERFECT_MATCH
DEFAULT_LONGITUDE = Config.DEFAULT_LONGITUDE

# 其他常量
TOKEN_EXPIRY_SECONDS = 600  # 配對token有效期10分鐘
MIN_MATCH_SCORE = THRESHOLD_ACCEPTABLE  # 統一使用可接受閾值作為最低分數

# 維護模式標誌
MAINTENANCE_MODE = False

# 管理員用戶ID列表
ADMIN_USER_IDS_STR = os.getenv("ADMIN_USER_IDS", "").strip()
ADMIN_USER_IDS = []
if ADMIN_USER_IDS_STR:
    try:
        ADMIN_USER_IDS = [int(id_str.strip()) for id_str in ADMIN_USER_IDS_STR.split(",") if id_str.strip().isdigit()]
        logger.info(f"載入管理員ID: {ADMIN_USER_IDS}")
    except Exception as e:
        logger.error(f"解析管理員ID失敗: {e}")
        ADMIN_USER_IDS = []

# 數據庫連接池
db_pool = None

# 對話狀態
(
    TERMS_ACCEPTANCE,
    ASK_BASIC_INFO,
    ASK_TIME_CONFIRMATION,
    ASK_HOUR_KNOWN,
    FIND_SOULMATE_RANGE,
    FIND_SOULMATE_PURPOSE,
) = range(6)
# ========1.2 配置與初始化結束 ========#

# ========1.3 維護模式檢查開始 ========#
def check_maintenance(func):
    """1.3.1 維護模式檢查裝飾器 - 用於控制系統維護期間的訪問"""
    async def wrapper(update, context, *args, **kwargs):
        if MAINTENANCE_MODE:
            user_id = update.effective_user.id
            
            if user_id not in ADMIN_USER_IDS:
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
    """1.3.2 檢查是否為管理員"""
    return user_id in ADMIN_USER_IDS

def check_admin_only(func):
    """1.3.3 管理員專用檢查裝飾器"""
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

# ========1.4 數據庫工具開始 ========#
def init_db_pool():
    """1.4.1 初始化數據庫連接池"""
    global db_pool
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # 最小連接數
            10, # 最大連接數
            DATABASE_URL,
            sslmode='require'
        )
        logger.info("數據庫連接池初始化成功")
    except Exception as e:
        logger.error(f"數據庫連接池初始化失敗: {e}")
        raise

def get_db_connection():
    """1.4.2 從連接池獲取數據庫連接"""
    global db_pool
    if db_pool is None:
        init_db_pool()
    
    try:
        conn = db_pool.getconn()
        return conn
    except Exception as e:
        logger.error(f"從連接池獲取連接失敗: {e}")
        # 嘗試直接連接
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            return conn
        except Exception as e2:
            logger.error(f"直接連接也失敗: {e2}")
            raise

def release_db_connection(conn):
    """1.4.3 釋放數據庫連接回連接池"""
    global db_pool
    if db_pool and conn:
        try:
            db_pool.putconn(conn)
        except Exception as e:
            logger.error(f"釋放連接回連接池失敗: {e}")
            try:
                conn.close()
            except:
                pass

def init_db():
    """1.4.4 初始化 PostgreSQL 數據庫"""
    conn = None
    try:
        conn = get_db_connection()
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
            target_gender TEXT DEFAULT '異性',
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
    finally:
        if conn:
            release_db_connection(conn)

def check_daily_limit(user_id: int) -> Tuple[bool, int]:
    """1.4.5 檢查每日配對限制"""
    conn = None
    try:
        conn = get_db_connection()
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
    finally:
        if conn:
            release_db_connection(conn)

def clear_user_data(telegram_id: int) -> bool:
    """1.4.6 清除用戶所有資料"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        conn.autocommit = False
        
        try:
            cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
            user_row = cur.fetchone()
            
            if not user_row:
                conn.commit()
                return True
                
            user_id = user_row[0]
            
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
    finally:
        if conn:
            release_db_connection(conn)

def get_internal_user_id(telegram_id: int) -> Optional[int]:
    """1.4.7 獲取內部用戶ID"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"獲取內部用戶ID失敗: {e}")
        return None
    finally:
        if conn:
            release_db_connection(conn)

def get_telegram_id(internal_user_id: int) -> Optional[int]:
    """1.4.8 獲取Telegram ID"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT telegram_id FROM users WHERE id = %s", (internal_user_id,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"獲取Telegram ID失敗: {e}")
        return None
    finally:
        if conn:
            release_db_connection(conn)

def get_username(internal_user_id: int) -> Optional[str]:
    """1.4.9 獲取用戶名"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE id = %s", (internal_user_id,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"獲取用戶名失敗: {e}")
        return None
    finally:
        if conn:
            release_db_connection(conn)

def _get_profile_base_data(internal_user_id: int, include_username: bool = False) -> Optional[Dict[str, Any]]:
    """1.4.10 獲取個人資料基礎數據 - 內部函數，避免代碼重複"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 構建查詢字段
        if include_username:
            fields = "u.username, "
        else:
            fields = ""
        
        fields += """
            p.birth_year, p.birth_month, p.birth_day, p.birth_hour, p.birth_minute, 
            p.hour_confidence, p.gender, p.target_gender,
            p.year_pillar, p.month_pillar, p.day_pillar, p.hour_pillar,
            p.zodiac, p.day_stem, p.day_stem_element,
            p.wood, p.fire, p.earth, p.metal, p.water,
            p.day_stem_strength, p.strength_score, p.useful_elements, p.harmful_elements,
            p.spouse_star_status, p.spouse_star_effective, p.spouse_palace_status, p.pressure_score,
            p.cong_ge_type, p.shi_shen_structure, p.shen_sha_data
        """
        
        query = f"""
            SELECT {fields}
            FROM users u
            JOIN profiles p ON u.id = p.user_id
            WHERE u.id = %s
        """
        
        cur.execute(query, (internal_user_id,))
        row = cur.fetchone()
        
        if not row:
            return None
        
        # 解析結果
        index = 0
        if include_username:
            username = row[index]
            index += 1
        else:
            username = None
        
        # 修正：正確計算索引位置
        shen_sha_index = 30 if include_username else 29
        shen_sha_json = row[shen_sha_index] if shen_sha_index < len(row) else None
        
        # 安全地解析JSON數據
        shen_sha_data = {"names": "無", "bonus": 0}
        if shen_sha_json:
            try:
                if isinstance(shen_sha_json, str) and shen_sha_json.strip():
                    if shen_sha_json.startswith('{') and shen_sha_json.endswith('}'):
                        shen_sha_data = json.loads(shen_sha_json)
                    else:
                        shen_sha_data = {"names": shen_sha_json, "bonus": 0}
                elif isinstance(shen_sha_json, dict):
                    shen_sha_data = shen_sha_json
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"解析神煞數據失敗: {e}, 數據: {shen_sha_json}, 使用默認值")
                shen_sha_data = {"names": "無", "bonus": 0}
        
        profile_data = {
            "birth_year": row[index],
            "birth_month": row[index + 1],
            "birth_day": row[index + 2],
            "birth_hour": row[index + 3],
            "birth_minute": row[index + 4],
            "hour_confidence": row[index + 5],
            "gender": row[index + 6],
            "target_gender": row[index + 7],
            "year_pillar": row[index + 8],
            "month_pillar": row[index + 9],
            "day_pillar": row[index + 10],
            "hour_pillar": row[index + 11],
            "zodiac": row[index + 12],
            "day_stem": row[index + 13],
            "day_stem_element": row[index + 14],
            "elements": {
                "木": float(row[index + 15] or 0),
                "火": float(row[index + 16] or 0),
                "土": float(row[index + 17] or 0),
                "金": float(row[index + 18] or 0),
                "水": float(row[index + 19] or 0)
            },
            "day_stem_strength": row[index + 20] or "中",
            "strength_score": float(row[index + 21] or 50),
            "useful_elements": (row[index + 22] or "").split(',') if row[index + 22] else [],
            "harmful_elements": (row[index + 23] or "").split(',') if row[index + 23] else [],
            "spouse_star_status": row[index + 24] or "未知",
            "spouse_star_effective": row[index + 25] or "未知",
            "spouse_palace_status": row[index + 26] or "未知",
            "pressure_score": float(row[index + 27] or 0),
            "cong_ge_type": row[index + 28] or "正常",
            "shi_shen_structure": row[index + 29] or "普通結構",
            "shen_sha_names": shen_sha_data.get("names", "無"),
            "shen_sha_bonus": shen_sha_data.get("bonus", 0)
        }
        
        if include_username:
            profile_data["username"] = username
            
        return profile_data
        
    except Exception as e:
        logger.error(f"獲取個人資料失敗: {e}", exc_info=True)
        return None
    finally:
        if conn:
            release_db_connection(conn)

def get_profile_data(internal_user_id: int) -> Optional[Dict[str, Any]]:
    """1.4.11 獲取完整的個人資料數據，用於/profile命令"""
    return _get_profile_base_data(internal_user_id, include_username=True)

def get_raw_profile_for_match(internal_user_id: int) -> Optional[Dict[str, Any]]:
    """1.4.12 獲取原始個人資料數據，用於配對計算"""
    return _get_profile_base_data(internal_user_id, include_username=False)

def check_user_has_profile(telegram_id: int) -> Tuple[bool, Optional[str]]:
    """1.4.13 檢查用戶是否有完整的個人資料"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        user_row = cur.fetchone()
        
        if not user_row:
            return False, "未找到註冊記錄，請先使用 /start 註冊"
        
        user_id = user_row[0]
        
        cur.execute("SELECT COUNT(*) FROM profiles WHERE user_id = %s", (user_id,))
        profile_count = cur.fetchone()[0]
        
        if profile_count == 0:
            return False, "尚未完成個人資料輸入，請使用 /start 完成註冊流程"
        
        cur.execute("""
            SELECT gender, year_pillar 
            FROM profiles WHERE user_id = %s
        """, (user_id,))
        profile_row = cur.fetchone()
        
        if not profile_row:
            return False, "個人資料讀取失敗，請使用 /start 重新註冊"
        
        gender, year_pillar = profile_row
        
        if not gender or gender == "":
            return False, "性別資料缺失，請使用 /start 重新輸入"
        
        if not year_pillar or year_pillar == "":
            return False, "八字數據未生成，請使用 /start 重新計算"
        
        return True, None
        
    except Exception as e:
        logger.error(f"檢查用戶資料失敗: {e}", exc_info=True)
        return False, f"系統錯誤：{str(e)}"
    finally:
        if conn:
            release_db_connection(conn)
# ========1.4 數據庫工具結束 ========#

# ========1.5 隱私條款模組開始 ========#
@check_maintenance
async def show_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.5.1 顯示隱私條款"""
    keyboard = [["✅ 同意並繼續", "❌ 不同意"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True, resize_keyboard=True)

    from texts import PRIVACY_TERMS
    
    await update.message.reply_text(
        PRIVACY_TERMS,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return TERMS_ACCEPTANCE

@check_maintenance
async def handle_terms_acceptance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.5.2 處理隱私條款同意"""
    text = update.message.text.strip()

    if text == "✅ 同意並繼續":
        from texts import BASIC_INFO_FORMAT_TEXT
        await update.message.reply_text(
            "✅ 感謝您同意隱私條款！\n\n"
            "現在開始註冊流程。\n\n"
            f"{BASIC_INFO_FORMAT_TEXT}",
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
# ========1.5 隱私條款模組結束 ========#

# ========1.6 簡化註冊流程開始 ========#
@check_maintenance
async def ask_basic_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.6.1 第一步：詢問所有基本信息"""
    text = update.message.text.strip()
    
    if text == "重新輸入基本信息":
        from texts import BASIC_INFO_FORMAT_TEXT
        await update.message.reply_text(
            "請重新輸入所有基本信息：\n\n" + BASIC_INFO_FORMAT_TEXT,
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_BASIC_INFO
    
    parts = text.split()
    
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
        gender = parts[0]
        year = int(parts[1])
        month = int(parts[2])
        day = int(parts[3])
        hour = int(parts[4])
        minute = int(parts[5]) if len(parts) > 5 else 0
        target_gender = parts[6] if len(parts) > 6 else "異性"
        longitude = float(parts[7]) if len(parts) > 7 else DEFAULT_LONGITUDE
        
        # 驗證輸入
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
        
        # 儲存到用戶數據
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
        
        from texts import CONFIRM_TIME_TEXT
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
async def ask_time_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.6.2 第二步：確認時間精度"""
    text = update.message.text.strip()
    
    if text == "✅ 完全確定（知道確切時間）":
        context.user_data["hour_known"] = "yes"
        context.user_data["hour_confidence"] = "高"
        return await complete_registration(update, context)
        
    elif text == "🤔 大約知道（知道大概時段）":
        context.user_data["hour_known"] = "approximate"
        context.user_data["hour_confidence"] = "中"
        
        from texts import APPROXIMATE_HOUR_DESCRIPTION
        await update.message.reply_text(
            APPROXIMATE_HOUR_DESCRIPTION,
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_HOUR_KNOWN
        
    elif text == "❓ 完全不知道（使用預設時間）":
        context.user_data["hour_known"] = "no"
        context.user_data["hour_confidence"] = "低"
        return await complete_registration(update, context)
        
    elif text == "🔄 重新輸入基本信息":
        from texts import BASIC_INFO_FORMAT_TEXT
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
async def ask_hour_known(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.6.3 處理大約知道的時間描述"""
    description = update.message.text.strip()
    
    estimated_hour = 12
    hour_keywords = {
        "早上": 7, "上午": 9, "中午": 12, "下午": 15,
        "傍晚": 18, "晚上": 20, "深夜": 23, "半夜": 0
    }
    
    for keyword, hour in hour_keywords.items():
        if keyword in description:
            estimated_hour = hour
            break
    
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

async def complete_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.6.4 完成註冊流程"""
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
        bazi = calculate_bazi(
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
    except Exception as e:
        logger.error(f"八字計算未預期錯誤: {e}")
        await update.message.reply_text("八字計算發生未知錯誤，請重新輸入 /start")
        return ConversationHandler.END
    
    telegram_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not username:
        from texts import TELEGRAM_USERNAME_MISSING_TEXT
        await update.message.reply_text(TELEGRAM_USERNAME_MISSING_TEXT)
        return ConversationHandler.END
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
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
        
        year_pillar = bazi.get("year_pillar", "")
        month_pillar = bazi.get("month_pillar", "")
        day_pillar = bazi.get("day_pillar", "")
        hour_pillar = bazi.get("hour_pillar", "")
        zodiac = bazi.get("zodiac", "")
        day_stem = bazi.get("day_stem", "")
        day_stem_element = bazi.get("day_stem_element", "")
        day_stem_strength = bazi.get("day_stem_strength", "中")
        strength_score = bazi.get("strength_score", 50)
        useful_elements = bazi.get("useful_elements", [])
        harmful_elements = bazi.get("harmful_elements", [])
        spouse_star_status = bazi.get("spouse_star_status", "未知")
        spouse_star_effective = bazi.get("spouse_star_effective", "未知")
        spouse_palace_status = bazi.get("spouse_palace_status", "未知")
        pressure_score = bazi.get("pressure_score", 0)
        cong_ge_type = bazi.get("cong_ge_type", "正常")
        shi_shen_structure = bazi.get("shi_shen_structure", "普通結構")
        shen_sha_names = bazi.get("shen_sha_names", "無")
        shen_sha_bonus = bazi.get("shen_sha_bonus", 0)
        
        shen_sha_data = json.dumps({
            "names": shen_sha_names,
            "bonus": shen_sha_bonus
        })
        
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
            year_pillar, month_pillar, day_pillar, hour_pillar,
            zodiac, day_stem, day_stem_element,
            float(elements.get("木", 0)), float(elements.get("火", 0)),
            float(elements.get("土", 0)), float(elements.get("金", 0)),
            float(elements.get("水", 0)), day_stem_strength,
            strength_score, ','.join(useful_elements),
            ','.join(harmful_elements), spouse_star_status,
            spouse_star_effective, spouse_palace_status,
            pressure_score, cong_ge_type,
            shi_shen_structure, shen_sha_data
        ))
        
        conn.commit()
        
        logger.info(f"用戶 {telegram_id} 註冊成功，內部ID: {internal_user_id}")
        
    except Exception as e:
        logger.error(f"數據庫操作失敗: {e}", exc_info=True)
        await update.message.reply_text("資料儲存失敗，請重試", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    finally:
        if conn:
            release_db_connection(conn)
    
    # 準備顯示資料
    bazi_data_for_display = {
        "username": username,
        "year_pillar": year_pillar,
        "month_pillar": month_pillar,
        "day_pillar": day_pillar,
        "hour_pillar": hour_pillar,
        "zodiac": zodiac,
        "day_stem": day_stem,
        "day_stem_element": day_stem_element,
        "gender": gender,
        "cong_ge_type": cong_ge_type,
        "shi_shen_structure": shi_shen_structure,
        "day_stem_strength": day_stem_strength,
        "strength_score": strength_score,
        "useful_elements": useful_elements,
        "harmful_elements": harmful_elements,
        "spouse_star_status": spouse_star_status,
        "spouse_star_effective": spouse_star_effective,
        "spouse_palace_status": spouse_palace_status,
        "pressure_score": pressure_score,
        "shen_sha_names": shen_sha_names,
        "shen_sha_bonus": shen_sha_bonus,
        "elements": elements,
        "hour_confidence": hour_confidence,
        "birth_year": year,
        "birth_month": month,
        "birth_day": day,
        "birth_hour": hour,
        "birth_minute": minute
    }
    
    profile_result = BaziFormatters.format_personal_data(bazi_data_for_display, username)
    
    confidence_map = {
        "高": "（高信心度）",
        "中": "（中信心度，時辰估算）",
        "低": "（低信心度，時辰未知）"
    }
    confidence_text = confidence_map.get(hour_confidence, "（信心度未知）")
    
    await update.message.reply_text(
        f"✅ 註冊完成！資料已儲存。{confidence_text}\n\n{profile_result}\n\n祝你找到好姻緣！💕",
        reply_markup=ReplyKeyboardRemove(),
    )
    
    telegram_id = update.effective_user.id
    
    from texts import FUNCTION_MENU_TEXT, ADMIN_MENU_TEXT
    
    function_menu = FUNCTION_MENU_TEXT.format(target_gender=target_gender)
    
    if is_admin(telegram_id):
        function_menu += ADMIN_MENU_TEXT
    
    await update.message.reply_text(function_menu)
    
    return ConversationHandler.END

@check_maintenance
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.6.5 取消流程"""
    await update.message.reply_text("已取消流程。", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
# ========1.6 簡化註冊流程結束 ========#

# ========1.7 命令處理函數開始 ========#
@check_maintenance
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.7.1 開始命令 - 顯示隱私條款"""
    user = update.effective_user
    
    if MAINTENANCE_MODE and not is_admin(user.id):
        from texts import MAINTENANCE_MODE_TEXT
        await update.message.reply_text(MAINTENANCE_MODE_TEXT)
        return ConversationHandler.END
    
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
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.7.2 幫助命令"""
    from texts import HELP_TEXT
    await update.message.reply_text(HELP_TEXT)

@check_maintenance
async def explain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.7.3 解釋算法命令"""
    from texts import EXPLANATION_TEXT
    await update.message.reply_text(EXPLANATION_TEXT)

@check_maintenance
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.7.4 查看個人資料"""
    telegram_id = update.effective_user.id
    
    has_profile, error_msg = check_user_has_profile(telegram_id)
    if not has_profile:
        await update.message.reply_text(f"{error_msg}")
        return
    
    internal_user_id = get_internal_user_id(telegram_id)
    if not internal_user_id:
        from texts import USER_NOT_FOUND_TEXT
        await update.message.reply_text(USER_NOT_FOUND_TEXT)
        return
    
    profile_data = get_profile_data(internal_user_id)
    
    if not profile_data:
        from texts import PROFILE_INCOMPLETE_TEXT
        await update.message.reply_text(PROFILE_INCOMPLETE_TEXT)
        return
    
    username = profile_data.get("username", "未知用戶")
    
    profile_text = BaziFormatters.format_personal_data(profile_data, username)
    
    import random
    from texts import HEALTH_QUOTES
    health_quote = random.choice(HEALTH_QUOTES)
    
    full_text = f"{profile_text}\n\n💚 {health_quote}"
    
    await update.message.reply_text(full_text)

@check_maintenance
async def match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.7.5 開始配對 - 主要配對功能，尋找合適對象"""
    telegram_id = update.effective_user.id
    
    has_profile, error_msg = check_user_has_profile(telegram_id)
    if not has_profile:
        await update.message.reply_text(f"{error_msg}")
        return
    
    internal_user_id = get_internal_user_id(telegram_id)
    if not internal_user_id:
        from texts import USER_NOT_FOUND_TEXT
        await update.message.reply_text(USER_NOT_FOUND_TEXT)
        return
    
    allowed, match_count = check_daily_limit(internal_user_id)
    if not allowed:
        from texts import DAILY_LIMIT_EXCEEDED_TEXT
        await update.message.reply_text(
            DAILY_LIMIT_EXCEEDED_TEXT.format(
                limit=DAILY_MATCH_LIMIT,
                count=match_count
            )
        )
        return
    
    me_profile = get_raw_profile_for_match(internal_user_id)
    
    if me_profile is None:
        from texts import PROFILE_INCOMPLETE_TEXT
        await update.message.reply_text(PROFILE_INCOMPLETE_TEXT)
        return
    
    my_gender = me_profile.get("gender")
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT target_gender FROM profiles WHERE user_id = %s", (internal_user_id,))
        target_gender_row = cur.fetchone()
        target_gender = target_gender_row[0] if target_gender_row else "異性"
        
        gender_condition = ""
        gender_params = []
        
        if target_gender == "異性":
            if my_gender == "男":
                gender_condition = "p.gender = '女'"
            elif my_gender == "女":
                gender_condition = "p.gender = '男'"
            else:
                gender_condition = "p.gender != %s"
                gender_params.append(my_gender)
        elif target_gender == "同性":
            gender_condition = "p.gender = %s"
            gender_params.append(my_gender)
        elif target_gender in ["男", "女"]:
            gender_condition = "p.gender = %s"
            gender_params.append(target_gender)
        else:
            gender_condition = "p.gender != %s"
            gender_params.append(my_gender)
        
        query_params = [internal_user_id] + gender_params + [internal_user_id, internal_user_id]
        
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
            LIMIT 20
        """
        
        cur.execute(query, query_params)
        rows = cur.fetchall()
        
        logger.info(f"找到 {len(rows)} 個潛在配對對象")
        
    except Exception as e:
        logger.error(f"數據庫查詢失敗: {e}", exc_info=True)
        await update.message.reply_text("配對查詢失敗，請稍後再試。")
        return
    finally:
        if conn:
            release_db_connection(conn)
    
    if not rows:
        from texts import NO_MATCHES_TEXT
        await update.message.reply_text(NO_MATCHES_TEXT)
        return
    
    matches = []
    processed_count = 0
    
    for r in rows:
        processed_count += 1
        other_internal_id = r[0]
        
        try:
            other_profile = {
                "birth_year": r[3],
                "birth_month": r[4],
                "birth_day": r[5],
                "birth_hour": r[6],
                "birth_minute": r[7] if r[7] is not None else 0,
                "hour_confidence": r[8],
                "gender": r[9],
                "year_pillar": r[10],
                "month_pillar": r[11],
                "day_pillar": r[12],
                "hour_pillar": r[13],
                "zodiac": r[14],
                "day_stem": r[15],
                "day_stem_element": r[16],
                "elements": {
                    "木": float(r[17] or 0),
                    "火": float(r[18] or 0),
                    "土": float(r[19] or 0),
                    "金": float(r[20] or 0),
                    "水": float(r[21] or 0)
                },
                "day_stem_strength": r[22] or "中",
                "strength_score": float(r[23] or 50),
                "useful_elements": (r[24] or "").split(',') if r[24] else [],
                "harmful_elements": (r[25] or "").split(',') if r[25] else [],
                "spouse_star_status": r[26] or "未知",
                "spouse_star_effective": r[27] or "未知",
                "spouse_palace_status": r[28] or "未知",
                "pressure_score": float(r[29] or 0),
                "cong_ge_type": r[30] or "正常",
                "shi_shen_structure": r[31] or "普通結構",
                "shen_sha_names": "未知",
                "shen_sha_bonus": 0
            }
            
            if r[32]:
                try:
                    shen_sha_data = json.loads(r[32]) if isinstance(r[32], str) else r[32]
                    other_profile["shen_sha_names"] = shen_sha_data.get("names", "未知")
                    other_profile["shen_sha_bonus"] = shen_sha_data.get("bonus", 0)
                except:
                    pass
            
            match_result = calculate_match(
                me_profile,
                other_profile,
                my_gender,
                other_profile["gender"],
                is_testpair=False
            )
            
            score = match_result.get("score", 0)
            
            if score >= MIN_MATCH_SCORE:
                matches.append({
                    "internal_id": other_internal_id,
                    "telegram_id": r[1],
                    "username": r[2] or "匿名用戶",
                    "profile": other_profile,
                    "score": score,
                    "match_result": match_result
                })
                logger.info(f"找到合格配對: 分數={score:.1f}, 對方ID={other_internal_id}")
            
        except MatchError as e:
            logger.debug(f"配對計算錯誤: {e}")
            continue
        except Exception as e:
            logger.debug(f"其他配對錯誤: {e}")
            continue
    
    logger.info(f"處理了 {processed_count} 個對象，找到 {len(matches)} 個合格配對")
    
    if not matches:
        from texts import NO_QUALIFIED_MATCHES_TEXT
        await update.message.reply_text(NO_QUALIFIED_MATCHES_TEXT)
        return
    
    matches.sort(key=lambda x: x["score"], reverse=True)
    best_match = matches[0]
    other_profile = best_match["profile"]
    match_result = best_match.get("match_result", {})
    
    timestamp = int(datetime.now().timestamp())
    data_str = f"{internal_user_id}_{best_match['internal_id']}_{timestamp}"
    token = hashlib.sha256(
        f"{data_str}_{SECRET_KEY}".encode()).hexdigest()[:12]
    
    accept_data = f"accept_{data_str}_{token}"
    reject_data = f"reject_{data_str}_{token}"
    
    keyboard = [
        [InlineKeyboardButton("✅ 有興趣", callback_data=accept_data),
         InlineKeyboardButton("❌ 略過", callback_data=reject_data)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 儲存當前配對信息到context.user_data
    context.user_data["current_match"] = {
        "user_a": internal_user_id,
        "user_b": best_match["internal_id"],
        "score": best_match["score"],
        "token": token,
        "timestamp": timestamp,
        "match_result": match_result,
        "username_a": update.effective_user.username or "未知用戶",
        "username_b": best_match["username"]
    }
    
    # 不顯示對方username，只顯示基本資料
    user_a_name = "您"
    match_text = BaziFormatters.format_match_result(
        match_result, me_profile, other_profile, 
        user_a_name=user_a_name, 
        user_b_name="對方"
    )
    
    await update.message.reply_text(match_text)
    
    from texts import MATCH_INVITATION_TEXT
    await update.message.reply_text(MATCH_INVITATION_TEXT, reply_markup=reply_markup)
    
    # 關鍵修正：立即通知對方用戶B
    try:
        other_telegram_id = get_telegram_id(best_match["internal_id"])
        if other_telegram_id:
            # 為對方生成專用的按鈕數據
            other_timestamp = int(datetime.now().timestamp())
            other_data_str = f"{internal_user_id}_{best_match['internal_id']}_{other_timestamp}"
            other_token = hashlib.sha256(
                f"{other_data_str}_{SECRET_KEY}".encode()).hexdigest()[:12]
            
            other_accept_data = f"accept_{other_data_str}_{other_token}"
            other_reject_data = f"reject_{other_data_str}_{other_token}"
            
            other_keyboard = [
                [InlineKeyboardButton("✅ 有興趣", callback_data=other_accept_data),
                 InlineKeyboardButton("❌ 略過", callback_data=other_reject_data)]
            ]
            other_reply_markup = InlineKeyboardMarkup(other_keyboard)
            
            # 為對方儲存配對信息到數據庫，以便按鈕回調時讀取
            conn = None
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                
                cur.execute("""
                    INSERT INTO matches (user_a, user_b, score, match_details, user_a_accepted, user_b_accepted)
                    VALUES (%s, %s, %s, %s, 0, 0)
                    ON CONFLICT (user_a, user_b) DO UPDATE SET
                        score = EXCLUDED.score,
                        match_details = EXCLUDED.match_details,
                        created_at = CURRENT_TIMESTAMP
                """, (
                    internal_user_id,  # user_a
                    best_match["internal_id"],  # user_b
                    best_match["score"],
                    json.dumps(match_result)
                ))
                
                conn.commit()
                logger.info(f"為對方儲存配對信息: user_a={internal_user_id}, user_b={best_match['internal_id']}")
                
            except Exception as e:
                logger.error(f"儲存對方配對信息失敗: {e}")
            finally:
                if conn:
                    release_db_connection(conn)
            
            # 通知對方用戶B
            other_user_name = "您"
            other_match_text = BaziFormatters.format_match_result(
                match_result, other_profile, me_profile,  # 注意：這裡交換了位置
                user_a_name=other_user_name, 
                user_b_name="對方"
            )
            
            await context.bot.send_message(
                chat_id=other_telegram_id,
                text=other_match_text
            )
            await context.bot.send_message(
                chat_id=other_telegram_id,
                text=MATCH_INVITATION_TEXT,
                reply_markup=other_reply_markup
            )
            
            logger.info(f"已通知對方用戶B: telegram_id={other_telegram_id}")
        else:
            logger.warning(f"無法獲取對方telegram_id: internal_id={best_match['internal_id']}")
    except Exception as e:
        logger.error(f"通知對方用戶B失敗: {e}")

@check_maintenance
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.7.6 測試命令"""
    await update.message.reply_text("✅ Bot 正在運行中！")

@check_maintenance
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.7.7 清除用戶所有資料"""
    telegram_id = update.effective_user.id

    has_args = context.args is not None and len(context.args) > 0
    
    if has_args and context.args[0] == "confirm":
        success = clear_user_data(telegram_id)
        if success:
            from texts import CLEAR_SUCCESS_TEXT
            await update.message.reply_text(CLEAR_SUCCESS_TEXT)
        else:
            from texts import CLEAR_FAILED_TEXT
            await update.message.reply_text(CLEAR_FAILED_TEXT)
    else:
        from texts import CLEAR_CONFIRM_TEXT
        await update.message.reply_text(CLEAR_CONFIRM_TEXT)

@check_maintenance
async def test_pair_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.7.8 獨立測試任意兩個八字配對"""
    if len(context.args) < 10:
        from texts import TESTPAIR_FORMAT_TEXT
        await update.message.reply_text(TESTPAIR_FORMAT_TEXT)
        return
    
    try:
        year1, month1, day1, hour1 = map(int, context.args[:4])
        gender1 = context.args[4]
        year2, month2, day2, hour2 = map(int, context.args[5:9])
        gender2 = context.args[9] if len(context.args) > 9 else "女"
        
        minute1 = int(context.args[10]) if len(context.args) > 10 else 0
        minute2 = int(context.args[11]) if len(context.args) > 11 else 0
        longitude1 = float(context.args[12]) if len(context.args) > 12 else DEFAULT_LONGITUDE
        longitude2 = float(context.args[13]) if len(context.args) > 13 else DEFAULT_LONGITUDE
        
        if gender1 not in ["男", "女"]:
            from texts import TESTPAIR_INVALID_GENDER_TEXT
            await update.message.reply_text(TESTPAIR_INVALID_GENDER_TEXT)
            return
        
        if gender2 not in ["男", "女"]:
            from texts import TESTPAIR_INVALID_GENDER_TEXT
            await update.message.reply_text(TESTPAIR_INVALID_GENDER_TEXT)
            return
        
        try:
            datetime(year1, month1, day1)
            datetime(year2, month2, day2)
        except ValueError:
            from texts import TESTPAIR_INVALID_DATE_TEXT
            await update.message.reply_text(TESTPAIR_INVALID_DATE_TEXT)
            return
        
        if not 0 <= hour1 <= 23 or not 0 <= hour2 <= 23:
            from texts import TESTPAIR_INVALID_HOUR_TEXT
            await update.message.reply_text(TESTPAIR_INVALID_HOUR_TEXT)
            return
        
        if not 0 <= minute1 <= 59 or not 0 <= minute2 <= 59:
            from texts import TESTPAIR_INVALID_MINUTE_TEXT
            await update.message.reply_text(TESTPAIR_INVALID_MINUTE_TEXT)
            return
        
        if not -180 <= longitude1 <= 180 or not -180 <= longitude2 <= 180:
            from texts import TESTPAIR_INVALID_LONGITUDE_TEXT
            await update.message.reply_text(TESTPAIR_INVALID_LONGITUDE_TEXT)
            return
        
        bazi1_result = calculate_bazi(
            year1, month1, day1, hour1, 
            gender=gender1,
            hour_confidence="高",
            minute=minute1,
            longitude=longitude1
        )
        bazi2_result = calculate_bazi(
            year2, month2, day2, hour2,
            gender=gender2,
            hour_confidence="高",
            minute=minute2,
            longitude=longitude2
        )
        
        if not bazi1_result or not bazi2_result:
            from texts import TESTPAIR_BAZI_CALC_FAILED_TEXT
            await update.message.reply_text(TESTPAIR_BAZI_CALC_FAILED_TEXT)
            return
        
        match_result = calculate_match(bazi1_result, bazi2_result, gender1, gender2, is_testpair=True)
        
        match_text = BaziFormatters.format_test_pair_result(match_result, bazi1_result, bazi2_result)
        
        await update.message.reply_text(match_text)
        
        from texts import TESTPAIR_INDEPENDENT_NOTE_TEXT
        await update.message.reply_text(TESTPAIR_INDEPENDENT_NOTE_TEXT)
        
    except Exception as e:
        logger.error(f"測試配對失敗: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 測試失敗: {str(e)}\n請檢查輸入格式是否正確。")

@check_maintenance
@check_admin_only
async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.7.9 維護模式命令 - 僅管理員可用"""
    global MAINTENANCE_MODE
    
    if context.args and context.args[0] == "on":
        MAINTENANCE_MODE = True
        from texts import MAINTENANCE_ON_TEXT
        await update.message.reply_text(MAINTENANCE_ON_TEXT)
    elif context.args and context.args[0] == "off":
        MAINTENANCE_MODE = False
        from texts import MAINTENANCE_OFF_TEXT
        await update.message.reply_text(MAINTENANCE_OFF_TEXT)
    else:
        from texts import MAINTENANCE_STATUS_TEMPLATE
        status = "🔧 **開啟**" if MAINTENANCE_MODE else "✅ **關閉**"
        await update.message.reply_text(
            MAINTENANCE_STATUS_TEMPLATE.format(status=status)
        )
# ========1.7 命令處理函數結束 ========#

# ========1.8 Find Soulmate 流程函數開始 ========#
@check_maintenance
async def find_soulmate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.8.1 開始真命天子搜尋"""
    telegram_id = update.effective_user.id
    
    has_profile, error_msg = check_user_has_profile(telegram_id)
    if not has_profile:
        await update.message.reply_text(f"{error_msg}")
        return ConversationHandler.END
    
    internal_user_id = get_internal_user_id(telegram_id)
    
    if not internal_user_id:
        from texts import USER_NOT_FOUND_TEXT
        await update.message.reply_text(USER_NOT_FOUND_TEXT)
        return ConversationHandler.END
    
    allowed, match_count = check_daily_limit(internal_user_id)
    if not allowed:
        from texts import DAILY_LIMIT_EXCEEDED_TEXT
        await update.message.reply_text(
            DAILY_LIMIT_EXCEEDED_TEXT.format(
                limit=DAILY_MATCH_LIMIT,
                count=match_count
            )
        )
        return ConversationHandler.END
    
    from texts import FIND_SOULMATE_WELCOME_TEXT
    await update.message.reply_text(FIND_SOULMATE_WELCOME_TEXT)
    
    return FIND_SOULMATE_RANGE

@check_maintenance
async def find_soulmate_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.8.2 處理搜尋年份範圍"""
    text = update.message.text.strip()
    
    if '-' not in text:
        from texts import FIND_SOULMATE_INVALID_RANGE_TEXT
        await update.message.reply_text(FIND_SOULMATE_INVALID_RANGE_TEXT)
        return FIND_SOULMATE_RANGE
    
    try:
        start_year, end_year = map(int, text.split('-'))
        
        if start_year < 1900 or end_year > datetime.now().year:
            from texts import FIND_SOULMATE_YEAR_RANGE_ERROR_TEXT
            await update.message.reply_text(
                FIND_SOULMATE_YEAR_RANGE_ERROR_TEXT.format(
                    current_year=datetime.now().year
                )
            )
            return FIND_SOULMATE_RANGE
        
        if end_year - start_year > 20:
            from texts import FIND_SOULMATE_RANGE_TOO_LARGE_TEXT
            await update.message.reply_text(FIND_SOULMATE_RANGE_TOO_LARGE_TEXT)
            return FIND_SOULMATE_RANGE
        
        if start_year >= end_year:
            from texts import FIND_SOULMATE_START_END_ERROR_TEXT
            await update.message.reply_text(FIND_SOULMATE_START_END_ERROR_TEXT)
            return FIND_SOULMATE_RANGE
        
        date_count = (end_year - start_year + 1) * 365
        if date_count > 10000:
            from texts import FIND_SOULMATE_TOO_MANY_DATES_TEXT
            await update.message.reply_text(
                FIND_SOULMATE_TOO_MANY_DATES_TEXT.format(date_count=date_count)
            )
            return FIND_SOULMATE_RANGE
        
        context.user_data["soulmate_range"] = (start_year, end_year)
        
        keyboard = [["💖 尋找正緣", "🤝 事業合夥"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        from texts import FIND_SOULMATE_CONFIRM_RANGE_TEXT
        await update.message.reply_text(
            FIND_SOULMATE_CONFIRM_RANGE_TEXT.format(
                start_year=start_year,
                end_year=end_year,
                date_count=date_count
            ),
            reply_markup=reply_markup
        )
        
        return FIND_SOULMATE_PURPOSE
        
    except ValueError:
        from texts import FIND_SOULMATE_INVALID_RANGE_TEXT
        await update.message.reply_text(FIND_SOULMATE_INVALID_RANGE_TEXT)
        return FIND_SOULMATE_RANGE
    except Exception as e:
        logger.error(f"處理年份範圍失敗: {e}")
        await update.message.reply_text("處理失敗，請重新輸入")
        return FIND_SOULMATE_RANGE

@check_maintenance
async def find_soulmate_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.8.3 處理搜尋目的並開始計算"""
    text = update.message.text.strip()
    
    purpose_map = {
        "💖 尋找正緣": "正緣",
        "🤝 事業合夥": "合夥"
    }
    
    if text not in purpose_map:
        from texts import FIND_SOULMATE_PURPOSE_PROMPT_TEXT
        await update.message.reply_text(FIND_SOULMATE_PURPOSE_PROMPT_TEXT)
        return FIND_SOULMATE_PURPOSE
    
    purpose = purpose_map[text]
    start_year, end_year = context.user_data.get("soulmate_range", (1990, 1999))
    
    date_count = (end_year - start_year + 1) * 365
    
    from texts import FIND_SOULMATE_CALCULATING_TEXT
    calculating_msg = await update.message.reply_text(
        FIND_SOULMATE_CALCULATING_TEXT.format(
            start_year=start_year,
            end_year=end_year,
            date_count=date_count
        ),
        reply_markup=ReplyKeyboardRemove()
    )
    
    try:
        telegram_id = update.effective_user.id
        internal_user_id = get_internal_user_id(telegram_id)
        
        user_profile = get_raw_profile_for_match(internal_user_id)
        
        if not user_profile:
            from texts import PROFILE_INCOMPLETE_TEXT
            await update.message.reply_text(PROFILE_INCOMPLETE_TEXT)
            return ConversationHandler.END
        
        user_gender = user_profile.get("gender")
        
        logger.info(f"開始真命天子搜尋：範圍{start_year}-{end_year}, 目的{purpose}, 性別{user_gender}")
        
        top_matches = SoulmateFinder.find_top_matches(
            user_profile, user_gender, start_year, end_year, purpose, limit=5
        )
        
        logger.info(f"真命天子搜尋完成：找到{len(top_matches)}個匹配")
        
        if not top_matches:
            from texts import FIND_SOULMATE_NO_RESULTS_TEXT
            await update.message.reply_text(
                FIND_SOULMATE_NO_RESULTS_TEXT.format(
                    start_year=start_year,
                    end_year=end_year
                )
            )
            return ConversationHandler.END
        
        from texts import FIND_SOULMATE_COMPLETE_TEXT
        await update.message.reply_text(
            FIND_SOULMATE_COMPLETE_TEXT.format(count=len(top_matches))
        )
        
        formatted_message = format_find_soulmate_result(top_matches, start_year, end_year, purpose)
        
        await update.message.reply_text(formatted_message)
        
    except Exception as e:
        logger.error(f"搜尋真命天子失敗: {e}", exc_info=True)
        from texts import FIND_SOULMATE_SEARCH_ERROR_TEXT
        await update.message.reply_text(
            FIND_SOULMATE_SEARCH_ERROR_TEXT.format(error=str(e))
        )
    
    return ConversationHandler.END

@check_maintenance
async def find_soulmate_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.8.4 取消真命天子搜尋"""
    from texts import FIND_SOULMATE_CANCELLED_TEXT
    await update.message.reply_text(FIND_SOULMATE_CANCELLED_TEXT, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
# ========1.8 Find Soulmate 流程函數結束 ========#

# ========1.9 按鈕回調處理函數開始 ========#
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.9.1 處理按鈕回調 - 修正配對邏輯"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    telegram_id = query.from_user.id
    internal_user_id = get_internal_user_id(telegram_id)
    
    if not internal_user_id:
        await query.edit_message_text("無法識別用戶，請重新註冊 /start。")
        return
    
    if data.startswith("accept_"):
        parts = data.split("_")
        if len(parts) != 5:
            from texts import MATCH_INVALID_TEXT
            await query.edit_message_text(MATCH_INVALID_TEXT)
            return
        
        _, user_a_str, user_b_str, timestamp_str, token = parts
        data_str = f"{user_a_str}_{user_b_str}_{timestamp_str}"
        expected_token = hashlib.sha256(
            f"{data_str}_{SECRET_KEY}".encode()).hexdigest()[:12]
        
        if token != expected_token:
            from texts import MATCH_INVALID_TEXT
            await query.edit_message_text(MATCH_INVALID_TEXT)
            return
        
        try:
            timestamp = int(timestamp_str)
            current_time = datetime.now().timestamp()
            if current_time - timestamp > TOKEN_EXPIRY_SECONDS:
                from texts import MATCH_EXPIRED_TEXT
                await query.edit_message_text(MATCH_EXPIRED_TEXT)
                return
        except BaseException:
            from texts import MATCH_INVALID_TEXT
            await query.edit_message_text(MATCH_INVALID_TEXT)
            return
        
        user_a_id = int(user_a_str)
        user_b_id = int(user_b_str)
        
        # 關鍵修正：正確識別當前用戶的角色
        is_user_a = (internal_user_id == user_a_id)
        
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # 從數據庫讀取配對信息
            cur.execute("""
                SELECT id, user_a_accepted, user_b_accepted, score, match_details
                FROM matches
                WHERE (user_a = %s AND user_b = %s)
                   OR (user_a = %s AND user_b = %s)
            """, (user_a_id, user_b_id, user_b_id, user_a_id))
            
            match_row = cur.fetchone()
            
            if not match_row:
                from texts import MATCH_INVALID_TEXT
                await query.edit_message_text(MATCH_INVALID_TEXT)
                return
            
            match_id, user_a_accepted, user_b_accepted, match_score, match_details_str = match_row
            
            logger.info(f"處理接受按鈕: match_id={match_id}, 當前用戶是user_a={is_user_a}, 當前狀態: A接受={user_a_accepted}, B接受={user_b_accepted}")
            
            # 更新接受狀態
            if is_user_a:
                user_a_accepted = 1
                cur.execute("""
                    UPDATE matches
                    SET user_a_accepted = 1
                    WHERE id = %s
                """, (match_id,))
                logger.info(f"用戶A接受配對: user_a_id={user_a_id}")
            else:
                user_b_accepted = 1
                cur.execute("""
                    UPDATE matches
                    SET user_b_accepted = 1
                    WHERE id = %s
                """, (match_id,))
                logger.info(f"用戶B接受配對: user_b_id={user_b_id}")
            
            conn.commit()
            
            # 獲取用戶信息
            a_telegram_id = get_telegram_id(user_a_id)
            b_telegram_id = get_telegram_id(user_b_id)
            a_username = get_username(user_a_id) or "未設定用戶名"
            b_username = get_username(user_b_id) or "未設定用戶名"
            
            # 檢查是否雙方都接受
            if user_a_accepted == 1 and user_b_accepted == 1:
                # 雙方都接受，交換username
                if match_score < THRESHOLD_ACCEPTABLE:
                    from texts import SCORE_TOO_LOW_TEXT
                    await query.edit_message_text(
                        SCORE_TOO_LOW_TEXT.format(
                            score=match_score,
                            threshold=THRESHOLD_ACCEPTABLE
                        )
                    )
                    return
                
                current_user_username = a_username if is_user_a else b_username
                other_user_username = b_username if is_user_a else a_username
                
                from new_calculator import ScoringEngine
                rating = ScoringEngine.get_rating(match_score)
                
                # 修正：配對成功消息只顯示username，不顯示詳細分析
                from texts import MATCH_SUCCESS_TEXT_TEMPLATE, MATCH_SUCCESS_NO_USERNAME_TEXT
                match_text = MATCH_SUCCESS_TEXT_TEMPLATE.format(
                    rating=rating,
                    score=match_score,
                    username=other_user_username
                )
                
                if other_user_username == "未設定用戶名":
                    match_text += MATCH_SUCCESS_NO_USERNAME_TEXT
                
                await query.edit_message_text(match_text)
                
                # 通知對方
                try:
                    other_telegram_id = b_telegram_id if is_user_a else a_telegram_id
                    
                    other_text = MATCH_SUCCESS_TEXT_TEMPLATE.format(
                        rating=rating,
                        score=match_score,
                        username=current_user_username
                    )
                    
                    if current_user_username == "未設定用戶名":
                        other_text += MATCH_SUCCESS_NO_USERNAME_TEXT
                    
                    await context.bot.send_message(chat_id=other_telegram_id, text=other_text)
                    logger.info(f"已通知對方配對成功: other_telegram_id={other_telegram_id}")
                    
                except Exception as e:
                    logger.error(f"無法通知對方: {e}")
            else:
                # 只有一方接受
                from texts import MATCH_WAITING_TEXT
                await query.edit_message_text(MATCH_WAITING_TEXT)
                logger.info(f"用戶接受配對，等待對方: 用戶{'A' if is_user_a else 'B'}")
                
        except Exception as e:
            logger.error(f"處理接受按鈕失敗: {e}", exc_info=True)
            await query.edit_message_text("處理失敗，請稍後再試。")
        finally:
            if conn:
                release_db_connection(conn)
    
    elif data.startswith("reject_"):
        from texts import MATCH_REJECTED_TEXT
        await query.edit_message_text(MATCH_REJECTED_TEXT)
        logger.info(f"用戶略過配對: user_id={internal_user_id}")
# ========1.9 按鈕回調處理函數結束 ========#

# ========1.10 管理員專用命令開始 ========#
@check_maintenance
@check_admin_only
async def admin_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.10.1 運行管理員測試"""
    try:
        from texts import ADMIN_TEST_START_TEXT
        await update.message.reply_text(ADMIN_TEST_START_TEXT)
        
        from admin_service import AdminService
        admin_service = AdminService()
        results = await admin_service.run_admin_tests()
        formatted = admin_service.format_test_results_pro(results)
        
        if len(formatted) > 4000:
            parts = [formatted[i:i+4000] for i in range(0, len(formatted), 4000)]
            for part in parts:
                await update.message.reply_text(part)
        else:
            await update.message.reply_text(formatted)
            
    except ImportError as e:
        logger.error(f"導入管理員服務失敗: {e}")
        from texts import ADMIN_TEST_IMPORT_ERROR_TEXT
        await update.message.reply_text(ADMIN_TEST_IMPORT_ERROR_TEXT.format(error=str(e)))
    except Exception as e:
        logger.error(f"管理員測試失敗: {e}", exc_info=True)
        from texts import ADMIN_TEST_FAILED_TEXT
        await update.message.reply_text(ADMIN_TEST_FAILED_TEXT.format(error=str(e)))

@check_maintenance
@check_admin_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.10.2 查看系統統計"""
    try:
        from texts import STATS_FETCHING_TEXT
        await update.message.reply_text(STATS_FETCHING_TEXT)
        
        from admin_service import AdminService
        admin_service = AdminService()
        stats = await admin_service.get_system_stats()
        formatted = admin_service.format_system_stats(stats)
        
        await update.message.reply_text(formatted)
            
    except ImportError as e:
        logger.error(f"導入管理員服務失敗: {e}")
        from texts import STATS_IMPORT_ERROR_TEXT
        await update.message.reply_text(STATS_IMPORT_ERROR_TEXT.format(error=str(e)))
    except Exception as e:
        logger.error(f"獲取統計失敗: {e}", exc_info=True)
        from texts import STATS_FAILED_TEXT
        await update.message.reply_text(STATS_FAILED_TEXT.format(error=str(e)))

@check_maintenance
@check_admin_only
async def quick_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.10.3 運行一鍵快速測試"""
    try:
        from texts import QUICK_TEST_START_TEXT
        await update.message.reply_text(QUICK_TEST_START_TEXT)
        
        from admin_service import AdminService
        admin_service = AdminService()
        results = await admin_service.run_quick_test()
        formatted = admin_service.format_quick_test_results(results)
        
        await update.message.reply_text(formatted)
            
    except ImportError as e:
        logger.error(f"導入管理員服務失敗: {e}")
        from texts import ADMIN_TEST_IMPORT_ERROR_TEXT
        await update.message.reply_text(ADMIN_TEST_IMPORT_ERROR_TEXT.format(error=str(e)))
    except AttributeError as e:
        logger.error(f"快速測試方法缺失: {e}")
        from texts import QUICK_TEST_METHOD_MISSING_TEXT
        await update.message.reply_text(QUICK_TEST_METHOD_MISSING_TEXT.format(error=str(e)))
    except Exception as e:
        logger.error(f"快速測試失敗: {e}", exc_info=True)
        from texts import QUICK_TEST_FAILED_TEXT
        await update.message.reply_text(QUICK_TEST_FAILED_TEXT.format(error=str(e)))

@check_maintenance
@check_admin_only  
async def list_tests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """1.10.4 列出所有測試案例"""
    try:
        from admin_service import ADMIN_TEST_CASES
        text = "📋 可用測試案例：\n\n"
        
        for i, test in enumerate(ADMIN_TEST_CASES, 1):
            text += f"{i}. {test['description']}\n"
            if len(text) > 3500:
                await update.message.reply_text(text)
                text = ""
        
        if text:
            await update.message.reply_text(text)
            
    except ImportError as e:
        logger.error(f"導入測試案例失敗: {e}")
        from texts import LIST_TESTS_IMPORT_ERROR_TEXT
        await update.message.reply_text(LIST_TESTS_IMPORT_ERROR_TEXT.format(error=str(e)))
    except Exception as e:
        logger.error(f"列出測試失敗: {e}", exc_info=True)
        from texts import LIST_TESTS_FAILED_TEXT
        await update.message.reply_text(LIST_TESTS_FAILED_TEXT.format(error=str(e)))
# ========1.10 管理員專用命令結束 ========#

# ========1.11 主程序開始 ========#
def main():
    import time
    
    logger.info("⏳ 等待舊實例清理...")
    time.sleep(3)
    
    init_db_pool()
    init_db()
    
    token = os.getenv("BOT_TOKEN", "").strip()
    
    if not token:
        logger.error("錯誤: BOT_TOKEN 環境變數未設定！")
        raise ValueError("BOT_TOKEN 未設定")
    
    token = token.replace('\n', '').replace('\r', '')
    
    try:
        app = Application.builder().token(token).build()
        
        async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        app.add_handler(main_conv_handler)
        app.add_handler(soulmate_conv_handler)
        
        # 基本命令
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("profile", profile))
        app.add_handler(CommandHandler("explain", explain_command))
        app.add_handler(CommandHandler("test", test_command))
        app.add_handler(CommandHandler("clear", clear_command))
        app.add_handler(CommandHandler("testpair", test_pair_command))
        app.add_handler(CommandHandler("match", match))
        
        # 管理員命令
        app.add_handler(CommandHandler("maintenance", maintenance_command))
        app.add_handler(CommandHandler("admintest", admin_test_command))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CommandHandler("quicktest", quick_test_command))
        app.add_handler(CommandHandler("listtests", list_tests_command))
        
        # 回調處理
        app.add_handler(CallbackQueryHandler(button_callback))
        
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            close_loop=False
        )
        
    except Exception as e:
        logger.error(f"❌ Bot 啟動失敗: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()
# ========1.11 主程序結束 ========#

# 🔖 文件信息
# 引用文件：new_calculator.py, bazi_soulmate.py, texts.py, admin_service.py
# 被引用文件：無

# 🔖 Section目錄
# 1.1 導入模組
# 1.2 配置與初始化
# 1.3 維護模式檢查
# 1.4 數據庫工具
# 1.5 隱私條款模組
# 1.6 簡化註冊流程
# 1.7 命令處理函數
# 1.8 Find Soulmate 流程函數
# 1.9 按鈕回調處理函數
# 1.10 管理員專用命令
# 1.11 主程序

# 🔖 修正紀錄
# 2026-02-08: 徹底修復配對流程，確保用戶A按/match後立即通知用戶B
# 2026-02-08: 修復按鈕回調邏輯，確保雙方都按"有興趣"時正確交換username
# 2026-02-08: 修正按鈕數據生成邏輯，為雙方生成不同的按鈕數據
# 2026-02-08: 在match函數中立即儲存配對信息到數據庫，確保按鈕回調可讀取
# 2026-02-08: 修正配對成功消息格式，移除詳細配對分析，只顯示對方username
# 2026-02-08: 將所有長文本搬遷到texts.py，保持代碼整潔
# 2026-02-08: 保持所有現有功能不變，僅修正核心問題
# 2026-02-08: 徹底解決find_soulmate問題，確保至少找到一個80分以上配對
