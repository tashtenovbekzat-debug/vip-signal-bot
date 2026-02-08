import os
import time
import sqlite3
import threading
from datetime import datetime, timedelta

import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ================== НАСТРОЙКИ ==================
# BOT_TOKEN — ТОЛЬКО в Railway Variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in Railway Variables")

# Можно оставить так (как у тебя), это ок:
ADMIN_ID = 8394704301
VIP_CHANNEL = -1003735072360

# Тарифы (дни)
VIP1_DAYS = 30
VIP3_DAYS = 90

PRICE_TEXT = (
    "💎 <b>ALPHA GOLD VIP</b>\n\n"
    "1 месяц — <b>200$</b>\n"
    "3 месяца — <b>500$</b>\n\n"
    "Нажми: ✅ <b>Я оплатил</b>"
)

WATERMARK = "© <b>ALPHA GOLD PRIVATE</b> • Elite System"
DEFAULT_TF = "M5"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ================== БАЗА (SQLite) ==================
DB_PATH = "alphagold.db"

def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    con = db()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vip_subscriptions (
            user_id INTEGER PRIMARY KEY,
            expires_at INTEGER NOT NULL,
            plan TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)
    con.commit()
    con.close()

init_db()

# ================== SIGNAL QUEUE ==================
pending_signals = {}  # sig_id -> text

def new_sig_id() -> str:
    return str(int(time.time() * 1000))

# ================== КНОПКИ ==================
def main_menu(user_id: int):
    is_admin = (user_id == ADMIN_ID)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Цена VIP"))
    kb.add(KeyboardButton("✅ Я оплатил"))
    kb.add(KeyboardButton("🆔 Мой ID"))
    kb.add(KeyboardButton("⏳ Мой VIP срок"))

    if is_admin:
        kb.add(KeyboardButton("🧪 L1 Test Signal"))
        kb.add(KeyboardButton("📝 Создать сигнал"))
        kb.add(KeyboardButton("📌 Админ: команды"))
    return kb

# ================== START / BASIC ==================
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>ALPHA GOLD VIP</b> 🔥\n\n"
        "Добро пожаловать в закрытую VIP систему.\n"
        "Выбери действие ниже:",
        reply_markup=main_menu(message.from_user.id)
    )

@bot.message_handler(commands=["ping"])
def ping(message):
    bot.reply_to(message, "pong ✅ Бот работает")

@bot.message_handler(commands=["id"])
def cmd_id(message):
    bot.send_message(message.chat.id, f"Твой ID: <code>{message.from_user.id}</code>")

@bot.message_handler(func=lambda m: m.text == "🆔 Мой ID")
def btn_id(message):
    cmd_id(message)

@bot.message_handler(func=lambda m: m.text == "💰 Цена VIP")
def btn_price(message):
    bot.send_message(message.chat.id, PRICE_TEXT)

# ================== VIP: Проверка срока ==================
def get_sub(user_id: int):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT expires_at, plan FROM vip_subscriptions WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    con.close()
    return row

@bot.message_handler(commands=["myvip"])
def myvip_cmd(message):
    row = get_sub(message.from_user.id)
    if not row:
        bot.send_message(message.chat.id, "У тебя нет активного VIP доступа.")
        return

    expires_at, plan = row
    dt = datetime.utcfromtimestamp(expires_at)
    bot.send_message(
        message.chat.id,
        f"👑 VIP: <b>{plan}</b>\n"
        f"⏳ До: <b>{dt} UTC</b>\n\n"
        f"{WATERMARK}"
    )

@bot.message_handler(func=lambda m: m.text == "⏳ Мой VIP срок")
def myvip_btn(message):
    myvip_cmd(message)

# ================== ОПЛАТА (заявка админу) ==================
@bot.message_handler(func=lambda m: m.text == "✅ Я оплатил")
def paid(message):
    user_id = message.from_user.id
    username = message.from_user.username or "-"

    text = (
        "💸 <b>Новая заявка (оплата)</b>\n\n"
        f"ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n\n"
        "Выдай доступ командой:\n"
        f"<code>/vip1 {user_id}</code>  (30 дней)\n"
        f"<code>/vip3 {user_id}</code>  (90 дней)\n\n"
        f"{WATERMARK}"
    )

    bot.send_message(ADMIN_ID, text)
    bot.send_message(message.chat.id, "⏳ Заявка отправлена админу. Ожидай доступ.")

# ================== VIP: Выдача/удаление ==================
def save_subscription(user_id: int, days: int, plan: str):
    expires_at = int((datetime.utcnow() + timedelta(days=days)).timestamp())
    con = db()
    cur = con.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO vip_subscriptions(user_id, expires_at, plan, created_at)
        VALUES(?,?,?,?)
    """, (user_id, expires_at, plan, int(time.time())))
    con.commit()
    con.close()
    return expires_at

def grant_access(user_id: int, days: int, plan: str):
    # одноразовая ссылка
    link = bot.create_chat_invite_link(chat_id=VIP_CHANNEL, member_limit=1)
    expires_at = save_subscription(user_id, days, plan)

    dt = datetime.utcfromtimestamp(expires_at)

    bot.send_message(
        user_id,
        "✅ <b>Доступ активирован</b>\n"
        f"Тариф: <b>{plan}</b>\n"
        f"Срок: <b>{days} дней</b>\n"
        f"До: <b>{dt} UTC</b>\n\n"
        "Ссылка в VIP (одноразовая):\n"
        f"{link.invite_link}\n\n"
        f"{WATERMARK}"
    )

def revoke_access(user_id: int, reason: str = "VIP закончился"):
    # удалить из канала
    try:
        bot.ban_chat_member(VIP_CHANNEL, user_id)
        bot.unban_chat_member(VIP_CHANNEL, user_id)  # чтобы мог снова зайти после продления
    except Exception:
        pass

    # удалить из базы
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM vip_subscriptions WHERE user_id=?", (user_id,))
    con.commit()
    con.close()

    # уведомить
    try:
        bot.send_message(user_id, f"⏳ {reason}\nПродлить доступ можно через бота.\n\n{WATERMARK}")
    except Exception:
        pass

# Админ: /vip1 id
@bot.message_handler(commands=["vip1"])
def vip1_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Ты не админ ❌")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Формат: <code>/vip1 123456789</code>")
        return

    user_id = int(parts[1])
    grant_access(user_id, VIP1_DAYS, "VIP 1 MONTH")
    bot.send_message(message.chat.id, f"✅ Выдан VIP1 на {VIP1_DAYS} дней пользователю <code>{user_id}</code>")

# Админ: /vip3 id
@bot.message_handler(commands=["vip3"])
def vip3_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Ты не админ ❌")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Формат: <code>/vip3 123456789</code>")
        return

    user_id = int(parts[1])
    grant_access(user_id, VIP3_DAYS, "VIP 3 MONTHS")
    bot.send_message(message.chat.id, f"✅ Выдан VIP3 на {VIP3_DAYS} дней пользователю <code>{user_id}</code>")

# Админ: /ban id
@bot.message_handler(commands=["ban"])
def ban_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Ты не админ ❌")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Формат: <code>/ban 123456789</code>")
        return
    user_id = int(parts[1])
    revoke_access(user_id, reason="🚫 Доступ отключён админом")
    bot.send_message(message.chat.id, f"Готово. Пользователь <code>{user_id}</code> удалён/отключён ✅")

# ================== AUTO EXPIRE (каждые 10 минут) ==================
def expire_loop():
    while True:
        try:
            now = int(time.time())
            con = db()
            cur = con.cursor()
            cur.execute("SELECT user_id, expires_at FROM vip_subscriptions")
            rows = cur.fetchall()
            con.close()

            for user_id, expires_at in rows:
                if expires_at <= now:
                    revoke_access(int(user_id), reason="⏳ VIP доступ закончился")
        except Exception:
            pass

        time.sleep(600)

threading.Thread(target=expire_loop, daemon=True).start()

# ================== SIGNAL ENGINE (ручной + подтверждение) ==================
def build_signal_text(symbol: str, direction: str, entry: str, tp1: str, tp2: str, sl: str,
                      tf: str = DEFAULT_TF, confidence: str = "88-92%", mode: str = "SAFE ELITE") -> str:
    d = (direction or "").upper().strip()
    if d not in ("BUY", "SELL"):
        d = "BUY"
    dot = "🟢" if d == "BUY" else "🔴"

    return (
        "👑 <b>ALPHA GOLD VIP SIGNAL</b>\n\n"
        f"📊 <b>{symbol}</b>\n"
        f"Signal: <b>{d}</b> {dot}\n"
        f"TF: <b>{tf}</b>\n\n"
        f"Entry: <b>{entry}</b>\n"
        f"TP1: <b>{tp1}</b>\n"
        f"TP2: <b>{tp2}</b>\n"
        f"SL: <b>{sl}</b>\n\n"
        f"Mode: <b>{mode}</b>\n"
        f"Confidence: <b>{confidence}</b>\n\n"
        f"{WATERMARK}"
    )

def send_to_admin_for_approve(text_vip: str, title: str = "SIGNAL"):
    sig_id = new_sig_id()
    pending_signals[sig_id] = text_vip

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("✅ OK в VIP", callback_data=f"appr:{sig_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"rej:{sig_id}")
    )
    bot.send_message(ADMIN_ID, f"📩 <b>{title}</b>\n\n{text_vip}", reply_markup=kb)

@bot.message_handler(commands=["l1test"])
def l1test(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Только админ ❌")
        return

    text_vip = build_signal_text(
        symbol="GOLD (XAUUSD)",
        direction="BUY",
        entry="TEST",
        tp1="TEST",
        tp2="TEST",
        sl="TEST",
        tf=DEFAULT_TF,
        confidence="TEST",
        mode="L1 TEST"
    )
    send_to_admin_for_approve(text_vip, title="L1 TEST SIGNAL")

@bot.message_handler(func=lambda m: m.text == "🧪 L1 Test Signal")
def l1test_btn(message):
    if message.from_user.id == ADMIN_ID:
        l1test(message)

@bot.message_handler(func=lambda m: m.text == "📝 Создать сигнал")
def how_to_signal(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        "Отправь сигнал командой:\n"
        "<code>/signal BUY entry tp1 tp2 sl</code>\n\n"
        "Пример:\n"
        "<code>/signal BUY 2031 2039 2046 2024</code>"
    )

@bot.message_handler(commands=["signal"])
def manual_signal(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Только админ ❌")
        return

    parts = message.text.split()
    if len(parts) != 6:
        bot.send_message(
            message.chat.id,
            "Формат:\n<code>/signal BUY entry tp1 tp2 sl</code>\n\n"
            "Пример:\n<code>/signal BUY 2031 2039 2046 2024</code>"
        )
        return

    _, direction, entry, tp1, tp2, sl = parts
    text_vip = build_signal_text(
        symbol="GOLD (XAUUSD)",
        direction=direction,
        entry=entry, tp1=tp1, tp2=tp2, sl=sl,
        tf=DEFAULT_TF,
        confidence="88-92%",
        mode="SAFE ELITE"
    )
    send_to_admin_for_approve(text_vip, title="NEW SIGNAL (MANUAL)")

@bot.callback_query_handler(func=lambda c: True)
def on_callback(call):
    try:
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Только админ", show_alert=True)
            return

        data = call.data or ""
        if data.startswith("appr:"):
            sig_id = data.split(":", 1)[1]
            text = pending_signals.pop(sig_id, None)
            if not text:
                bot.answer_callback_query(call.id, "Сигнал не найден", show_alert=True)
                return

            bot.send_message(VIP_CHANNEL, text)
            bot.answer_callback_query(call.id, "Отправлено в VIP ✅")

        elif data.startswith("rej:"):
            sig_id = data.split(":", 1)[1]
            pending_signals.pop(sig_id, None)
            bot.answer_callback_query(call.id, "Отклонено ❌")
        else:
            bot.answer_callback_query(call.id, "Неизвестная команда")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка: {e}", show_alert=True)

# ================== ADMIN HELP ==================
@bot.message_handler(func=lambda m: m.text == "📌 Админ: команды")
def admin_help(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        "👑 <b>Админ команды</b>\n\n"
        "<code>/vip1 ID</code> — доступ 30 дней\n"
        "<code>/vip3 ID</code> — доступ 90 дней\n"
        "<code>/ban ID</code> — удалить/отключить\n\n"
        "<code>/signal BUY entry tp1 tp2 sl</code> — создать сигнал\n"
        "<code>/l1test</code> — тест сигнал\n"
        "<code>/ping</code> — проверка бота\n"
    )

# ================== RUN ==================
if __name__ == "__main__":
    # Важно: один деплой / один процесс, иначе будет конфликт getUpdates
    bot.infinity_polling(timeout=60, long_polling_timeout=60)