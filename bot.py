import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ====== НАСТРОЙКИ (токен только в Railway Variables) ======
BOT_TOKEN = os.getenv("BOT_TOKEN", "8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in Railway Variables")

ADMIN_ID = 8394704301  # твой Telegram ID (админ)
VIP_CHANNEL = -1003735072360  # твой VIP канал (chat_id)

PRICE_TEXT = (
    "💎 VIP доступ:\n\n"
    "1 месяц — 200$\n"
    "3 месяца — 500$\n\n"
    "После оплаты нажми: ✅ Я оплатил"
)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Цена VIP"))
    kb.add(KeyboardButton("✅ Я оплатил"))
    kb.add(KeyboardButton("🆔 Мой ID"))
    return kb


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>ALPHA GOLD VIP</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы 📈\n"
        "Выбери действие ниже:",
        reply_markup=main_menu()
    )


@bot.message_handler(commands=["ping"])
def ping(message):
    bot.reply_to(message, "pong ✅ Бот работает")


@bot.message_handler(commands=["id"])
def cmd_id(message):
    bot.send_message(message.chat.id, f"Твой ID: <code>{message.from_user.id}</code>")


@bot.message_handler(func=lambda m: m.text == "🆔 Мой ID")
def btn_id(message):
    cmd_id(message)


@bot.message_handler(func=lambda m: m.text == "💰 Цена VIP")
def btn_price(message):
    bot.send_message(message.chat.id, PRICE_TEXT)


@bot.message_handler(func=lambda m: m.text == "✅ Я оплатил")
def btn_paid(message):
    user_id = message.from_user.id
    username = message.from_user.username or "-"

    text = (
        "💸 <b>Новая оплата</b>\n\n"
        f"ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n\n"
        f"Подтвердить:\n<code>/ok {user_id}</code>"
    )

    # 1) Пишем админу в ЛИЧКУ (это тебе)
    bot.send_message(ADMIN_ID, text)

    # 2) (необязательно) Пишем в канал — только если бот админ и имеет право постить
    try:
        bot.send_message(VIP_CHANNEL, f"Заявка на доступ от <code>{user_id}</code> (@{username})")
    except Exception:
        pass

    bot.send_message(message.chat.id, "⏳ Отправлено админу. Ожидай доступ.")


@bot.message_handler(commands=["ok"])
def approve(message):
    # Только админ подтверждает
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Ты не админ ❌")
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Пиши так: <code>/ok 123456789</code>")
        return

    try:
        user_id = int(parts[1])

        # Создаём одноразовую ссылку в VIP канал
        # ВАЖНО: бот должен быть админом в канале и иметь право "Manage invite links"
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
    bot.infinity_polling(timeout=60, long_polling_timeout=60)