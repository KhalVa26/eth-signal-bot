import logging
from config import CHECK_INTERVAL, SYMBOL, TIMEFRAME, CHAT_ID
from telegram_bot import build_bot
import ccxt
import pandas as pd
import ta

logging.basicConfig(level=logging.INFO)

last_signal = None

# ===== sync fetch OHLCV =====
def get_ohlcv(symbol, timeframe, limit=200):
    exchange = ccxt.binance()
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    exchange.close()
    df = pd.DataFrame(bars, columns=["time", "open", "high", "low", "close", "volume"])
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df.set_index("time", inplace=True)
    return df

# ===== signal logic =====
def generate_signal():
    global last_signal
    df = get_ohlcv(SYMBOL, TIMEFRAME)
    df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["ema200"] = ta.trend.ema_indicator(df["close"], window=200)
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)
    last = df.iloc[-1]
    price = last["close"]
    atr = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=14).iloc[-1]
    signal = None
    if last["ema50"] > last["ema200"] and 40 < last["rsi"] < 50:
        signal = {"type":"LONG","entry":round(price,2),"stop":round(price-atr*1.5,2),"take":round(price+atr*3,2)}
    elif last["ema50"] < last["ema200"] and 50 < last["rsi"] < 60:
        signal = {"type":"SHORT","entry":round(price,2),"stop":round(price+atr*1.5,2),"take":round(price-atr*3,2)}
    if signal == last_signal:
        return None
    last_signal = signal
    return signal

# ===== JobQueue task for auto signals =====
def auto_signal_job(context):
    signal = generate_signal()
    if signal:
        text = f"""
AUTO SIGNAL ⚡

ETH/USDT {signal['type']}

Entry: {signal['entry']}
Stop: {signal['stop']}
Take: {signal['take']}
"""
        context.bot.send_message(chat_id=CHAT_ID, text=text)

# ===== main =====
def main():
    app = build_bot(generate_signal)

    # ===== запускаємо auto signal через JobQueue =====
    # interval в секундах
    app.job_queue.run_repeating(auto_signal_job, interval=CHECK_INTERVAL, first=10)

    # ===== запуск Telegram бота =====
    app.run_polling()

if __name__ == "__main__":
    main()
