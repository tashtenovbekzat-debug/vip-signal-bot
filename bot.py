import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен")

ADMIN_ID = 8394704301

VIP_LINK = "https://t.me/+9CHxKiRNxu41NWJk"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ===== КНОПКИ =====
def main_buttons():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Цена VIP"))
    kb.add(KeyboardButton("✅ Я оплатил"))
    kb.add(KeyboardButton("🆔 Мой ID"))
    return kb


@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(
        m.chat.id,
        "🔥 <b>ALPHA GOLD VIP</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы 📈\n"
        "Выбери действие ниже:",
        reply_markup=main_buttons()
    )


@bot.message_handler(func=lambda m: m.text == "💰 Цена VIP")
def price(m):
    bot.send_message(
        m.chat.id,
        "💎 <b>VIP доступ:</b>\n\n"
        "1 месяц — 200$\n"
        "3 месяца — 500$\n\n"
        "После оплаты нажми: ✅ Я оплатил"
    )


@bot.message_handler(func=lambda m: m.text == "🆔 Мой ID")
def myid(m):
    bot.send_message(m.chat.id, f"Твой ID:\n<code>{m.from_user.id}</code>")


@bot.message_handler(func=lambda m: m.text == "✅ Я оплатил")
def paid(m):
    user_id = m.from_user.id
    username = m.from_user.username or "-"

    text = (
        "💸 <b>Новая оплата</b>\n\n"
        f"ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n\n"
        f"Подтвердить:\n"
        f"/ok {user_id}"
    )

    bot.send_message(ADMIN_ID, text)
    bot.send_message(m.chat.id, "⏳ Отправлено админу. Ожидай доступ.")


@bot.message_handler(commands=["ok"])
def ok(m):
    if m.from_user.id != ADMIN_ID:
        return

    parts = m.text.split()
    if len(parts) < 2:
        bot.reply_to(m, "Пиши так:\n/ok 123456789")
        return

    user_id = int(parts[1])

    try:
        bot.send_message(
            user_id,
            "🎉 <b>Оплата подтверждена!</b>\n\n"
            "Вот доступ в VIP канал:\n"
            f"{VIP_LINK}"
        )
        bot.reply_to(m, "Пользователь получил доступ ✅")
    except:
        bot.reply_to(m, "Он не нажал /start")


print("BOT STARTED")
bot.infinity_polling()