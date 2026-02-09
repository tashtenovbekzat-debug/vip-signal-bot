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
BOT_TOKEN = os.getenv("BOT_TOKEN", "8492510753:AAFhTasMnqf-Mi-OhLVFrRsC74lol0_imVU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is empty. Set BOT_TOKEN in Railway Variables")

ADMIN_ID = 8394704301
VIP_CHANNEL = -1003735072360

# 0/1 (по умолчанию выключено)
SEND_REQUESTS_TO_VIP_CHANNEL = os.getenv("SEND_REQUESTS_TO_VIP_CHANNEL", "0").strip() == "1"

# ================== TEXT / BRAND ==================
PRICE_TEXT = (
    "💎 <b>ALPHA GOLD VIP</b>\n\n"
    "✅ 1 месяц — <b>200$</b>\n"
    "✅ 3 месяца — <b>500$</b>\n\n"
    "После оплаты нажми: ✅ <b>Я оплатил</b>"
)
WATERMARK = "© <b>ALPHA GOLD PRIVATE</b> • Elite System"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ================== IMPORTANT (Railway fix) ==================
# Если когда-то был webhook — polling может молчать. Снимаем webhook.
try:
    bot.remove_webhook()
    time.sleep(1)
except Exception:
    pass

# ================== STORAGE (подписки) ==================
SUBS_FILE = "subs.json"
LOCK = threading.Lock()
subs = {}  # "user_id": {"expires_at": int, "plan_days": int, "granted_at": int}

def load_subs():
    global subs
    try:
        if os.path.exists(SUBS_FILE):
            with open(SUBS_FILE, "r", encoding="utf-8") as f:
                subs = json.load(f)
        else:
            subs = {}
    except Exception:
        subs = {}

def save_subs():
    try:
        with open(SUBS_FILE, "w", encoding="utf-8") as f:
            json.dump(subs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

load_subs()

# ================== SIGNAL FORMAT ==================
def build_signal_text(symbol: str, direction: str, entry: str, tp1: str, tp2: str, sl: str,
                      tf: str = "M5", confidence: str = "92-97%", mode: str = "SAFE ELITE") -> str:
    d = (direction or "").upper().strip()
    if d not in ("BUY", "SELL"):
        d = "BUY"
    dot = "🟢" if d == "BUY" else "🔴"
    symbol = (symbol or "XAUUSD").upper().strip()

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

# ================== VIP HELPERS ==================
def _fmt_dt(ts: int) -> str:
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
    except Exception:
        return str(ts)

def _left_seconds(expires_at: int) -> int:
    return int(expires_at - time.time())

def _human_left(sec: int) -> str:
    if sec <= 0:
        return "0д"
    days = sec // 86400
    hours = (sec % 86400) // 3600
    mins = (sec % 3600) // 60
    if days > 0:
        return f"{days}д {hours}ч"
    if hours > 0:
        return f"{hours}ч {mins}м"
    return f"{mins}м"

def vip_status_text(user_id: int) -> str:
    with LOCK:
        s = subs.get(str(user_id))
    if not s:
        return "VIP: ❌ нет подписки"
    left = _left_seconds(int(s["expires_at"]))
    return (
        "VIP: ✅ активен\n"
        f"Осталось: <b>{_human_left(left)}</b>\n"
        f"До: <code>{_fmt_dt(int(s['expires_at']))}</code>"
    )

def revoke_vip(user_id: int):
    try:
        bot.ban_chat_member(VIP_CHANNEL, user_id)
        bot.unban_chat_member(VIP_CHANNEL, user_id)
    except Exception:
        pass

def grant_vip(user_id: int, plan_days: int):
    expire_date = int(time.time()) + 600
    link = bot.create_chat_invite_link(
        chat_id=VIP_CHANNEL,
        member_limit=1,
        expire_date=expire_date
    )
    now = int(time.time())
    expires_at = now + plan_days * 86400

    with LOCK:
        subs[str(user_id)] = {
            "expires_at": expires_at,
            "plan_days": plan_days,
            "granted_at": now
        }
        save_subs()

    return link.invite_link, expires_at

# ================== UI ==================
def main_menu(user_id: int):
    is_admin = (user_id == ADMIN_ID)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Цена VIP"))
    kb.add(KeyboardButton("✅ Я оплатил"))
    kb.add(KeyboardButton("🆔 Мой ID"))
    kb.add(KeyboardButton("📌 VIP Статус"))
    if is_admin:
        kb.add(KeyboardButton("🧪 Test Signal"))
        kb.add(KeyboardButton("📝 Создать сигнал"))
    return kb

def admin_payment_keyboard(user_id: int):
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🔥 VIP 30 дней (200$)", callback_data=f"vip:30:{user_id}"),
        InlineKeyboardButton("💎 VIP 90 дней (500$)", callback_data=f"vip:90:{user_id}")
    )
    kb.row(
        InlineKeyboardButton("ℹ️ VIP INFO", callback_data=f"vipinfo:{user_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"viprej:{user_id}")
    )
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

@bot.message_handler(commands=["vip"])
def vip_cmd(message):
    bot.send_message(message.chat.id, vip_status_text(message.from_user.id))

@bot.message_handler(func=lambda m: m.text == "📌 VIP Статус")
def vip_btn(message):
    bot.send_message(message.chat.id, vip_status_text(message.from_user.id))

# ================== PAYMENT REQUEST ==================
last_paid_click = {}

@bot.message_handler(func=lambda m: m.text == "✅ Я оплатил")
def btn_paid(message):
    user_id = message.from_user.id
    username = message.from_user.username or "-"

    now = time.time()
    if user_id in last_paid_click and (now - last_paid_click[user_id]) < 20:
        bot.send_message(message.chat.id, "⏳ Уже отправлено. Подожди немного.")
        return
    last_paid_click[user_id] = now

    text = (
        "💸 <b>Новая заявка (оплата)</b>\n\n"
        f"ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n\n"
        "Выдай доступ кнопкой ниже:\n\n"
        f"{WATERMARK}"
    )

    bot.send_message(ADMIN_ID, text, reply_markup=admin_payment_keyboard(user_id))

    if SEND_REQUESTS_TO_VIP_CHANNEL:
        try:
            bot.send_message(VIP_CHANNEL, f"Заявка на доступ от <code>{user_id}</code> (@{username})")
        except Exception:
            pass

    bot.send_message(message.chat.id, "⏳ Заявка отправлена админу. Ожидай доступ.")

# ================== ADMIN: SIGNALS ==================
@bot.message_handler(func=lambda m: m.text == "🧪 Test Signal")
def test_btn(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = build_signal_text("XAUUSD", "BUY", "TEST", "TP1", "TP2", "SL", tf="M5", confidence="TEST", mode="TEST")
    bot.send_message(ADMIN_ID, text)

@bot.message_handler(func=lambda m: m.text == "📝 Создать сигнал")
def signal_help(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        "Формат:\n"
        "<code>/send XAUUSD BUY entry tp1 tp2 sl</code>\n\n"
        "Пример:\n"
        "<code>/send XAUUSD BUY 2031 2039 2046 2024</code>"
    )

@bot.message_handler(commands=["send"])
def send_signal(message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) != 7:
        bot.send_message(ADMIN_ID, "Формат:\n<code>/send XAUUSD BUY entry tp1 tp2 sl</code>")
        return

    _, symbol, direction, entry, tp1, tp2, sl = parts
    text = build_signal_text(symbol, direction, entry, tp1, tp2, sl, tf="M5", confidence="92-97%", mode="SAFE ELITE")

    bot.send_message(ADMIN_ID, "🚀 <b>SIGNAL SENT</b>\n\n" + text)
    bot.send_message(VIP_CHANNEL, text)

# ================== CALLBACKS ==================
@bot.callback_query_handler(func=lambda c: True)
def on_callback(call):
    try:
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Только админ", show_alert=True)
            return

        data = call.data or ""

        if data.startswith("vip:"):
            _, days_str, user_id_str = data.split(":")
            plan_days = int(days_str)
            user_id = int(user_id_str)

            invite_link, expires_at = grant_vip(user_id, plan_days)

            try:
                bot.send_message(
                    user_id,
                    "✅ <b>Оплата подтверждена.</b>\n"
                    f"План: <b>{plan_days} дней</b>\n"
                    "Ссылка в VIP канал (одноразовая, действует 10 минут):\n"
                    f"{invite_link}\n\n"
                    f"{WATERMARK}"
                )
            except Exception as e:
                bot.send_message(
                    ADMIN_ID,
                    f"⚠️ Не смог отправить пользователю <code>{user_id}</code> ссылку.\n"
                    f"Причина: {e}\n"
                    "Пусть пользователь сначала нажмёт /start в боте."
                )

            bot.answer_callback_query(call.id, "VIP выдан ✅")
            bot.send_message(
                ADMIN_ID,
                f"✅ VIP выдан <code>{user_id}</code> на <b>{plan_days} дней</b>.\n"
                f"Истекает: <code>{_fmt_dt(expires_at)}</code>\n\n"
                f"{vip_status_text(user_id)}"
            )
            return

        if data.startswith("vipinfo:"):
            user_id = int(data.split(":", 1)[1])
            bot.answer_callback_query(call.id, "OK")
            bot.send_message(ADMIN_ID, vip_status_text(user_id))
            return

        if data.startswith("viprej:"):
            user_id = int(data.split(":", 1)[1])
            bot.answer_callback_query(call.id, "Отклонено ❌")
            bot.send_message(ADMIN_ID, f"❌ Заявка отклонена для <code>{user_id}</code>")
            try:
                bot.send_message(user_id, "❌ Оплата не подтверждена. Напиши админу.")
            except Exception:
                pass
            return

        bot.answer_callback_query(call.id, "Неизвестная команда")

    except Exception as e:
        try:
            bot.answer_callback_query(call.id, f"Ошибка: {e}", show_alert=True)
        except Exception:
            pass

# ================== AUTO EXPIRE WORKER ==================
def expire_worker():
    while True:
        try:
            now = int(time.time())
            expired = []

            with LOCK:
                for uid, info in list(subs.items()):
                    if int(info.get("expires_at", 0)) <= now:
                        expired.append(int(uid))

            for user_id in expired:
                revoke_vip(user_id)
                with LOCK:
                    subs.pop(str(user_id), None)
                    save_subs()

                try:
                    bot.send_message(
                        user_id,
                        "⛔️ VIP срок закончился. Доступ закрыт.\n\n"
                        "Хочешь продлить — нажми ✅ <b>Я оплатил</b>."
                    )
                except Exception:
                    pass

                try:
                    bot.send_message(ADMIN_ID, f"⏳ VIP истёк у <code>{user_id}</code> — удалён из канала.")
                except Exception:
                    pass

        except Exception:
            pass

        time.sleep(300)

# ================== ANTI-CRASH POLLING ==================
def run_polling_forever():
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception:
            time.sleep(3)

if __name__ == "__main__":
    threading.Thread(target=expire_worker, daemon=True).start()
    run_polling_forever()