import os
import telebot

TOKEN = os.getenv("8492510753:AAGesCCRSWAQe9hvYwBRgRhOxGqY3D5YxGA")
ADMIN_ID = 8394704301
VIP_CHANNEL = -1003735072360

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>VIP GOLD SIGNAL BOT</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы.\n"
        "Доступ в VIP канал платный.\n"
        "После оплаты админ выдаст доступ.\n\n"
        "Отправь /id чтобы узнать свой ID"
    )


@bot.message_handler(commands=["id"])
def get_id(message):
    bot.send_message(message.chat.id, f"Твой ID: <code>{message.from_user.id}</code>")


@bot.message_handler(commands=["give"])
def give_access(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Ты не админ ❌")
        return

    try:
        user_id = int(message.text.split()[1])

        link = bot.create_chat_invite_link(
            chat_id=VIP_CHANNEL,
            member_limit=1
        )

        bot.send_message(
            user_id,
            f"✅ Оплата получена!\nВот доступ в VIP канал:\n{link.invite_link}"
        )

        bot.send_message(message.chat.id, "Готово. Пользователь добавлен ✅")

    except:
        bot.send_message(message.chat.id, "Ошибка. Пиши так: /give 123456789")


bot.infinity_polling()