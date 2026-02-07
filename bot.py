import os
import telebot

# ====== ТВОИ ДАННЫЕ ======
BOT_TOKEN = os.getenv("8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU")
ADMIN_ID = 8394704301   # твой Telegram ID
VIP_CHANNEL = -1003735072360  # твой VIP канал

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в Railway")

bot = telebot.TeleBot(BOT_TOKEN)


# ===== Проверка жив ли бот =====
@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "pong 🔥 Бот работает")


# ===== Когда человек пишет боту =====
@bot.message_handler(func=lambda m: True)
def get_user(message):
    user_id = message.from_user.id
    username = message.from_user.username

    text = f"""
🔥 Новый пользователь

ID: {user_id}
Username: @{username}
"""

    bot.send_message(ADMIN_ID, text)
    bot.reply_to(message, "Админ скоро ответит ✅")


# ===== Команда выдать доступ =====
@bot.message_handler(commands=['give'])
def give_access(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.text.split()[1])

        link = bot.create_chat_invite_link(VIP_CHANNEL, member_limit=1)

        bot.send_message(user_id,
        f"💎 Оплата получена!\nВот доступ в VIP канал:\n{link.invite_link}")

        bot.reply_to(message, "Пользователь добавлен в VIP ✅")

    except:
        bot.reply_to(message, "Ошибка. Пиши:\n/give 123456789")


print("Бот запущен...")
bot.infinity_polling()