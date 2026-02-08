import os
import time
import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ================== CONFIG (Railway Variables) ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in Railway Variables")

ADMIN_ID = int(os.getenv("ADMIN_ID", "8394704301"))
VIP_CHANNEL = int(os.getenv("VIP_CHANNEL", "-1003735072360"))

# ================== STYLE (ALPHA GOLD №1) ==================
DEFAULT_TF = os.getenv("DEFAULT_TF", "M15").strip()          # мы выбрали M15
DEFAULT_MODE = os.getenv("DEFAULT_MODE", "GOD BALANCE ELITE").strip()
DEFAULT_RISK = os.getenv("DEFAULT_RISK", "1–2%").strip()
DEFAULT_CONF = os.getenv("DEFAULT_CONF", "88–92%").strip()

PRICE_TEXT = (
    "💎 <b>ALPHA GOLD VIP</b>\n\n"
    "1 месяц — <b>200$</b>\n"
    "3 месяца — <b>500$</b>\n\n"
    "После оплаты нажми: ✅ <b>Я оплатил</b>"
)

WATERMARK = "© <b>ALPHA GOLD PRIVATE</b> • Elite System"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# pending_signals: sig_id -> {"text": str, "created": float}
pending_signals = {}
PENDING_TTL_SECONDS = 6 * 60 * 60  # 6 часов


# ================== UTIL ==================
def _new_sig_id() -> str:
    return str(int(time.time() * 1000))


def _cleanup_pending():
    """Удаляем старые сигналы, чтобы не копились."""
    now = time.time()
    old_ids = [sid for sid, item in pending_signals.items() if now - item["created"] > PENDING_TTL_SECONDS]
    for sid in old_ids:
        pending_signals.pop(sid, None)


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ================== KEYBOARD ==================
def main_menu(user_id: int):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Цена VIP"))
    kb.add(KeyboardButton("✅ Я оплатил"))
    kb.add(KeyboardButton("🆔 Мой ID"))
    if _is_admin(user_id):
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


# ================== PAYMENT FLOW ==================
@bot.message_handler(func=lambda m: m.text == "✅ Я оплатил")
def btn_paid(message):
    user_id = message.from_user.id
    username = message.from_user.username or "-"

    text = (
        "💸 <b>Новая заявка (оплата)</b>\n\n"
        f"ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n\n"
        f"Подтвердить:\n<code>/ok {user_id}</code>\n\n"
        f"{WATERMARK}"
    )

    bot.send_message(ADMIN_ID, text)

    # в VIP канал (не обязательно)
    try:
        bot.send_message(VIP_CHANNEL, f"Заявка на доступ от <code>{user_id}</code> (@{username})")
    except Exception:
        pass

    bot.send_message(message.chat.id, "⏳ Заявка отправлена админу. Ожидай доступ.")


@bot.message_handler(commands=["ok"])
def approve_payment(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Ты не админ ❌")
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Пиши так: <code>/ok 123456789</code>")
        return

    try:
        user_id = int(parts[1])

        link = bot.create_chat_invite_link(
            chat_id=VIP_CHANNEL,
            member_limit=1
        )

        bot.send_message(
            user_id,
            "✅ Оплата подтверждена.\n"
            "Вот ссылка в VIP канал (одноразовая):\n"
            f"{link.invite_link}\n\n"
            f"{WATERMARK}"
        )

        bot.send_message(message.chat.id, f"Готово ✅ Ссылка отправлена пользователю {user_id}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


# ================== SIGNAL BUILD ==================
def build_signal_text(
    direction: str, entry: str, tp1: str, tp2: str, sl: str,
    tf: str = None, confidence: str = None, mode: str = None, risk: str = None
) -> str:
    d = (direction or "").upper().strip()
    if d not in ("BUY", "SELL"):
        d = "BUY"
    dot = "🟢" if d == "BUY" else "🔴"

    tf = (tf or DEFAULT_TF).strip()
    confidence = (confidence or DEFAULT_CONF).strip()
    mode = (mode or DEFAULT_MODE).strip()
    risk = (risk or DEFAULT_RISK).strip()

    return (
        "👑 <b>ALPHA GOLD VIP SIGNAL</b>\n\n"
        "📊 <b>GOLD (XAUUSD)</b>\n"
        f"Signal: <b>{d}</b> {dot}\n"
        f"TF: <b>{tf}</b>\n\n"
        f"Entry: <b>{entry}</b>\n"
        f"TP1: <b>{tp1}</b>\n"
        f"TP2: <b>{tp2}</b>\n"
        f"SL: <b>{sl}</b>\n\n"
        f"Risk: <b>{risk}</b>\n"
        f"Mode: <b>{mode}</b>\n"
        f"Confidence: <b>{confidence}</b>\n\n"
        f"{WATERMARK}"
    )


def send_to_admin_for_approve(text_vip: str, title: str = "SIGNAL"):
    _cleanup_pending()
    sig_id = _new_sig_id()
    pending_signals[sig_id] = {"text": text_vip, "created": time.time()}

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("✅ OK в VIP", callback_data=f"appr:{sig_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"rej:{sig_id}")
    )

    bot.send_message(ADMIN_ID, f"📩 <b>{title}</b>\n\n{text_vip}", reply_markup=kb)


# ================== L1 TEST ==================
@bot.message_handler(commands=["l1test"])
def l1test_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Только админ ❌")
        return

    text_vip = build_signal_text(
        direction="BUY",
        entry="TEST",
        tp1="TEST",
        tp2="TEST",
        sl="TEST",
        tf=DEFAULT_TF,
        confidence="TEST",
        mode="L1 TEST",
        risk=DEFAULT_RISK
    )
    send_to_admin_for_approve(text_vip, title="L1 TEST SIGNAL")


@bot.message_handler(func=lambda m: m.text == "🧪 L1 Test Signal")
def l1test_btn(message):
    if message.from_user.id != ADMIN_ID:
        return
    l1test_cmd(message)


# ================== MANUAL SIGNAL (старый формат) ==================
@bot.message_handler(commands=["signal"])
def signal_cmd(message):
    """
    Старый формат (оставляем):
    /signal BUY entry tp1 tp2 sl
    Пример:
    /signal BUY 2031 2039 2046 2024
    """
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Только админ ❌")
        return

    parts = message.text.split()
    if len(parts) != 6:
        bot.send_message(
            message.chat.id,
            "Формат:\n"
            "<code>/signal BUY entry tp1 tp2 sl</code>\n\n"
            "Пример:\n"
            "<code>/signal BUY 2031 2039 2046 2024</code>"
        )
        return

    _, direction, entry, tp1, tp2, sl = parts
    text_vip = build_signal_text(direction, entry, tp1, tp2, sl)
    send_to_admin_for_approve(text_vip, title="NEW SIGNAL (MANUAL)")


# ================== MANUAL SIGNAL (новый расширенный) ==================
@bot.message_handler(commands=["signal2"])
def signal2_cmd(message):
    """
    Новый формат:
    /signal2 BUY entry tp1 tp2 sl [confidence] [tf]
    Пример:
    /signal2 BUY 2031 2039 2046 2024 91 M15
    confidence и tf можно не писать
    """
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Только админ ❌")
        return

    parts = message.text.split()
    if len(parts) < 6:
        bot.send_message(
            message.chat.id,
            "Формат:\n"
            "<code>/signal2 BUY entry tp1 tp2 sl [confidence] [tf]</code>\n\n"
            "Пример:\n"
            "<code>/signal2 BUY 2031 2039 2046 2024 91 M15</code>"
        )
        return

    # parts: /signal2 dir entry tp1 tp2 sl conf tf
    direction = parts[1]
    entry = parts[2]
    tp1 = parts[3]
    tp2 = parts[4]
    sl = parts[5]
    confidence = parts[6] if len(parts) >= 7 else DEFAULT_CONF
    tf = parts[7] if len(parts) >= 8 else DEFAULT_TF

    text_vip = build_signal_text(direction, entry, tp1, tp2, sl, tf=tf, confidence=f"{confidence}%")
    send_to_admin_for_approve(text_vip, title="NEW SIGNAL (MANUAL v2)")


@bot.message_handler(func=lambda m: m.text == "📝 Создать сигнал")
def signal_btn(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        "Команды для сигналов:\n\n"
        "1) Обычный:\n"
        "<code>/signal BUY entry tp1 tp2 sl</code>\n"
        "Пример:\n"
        "<code>/signal BUY 2031 2039 2046 2024</code>\n\n"
        "2) Расширенный:\n"
        "<code>/signal2 BUY entry tp1 tp2 sl 91 M15</code>\n"
    )


# ================== CALLBACK APPROVE/REJECT ==================
@bot.callback_query_handler(func=lambda c: True)
def on_callback(call):
    try:
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Только админ", show_alert=True)
            return

        _cleanup_pending()

        data = call.data or ""
        if data.startswith("appr:"):
            sig_id = data.split(":", 1)[1]
            item = pending_signals.pop(sig_id, None)
            if not item:
                bot.answer_callback_query(call.id, "Сигнал не найден/устарел", show_alert=True)
                return

            bot.send_message(VIP_CHANNEL, item["text"])
            bot.answer_callback_query(call.id, "Отправлено в VIP ✅")

        elif data.startswith("rej:"):
            sig_id = data.split(":", 1)[1]
            pending_signals.pop(sig_id, None)
            bot.answer_callback_query(call.id, "Отклонено ❌")

        else:
            bot.answer_callback_query(call.id, "Неизвестная команда")

    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка: {e}", show_alert=True)


if __name__ == "__main__":
    bot.infinity_polling(timeout=60, long_polling_timeout=60)