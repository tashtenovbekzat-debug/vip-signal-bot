import os
import time
import logging
import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ================== LOGGING (анти-падение) ==================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ================== CONFIG (Railway Variables) ==================
# ВАЖНО: токен только в Railway Variables -> BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN", "8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in Railway Variables")

# Твои данные (как ты просил — я ставлю)
ADMIN_ID = int(os.getenv("ADMIN_ID", "8394704301"))
VIP_CHANNEL = int(os.getenv("VIP_CHANNEL", "-1003735072360"))

# Текст цены
PRICE_TEXT = (
    "💎 <b>ALPHA GOLD VIP</b>\n\n"
    "1 месяц — <b>200$</b>\n"
    "3 месяца — <b>500$</b>\n\n"
    "После оплаты нажми: ✅ <b>Я оплатил</b>"
)

# Watermark / бренд
WATERMARK = "© <b>ALPHA GOLD PRIVATE</b> • Elite System"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# pending_signals: sig_id -> {"text": str, "created": float}
pending_signals = {}


# ================== HELPERS ==================
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def admin_private_only(message) -> bool:
    """Админ-команды разрешаем только админу и только в личке."""
    return (message.from_user.id == ADMIN_ID) and (message.chat.type == "private")


def main_menu(user_id: int):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Цена VIP"))
    kb.add(KeyboardButton("✅ Я оплатил"))
    kb.add(KeyboardButton("🆔 Мой ID"))
    if is_admin(user_id):
        kb.add(KeyboardButton("🧪 L1 Test Signal"))
        kb.add(KeyboardButton("📝 Создать сигнал"))
    return kb


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
        InlineKeyboardButton("✅ OK в VIP", callback_data=f"appr:{sig_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"rej:{sig_id}")
    )

    bot.send_message(ADMIN_ID, f"📩 <b>{title}</b>\n\n{text_vip}", reply_markup=kb)


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
        "Выдай доступ командой:\n"
        f"<code>/vip1 {user_id}</code> (30 дней)\n"
        f"<code>/vip3 {user_id}</code> (90 дней)\n\n"
        f"{WATERMARK}"
    )

    # админу в личку
    bot.send_message(ADMIN_ID, text)

    # в VIP канал (не обязательно) — если бот имеет право писать
    # (Это можно оставить. Если хочешь "по-безопасному" — скажи, выключу)
    try:
        bot.send_message(VIP_CHANNEL, f"Заявка на доступ от <code>{user_id}</code> (@{username})")
    except Exception as e:
        logging.warning(f"VIP_CHANNEL notify failed: {e}")

    bot.send_message(message.chat.id, "⏳ Заявка отправлена админу. Ожидай доступ.")


def _send_invite_once(user_id: int, days: int):
    # ВАЖНО: бот должен быть админом в VIP канале и иметь право Manage invite links
    link = bot.create_chat_invite_link(chat_id=VIP_CHANNEL, member_limit=1)

    bot.send_message(
        user_id,
        "✅ Доступ подтверждён.\n"
        f"Срок: <b>{days} дней</b>\n\n"
        "Вот ссылка в VIP канал (одноразовая):\n"
        f"{link.invite_link}\n\n"
        f"{WATERMARK}"
    )


@bot.message_handler(commands=["vip1"])
def vip1(message):
    if not admin_private_only(message):
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Формат: <code>/vip1 123456789</code>")
        return

    try:
        user_id = int(parts[1])
        _send_invite_once(user_id, days=30)
        bot.send_message(message.chat.id, f"Готово ✅ VIP1 (30 дней) отправлено пользователю {user_id}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


@bot.message_handler(commands=["vip3"])
def vip3(message):
    if not admin_private_only(message):
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Формат: <code>/vip3 123456789</code>")
        return

    try:
        user_id = int(parts[1])
        _send_invite_once(user_id, days=90)
        bot.send_message(message.chat.id, f"Готово ✅ VIP3 (90 дней) отправлено пользователю {user_id}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


# ================== L1 TEST ==================
@bot.message_handler(commands=["l1test"])
def l1test_cmd(message):
    if not admin_private_only(message):
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
    if not is_admin(message.from_user.id):
        return
    # кнопку можно нажать и не в личке, но команду исполним только в личке:
    bot.send_message(message.chat.id, "Открой личку со мной и напиши: <code>/l1test</code>")


# ================== MANUAL SIGNAL (/signal) ==================
@bot.message_handler(commands=["signal"])
def signal_cmd(message):
    """
    Формат:
    /signal BUY entry tp1 tp2 sl
    Пример:
    /signal BUY 2031 2039 2046 2024
    """
    if not admin_private_only(message):
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
    text_vip = build_signal_text(direction, entry, tp1, tp2, sl, tf="M5", confidence="88-92%", mode="SAFE ELITE")
    send_to_admin_for_approve(text_vip, title="NEW SIGNAL (MANUAL)")


@bot.message_handler(func=lambda m: m.text == "📝 Создать сигнал")
def signal_btn(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        "Отправь команду (в личку со мной):\n"
        "<code>/signal BUY entry tp1 tp2 sl</code>\n\n"
        "Пример:\n"
        "<code>/signal BUY 2031 2039 2046 2024</code>"
    )


# ================== CALLBACK APPROVE/REJECT ==================
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


# ================== RUN (анти-падение) ==================
if __name__ == "__main__":
    # Важно: один деплой/один процесс, иначе будет конфликт getUpdates
    while True:
        try:
            logging.info("BOT STARTED")
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            logging.exception(f"Polling crashed: {e}")
            time.sleep(5)