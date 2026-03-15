from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

keyboard = [["📊 Отримати сигнал"]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def build_bot(signal_func):
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
    app.bot_data["signal_func"] = signal_func

    async def start(update: Update, context):
        await update.message.reply_text(
            "ETH Signal Bot запущений 🚀",
            reply_markup=markup
        )

    async def manual_signal(update: Update, context):
        # Викликаємо сигнал синхронно у головному потоці
        signal = context.bot_data["signal_func"]()
        if not signal:
            await update.message.reply_text("Сигналу зараз немає ❌")
            return
        text = f"""
ETH/USDT {signal['type']} 📈

Entry: {signal['entry']}
Stop: {signal['stop']}
Take: {signal['take']}

Strategy: EMA50 / EMA200 / RSI
TF: 15m
"""
        await update.message.reply_text(text)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Отримати сигнал"), manual_signal))

    return app
