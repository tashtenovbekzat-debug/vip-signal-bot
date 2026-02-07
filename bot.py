import os
import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ====== НАСТРОЙКИ (ТОКЕН ТОЛЬКО В Railway Variables) ======
BOT_TOKEN = os.getenv("BOT_TOKEN", "8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in Railway Variables")

ADMIN_ID = 8394704301           # твой Telegram ID (админ)
VIP_CHANNEL = -1003735072360    # твой VIP канал (chat_id)

PRICE_TEXT = (
    "💎 VIP доступ:\n\n"
    "1 месяц — 200$\n"
    "3 месяца — 500$\n\n"
    "После оплаты нажми: ✅ Я оплатил"
)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ====== L1 (тест сигналов + подтверждение) ======
pending_signals = {}  # sig_id -> text


def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Цена VIP"))
    kb.add(KeyboardButton("✅ Я оплатил"))
    kb.add(KeyboardButton("🆔 Мой ID"))
    kb.add(KeyboardButton("🧪 L1 Test Signal"))
    return kb


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>ALPHA GOLD VIP</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы 📈\n"
        "Выбери действие ниже:",
        reply_markup=main_menu()
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


# ====== Оплата: пользователь нажал "Я оплатил" ======
@bot.message_handler(func=lambda m: m.text == "✅ Я оплатил")
def btn_paid(message):
    user_id = message.from_user.id
    username = message.from_user.username or "-"

    text = (
        "💸 <b>Новая заявка (оплата)</b>\n\n"
        f"ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n\n"
        f"Подтвердить:\n<code>/ok {user_id}</code>"
    )

    # админу в личку
    bot.send_message(ADMIN_ID, text)

    # в VIP канал (не обязательно)
    try:
        bot.send_message(VIP_CHANNEL, f"Заявка на доступ от <code>{user_id}</code> (@{username})")
    except Exception:
        pass

    bot.send_message(message.chat.id, "⏳ Отправлено админу. Ожидай доступ.")


# ====== Админ подтверждает оплату и выдает одноразовую ссылку ======
@bot.message_handler(commands=["ok"])
def approve(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Ты не админ ❌")
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Пиши так: <code>/ok 123456789</code>")
        return

    try:
        user_id = int(parts[1])

        # ВАЖНО: бот должен быть админом в канале
        # и иметь право "Manage invite links"
        link = bot.create_chat_invite_link(
            chat_id=VIP_CHANNEL,
            member_limit=1
        )

        bot.send_message(
            user_id,
            "✅ Оплата подтверждена.\n"
            "Вот ссылка в VIP канал (одноразовая):\n"
            f"{link.invite_link}"
        )

        bot.send_message(message.chat.id, f"Готово ✅ Ссылка отправлена пользователю {user_id}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


# ====== L1 TEST SIGNAL ======
def send_to_admin_for_approve(text_vip: str):
    sig_id = str(len(pending_signals) + 1)
    pending_signals[sig_id] = text_vip

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("✅ OK в VIP", callback_data=f"appr:{sig_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"rej:{sig_id}")
    )

    bot.send_message(ADMIN_ID, f"🧪 <b>L1 TEST SIGNAL</b>\n\n{text_vip}", reply_markup=kb)


@bot.message_handler(commands=["l1test"])
def l1test_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Только админ ❌")
        return

    text_vip = (
        "👑 <b>ALPHA GOLD VIP SIGNAL</b>\n\n"
        "📊 <b>GOLD (XAUUSD)</b>\n"
        "Signal: <b>TEST BUY</b>\n"
        "TF: <b>M5</b>\n"
        "Entry: <b>TEST</b>\n"
        "TP1: <b>TEST</b>\n"
        "TP2: <b>TEST</b>\n"
        "SL: <b>TEST</b>\n\n"
        "Risk: <b>VIP Medium</b>\n"
        "Confidence: <b>TEST</b>\n"
    )
    send_to_admin_for_approve(text_vip)


@bot.message_handler(func=lambda m: m.text == "🧪 L1 Test Signal")
def l1test_btn(message):
    # кнопка в меню
    if message.from_user.id != ADMIN_ID:
        return
    l1test_cmd(message)


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


if __name__ == "__main__":
    bot.infinity_polling(timeout=60, long_polling_timeout=60)