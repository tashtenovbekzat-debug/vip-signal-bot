import os
import telebot
from telebot.apihelper import ApiTelegramException

def must_env(name: str) -> str:
    val = os.getenv(name, "").strip()
    if not val:
        raise ValueError(f"{name} is not set (Railway Variables)")
    return val

BOT_TOKEN = must_env"8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU"
ADMIN_ID = int(must_enc"8394704301")
VIP_CHANNEL = must_env"-1003735072360"  # должно быть -100xxxxxxxxxx

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


def notify_admin(text: str):
    try:
        bot.send_message(ADMIN_ID, text)
    except Exception:
        pass


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>VIP GOLD SIGNAL BOT</b> 🔥\n\n"
        "Доступ в VIP канал платный. Напиши администратору.\n\n"
        "Команды:\n"
        "• /id — узнать свой ID\n"
        "• /ping — проверить бота"
    )


@bot.message_handler(commands=["ping"])
def ping(message):
    bot.reply_to(message, "pong ✅")


@bot.message_handler(commands=["id"])
def get_id(message):
    bot.send_message(message.chat.id, f"Твой ID: <code>{message.from_user.id}</code>")


@bot.message_handler(commands=["give"])
def give_access(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Ты не админ ❌")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Пиши так: <code>/give 123456789</code>")
        return

    try:
        user_id = int(parts[1])

        # создаём одноразовую ссылку
        link = bot.create_chat_invite_link(
            chat_id=VIP_CHANNEL,
            member_limit=1
        )

        bot.send_message(
            user_id,
            "✅ Оплата подтверждена.\n"
            "Вот одноразовая ссылка в VIP канал:\n"
            f"{link.invite_link}"
        )
        bot.reply_to(message, f"Готово ✅ Ссылка отправлена пользователю {user_id}")

    except ApiTelegramException as e:
        # самые частые ошибки разжёвываем
        msg = str(e)
        if "chat not found" in msg:
            bot.reply_to(message,
                "❌ chat not found.\n"
                "Проверь VIP_CHANNEL (должен быть -100xxxxxxxxxx) и что бот добавлен админом в канал."
            )
        elif "not enough rights" in msg or "CHAT_ADMIN_REQUIRED" in msg:
            bot.reply_to(message,
                "❌ У бота нет прав.\n"
                "Сделай бота админом в канале и включи право 'Invite Users / Add Users'."
            )
        else:
            bot.reply_to(message, f"❌ Ошибка Telegram: {e}")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")


if __name__ == "__main__":
    notify_admin("✅ Бот запустился и в сети.")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)