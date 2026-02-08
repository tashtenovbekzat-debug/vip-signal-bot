import os
import time
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ====== ВСТАВЬ СЮДА СВОЙ BOT TOKEN ======
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

ADMIN_ID = 8394704301
VIP_CHANNEL = -1003735072360

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ====== АНТИ-ПАДЕНИЕ ======
while True:
    try:

        def menu(uid):
            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add(KeyboardButton("💰 Цена VIP"))
            kb.add(KeyboardButton("✅ Я оплатил"))
            kb.add(KeyboardButton("🆔 Мой ID"))
            if uid == ADMIN_ID:
                kb.add(KeyboardButton("📊 Отправить сигнал"))
            return kb

        # ===== START =====
        @bot.message_handler(commands=["start"])
        def start(msg):
            bot.send_message(
                msg.chat.id,
                "🔥 <b>ALPHA GOLD VIP</b> 🔥\n\n"
                "№1 Gold Signals in world",
                reply_markup=menu(msg.from_user.id)
            )

        # ===== ID =====
        @bot.message_handler(func=lambda m: m.text == "🆔 Мой ID")
        def myid(msg):
            bot.send_message(msg.chat.id, f"Твой ID: <code>{msg.from_user.id}</code>")

        # ===== PRICE =====
        @bot.message_handler(func=lambda m: m.text == "💰 Цена VIP")
        def price(msg):
            bot.send_message(
                msg.chat.id,
                "💎 VIP ДОСТУП\n\n"
                "1 месяц — 200$\n"
                "3 месяца — 500$\n\n"
                "После оплаты нажми: Я оплатил"
            )

        # ===== PAYMENT =====
        @bot.message_handler(func=lambda m: m.text == "✅ Я оплатил")
        def paid(msg):
            user = msg.from_user.id
            username = msg.from_user.username or "none"

            bot.send_message(
                ADMIN_ID,
                f"💸 ОПЛАТА\n\nID: {user}\n@{username}\n\n"
                f"Ответь:\n/ok {user} 30\nили\n/ok {user} 90"
            )

            bot.send_message(msg.chat.id, "⏳ Ожидай подтверждение")

        # ===== OK ADMIN =====
        @bot.message_handler(commands=["ok"])
        def ok(msg):
            if msg.from_user.id != ADMIN_ID:
                return

            try:
                parts = msg.text.split()
                user_id = int(parts[1])
                days = int(parts[2])

                link = bot.create_chat_invite_link(
                    chat_id=VIP_CHANNEL,
                    member_limit=1
                )

                bot.send_message(
                    user_id,
                    f"✅ Оплата подтверждена\n"
                    f"Доступ: {days} дней\n\n"
                    f"Вход в VIP:\n{link.invite_link}"
                )

                bot.send_message(msg.chat.id, "Готово")

            except Exception as e:
                bot.send_message(msg.chat.id, f"Ошибка: {e}")

        # ===== SEND SIGNAL ADMIN =====
        @bot.message_handler(func=lambda m: m.text == "📊 Отправить сигнал")
        def siginfo(msg):
            if msg.from_user.id != ADMIN_ID:
                return
            bot.send_message(msg.chat.id, "Отправь так:\n/signal BUY 2031 2040 2050 2020")

        @bot.message_handler(commands=["signal"])
        def signal(msg):
            if msg.from_user.id != ADMIN_ID:
                return
            try:
                parts = msg.text.split()
                direction = parts[1]
                entry = parts[2]
                tp1 = parts[3]
                tp2 = parts[4]
                sl = parts[5]

                text = (
                    "👑 <b>ALPHA GOLD VIP SIGNAL</b>\n\n"
                    f"Direction: <b>{direction}</b>\n"
                    f"Entry: {entry}\n"
                    f"TP1: {tp1}\n"
                    f"TP2: {tp2}\n"
                    f"SL: {sl}\n\n"
                    "🔥 Elite Gold System"
                )

                bot.send_message(VIP_CHANNEL, text)
                bot.send_message(msg.chat.id, "Сигнал отправлен 🚀")

            except:
                bot.send_message(msg.chat.id, "Ошибка формата")

        print("BOT STARTED")
        bot.infinity_polling()

    except Exception as e:
        print("CRASH:", e)
        time.sleep(5)