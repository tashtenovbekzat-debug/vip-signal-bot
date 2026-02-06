import os
import telebot

TOKEN = os.getenv
8492510753:AAF34ckhpjbuZnW2f5JHMCx-TOeqfwdQ8Z4
# Проверка токена
if not TOKEN or ":" not in TOKEN:
    raise ValueError("BOT_TOKEN is missing or invalid (must contain ':')")

# ВАЖНО: bot создаём ДО декораторов
bot = telebot.TeleBot(TOKEN)

VIP_CHANNEL = os.getenv("VIP_CHANNEL", "@alphagoldvip_channel")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 VIP GOLD SIGNAL BOT 🔥\n\n"
        "Добро пожаловать в VIP сигналы.\n"
        "Для доступа нужна оплата.\n\n"
        "После оплаты бот автоматически откроет доступ."
    )

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.send_message(message.chat.id, f"Твой ID: {message.chat.id}")

print("Bot is running...")
bot.infinity_polling(skip_pending=True)