import os
import time
import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ================== НАСТРОЙКИ ==================
# BOT_TOKEN ТОЛЬКО в Railway Variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in Railway Variables")

# Твои данные (оставляем как есть)
ADMIN_ID = 8394704301
VIP_CHANNEL = -1003735072360

# Текст цены
PRICE_TEXT = (
    "💎 <b>ALPHA GOLD VIP</b>\n\n"
    "1 месяц — <b>200$</b>\n"
    "3 месяца — <b>500$</b>\n\n"
    "После оплаты нажми: ✅ <b>Я оплатил</b>"
)

# Watermark (бренд + анти-копирование)
WATERMARK = "© <b>ALPHA GOLD PRIVATE</b> • Elite System"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# pending_signals: sig_id -> {"text": ..., "created": ..., "from": ...}
pending_signals = {}


# ================== КНОПКИ ==================
def main_menu(is_admin: bool):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Цена VIP"))
    kb.add(KeyboardButton("✅ Я оплатил"))
    kb.add(KeyboardButton("🆔 Мой ID"))
    if is_admin:
        kb.add(KeyboardButton("🧪 L1 Test Signal"))
        kb.add(KeyboardButton("📝 Создать сигнал"))
    return kb


# ================== START / HELP ==================
@bot.message_handler(commands=["start"])
def start(message):
    is_admin = (message.from_user.id == ADMIN_ID)
    bot.send_message(
        message.chat.id,
        "🔥 <b>ALPHA GOLD VIP</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы.\n"
        "Выбери действие ниже:",
        reply_markup=main_menu(is_admin)
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


# ================== ОПЛАТА: "Я оплатил" ==================
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

    # админу в личку
    bot.send_message(ADMIN_ID, text)

    # (необязательно) в VIP канал — только если бот имеет право писать
    try:
        bot.send_message(VIP_CHANNEL, f"Заявка на доступ от <code>{user_id}</code> (@{username})")
    except Exception:
        pass

    bot.send_message(message.chat.id, "⏳ Заявка отправлена админу. Ожидай доступ.")


# ================== АДМИН: /ok <user_id> ==================
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

        # ВАЖНО: бот должен быть админом в VIP канале
        # и иметь право "Manage invite links"
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


# ================== СИГНАЛЫ: вспомогательные ==================
def _new_sig_id() -> str:
    # уникальный id
    return str(int(time.time() * 1000))


def send_to_admin_for_approve(text_vip: str, title: str = "SIGNAL"):
    sig_id = _new_sig_id()
    pending_signals[sig_id] = {
        "text": text_vip,
        "created": time.time()
    }

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("✅ OK в VIP", callback_data=f"appr:{sig_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"rej:{sig_id}")
    )

    bot.send_message(
        ADMIN_ID,
        f"📩 <b>{title}</b>\n\n{text_vip}",
        reply_markup=kb
    )


def build_signal_text(
    direction: str,
    entry: str,
    tp1: str,
    tp2: str,
    sl: str,
    tf: str = "M5",
    confidence: str = "88-92%",
    mode: str = "SAFE ELITE"
) -> str:
    direction = direction.upper().strip()
    if direction not in ("BUY", "SELL"):
        direction = "BUY"

    arrow = "🟢" if direction == "BUY" else "🔴"

    return (
        "👑 <b>ALPHA GOLD VIP SIGNAL</b>\n\n"
        "📊 <b>GOLD (XAUUSD)</b>\n"
        f"Signal: <b>{direction}</b> {arrow}\n"
        f"TF: <b>{tf}</b>\n\n"
        f"Entry: <b>{entry}</b>\n"
        f"TP1: <b>{tp1}</b>\n"
        f"TP2: <b>{tp2}</b>\n"
        f"SL: <b>{sl}</b>\n\n"
        f"Mode: <b>{mode}</b>\n"
        f"Confidence: <b>{confidence}</b>\n\n"
        f"{WATERMARK}"
    )


# ================== L1 TEST SIGNAL (оставляем) ==================
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
        tf="M5",
        confidence="TEST",
        mode="L1 TEST"
    )
    send_to_admin_for_approve(text_vip, title="L1 TEST SIGNAL")


@bot.message_handler(func=lambda m: m.text == "🧪 L1 Test Signal")
def l1test_btn(message):
    if message.from_user.id != ADMIN_ID:
        return
    l1test_cmd(message)


# ================== НОВОЕ: /signal и кнопка "Создать сигнал" ==================
@bot.message_handler(commands=["signal"])
def signal_cmd(message):
    """
    Формат:
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
    text_vip = build_signal_text(
        direction=direction,
        entry=entry,
        tp1=tp1,
        tp2=tp2,
        sl=sl,
        tf="M5",
        confidence="88-92%",
        mode="SAFE ELITE"
    )
    send_to_admin_for_approve(text_vip, title="NEW SIGNAL (MANUAL)")


@bot.message_handler(func=lambda m: m.text == "📝 Создать сигнал")
def signal_btn(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        "Отправь команду в таком формате:\n"
        "<code>/signal BUY entry tp1 tp2 sl</code>\n\n"
        "Пример:\n"
        "<code>/signal BUY 2031 2039 2046 2024</code>"
    )


# ================== CALLBACK: approve / reject ==================
@bot.callback_query_handler(func=lambda c: True)
def on_callback(call):
    try:
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Только админ", show_alert=True)
            return

        data = call.data or ""
        if data.startswith("appr:"):
            sig_id = data.split(":", 1)[1]
            item = pending_signals.pop(sig_id, None)
            if not item:
                bot.answer_callback_query(call.id, "Сигнал не найден", show_alert=True)
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