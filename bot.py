import telebot

TOKEN = "AAF34ckhpjbuZnW2f5JHMCx-TOeqfwdQ8Z4"

VIP_CHANNEL = "@alphagoldvip_channel"
ADMIN_ID = 123456789

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
    "🔥 VIP GOLD SIGNAL BOT 🔥\n\n"
    "Добро пожаловать в VIP сигналы.\n"
    "Для доступа нужна оплата.\n\n"
    "После оплаты бот автоматически откроет доступ.")

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.send_message(message.chat.id, f"Твой ID: {message.chat.id}")

bot.polling()