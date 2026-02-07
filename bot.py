import os
import telebot

def must_env(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise ValueError(f"{name} is not set")
    return v

BOT_TOKEN = must_env("8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU")
ADMIN_ID = int(must_env("8394704301"))

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

WELCOME_TEXT = (
    "🔥 <b>VIP GOLD SIGNAL BOT</b> 🔥\n\n"
    "Добро пожаловать в VIP.\n"
    "Для доступа нужна оплата.\n\n"
    "✅ Узнать свой ID: /id\n"
    "✍️ Напиши любое сообщение — я отправлю заявку админу."
)

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, WELCOME_TEXT)

@bot.message_handler(commands=["ping"])
def ping(m):
    bot.reply_to(m, "pong ✅")

@bot.message_handler(commands=["id"])
def get_id(m):
    bot.send_message(m.chat.id, f"Твой ID: <code>{m.from_user.id}</code>")

# Админ подтверждает заявку (просто отметка)
@bot.message_handler(commands=["ok"])
def ok(m):
    if m.from_user.id != ADMIN_ID:
        bot.reply_to(m, "Ты не админ ❌")
        return

    parts = m.text.split()
    if len(parts) < 2:
        bot.reply_to(m, "Пиши так: <code>/ok 123456789</code>")
        return

    user_id = int(parts[1])
    try:
        bot.send_message(user_id, "✅ Оплата подтверждена. Админ скоро добавит тебя в VIP.")
        bot.reply_to(m, f"Готово ✅ Я сообщил пользователю {user_id}")
    except Exception as e:
        bot.reply_to(m, f"Не смог написать пользователю. Он должен нажать /start.\nОшибка: {e}")

# Любое сообщение от пользователя = заявка админу
@bot.message_handler(func=lambda m: True)
def application(m):
    user_id = m.from_user.id
    username = m.from_user.username or "-"
    name = (m.from_user.first_name or "") + (" " + m.from_user.last_name if m.from_user.last_name else "")
    text = (
        "🆕 <b>Заявка в VIP</b>\n"
        f"ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n"
        f"Имя: {name.strip() if name.strip() else '-'}\n\n"
        f"Сообщение: {m.text}\n\n"
        f"Команда подтверждения: <code>/ok {user_id}</code>"
    )

    try:
        bot.send_message(ADMIN_ID, text)
    except Exception:
        pass

    bot.reply_to(m, "✅ Заявка отправлена админу. Ожидай ответ.")

if __name__ == "__main__":
    # Пинг админу при старте (чтобы видеть что бот жив)
    try:
        bot.send_message(ADMIN_ID, "✅ Бот запущен и работает.")
    except Exception:
        pass

    bot.infinity_polling(timeout=60, long_polling_timeout=60)