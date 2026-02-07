import os
import telebot

TOKEN = os.getenv"8492510753:AAHK9aIoguNGa6CJMUr2XrXad04Vwk_uF28".strip()
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Лучше использовать ID канала вида -100xxxxxxxxxx
VIP_CHANNEL = os.getenv("VIP_CHANNEL", "").strip()
if not VIP_CHANNEL:
    raise ValueError("VIP_CHANNEL is not set")

ADMIN_ID = os.getenv("ADMIN_ID", "").strip()
if not ADMIN_ID:
    raise ValueError("ADMIN_ID is not set")
ADMIN_ID = int(ADMIN_ID)8394704301

# (необязательно) цена/текст оплаты
PRICE_TEXT = os.getenv("PRICE_TEXT", "Для доступа нужна оплата. Напиши администратору.").strip()


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>VIP GOLD SIGNAL BOT</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы.\n"
        f"{PRICE_TEXT}\n\n"
        "Команда для проверки: /id",
    )


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

        # IMPORTANT:
        # бот должен быть админом в канале и иметь право создавать инвайты
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


if __name__ == "__main__":
    # long polling для Railway
    bot.infinity_polling(timeout=60, long_polling_timeout=60)