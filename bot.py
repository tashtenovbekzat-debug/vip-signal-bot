import telebot

TOKEN = "8492510753:AAHK9aIoguNGa6CJMUr2XrXad04Vwk_uF28"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# твой канал
VIP_CHANNEL = "@alphagold_elite_signal"

# твой ID админа
ADMIN_ID = 8394704301

PRICE_TEXT = "Доступ в VIP канал платный. Напиши администратору."


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>VIP GOLD SIGNAL BOT</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы.\n"
        f"{PRICE_TEXT}\n\n"
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

    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Пиши: /give ID")
        return

    user_id = int(parts[1])

    try:
        link = bot.create_chat_invite_link(
            chat_id=VIP_CHANNEL,
            member_limit=1
        )

        bot.send_message(
            user_id,
            f"✅ Оплата подтверждена!\nВот ссылка в VIP канал:\n{link.invite_link}"
        )

        bot.send_message(message.chat.id, "Готово ✅")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


print("Бот запущен...")
bot.infinity_polling()