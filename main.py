import os
import time
import telebot

# ====== CONFIG ======
BOT_TOKEN = (os.getenv("BOT_TOKEN") or "8492510753:AAFhTasMnqf-Mi-OhLVFrRsC74lol0_imVU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in Railway Variables")

ADMIN_ID = 8394704301
VIP_CHANNEL = -1003735072360

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

WATERMARK = "© <b>ALPHA GOLD PRIVATE</b>"

# ===== СИГНАЛ ФОРМАТ =====
def build_signal(symbol, direction, entry, tp1, tp2, sl, tf="M5", confidence="92-97%", mode="SAFE ELITE"):
    direction = (direction or "").upper().strip()
    if direction not in ("BUY", "SELL"):
        direction = "BUY"
    dot = "🟢" if direction == "BUY" else "🔴"
    symbol = (symbol or "XAUUSD").upper().strip()

    return (
        "👑 <b>ALPHA GOLD VIP SIGNAL</b>\n\n"
        f"📊 <b>{symbol}</b>\n"
        f"Signal: <b>{direction}</b> {dot}\n"
        f"TF: <b>{tf}</b>\n\n"
        f"Entry: <b>{entry}</b>\n"
        f"TP1: <b>{tp1}</b>\n"
        f"TP2: <b>{tp2}</b>\n"
        f"SL: <b>{sl}</b>\n\n"
        f"Mode: <b>{mode}</b>\n"
        f"Confidence: <b>{confidence}</b>\n\n"
        f"{WATERMARK}"
    )

# ===== START / PING =====
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, "🔥 <b>ALPHA GOLD VIP</b> ✅\n\nБот онлайн.\nКоманда: /send")

@bot.message_handler(commands=["ping"])
def ping(msg):
    bot.reply_to(msg, "pong ✅")

# ===== АВТО СИГНАЛ (тебе + VIP) =====
@bot.message_handler(commands=["send"])
def send_signal(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    parts = msg.text.split()
    # /send XAUUSD BUY 2030 2040 2050 2020
    if len(parts) != 7:
        bot.send_message(ADMIN_ID, "Формат:\n<code>/send XAUUSD BUY entry tp1 tp2 sl</code>")
        return

    _, symbol, direction, entry, tp1, tp2, sl = parts
    text = build_signal(symbol, direction, entry, tp1, tp2, sl)

    # тебе
    bot.send_message(ADMIN_ID, "🚀 <b>SIGNAL SENT</b>\n\n" + text)
    # VIP канал
    bot.send_message(VIP_CHANNEL, text)

# ===== TEST =====
@bot.message_handler(commands=["test"])
def test(msg):
    if msg.from_user.id == ADMIN_ID:
        text = build_signal("XAUUSD", "BUY", "TEST", "TP1", "TP2", "SL")
        bot.send_message(ADMIN_ID, text)

def run():
    # ВАЖНО: отключаем webhook, иначе polling часто "молчит"
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception:
        pass

    print("ALPHA GOLD RUNNING...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            print("Polling error:", e)
            time.sleep(3)

if __name__ == "__main__":
    run()