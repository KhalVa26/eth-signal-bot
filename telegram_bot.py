from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN

# ===== ГОЛОВНЕ МЕНЮ =====
keyboard = [
    ["📊 Отримати сигнал"],
    ["🪙 Монети"]
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ===== МЕНЮ МОНЕТ =====
coins_keyboard = [
    ["BTC/USDT", "ETH/USDT"],
    ["SOL/USDT", "BNB/USDT"],
    ["ATOM/USDT"],
    ["⬅️ Назад"]
]
coins_markup = ReplyKeyboardMarkup(coins_keyboard, resize_keyboard=True)


async def start(update: Update, context):
    await update.message.reply_text(
        "Signal Bot запущений 🚀",
        reply_markup=markup
    )


# ===== ВСІ СИГНАЛИ =====
async def manual_signal(update: Update, context):

    signals = context.bot_data["signal_func"]()

    if not signals:
        await update.message.reply_text("Сигналів зараз немає ❌")
        return

    for signal in signals:
        text = format_signal(signal)
        await update.message.reply_text(text)


# ===== МЕНЮ МОНЕТ =====
async def coins_menu(update: Update, context):
    await update.message.reply_text(
        "Оберіть монету:",
        reply_markup=coins_markup
    )


# ===== СИГНАЛ ПО КОНКРЕТНІЙ МОНЕТІ =====
async def coin_signal(update: Update, context):

    symbol = update.message.text

    if symbol == "⬅️ Назад":
        await start(update, context)
        return

    signals = context.bot_data["signal_func"](symbol)

    if not signals:
        await update.message.reply_text(f"{symbol} — сигналу немає ❌")
        return

    signal = signals[0]
    text = format_signal(signal)

    await update.message.reply_text(text)


# ===== ФОРМАТ =====
def format_signal(signal):

    return f"""
{signal['symbol']} {signal['type']} 📈

Entry: {signal['entry']}
Stop: {signal['stop']}
Take: {signal['take']}

Strategy: EMA50 / EMA200 / RSI
TF: 15m
"""


# ===== БІЛД БОТА =====
def build_bot(signal_func):

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.bot_data["signal_func"] = signal_func

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(filters.Regex("Отримати сигнал"), manual_signal)
    )

    app.add_handler(
        MessageHandler(filters.Regex("Монети"), coins_menu)
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("BTC/USDT|ETH/USDT|SOL/USDT|BNB/USDT|ATOM/USDT|⬅️ Назад"),
            coin_signal
        )
    )

    return app
