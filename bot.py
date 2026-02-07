import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ВСТАВЬ СЮДА СВОЙ BOT TOKEN
BOT_TOKEN = "8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU"

# ТВОЙ TELEGRAM ID (АДМИН)
ADMIN_ID = 8394704301

# ТВОЙ VIP КАНАЛ (ссылка)
VIP_LINK = "https://t.me/+9CHxKiRNxu41NWJk"

# USDT TRC20 адрес
TRC20_ADDRESS = "TNAUbEavtKGw9DCEAUoM76cRUyDQkBEj8j"

# ЦЕНЫ
PRICE_1M = "200$"
PRICE_3M = "500$"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

user_state = {}
user_plan = {}

def menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💰 Оплатить USDT", callback_data="pay"))
    kb.add(InlineKeyboardButton("✅ Я оплатил", callback_data="paid"))
    kb.add(InlineKeyboardButton("🆔 Мой ID", callback_data="id"))
    return kb

def planmenu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("1 месяц — 200$", callback_data="1m"))
    kb.add(InlineKeyboardButton("3 месяца — 500$", callback_data="3m"))
    return kb

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id,
    "🔥 <b>ALPHA GOLD VIP</b>\n\n"
    "Точные VIP сигналы.\n"
    "Нажми оплатить чтобы получить доступ.",
    reply_markup=menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.from_user.id

    if call.data == "id":
        bot.send_message(uid, f"Твой ID: <code>{uid}</code>")

    if call.data == "pay":
        bot.send_message(uid,
        f"💰 <b>Оплата USDT TRC20</b>\n\n"
        f"Адрес:\n<code>{TRC20_ADDRESS}</code>\n\n"
        f"1 месяц — {PRICE_1M}\n"
        f"3 месяца — {PRICE_3M}\n\n"
        "Выбери тариф:",
        reply_markup=planmenu())

    if call.data == "1m":
        user_plan[uid] = "1 месяц 200$"
        bot.send_message(uid,"После оплаты нажми: ✅ Я оплатил")

    if call.data == "3m":
        user_plan[uid] = "3 месяца 500$"
        bot.send_message(uid,"После оплаты нажми: ✅ Я оплатил")

    if call.data == "paid":
        user_state[uid] = "wait"
        bot.send_message(uid,"Отправь TXID или скрин оплаты сюда.")

@bot.message_handler(content_types=['text','photo'])
def proof(msg):
    uid = msg.from_user.id

    if user_state.get(uid) != "wait":
        return

    user_state[uid] = "done"

    username = msg.from_user.username
    plan = user_plan.get(uid,"не выбрал")

    bot.send_message(ADMIN_ID,
    f"💸 НОВАЯ ОПЛАТА\n\n"
    f"ID: {uid}\n"
    f"User: @{username}\n"
    f"Тариф: {plan}\n\n"
    f"Подтвердить доступ:\n"
    f"/ok {uid}")

    bot.forward_message(ADMIN_ID, msg.chat.id, msg.message_id)

    bot.send_message(uid,"⏳ Отправлено админу. Жди подтверждения.")

@bot.message_handler(commands=['ok'])
def give(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    try:
        uid = int(msg.text.split()[1])
        bot.send_message(uid,
        f"✅ Оплата подтверждена!\n\n"
        f"Вот доступ в VIP:\n{VIP_LINK}")
        bot.send_message(msg.chat.id,"Готово. Пользователь добавлен.")
    except:
        bot.send_message(msg.chat.id,"Ошибка.")

print("BOT STARTED")
bot.infinity_polling()