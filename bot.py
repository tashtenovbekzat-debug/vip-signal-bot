import os
import time
import json
import threading
import hashlib
import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from flask import Flask, request, jsonify

# ================== ENV / SETTINGS ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8492510753:AAGHwAzTlKFHn_XsDtimZ98DJxXwOkb3NoU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

ADMIN_ID = int(os.getenv("ADMIN_ID", "8394704301").strip())
VIP_CHANNEL = int(os.getenv("VIP_CHANNEL", "-1003735072360").strip())

# Secret for TradingView webhook protection
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()  # set in Railway Variables
if not WEBHOOK_SECRET:
    WEBHOOK_SECRET = "CHANGE_ME_SECRET"  # обязательно поменяй в Railway Variables

PRICE_TEXT = os.getenv(
    "PRICE_TEXT",
    "💎 <b>ALPHA GOLD VIP</b>\n\n"
    "1 месяц — <b>200$</b>\n"
    "3 месяца — <b>500$</b>\n\n"
    "После оплаты нажми: ✅ <b>Я оплатил</b>"
).strip()

WATERMARK = os.getenv("WATERMARK", "© <b>ALPHA GOLD PRIVATE</b> • Elite System").strip()

# ================== BOT / APP ==================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

# sig_id -> {"text":..., "symbol":..., "dir":..., "created":..., "hash":...}
pending_signals = {}
# sig_id -> {"symbol":..., "dir":..., "tf":..., "entry":..., "tps":[...], "sl":..., "created":...}
sent_signals = {}

# ================== UI ==================
def main_menu(is_admin: bool):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Цена VIP"))
    kb.add(KeyboardButton("✅ Я оплатил"))
    kb.add(KeyboardButton("🆔 Мой ID"))
    if is_admin:
        kb.add(KeyboardButton("🧪 L1 Test Signal"))
        kb.add(KeyboardButton("📝 Создать сигнал"))
    return kb

def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def _new_sig_id() -> str:
    return str(int(time.time() * 1000))

def _short_hash(s: str) -> str:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return h[:10]

def build_signal_text(
    symbol: str,
    direction: str,
    tf: str,
    entry: str,
    tps: list,
    sl: str,
    confidence: str = "88-92%",
    mode: str = "SAFE ELITE",
    sig_id: str | None = None
) -> str:
    symbol = (symbol or "XAUUSD").upper().strip()
    direction = (direction or "BUY").upper().strip()
    tf = (tf or "M5").upper().strip()

    if direction not in ("BUY", "SELL"):
        direction = "BUY"

    arrow = "🟢" if direction == "BUY" else "🔴"
    tps = [str(x) for x in (tps or []) if str(x).strip()]
    while len(tps) < 2:
        tps.append("—")

    # unique code for anti-leak tracking (basic)
    base = f"{sig_id}|{symbol}|{direction}|{tf}|{entry}|{','.join(tps)}|{sl}|{mode}"
    code = _short_hash(base) if sig_id else _short_hash(base + str(time.time()))

    lines = [
        "👑 <b>ALPHA GOLD ELITE SIGNAL</b>",
        "",
        f"📊 <b>{symbol}</b>  •  TF: <b>{tf}</b>",
        f"Signal: <b>{direction}</b> {arrow}",
        "",
        f"Entry: <b>{entry}</b>",
        f"TP1: <b>{tps[0]}</b>",
        f"TP2: <b>{tps[1]}</b>",
    ]

    if len(tps) >= 3 and tps[2] != "—":
        lines.append(f"TP3: <b>{tps[2]}</b>")

    lines += [
        f"SL: <b>{sl}</b>",
        "",
        f"Mode: <b>{mode}</b>",
        f"Confidence: <b>{confidence}</b>",
        "",
        f"ID: <code>{sig_id or '—'}</code>  •  Code: <code>{code}</code>",
        WATERMARK
    ]
    return "\n".join(lines)

def send_to_admin_for_approve(text_vip: str, title: str, sig_id: str):
    pending_signals[sig_id] = {
        "text": text_vip,
        "created": time.time(),
    }

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("✅ OK → VIP", callback_data=f"appr:{sig_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"rej:{sig_id}")
    )

    bot.send_message(ADMIN_ID, f"📩 <b>{title}</b>\n\n{text_vip}", reply_markup=kb)

def send_result_buttons_to_admin(sig_id: str):
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("TP1 ✅", callback_data=f"res:{sig_id}:tp1"),
        InlineKeyboardButton("TP2 ✅", callback_data=f"res:{sig_id}:tp2"),
        InlineKeyboardButton("TP3 ✅", callback_data=f"res:{sig_id}:tp3"),
    )
    kb.row(
        InlineKeyboardButton("SL ❌", callback_data=f"res:{sig_id}:sl"),
        InlineKeyboardButton("CLOSE 🔒", callback_data=f"res:{sig_id}:close"),
    )
    bot.send_message(ADMIN_ID, f"📊 Управление результатом\nID: <code>{sig_id}</code>", reply_markup=kb)

# ================== BOT COMMANDS ==================
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>ALPHA GOLD VIP</b> 🔥\n\n"
        "Система активна.\n"
        "Выбери действие ниже:",
        reply_markup=main_menu(_is_admin(message.from_user.id))
    )

@bot.message_handler(commands=["ping"])
def ping(message):
    bot.reply_to(message, "pong ✅")

@bot.message_handler(commands=["id"])
def cmd_id(message):
    bot.send_message(message.chat.id, f"Твой ID: <code>{message.from_user.id}</code>")

@bot.message_handler(func=lambda m: m.text == "🆔 Мой ID")
def btn_id(message):
    cmd_id(message)

@bot.message_handler(func=lambda m: m.text == "💰 Цена VIP")
def btn_price(message):
    bot.send_message(message.chat.id, PRICE_TEXT)

@bot.message_handler(func=lambda m: m.text == "✅ Я оплатил")
def btn_paid(message):
    user_id = message.from_user.id
    username = message.from_user.username or "-"

    text = (
        "💸 <b>Новая заявка (оплата)</b>\n\n"
        f"ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n\n"
        f"Подтвердить:\n<code>/ok {user_id}</code>\n\n"
        f"{WATERMARK}"
    )
    bot.send_message(ADMIN_ID, text)
    bot.send_message(message.chat.id, "⏳ Отправлено админу. Ожидай доступ.")

@bot.message_handler(commands=["ok"])
def approve_payment(message):
    if not _is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Ты не админ ❌")
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Пиши так: <code>/ok 123456789</code>")
        return

    try:
        user_id = int(parts[1])
        link = bot.create_chat_invite_link(chat_id=VIP_CHANNEL, member_limit=1)

        bot.send_message(
            user_id,
            "✅ Оплата подтверждена.\n"
            "Вот ссылка в VIP канал (одноразовая):\n"
            f"{link.invite_link}\n\n{WATERMARK}"
        )
        bot.send_message(message.chat.id, f"Готово ✅ Ссылка отправлена пользователю {user_id}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

# ---- L1 Test ----
@bot.message_handler(commands=["l1test"])
def l1test_cmd(message):
    if not _is_admin(message.from_user.id):
        return
    sig_id = _new_sig_id()
    text = build_signal_text(
        symbol="XAUUSD",
        direction="BUY",
        tf="M5",
        entry="TEST",
        tps=["TEST", "TEST", "—"],
        sl="TEST",
        confidence="TEST",
        mode="L1 TEST",
        sig_id=sig_id
    )
    send_to_admin_for_approve(text, "L1 TEST SIGNAL", sig_id)

@bot.message_handler(func=lambda m: m.text == "🧪 L1 Test Signal")
def l1test_btn(message):
    if not _is_admin(message.from_user.id):
        return
    l1test_cmd(message)

# ---- Manual signal creation ----
@bot.message_handler(commands=["signal"])
def signal_cmd(message):
    """
    Format:
    /signal BUY entry tp1 tp2 sl [tp3]
    Example:
    /signal BUY 2031 2039 2046 2024
    /signal SELL 2040 2032 2024 2048 2015
    """
    if not _is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Только админ ❌")
        return

    parts = message.text.split()
    if len(parts) not in (6, 7):
        bot.send_message(
            message.chat.id,
            "Формат:\n"
            "<code>/signal BUY entry tp1 tp2 sl [tp3]</code>\n\n"
            "Пример:\n"
            "<code>/signal BUY 2031 2039 2046 2024</code>"
        )
        return

    direction = parts[1]
    entry = parts[2]
    tp1 = parts[3]
    tp2 = parts[4]
    sl = parts[5]
    tp3 = parts[6] if len(parts) == 7 else None

    sig_id = _new_sig_id()
    tps = [tp1, tp2]
    if tp3:
        tps.append(tp3)

    text = build_signal_text(
        symbol="XAUUSD",
        direction=direction,
        tf="M5",
        entry=entry,
        tps=tps,
        sl=sl,
        confidence="88-92%",
        mode="SAFE ELITE",
        sig_id=sig_id
    )
    send_to_admin_for_approve(text, "NEW SIGNAL (MANUAL)", sig_id)

@bot.message_handler(func=lambda m: m.text == "📝 Создать сигнал")
def signal_btn(message):
    if not _is_admin(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        "Создай сигнал командой:\n"
        "<code>/signal BUY entry tp1 tp2 sl [tp3]</code>\n\n"
        "Пример:\n"
        "<code>/signal BUY 2031 2039 2046 2024</code>"
    )

# ---- Callback buttons (approve/reject/results) ----
@bot.callback_query_handler(func=lambda c: True)
def on_callback(call):
    if not _is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "Только админ", show_alert=True)
        return

    data = call.data or ""

    try:
        # Approve signal -> send to VIP and save as sent
        if data.startswith("appr:"):
            sig_id = data.split(":", 1)[1]
            item = pending_signals.pop(sig_id, None)
            if not item:
                bot.answer_callback_query(call.id, "Сигнал не найден", show_alert=True)
                return

            bot.send_message(VIP_CHANNEL, item["text"])
            bot.answer_callback_query(call.id, "Отправлено в VIP ✅")

            # store minimal info for results
            sent_signals[sig_id] = {"created": time.time()}
            send_result_buttons_to_admin(sig_id)
            return

        # Reject
        if data.startswith("rej:"):
            sig_id = data.split(":", 1)[1]
            pending_signals.pop(sig_id, None)
            bot.answer_callback_query(call.id, "Отклонено ❌")
            return

        # Results posting
        if data.startswith("res:"):
            _, sig_id, action = data.split(":", 2)

            if sig_id not in sent_signals:
                bot.answer_callback_query(call.id, "Нет такого отправленного сигнала", show_alert=True)
                return

            if action == "tp1":
                bot.send_message(VIP_CHANNEL, f"✅ <b>TP1 HIT</b>\nID: <code>{sig_id}</code>\n{WATERMARK}")
                bot.answer_callback_query(call.id, "TP1 posted ✅")
            elif action == "tp2":
                bot.send_message(VIP_CHANNEL, f"✅ <b>TP2 HIT</b>\nID: <code>{sig_id}</code>\n{WATERMARK}")
                bot.answer_callback_query(call.id, "TP2 posted ✅")
            elif action == "tp3":
                bot.send_message(VIP_CHANNEL, f"✅ <b>TP3 HIT</b>\nID: <code>{sig_id}</code>\n{WATERMARK}")
                bot.answer_callback_query(call.id, "TP3 posted ✅")
            elif action == "sl":
                bot.send_message(VIP_CHANNEL, f"❌ <b>SL HIT</b>\nID: <code>{sig_id}</code>\n{WATERMARK}")
                bot.answer_callback_query(call.id, "SL posted ❌")
            elif action == "close":
                bot.send_message(VIP_CHANNEL, f"🔒 <b>TRADE CLOSED</b>\nID: <code>{sig_id}</code>\n{WATERMARK}")
                bot.answer_callback_query(call.id, "Closed 🔒")
                # remove tracking
                sent_signals.pop(sig_id, None)
            else:
                bot.answer_callback_query(call.id, "Unknown action", show_alert=True)
            return

        bot.answer_callback_query(call.id, "Unknown command", show_alert=True)

    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка: {e}", show_alert=True)

# ================== WEBHOOK (TradingView -> Bot) ==================
@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.post("/webhook")
def webhook():
    # protection
    secret = request.args.get("secret", "").strip()
    if secret != WEBHOOK_SECRET:
        return jsonify({"ok": False, "error": "forbidden"}), 403

    try:
        payload = request.get_json(force=True) or {}
    except Exception:
        payload = {}

    # expected payload keys (you can customize in TradingView alert message JSON)
    symbol = payload.get("symbol", "XAUUSD")
    direction = payload.get("direction", "BUY")
    tf = payload.get("tf", "M5")
    entry = str(payload.get("entry", "—"))
    sl = str(payload.get("sl", "—"))
    tp1 = str(payload.get("tp1", payload.get("tp", "—")))
    tp2 = str(payload.get("tp2", "—"))
    tp3 = str(payload.get("tp3", ""))
    confidence = str(payload.get("confidence", "88-92%"))
    mode = str(payload.get("mode", "AUTO ELITE"))

    tps = [tp1, tp2]
    if tp3:
        tps.append(tp3)

    sig_id = _new_sig_id()
    text = build_signal_text(
        symbol=symbol,
        direction=direction,
        tf=tf,
        entry=entry,
        tps=tps,
        sl=sl,
        confidence=confidence,
        mode=mode,
        sig_id=sig_id
    )

    # send to admin for approval
    send_to_admin_for_approve(text, "AUTO SIGNAL (WEBHOOK)", sig_id)

    return jsonify({"ok": True, "sig_id": sig_id})

# ================== RUN BOTH (Flask + Telebot) ==================
def run_bot_polling():
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == "__main__":
    t = threading.Thread(target=run_bot_polling, daemon=True)
    t.start()

    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)