import os
import telebot

TOKEN = os.getenv("8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU", "").strip()
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

ADMIN_ID = int(os.getenv("ADMIN_ID", "8394704301").strip() or "0")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID is not set")

VIP_CHANNEL = os.getenv("VIP_CHANNEL", "-1003735072360").strip()
if not VIP_CHANNEL:
    raise ValueError("VIP_CHANNEL is not set")
VIP_CHANNEL = int(VIP_CHANNEL)  # должен быть -100...

PRICE_TEXT = os.getenv("PRICE_TEXT", "Для доступа нужна оплата. Напиши администратору.").strip()

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id,
                     "🔥 <b>VIP GOLD SIGNAL BOT</b> 🔥\n\n"
                     "Добро пожаловать в VIP сигналы.\n"
                     f"{PRICE_TEXT}\n\n"
                     "Команды:\n"
                     "• /id — узнать свой ID\n"
                     "• /ping — проверка бота\n")


@bot.message_handler(commands=["ping"])
def ping(m):
    bot.reply_to(m, "pong ✅")


@bot.message_handler(commands=["id"])
def get_id(m):
    bot.send_message(m.chat.id, f"Твой ID: <code>{m.from_user.id}</code>")


@bot.message_handler(commands=["give"])
def give(m):
    if m.from_user.id != ADMIN_ID:
        bot.send_message(m.chat.id, "Ты не админ ❌")
        return

    parts = m.text.split()
    if len(parts) < 2:
        bot.send_message(m.chat.id, "Пиши так: <code>/give 123456789</code>")
        return

    user_id = int(parts[1])

    link = bot.create_chat_invite_link(chat_id=VIP_CHANNEL, member_limit=1)

    bot.send_message(user_id,
                     "✅ Оплата подтверждена.\n"
                     "Вот одноразовая ссылка в VIP канал:\n"
                     f"{link.invite_link}")

    bot.send_message(m.chat.id, f"Готово ✅ Ссылка отправлена пользователю {user_id}")


if __name__ == "__main__":
    bot.infinity_polling(timeout=60, long_polling_timeout=60)