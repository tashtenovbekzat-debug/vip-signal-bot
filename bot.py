import telebot

TOKEN = "8492510753:AAHFLsoMJsjNtL79DCElEthTCd4Lkh7z7_Y"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
    "🔥 VIP GOLD SIGNAL BOT 🔥\n\n"
    "Добро пожаловать в VIP сигналы.\n"
    "Для доступа нужна оплата.\n"
    "После оплаты бот откроет доступ.")

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.send_message(message.chat.id, f"Твой ID: {message.from_user.id}")

print("Бот запущен...")
bot.infinity_polling()