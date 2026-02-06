import telebot

TOKEN = "8492510753:AAHK9aIoguNGa6CJMUr2XrXad04Vwk_uF28"
bot = telebot.TeleBot(TOKEN)

VIP_CHANNEL = "@alphagold_elite_signal"
ADMIN_ID = 8394704301

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
    "🔥 VIP GOLD SIGNAL BOT 🔥\n\n"
    "Добро пожаловать в VIP сигналы.\n"
    "Для доступа нужна оплата.\n\n"
    "После оплаты бот откроет доступ.")

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.send_message(message.chat.id, f"Твой ID: {message.from_user.id}")

bot.polling()