import telebot

# ВСТАВЬ СЮДА СВОЙ BOT TOKEN
TOKEN = "8492510753:AAHK9aIoguNGa6CJMUr2XrXad04Vwk_uF28"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ВСТАВЬ СЮДА chat_id КАНАЛА ВИДА -100...
VIP_CHANNEL = -1001234567890123

# ВСТАВЬ СЮДА СВОЙ TELEGRAM ID (у тебя: 8394704301)
ADMIN_ID = 8394704301

PRICE_TEXT = "Доступ в VIP канал платный. Напиши администратору."


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>VIP GOLD SIGNAL BOT</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы.\n"
        f"{PRICE_TEXT}\n\n"
        "Команда: /id",
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
        bot.send_message(message.chat.id, "Пиши так: <code>/give 123456789</code>")
        return

    try:
        user_id = int(parts[1])

        # ВАЖНО: пользователь должен хотя бы 1 раз нажать /start вашему боту,
        # иначе бот не сможет ему написать в личку.
        link = bot.create_chat_invite_link(chat_id=VIP_CHANNEL, member_limit=1)

        bot.send_message(
            user_id,
            "✅ Оплата подтверждена.\n"
            "Вот одноразовая ссылка в VIP канал:\n"
            f"{link.invite_link}"
        )

        bot.send_message(message.chat.id, f"Готово ✅ Ссылка отправлена пользователю {user_id}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


bot.infinity_polling(timeout=60, long_polling_timeout=60)