import os
import telebot

# BOT_TOKEN ставишь ТОЛЬКО в Railway Variables (не в код)
TOKEN = os.getenv("8492510753:AAG-4CI8R-40J5HhYUCe4SZjbcbgnUxRixM", "").strip()
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ✅ твой админ ID
ADMIN_ID = 8394704301

# ✅ твой VIP канал ID (важно с минусом -100...)
VIP_CHANNEL = -1003735072360

# (необязательно) текст оплаты
PRICE_TEXT = os.getenv("PRICE_TEXT", "Для доступа нужна оплата. Напиши администратору.").strip()


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>VIP GOLD SIGNAL BOT</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы.\n"
        f"{PRICE_TEXT}\n\n"
        "Команды:\n"
        "• /id — узнать свой ID\n"
        "• /price — цена/условия\n",
    )


@bot.message_handler(commands=["ping"])
def ping(message):
    bot.reply_to(message, "pong ✅")


@bot.message_handler(commands=["id"])
def get_id(message):
    bot.send_message(message.chat.id, f"Твой ID: <code>{message.from_user.id}</code>")


@bot.message_handler(commands=["price"])
def price(message):
    bot.send_message(message.chat.id, PRICE_TEXT)


@bot.message_handler(commands=["give"])
def give_access(message):
    # только админ может выдавать доступ
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Ты не админ ❌")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Пиши так: <code>/give 123456789</code>")
        return

    try:
        user_id = int(parts[1])

        # создаём одноразовую ссылку в канал
        link = bot.create_chat_invite_link(
            chat_id=VIP_CHANNEL,
            member_limit=1
        )

        # ⚠️ бот сможет написать пользователю ТОЛЬКО если пользователь уже нажал /start у бота
        bot.send_message(
            user_id,
            "✅ Оплата подтверждена.\n"
            "Вот одноразовая ссылка в VIP канал:\n"
            f"{link.invite_link}"
        )

        bot.send_message(message.chat.id, f"Готово ✅ Ссылка отправлена пользователю {user_id}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


if __name__ == "__main__":
    bot.infinity_polling(timeout=60, long_polling_timeout=60)