import os
import time
import telebot

# ================== CONFIG ==================
BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set (Railway Variables)")

ADMIN_ID = 8394704301
VIP_CHANNEL = -1003735072360

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ================== SIGNAL FORMAT ==================
def build_signal(symbol, direction, entry, tp1, tp2, sl):
    direction = (direction or "").upper().strip()
    if direction not in ("BUY", "SELL"):
        direction = "BUY"
    dot = "🟢" if direction == "BUY" else "🔴"
    symbol = (symbol or "XAUUSD").upper().strip()

    return (
        "👑 <b>ALPHA GOLD VIP SIGNAL</b>\n\n"
        f"📊 <b>{symbol}</b>\n"
        f"Signal: <b>{direction}</b> {dot}\n"
        "TF: <b>M5</b>\n\n"
        f"Entry: <b>{entry}</b>\n"
        f"TP1: <b>{tp1}</b>\n"
        f"TP2: <b>{tp2}</b>\n"
        f"SL: <b>{sl}</b>\n\n"
        "Mode: <b>SAFE ELITE</b>\n"
        "Confidence: <b>92-97%</b>\n\n"
        "© <b>ALPHA GOLD PRIVATE</b>"
    )

# ================== BASIC ==================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, "🔥 ALPHA GOLD ULTRA SYSTEM READY\n\nКоманды:\n/ping\n/send ...\n/test")

@bot.message_handler(commands=["ping"])
def ping(msg):
    bot.reply_to(msg, "pong ✅")

# ================== AUTO SIGNAL (ADMIN ONLY) ==================
@bot.message_handler(commands=["send"])
def send_signal(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    # /send XAUUSD BUY 2030 2040 2050 2020
    parts = msg.text.split()
    if len(parts) != 7:
        bot.send_message(ADMIN_ID, "Формат:\n<code>/send XAUUSD BUY entry tp1 tp2 sl</code>")
        return

    _, symbol, direction, entry, tp1, tp2, sl = parts
    text = build_signal(symbol, direction, entry, tp1, tp2, sl)

    # тебе (в личку)
    bot.send_message(ADMIN_ID, "🚀 <b>SIGNAL SENT</b>\n\n" + text)
    # в VIP канал
    bot.send_message(VIP_CHANNEL, text)

@bot.message_handler(commands=["test"])
def test(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    text = build_signal("XAUUSD", "BUY", "TEST", "TP1", "TP2", "SL")
    bot.send_message(ADMIN_ID, text)

# ================== ANTI-CRASH POLLING ==================
def run_forever():
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception:
            time.sleep(3)

if __name__ == "__main__":
    run_forever()