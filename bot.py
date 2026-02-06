import telebot

TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН_БОТА"
bot = telebot.TeleBot(TOKEN)

VIP_CHANNEL = "@alphagoldvip_channel"  # сюда потом поставим твой канал
ADMIN_ID = 123456789  # сюда потом поставим твой telegram id

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
    "🔥 VIP GOLD SIGNAL BOT 🔥\n\n"
    "Добро пожаловать в VIP сигналы.\n"
    "Для доступа нужна оплата.\n\n"
    "После оплаты бот автоматически откроет доступ.")

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.send_message(message.chat.id, f"Твой ID: {message.from_user.id}")

bot.polling()