# -*- coding: utf-8 -*-
"""
ALPHA GOLD VIP MONSTER 3 (clean build)

Команды:
  /start, /help
  /status              (показывает настройки — без токена)
  /vip                 (проверка VIP)
  /signal BUY XAUUSD 2030 2015     (VIP или админ) -> отправит в VIP канал
  /setvip 123456       (админ) добавить VIP по user_id
  /delvip 123456       (админ) удалить VIP по user_id
  /ai <текст>          (VIP или админ) AI (если подключен ключ)
"""

import os
import json
import logging
from pathlib import Path
from typing import Set, List, Optional

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, ContextTypes
)

# ----------------- LOGGING -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
log = logging.getLogger("monster3")

# ----------------- FILES -----------------
BASE_DIR = Path(__file__).resolve().parent
VIP_FILE = BASE_DIR / "vip_users.json"

# ----------------- ENV -----------------
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "1111# -*- coding: utf-8 -*-
"""
ALPHA GOLD VIP MONSTER 3 (clean build)

Команды:
  /start, /help
  /status              (показывает настройки — без токена)
  /vip                 (проверка VIP)
  /signal BUY XAUUSD 2030 2015     (VIP или админ) -> отправит в VIP канал
  /setvip 123456       (админ) добавить VIP по user_id
  /delvip 123456       (админ) удалить VIP по user_id
  /ai <текст>          (VIP или админ) AI (если подключен ключ)
"""

import os
import json
import logging
from pathlib import Path
from typing import Set, List, Optional

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, ContextTypes
)

# ----------------- LOGGING -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
log = logging.getLogger("monster3")

# ----------------- FILES -----------------
BASE_DIR = Path(__file__).resolve().parent
VIP_FILE = BASE_DIR / "vip_users.json"

# ----------------- ENV -----------------
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "").strip()
VIP_CHANNEL_ID_RAW = os.getenv("VIP_CHANNEL_ID", "").strip()
VIP_USERS_RAW = os.getenv("VIP_USERS", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

def parse_ids_csv(s: str) -> List[int]:
    out: List[int] = []
    for part in (s or "").replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            pass
    return out

ADMIN_IDS: Set[int] = set(parse_ids_csv(ADMIN_IDS_RAW))

def parse_channel_id(s: str) -> Optional[int]:
    s = (s or "").strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None

VIP_CHANNEL_ID: Optional[int] = parse_channel_id(VIP_CHANNEL_ID_RAW)

# ----------------- VIP STORAGE -----------------
def load_vips() -> Set[int]:
    v: Set[int] = set(parse_ids_csv(VIP_USERS_RAW))
    if VIP_FILE.exists():
        try:
            data = json.loads(VIP_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for x in data:
                    try:
                        v.add(int(x))
                    except Exception:
                        pass
        except Exception as e:
            log.warning("VIP file read error: %s", e)
    return v

def save_vips(vips: Set[int]) -> None:
    try:
        VIP_FILE.write_text(json.dumps(sorted(vips), ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log.warning("VIP file write error: %s", e)

VIP_USERS: Set[int] = load_vips()

# ----------------- HELPERS -----------------
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def is_vip(user_id: int) -> bool:
    return is_admin(user_id) or (user_id in VIP_USERS)

def safe_settings_text() -> str:
    return (
        "⚙️ <b>MONSTER 3 STATUS</b>\n"
        f"• ADMIN_IDS: <code>{', '.join(map(str, sorted(ADMIN_IDS))) if ADMIN_IDS else 'EMPTY'}</code>\n"
        f"• VIP_CHANNEL_ID: <code>{VIP_CHANNEL_ID if VIP_CHANNEL_ID is not None else 'EMPTY'}</code>\n"
        f"• VIP_USERS count: <b>{len(VIP_USERS)}</b>\n"
        f"• AI: <b>{'ON' if OPENAI_API_KEY else 'OFF'}</b>\n"
    )

# ----------------- COMMANDS -----------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    await update.message.reply_text(
        "🚀 ALPHA GOLD VIP MONSTER 3 запущен.\n"
        "Команды: /vip /signal /status /ai",
    )
    log.info("START by %s", uid)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/vip — проверка VIP\n"
        "/signal BUY XAUUSD 2030 2015 — отправить сигнал в VIP-канал (VIP/ADMIN)\n"
        "/status — настройки\n"
        "/setvip 12345 — добавить VIP (ADMIN)\n"
        "/delvip 12345 — удалить VIP (ADMIN)\n"
        "/ai текст — AI (VIP/ADMIN, если подключен ключ)\n"
    )

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(safe_settings_text(), parse_mode=ParseMode.HTML)

async def cmd_vip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if is_vip(uid):
        await update.message.reply_text("🔥 VIP доступ: ✅ РАЗРЕШЕН")
    else:
        await update.message.reply_text("❌ VIP нет. Купи VIP доступ.")

async def cmd_setvip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("⛔ Только админ.")
        return

    if not context.args:
        await update.message.reply_text("Пример: /setvip 123456789")
        return

    try:
        target = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Нужен числовой user_id.")
        return

    VIP_USERS.add(target)
    save_vips(VIP_USERS)
    await update.message.reply_text(f"✅ Добавил VIP: <code>{target}</code>", parse_mode=ParseMode.HTML)

async def cmd_delvip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("⛔ Только админ.")
        return

    if not context.args:
        await update.message.reply_text("Пример: /delvip 123456789")
        return

    try:
        target = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Нужен числовой user_id.")
        return

    if target in VIP_USERS:
        VIP_USERS.remove(target)
        save_vips(VIP_USERS)
        await update.message.reply_text(f"🗑 Удалил VIP: <code>{target}</code>", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("Этого user_id нет в VIP_USERS.")

async def cmd_signal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if not is_vip(uid):
        await update.message.reply_text("❌ VIP нет. Купи VIP доступ.")
        return

    if VIP_CHANNEL_ID is None:
        await update.message.reply_text("⚠️ VIP_CHANNEL_ID не задан в .env")
        return

    if len(context.args) < 4:
        await update.message.reply_text("Формат: /signal BUY XAUUSD 2030 2015")
        return

    action = context.args[0].upper()
    symbol = context.args[1].upper()
    tp = context.args[2]
    sl = context.args[3]

    text = (
        "📊 <b>GOLD SIGNAL</b>\n"
        f"<b>{action}</b> <b>{symbol}</b>\n"
        f"TP: <b>{tp}</b>\n"
        f"SL: <b>{sl}</b>\n"
    )

    await context.bot.send_message(chat_id=VIP_CHANNEL_ID, text=text, parse_mode=ParseMode.HTML)
    await update.message.reply_text("✅ Сигнал отправлен в VIP-канал.")

async def cmd_ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if not is_vip(uid):
        await update.message.reply_text("❌ VIP нет. Купи VIP доступ.")
        return

    prompt = " ".join(context.args).strip()
    if not prompt:
        await update.message.reply_text("Формат: /ai твой вопрос")
        return

    if not OPENAI_API_KEY:
        await update.message.reply_text("🤖 AI не подключен (OPENAI_API_KEY пустой).")
        return

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        # короткий ответ, чтобы быстро работало
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Reply in Russian."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
        )
        answer = resp.choices[0].message.content.strip()
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"⚠️ AI ошибка: {e}")

# ----------------- MAIN -----------------
def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN пустой. Заполни .env")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("vip", cmd_vip))
    app.add_handler(CommandHandler("setvip", cmd_setvip))
    app.add_handler(CommandHandler("delvip", cmd_delvip))
    app.add_handler(CommandHandler("signal", cmd_signal))
    app.add_handler(CommandHandler("ai", cmd_ai))

    log.info("BOT STARTED...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()").strip()
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "").strip()
VIP_CHANNEL_ID_RAW = os.getenv("VIP_CHANNEL_ID", "").strip()
VIP_USERS_RAW = os.getenv("VIP_USERS", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

def parse_ids_csv(s: str) -> List[int]:
    out: List[int] = []
    for part in (s or "").replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            pass
    return out

ADMIN_IDS: Set[int] = set(parse_ids_csv(ADMIN_IDS_RAW))

def parse_channel_id(s: str) -> Optional[int]:
    s = (s or "").strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None

VIP_CHANNEL_ID: Optional[int] = parse_channel_id(VIP_CHANNEL_ID_RAW)

# ----------------- VIP STORAGE -----------------
def load_vips() -> Set[int]:
    v: Set[int] = set(parse_ids_csv(VIP_USERS_RAW))
    if VIP_FILE.exists():
        try:
            data = json.loads(VIP_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for x in data:
                    try:
                        v.add(int(x))
                    except Exception:
                        pass
        except Exception as e:
            log.warning("VIP file read error: %s", e)
    return v

def save_vips(vips: Set[int]) -> None:
    try:
        VIP_FILE.write_text(json.dumps(sorted(vips), ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log.warning("VIP file write error: %s", e)

VIP_USERS: Set[int] = load_vips()

# ----------------- HELPERS -----------------
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def is_vip(user_id: int) -> bool:
    return is_admin(user_id) or (user_id in VIP_USERS)

def safe_settings_text() -> str:
    return (
        "⚙️ <b>MONSTER 3 STATUS</b>\n"
        f"• ADMIN_IDS: <code>{', '.join(map(str, sorted(ADMIN_IDS))) if ADMIN_IDS else 'EMPTY'}</code>\n"
        f"• VIP_CHANNEL_ID: <code>{VIP_CHANNEL_ID if VIP_CHANNEL_ID is not None else 'EMPTY'}</code>\n"
        f"• VIP_USERS count: <b>{len(VIP_USERS)}</b>\n"
        f"• AI: <b>{'ON' if OPENAI_API_KEY else 'OFF'}</b>\n"
    )

# ----------------- COMMANDS -----------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    await update.message.reply_text(
        "🚀 ALPHA GOLD VIP MONSTER 3 запущен.\n"
        "Команды: /vip /signal /status /ai",
    )
    log.info("START by %s", uid)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/vip — проверка VIP\n"
        "/signal BUY XAUUSD 2030 2015 — отправить сигнал в VIP-канал (VIP/ADMIN)\n"
        "/status — настройки\n"
        "/setvip 12345 — добавить VIP (ADMIN)\n"
        "/delvip 12345 — удалить VIP (ADMIN)\n"
        "/ai текст — AI (VIP/ADMIN, если подключен ключ)\n"
    )

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(safe_settings_text(), parse_mode=ParseMode.HTML)

async def cmd_vip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if is_vip(uid):
        await update.message.reply_text("🔥 VIP доступ: ✅ РАЗРЕШЕН")
    else:
        await update.message.reply_text("❌ VIP нет. Купи VIP доступ.")

async def cmd_setvip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("⛔ Только админ.")
        return

    if not context.args:
        await update.message.reply_text("Пример: /setvip 123456789")
        return

    try:
        target = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Нужен числовой user_id.")
        return

    VIP_USERS.add(target)
    save_vips(VIP_USERS)
    await update.message.reply_text(f"✅ Добавил VIP: <code>{target}</code>", parse_mode=ParseMode.HTML)

async def cmd_delvip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("⛔ Только админ.")
        return

    if not context.args:
        await update.message.reply_text("Пример: /delvip 123456789")
        return

    try:
        target = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Нужен числовой user_id.")
        return

    if target in VIP_USERS:
        VIP_USERS.remove(target)
        save_vips(VIP_USERS)
        await update.message.reply_text(f"🗑 Удалил VIP: <code>{target}</code>", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("Этого user_id нет в VIP_USERS.")

async def cmd_signal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if not is_vip(uid):
        await update.message.reply_text("❌ VIP нет. Купи VIP доступ.")
        return

    if VIP_CHANNEL_ID is None:
        await update.message.reply_text("⚠️ VIP_CHANNEL_ID не задан в .env")
        return

    if len(context.args) < 4:
        await update.message.reply_text("Формат: /signal BUY XAUUSD 2030 2015")
        return

    action = context.args[0].upper()
    symbol = context.args[1].upper()
    tp = context.args[2]
    sl = context.args[3]

    text = (
        "📊 <b>GOLD SIGNAL</b>\n"
        f"<b>{action}</b> <b>{symbol}</b>\n"
        f"TP: <b>{tp}</b>\n"
        f"SL: <b>{sl}</b>\n"
    )

    await context.bot.send_message(chat_id=VIP_CHANNEL_ID, text=text, parse_mode=ParseMode.HTML)
    await update.message.reply_text("✅ Сигнал отправлен в VIP-канал.")

async def cmd_ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if not is_vip(uid):
        await update.message.reply_text("❌ VIP нет. Купи VIP доступ.")
        return

    prompt = " ".join(context.args).strip()
    if not prompt:
        await update.message.reply_text("Формат: /ai твой вопрос")
        return

    if not OPENAI_API_KEY:
        await update.message.reply_text("🤖 AI не подключен (OPENAI_API_KEY пустой).")
        return

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        # короткий ответ, чтобы быстро работало
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Reply in Russian."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
        )
        answer = resp.choices[0].message.content.strip()
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"⚠️ AI ошибка: {e}")

# ----------------- MAIN -----------------
def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN пустой. Заполни .env")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("vip", cmd_vip))
    app.add_handler(CommandHandler("setvip", cmd_setvip))
    app.add_handler(CommandHandler("delvip", cmd_delvip))
    app.add_handler(CommandHandler("signal", cmd_signal))
    app.add_handler(CommandHandler("ai", cmd_ai))

    log.info("BOT STARTED...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()