import os
import telebot

TOKEN = os.getenv("BOT_TOKEN", "8492510753:AAGesCCRSWAQe9hvYwBRgRhOxGqY3D5YxGA").strip()
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

ADMIN_ID = os.getenv("ADMIN_ID", "8394704301").strip()
if not ADMIN_ID:
    raise ValueError("ADMIN_ID is not set")
ADMIN_ID = int(ADMIN_ID)

bot = telebot.TeleBot(TOKEN)

# 1) Когда в канале появится пост — бот поймает его и пришлёт тебе chat.id
@bot.channel_post_handler(func=lambda m: True)
def catch_channel_post(message):
    chat_id = message.chat.id
    title = message.chat.title
    bot.send_message(ADMIN_ID, f"✅ Channel detected!\nTitle: {title}\nVIP_CHANNEL = {chat_id}")

# 2) Команда для проверки что бот жив
@bot.message_handler(commands=["ping"])
def ping(message):
    bot.reply_to(message, "pong ✅")

if __name__ == "__main__":
    bot.infinity_polling(timeout=60, long_polling_timeout=60)