import os
import time
import json
import threading
import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ================== CONFIG ==================
BOT_TOKEN = (os.getenv("BOT_TOKEN") or "8492510753:AAFhTasMnqf-Mi-OhLVFrRsC74lol0_imVU").strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in Railway Variables")

ADMIN_ID = 8394704301
VIP_CHANNEL = -1003735072360  # канал/супергруппа

SEND_REQUESTS_TO_VIP_CHANNEL = (os.getenv("SEND_REQUESTS_TO_VIP_CHANNEL") or "0").strip() == "1"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ================== TEXT / BRAND ==================
PRICE_TEXT = (
    "💎 <b>ALPHA GOLD VIP</b>\n\n"
    "✅ 1 месяц — <b>200$</b>\n"
    "✅ 3 месяца — <b>500$</b>\n\n"
    "После оплаты нажми: ✅ <b>Я оплатил</b>"
)
WATERMARK = "© <b>ALPHA GOLD PRIVATE</b> • Elite System"

# ================== STORAGE (подписки) ==================
SUBS_FILE = "subs.json"
LOCK = threading.Lock()
subs = {}  # "user_id": {"expires_at": int, "plan_days": int, "granted_at": int}

def load_subs():
    global subs
    try:
        if os.path.exists(SUBS_FILE):
            with open(SUBS_FILE, "r", encoding="utf-8") as f:
                subs = json.load(f)
        else:
            subs = {}
    except Exception:
        subs = {}

def save_subs():
    try:
        with open(SUBS_FILE, "w", encoding="utf-8") as f:
            json.dump(subs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

load_subs()

# ================== ANTI-2-WORKERS ==================
LOCK_FILE = "/tmp/bot.lock"
_leader_lock_handle = None

def acquire_leader_lock() -> bool:
    global _leader_lock_handle
    try:
        _leader_lock_handle = open(LOCK_FILE, "w")
        if os.name == "posix":
            import fcntl
            fcntl.flock(_leader_lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        _leader_lock_handle.write(str(os.getpid()))
        _leader_lock_handle.flush()
        return True
    except Exception:
        return False

IS_LEADER = acquire_leader_lock()

# ================== SIGNAL FORMAT ==================
def build_signal_text(symbol: str, direction: str, entry: str, tp1: str, tp2: str, sl: str,
                      tf: str = "M5", confidence: str = "92-97%", mode: str = "SAFE ELITE",
                      tp3: str | None = None) -> str:
    d = (direction or "").upper().strip()
    if d not in ("BUY", "SELL"):
        d = "BUY"
    dot = "🟢" if d == "BUY" else "🔴"
    symbol = (symbol or "XAUUSD").upper().strip()

    lines = [
        "👑 <b>ALPHA GOLD VIP SIGNAL</b>",
        "",
        f"📊 <b>{symbol}</b>",
        f"Signal: <b>{d}</b> {dot}",
        f"TF: <b>{tf}</b>",
        "",
        f"Entry: <b>{entry}</b>",
        f"TP1: <b>{tp1}</b>",
        f"TP2: <b>{tp2}</b>",
    ]
    if tp3:
        lines.append(f"TP3: <b>{tp3}</b>")
    lines += [
        f"SL: <b>{sl}</b>",
        "",
        f"Mode: <b>{mode}</b>",
        f"Confidence: <b>{confidence}</b>",
        "",
        f"{WATERMARK}"
    ]
    return "\n".join(lines)

# pending_signals: sig_id -> {"text": str, "created": float}
pending_signals = {}

def _new_sig_id() -> str:
    return str(int(time.time() * 1000))

def send_to_admin_for_approve(text_vip: str, title: str = "SIGNAL"):
    sig_id = _new_sig_id()
    pending_signals[sig_id] = {"text": text_vip, "created": time.time()}

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("✅ OK в VIP", callback_data=f"apprsig:{sig_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"rejsig:{sig_id}")
    )
    bot.send_message(ADMIN_ID, f"📩 <b>{title}</b>\n\n{text_vip}", reply_markup=kb)

# ================== VIP HELPERS ==================
def _fmt_dt(ts: int) -> str:
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
    except Exception:
        return str(ts)

def _left_seconds(expires_at: int) -> int:
    return int(expires_at - time.time())

def _human_left(sec: int) -> str:
    if sec <= 0:
        return "0д"
    days = sec // 86400
    hours = (sec % 86400) // 3600
    mins = (sec % 3600) // 60
    if days > 0:
        return f"{days}д {hours}ч"
    if hours > 0:
        return f"{hours}ч {mins}м"
    return f"{mins}м"

def vip_status_text(user_id: int) -> str:
    with LOCK:
        s = subs.get(str(user_id))
    if not s:
        return "VIP: ❌ нет подписки"
    left = _left_seconds(int(s["expires_at"]))
    return (
        "VIP: ✅ активен\n"
        f"Осталось: <b>{_human_left(left)}</b>\n"
        f"До: <code>{_fmt_dt(int(s['expires_at']))}</code>"
    )

def revoke_vip(user_id: int):
    try:
        bot.ban_chat_member(VIP_CHANNEL, user_id)
        bot.unban_chat_member(VIP_CHANNEL, user_id)
    except Exception:
        pass

def grant_vip(user_id: int, plan_days: int):
    expire_date = int(time.time()) + 600
    link = bot.create_chat_invite_link(
        chat_id=VIP_CHANNEL,
        member_limit=1,
        expire_date=expire_date
    )

    now = int(time.time())
    expires_at = now + plan_days * 86400

    with LOCK:
        subs[str(user_id)] = {"expires_at": expires_at, "plan_days": plan_days, "granted_at": now}
        save_subs()

    return link.invite_link, expires_at

def vip_list_text(limit: int = 50) -> str:
    with LOCK:
        items = list(subs.items())
    items.sort(key=lambda x: int(x[1].get("expires_at", 0)), reverse=True)
    items = items[:limit]
    if not items:
        return "VIP List: пусто"
    out = ["📋 <b>VIP List</b>\n"]
    for uid, info in items:
        out.append(
            f"• <code>{uid}</code> — до <code>{_fmt_dt(int(info.get('expires_at', 0)))}</code>"
        )
    out.append("\n⚠️ Если Railway перезапускается и список пропадает — нужен Volume для subs.json.")
    return "\n".join(out)

# ================== UI ==================
def main_menu(user_id: int):
    is_admin = (user_id == ADMIN_ID)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Цена VIP"))
    kb.add(KeyboardButton("✅ Я оплатил"))
    kb.add(KeyboardButton("🆔 Мой ID"))
    kb.add(KeyboardButton("📌 VIP Статус"))
    if is_admin:
        kb.add(KeyboardButton("🧪 L1 Test Signal"))
        kb.add(KeyboardButton("📝 Создать сигнал"))
        kb.add(KeyboardButton("🚀 Авто-сигнал (без подтверждения)"))
        kb.add(KeyboardButton("📋 VIP List"))
    return kb

def admin_payment_keyboard(user_id: int):
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🔥 VIP 30 дней (200$)", callback_data=f"vip:30:{user_id}"),
        InlineKeyboardButton("💎 VIP 90 дней (500$)", callback_data=f"vip:90:{user_id}")
    )
    kb.row(
        InlineKeyboardButton("ℹ️ VIP INFO", callback_data=f"vipinfo:{user_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"viprej:{user_id}")
    )
    return kb

# ================== BASIC ==================
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 <b>ALPHA GOLD VIP</b> 🔥\n\n"
        "Добро пожаловать в VIP сигналы 📈\n"
        "Выбери действие ниже:",
        reply_markup=main_menu(message.from_user.id)
    )

@bot.message_handler(commands=["ping", "health"])
def ping(message):
    bot.reply_to(message, "pong ✅ Бот работает")

@bot.message_handler(commands=["id"])
def cmd_id(message):
    bot.send_message(message.chat.id, f"Твой ID: <code>{message.from_user.id}</code>")

@bot.message_handler(func=lambda m: m.text == "🆔 Мой ID")
def btn_id(message):
    cmd_id(message)

@bot.message_handler(func=lambda m: m.text == "💰 Цена VIP")
def btn_price(message):
    bot.send_message(message.chat.id, PRICE_TEXT)

@bot.message_handler(commands=["vip"])
def vip_cmd(message):
    bot.send_message(message.chat.id, vip_status_text(message.from_user.id))

@bot.message_handler(func=lambda m: m.text == "📌 VIP Статус")
def vip_btn(message):
    bot.send_message(message.chat.id, vip_status_text(message.from_user.id))

# ================== VIP LIST ==================
@bot.message_handler(func=lambda m: m.text == "📋 VIP List")
def vip_list_btn(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, vip_list_text())

@bot.message_handler(commands=["viplist"])
def vip_list_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, vip_list_text())

# ================== PAYMENT REQUEST ==================
last_paid_click = {}  # user_id -> timestamp

@bot.message_handler(func=lambda m: m.text == "✅ Я оплатил")
def btn_paid(message):
    user_id = message.from_user.id
    username = message.from_user.username or "-"

    now = time.time()
    if user_id in last_paid_click and (now - last_paid_click[user_id]) < 20:
        bot.send_message(message.chat.id, "⏳ Уже отправлено. Подожди немного.")
        return
    last_paid_click[user_id] = now

    text = (
        "💸 <b>Новая заявка (оплата)</b>\n\n"
        f"ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n\n"
        "Выдай доступ кнопкой ниже:\n\n"
        f"{WATERMARK}"
    )

    bot.send_message(ADMIN_ID, text, reply_markup=admin_payment_keyboard(user_id))

    if SEND_REQUESTS_TO_VIP_CHANNEL:
        try:
            bot.send_message(VIP_CHANNEL, f"Заявка на доступ от <code>{user_id}</code> (@{username})")
        except Exception:
            pass

    bot.send_message(message.chat.id, "⏳ Заявка отправлена админу. Ожидай доступ.")

# ================== ADMIN: SIGNALS ==================
@bot.message_handler(commands=["l1test"])
def l1test_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Только админ ❌")
        return
    text_vip = build_signal_text("XAUUSD", "BUY", "TEST", "TEST", "TEST", "TEST", tf="M5", confidence="TEST", mode="L1 TEST")
    send_to_admin_for_approve(text_vip, title="L1 TEST SIGNAL")

@bot.message_handler(func=lambda m: m.text == "🧪 L1 Test Signal")
def l1test_btn(message):
    if message.from_user.id != ADMIN_ID:
        return
    l1test_cmd(message)

@bot.message_handler(commands=["signal"])
def signal_cmd(message):
    """
    С подтверждением:
    /signal XAUUSD BUY entry tp1 tp2 sl
    или с TP3:
    /signal3 XAUUSD BUY entry tp1 tp2 tp3 sl
    """
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Только админ ❌")
        return

    parts = message.text.split()
    if len(parts) != 7:
        bot.send_message(message.chat.id,
            "Формат:\n<code>/signal XAUUSD BUY entry tp1 tp2 sl</code>\n"
            "Пример:\n<code>/signal XAUUSD BUY 2031 2039 2046 2024</code>"
        )
        return

    _, symbol, direction, entry, tp1, tp2, sl = parts
    text_vip = build_signal_text(symbol, direction, entry, tp1, tp2, sl, tf="M5", confidence="92-97%", mode="SAFE ELITE")
    send_to_admin_for_approve(text_vip, title="NEW SIGNAL (APPROVE)")

@bot.message_handler(commands=["signal3"])
def signal3_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Только админ ❌")
        return

    parts = message.text.split()
    if len(parts) != 8:
        bot.send_message(message.chat.id,
            "Формат:\n<code>/signal3 XAUUSD BUY entry tp1 tp2 tp3 sl</code>\n"
            "Пример:\n<code>/signal3 XAUUSD BUY 2031 2039 2046 2052 2024</code>"
        )
        return

    _, symbol, direction, entry, tp1, tp2, tp3, sl = parts
    text_vip = build_signal_text(symbol, direction, entry, tp1, tp2, sl, tp3=tp3, tf="M5", confidence="92-97%", mode="SAFE ELITE")
    send_to_admin_for_approve(text_vip, title="NEW SIGNAL TP3 (APPROVE)")

@bot.message_handler(commands=["send"])
def send_auto_cmd(message):
    """
    БЕЗ подтверждения:
    /send XAUUSD BUY entry tp1 tp2 sl
    /send3 XAUUSD BUY entry tp1 tp2 tp3 sl
    """
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) != 7:
        bot.send_message(ADMIN_ID,
            "Формат авто:\n<code>/send XAUUSD BUY entry tp1 tp2 sl</code>\n"
            "Пример:\n<code>/send XAUUSD BUY 2031 2039 2046 2024</code>"
        )
        return

    _, symbol, direction, entry, tp1, tp2, sl = parts
    text_vip = build_signal_text(symbol, direction, entry, tp1, tp2, sl, tf="M5", confidence="92-97%", mode="SAFE ELITE")

    # 1) тебе
    bot.send_message(ADMIN_ID, f"✅ <b>AUTO SENT</b>\n\n{text_vip}")

    # 2) в VIP канал
    try:
        bot.send_message(VIP_CHANNEL, text_vip)
    except Exception as e:
        bot.send_message(ADMIN_ID,
            f"❌ Не смог отправить в VIP канал.\n"
            f"Причина: <code>{e}</code>\n\n"
            "Проверь: бот добавлен в канал и у него есть право <b>Post Messages</b> (для канала) "
            "или право писать (для супергруппы)."
        )
        return

    bot.send_message(message.chat.id, "🚀 Отправлено (auto) ✅")

@bot.message_handler(commands=["send3"])
def send3_auto_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) != 8:
        bot.send_message(ADMIN_ID,
            "Формат авто:\n<code>/send3 XAUUSD BUY entry tp1 tp2 tp3 sl</code>\n"
            "Пример:\n<code>/send3 XAUUSD BUY 2031 2039 2046 2052 2024</code>"
        )
        return

    _, symbol, direction, entry, tp1, tp2, tp3, sl = parts
    text_vip = build_signal_text(symbol, direction, entry, tp1, tp2, sl, tp3=tp3, tf="M5", confidence="92-97%", mode="SAFE ELITE")

    bot.send_message(ADMIN_ID, f"✅ <b>AUTO SENT</b>\n\n{text_vip}")

    try:
        bot.send_message(VIP_CHANNEL, text_vip)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Ошибка отправки в VIP: <code>{e}</code>")
        return

    bot.send_message(message.chat.id, "🚀 Отправлено (auto) ✅")

@bot.message_handler(func=lambda m: m.text == "📝 Создать сигнал")
def signal_btn(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        "С подтверждением (OK/Reject):\n"
        "<code>/signal XAUUSD BUY entry tp1 tp2 sl</code>\n"
        "<code>/signal3 XAUUSD BUY entry tp1 tp2 tp3 sl</code>\n\n"
        "Без подтверждения (сразу в VIP):\n"
        "<code>/send XAUUSD BUY entry tp1 tp2 sl</code>\n"
        "<code>/send3 XAUUSD BUY entry tp1 tp2 tp3 sl</code>"
    )

@bot.message_handler(func=lambda m: m.text == "🚀 Авто-сигнал (без подтверждения)")
def signal_auto_btn(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        "Авто-сигнал (сразу в VIP + тебе):\n"
        "<code>/send XAUUSD BUY entry tp1 tp2 sl</code>\n"
        "<code>/send3 XAUUSD BUY entry tp1 tp2 tp3 sl</code>"
    )

# ================== CALLBACKS ==================
@bot.callback_query_handler(func=lambda c: True)
def on_callback(call):
    try:
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Только админ", show_alert=True)
            return

        data = call.data or ""

        if data.startswith("vip:"):
            _, days_str, user_id_str = data.split(":")
            plan_days = int(days_str)
            user_id = int(user_id_str)

            invite_link, expires_at = grant_vip(user_id, plan_days)

            try:
                bot.send_message(
                    user_id,
                    "✅ <b>Оплата подтверждена.</b>\n"
                    f"План: <b>{plan_days} дней</b>\n"
                    "Ссылка в VIP канал (одноразовая, 10 минут):\n"
                    f"{invite_link}\n\n"
                    f"{WATERMARK}"
                )
            except Exception as e:
                bot.send_message(
                    ADMIN_ID,
                    f"⚠️ Не смог отправить пользователю <code>{user_id}</code> ссылку.\n"
                    f"Причина: {e}\n"
                    "Пусть пользователь сначала нажмёт /start в боте."
                )

            bot.answer_callback_query(call.id, "VIP выдан ✅")
            bot.send_message(
                ADMIN_ID,
                f"✅ VIP выдан <code>{user_id}</code> на <b>{plan_days} дней</b>.\n"
                f"Истекает: <code>{_fmt_dt(expires_at)}</code>\n\n"
                f"{vip_status_text(user_id)}"
            )
            return

        if data.startswith("vipinfo:"):
            user_id = int(data.split(":", 1)[1])
            bot.answer_callback_query(call.id, "OK")
            bot.send_message(ADMIN_ID, vip_status_text(user_id))
            return

        if data.startswith("viprej:"):
            user_id = int(data.split(":", 1)[1])
            bot.answer_callback_query(call.id, "Отклонено ❌")
            bot.send_message(ADMIN_ID, f"❌ Заявка отклонена для <code>{user_id}</code>")
            try:
                bot.send_message(user_id, "❌ Оплата не подтверждена. Напиши админу.")
            except Exception:
                pass
            return

        if data.startswith("apprsig:"):
            sig_id = data.split(":", 1)[1]
            item = pending_signals.pop(sig_id, None)
            if not item:
                bot.answer_callback_query(call.id, "Сигнал не найден", show_alert=True)
                return

            bot.send_message(VIP_CHANNEL, item["text"])
            bot.send_message(ADMIN_ID, f"✅ <b>SENT TO VIP</b>\n\n{item['text']}")
            bot.answer_callback_query(call.id, "Отправлено в VIP ✅")
            return

        if data.startswith("rejsig:"):
            sig_id = data.split(":", 1)[1]
            pending_signals.pop(sig_id, None)
            bot.answer_callback_query(call.id, "Отклонено ❌")
            return

        bot.answer_callback_query(call.id, "Неизвестная команда")

    except Exception as e:
        try:
            bot.answer_callback_query(call.id, f"Ошибка: {e}", show_alert=True)
        except Exception:
            pass

# ================== AUTO EXPIRE WORKER ==================
def expire_worker():
    while True:
        try:
            now = int(time.time())
            expired = []

            with LOCK:
                for uid, info in list(subs.items()):
                    if int(info.get("expires_at", 0)) <= now:
                        expired.append(int(uid))

            for user_id in expired:
                revoke_vip(user_id)
                with LOCK:
                    subs.pop(str(user_id), None)
                    save_subs()

                try:
                    bot.send_message(
                        user_id,
                        "⛔️ VIP срок закончился. Доступ закрыт.\n\n"
                        "Хочешь продлить — нажми ✅ <b>Я оплатил</b>."
                    )
                except Exception:
                    pass

                try:
                    bot.send_message(ADMIN_ID, f"⏳ VIP истёк у <code>{user_id}</code> — удалён.")
                except Exception:
                    pass

        except Exception:
            pass

        time.sleep(300)

# ================== POLLING ==================
def run_polling_forever():
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception:
            time.sleep(3)

if __name__ == "__main__":
    if IS_LEADER:
        threading.Thread(target=expire_worker, daemon=True).start()
        run_polling_forever()
    else:
        while True:
            time.sleep(60)