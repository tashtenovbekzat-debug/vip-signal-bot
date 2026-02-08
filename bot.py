import os
import time
import json
import threading
import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in Railway Variables")

# ✅ Твои данные (уже заполнены)
ADMIN_ID = 8394704301
VIP_CHANNEL = -1003735072360

PRICE_TEXT = (
    "💎 <b>ALPHA GOLD VIP</b>\n\n"
    "1 месяц — <b>200$</b>\n"
    "3 месяца — <b>500$</b>\n\n"
    "После оплаты нажми: ✅ <b>Я оплатил</b>"
)

WATERMARK = "© <b>ALPHA GOLD PRIVATE</b> • Elite System"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ================== STORAGE ==================
DB_FILE = "vip_db.json"
db_lock = threading.Lock()

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_db(data: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

vip_db = load_db()  # vip_db[user_id] = {"expires_at": ts, "plan_days": 30/90}

# ================== SIGNALS ==================
pending_signals = {}

def _new_sig_id() -> str:
    return str(int(time.time() * 1000))

def build_signal_text(direction: str, entry: str, tp1: str, tp2: str, sl: str,
                      tf: str = "M5", confidence: str = "88-92%", mode: str = "SAFE ELITE") -> str:
    d = (direction or "").upper().strip()
    if d not in ("BUY", "SELL"):
        d = "BUY"
    dot = "🟢" if d == "BUY" else "🔴"
    return (
        "👑 <b>ALPHA GOLD VIP SIGNAL</b>\n\n"
        "📊 <b>GOLD (XAUUSD)</b>\n"
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
    sig_id = _new_sig_id()
    pending_signals[sig_id] = {"text": text_vip, "created": time.time()}

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("✅ OK в VIP", callback_data=f"sig_appr:{sig_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"sig_rej:{sig_id}")
    )

    bot.send_message(ADMIN_ID, f"📩 <b>{title}</b>\n\n{text_vip}", reply_markup=kb)

# ================== KEYBOARD ==================
def main_menu(user_id: int):
    is_admin = (user_id == ADMIN_ID)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Цена VIP"))
    kb.add(KeyboardButton("✅ Я оплатил"))
    kb.add(KeyboardButton("🆔 Мой ID"))
    if is_admin:
        kb.add(KeyboardButton("🧪 L1 Test Signal"))
        kb.add(KeyboardButton("📝 Создать сигнал"))
    return kb

# ================== BASIC ==================
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>ALPHA GOLD VIP</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы 📈\n"
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

# ================== VIP выдача (30/90 дней) ==================
def grant_vip(user_id: int, days: int):
    expires_at = int(time.time()) + days * 24 * 60 * 60

    # ВАЖНО: бот должен быть админом в VIP канале и иметь Manage invite links
    link = bot.create_chat_invite_link(
        chat_id=VIP_CHANNEL,
        member_limit=1
    )

    with db_lock:
        vip_db[str(user_id)] = {"expires_at": expires_at, "plan_days": days}
        save_db(vip_db)

    bot.send_message(
        user_id,
        "✅ Доступ активирован.\n"
        f"Срок: <b>{days} дней</b>\n"
        "Ссылка в VIP канал (одноразовая):\n"
        f"{link.invite_link}\n\n"
        f"{WATERMARK}"
    )

def remove_from_channel(user_id: int):
    # remove user (ban/unban) — работает и для каналов
    bot.ban_chat_member(VIP_CHANNEL, user_id)
    bot.unban_chat_member(VIP_CHANNEL, user_id)

def expiry_worker():
    while True:
        time.sleep(60)
        now = int(time.time())
        to_remove = []

        with db_lock:
            for uid, info in list(vip_db.items()):
                if info.get("expires_at", 0) <= now:
                    to_remove.append(uid)

        for uid in to_remove:
            try:
                remove_from_channel(int(uid))
                with db_lock:
                    vip_db.pop(uid, None)
                    save_db(vip_db)
                bot.send_message(ADMIN_ID, f"⛔ VIP закончился — пользователь {uid} удалён из канала.")
            except Exception as e:
                try:
                    bot.send_message(ADMIN_ID, f"⚠️ Не смог удалить {uid} из VIP: {e}")
                except Exception:
                    pass

threading.Thread(target=expiry_worker, daemon=True).start()

# ================== PAYMENT REQUEST (КНОПКИ ВМЕСТО КОМАНД) ==================
@bot.message_handler(func=lambda m: m.text == "✅ Я оплатил")
def btn_paid(message):
    user_id = message.from_user.id
    username = message.from_user.username or "-"

    text_admin = (
        "💸 <b>Новая заявка (оплата)</b>\n\n"
        f"ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n\n"
        "Выбери тариф кнопкой ниже:\n\n"
        f"{WATERMARK}"
    )

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("💎 VIP 30 дней (200$)", callback_data=f"vip:30:{user_id}"),
        InlineKeyboardButton("👑 VIP 90 дней (500$)", callback_data=f"vip:90:{user_id}")
    )
    kb.row(
        InlineKeyboardButton("❌ Отклонить", callback_data=f"viprej:{user_id}")
    )

    # ✅ Только админу в личку
    bot.send_message(ADMIN_ID, text_admin, reply_markup=kb)

    bot.send_message(message.chat.id, "⏳ Заявка отправлена админу. Ожидай доступ.")

# ================== L1 TEST ==================
@bot.message_handler(commands=["l1test"])
def l1test_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Только админ ❌")
        return

    text_vip = build_signal_text(
        direction="BUY", entry="TEST", tp1="TEST", tp2="TEST", sl="TEST",
        tf="M5", confidence="TEST", mode="L1 TEST"
    )
    send_to_admin_for_approve(text_vip, title="L1 TEST SIGNAL")

@bot.message_handler(func=lambda m: m.text == "🧪 L1 Test Signal")
def l1test_btn(message):
    if message.from_user.id != ADMIN_ID:
        return
    l1test_cmd(message)

# ================== MANUAL SIGNAL (/signal) ==================
@bot.message_handler(commands=["signal"])
def signal_cmd(message):
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
    text_vip = build_signal_text(direction, entry, tp1, tp2, sl)
    send_to_admin_for_approve(text_vip, title="NEW SIGNAL (MANUAL)")

@bot.message_handler(func=lambda m: m.text == "📝 Создать сигнал")
def signal_btn(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        "Отправь команду:\n"
        "<code>/signal BUY entry tp1 tp2 sl</code>\n\n"
        "Пример:\n"
        "<code>/signal BUY 2031 2039 2046 2024</code>"
    )

# ================== CALLBACKS (VIP + SIGNAL) ==================
@bot.callback_query_handler(func=lambda c: True)
def on_callback(call):
    try:
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Только админ", show_alert=True)
            return

        data = call.data or ""

        # ---- VIP approve buttons
        if data.startswith("vip:"):
            # vip:30:USERID or vip:90:USERID
            _, days_s, user_s = data.split(":")
            days = int(days_s)
            user_id = int(user_s)

            # чтобы не нажимали 2 раза — сразу ответ
            bot.answer_callback_query(call.id, "Делаю...", show_alert=False)

            grant_vip(user_id, days)

            # обновим сообщение админу (красиво)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id, f"✅ Выдан VIP на <b>{days} дней</b> пользователю <code>{user_id}</code>.")

            return

        if data.startswith("viprej:"):
            user_id = data.split(":", 1)[1]
            bot.answer_callback_query(call.id, "Отклонено ❌")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id, f"❌ Заявка отклонена: <code>{user_id}</code>")
            return

        # ---- SIGNAL approve/reject
        if data.startswith("sig_appr:"):
            sig_id = data.split(":", 1)[1]
            item = pending_signals.pop(sig_id, None)
            if not item:
                bot.answer_callback_query(call.id, "Сигнал не найден", show_alert=True)
                return
            bot.send_message(VIP_CHANNEL, item["text"])
            bot.answer_callback_query(call.id, "Отправлено в VIP ✅")
            return

        if data.startswith("sig_rej:"):
            sig_id = data.split(":", 1)[1]
            pending_signals.pop(sig_id, None)
            bot.answer_callback_query(call.id, "Отклонено ❌")
            return

        bot.answer_callback_query(call.id, "Неизвестная команда")

    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка: {e}", show_alert=True)

if __name__ == "__main__":
    bot.infinity_polling(timeout=60, long_polling_timeout=60)