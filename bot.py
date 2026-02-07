import os
import telebot

TOKEN = os.getenv("8492510753:AAHK9aIoguNGa6CJMUr2XrXad04Vwk_uF28", "").import os
import telebot

TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

VIP_CHANNEL = os.getenv("VIP_CHANNEL", "").strip()
if not VIP_CHANNEL:
    raise ValueError("VIP_CHANNEL is not set (use -100xxxxxxxxxx from @RawDataBot)")

ADMIN_ID = os.getenv("ADMIN_ID", "").strip()
if not ADMIN_ID:
    raise ValueError("ADMIN_ID is not set")
ADMIN_ID = int(ADMIN_ID)

PRICE_TEXT = os.getenv(
    "PRICE_TEXT",
    "Доступ в VIP канал платный. Напиши администратору."
).strip()

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


def resolve_chat_id(chat_value: str) -> int | str:
    """
    Возвращает chat_id (int) если возможно.
    Если передали @username — пробует получить id через get_chat().
    """
    v = chat_value.strip()
    if v.lstrip("-").isdigit():
        return int(v)

    # пробуем как @username
    try:
        chat = bot.get_chat(v)
        return chat.id
    except Exception:
        # оставим как есть, но create_chat_invite_link может упасть
        return v


RESOLVED_VIP_CHAT = resolve_chat_id(VIP_CHANNEL)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>VIP GOLD SIGNAL BOT</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы.\n"
        f"{PRICE_TEXT}\n\n"
        "Команды:\n"
        "• /id — узнать свой ID\n"
        "• /price — цена/условия\n"
    )


@bot.message_handler(commands=["id"])
def get_id(message):
    bot.send_message(message.chat.id, f"Твой ID: <code>{message.from_user.id}</code>")


@bot.message_handler(commands=["price"])
def price(message):
    bot.send_message(message.chat.id, PRICE_TEXT)


@bot.message_handler(commands=["debug"])
def debug(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        f"ADMIN_ID ok: <code>{ADMIN_ID}</code>\n"
        f"VIP_CHANNEL env: <code>{VIP_CHANNEL}</code>\n"
        f"VIP resolved: <code>{RESOLVED_VIP_CHAT}</code>"
    )
    try:
        chat = bot.get_chat(RESOLVED_VIP_CHAT)
        bot.send_message(message.chat.id, f"Bot sees channel ✅\nTitle: <b>{chat.title}</b>\nID: <code>{chat.id}</code>")
    except Exception as e:
        bot.send_message(message.chat.id, f"Bot DOES NOT see channel ❌\nОшибка: <code>{e}</code>")


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

        # Создаем одноразовую ссылку
        link = bot.create_chat_invite_link(
            chat_id=RESOLVED_VIP_CHAT,
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
        bot.send_message(
            message.chat.id,
            "❌ Ошибка при выдаче доступа.\n\n"
            "Чаще всего причины:\n"
            "1) VIP_CHANNEL не -100…\n"
            "2) бот не админ канала или нет права Invite links\n\n"
            f"Текст ошибки: <code>{e}</code>"
        )


if __name__ == "__main__":
    bot.infinity_polling(timeout=60, long_polling_timeout=60)strip()
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

VIP_CHANNEL = os.getenv("VIP_CHANNEL", "").strip()
if not VIP_CHANNEL:
    raise ValueError("VIP_CHANNEL is not set (use -100xxxxxxxxxx from @RawDataBot)")

ADMIN_ID = os.getenv("ADMIN_ID", "").strip()
if not ADMIN_ID:
    raise ValueError("ADMIN_ID is not set")
ADMIN_ID = int(ADMIN_ID)

PRICE_TEXT = os.getenv(
    "PRICE_TEXT",
    "Доступ в VIP канал платный. Напиши администратору."
).strip()

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


def resolve_chat_id(chat_value: str) -> int | str:
    """
    Возвращает chat_id (int) если возможно.
    Если передали @username — пробует получить id через get_chat().
    """
    v = chat_value.strip()
    if v.lstrip("-").isdigit():
        return int(v)

    # пробуем как @username
    try:
        chat = bot.get_chat(v)
        return chat.id
    except Exception:
        # оставим как есть, но create_chat_invite_link может упасть
        return v


RESOLVED_VIP_CHAT = resolve_chat_id(VIP_CHANNEL)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>VIP GOLD SIGNAL BOT</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы.\n"
        f"{PRICE_TEXT}\n\n"
        "Команды:\n"
        "• /id — узнать свой ID\n"
        "• /price — цена/условия\n"
    )


@bot.message_handler(commands=["id"])
def get_id(message):
    bot.send_message(message.chat.id, f"Твой ID: <code>{message.from_user.id}</code>")


@bot.message_handler(commands=["price"])
def price(message):
    bot.send_message(message.chat.id, PRICE_TEXT)


@bot.message_handler(commands=["debug"])
def debug(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        f"ADMIN_ID ok: <code>{ADMIN_ID}</code>\n"
        f"VIP_CHANNEL env: <code>{VIP_CHANNEL}</code>\n"
        f"VIP resolved: <code>{RESOLVED_VIP_CHAT}</code>"
    )
    try:
        chat = bot.get_chat(RESOLVED_VIP_CHAT)
        bot.send_message(message.chat.id, f"Bot sees channel ✅\nTitle: <b>{chat.title}</b>\nID: <code>{chat.id}</code>")
    except Exception as e:
        bot.send_message(message.chat.id, f"Bot DOES NOT see channel ❌\nОшибка: <code>{e}</code>")


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

        # Создаем одноразовую ссылку
        link = bot.create_chat_invite_link(
            chat_id=RESOLVED_VIP_CHAT,
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
        bot.send_message(
            message.chat.id,
            "❌ Ошибка при выдаче доступа.\n\n"
            "Чаще всего причины:\n"
            "1) VIP_CHANNEL не -100…\n"
            "2) бот не админ канала или нет права Invite links\n\n"
            f"Текст ошибки: <code>{e}</code>"
        )


if __name__ == "__main__":
    bot.infinity_polling(timeout=60, long_polling_timeout=60)