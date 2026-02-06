import telebot
import time

TOKEN = "8492510753:AAHK9aIoguNGa6CJMUr2XrXad04Vwk_uF28"
bot = telebot.TeleBot(TOKEN)

VIP_CHANNEL = "@alphagold_elite_signal"
ADMIN_ID = 8394704301  # сюда потом поставим твой ID

# старт
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
    "🔥 VIP GOLD SIGNAL BOT 🔥\n\n"
    "Добро пожаловать в VIP сигналы.\n"
    "Для доступа нужна оплата.\n\n"
    "После оплаты отправь чек сюда.")

# получить id
@bot.message_handler(commands=['id'])
def get_id(message):
    bot.send_message(message.chat.id, f"Твой ID: {message.from_user.id}")

# админ подтверждает оплату
@bot.message_handler(commands=['give'])
def give_access(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.text.split()[1])
        link = bot.create_chat_invite_link(VIP_CHANNEL, member_limit=1)
        bot.send_message(user_id,
        f"Оплата подтверждена ✅\n"
        f"Вот доступ в VIP:\n{link.invite_link}")
        bot.send_message(message.chat.id, "Готово. Доступ выдан.")
    except:
        bot.send_message(message.chat.id, "Ошибка. Пиши: /give ID")

bot.infinity_polling()