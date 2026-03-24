import logging
import asyncio

from config import CHECK_INTERVAL, SYMBOLS, TIMEFRAME, CHAT_ID
from market import get_ohlcv
from strategy import check_signal
from telegram_bot import build_bot

logging.basicConfig(level=logging.INFO)

last_signals = {}  # по кожній монеті


def generate_signal(symbol=None):

    global last_signals

    signals = []

    symbols_to_check = [symbol] if symbol else SYMBOLS

    for sym in symbols_to_check:

        df = get_ohlcv(sym, TIMEFRAME)

        # ✅ захист від помилок API
        if df is None or df.empty:
            continue

        try:
            signal = check_signal(df, sym)
        except Exception as e:
            print(f"Error on {sym}: {e}")
            continue

        if signal:

            # перевірка на дубль
            if last_signals.get(sym) == signal:
                continue

            last_signals[sym] = signal
            signal["symbol"] = sym
            signals.append(signal)

    return signals


async def auto_signal(app):

    while True:

        try:
            signals = generate_signal()

            if signals:

                for signal in signals:

                    text = f"""
AUTO SIGNAL ⚡

{signal['symbol']} {signal['type']}

Entry: {signal['entry']}
Stop: {signal['stop']}
Take: {signal['take']}
"""

                    await app.bot.send_message(
                        chat_id=CHAT_ID,
                        text=text
                    )

        except Exception as e:
            print(f"AUTO LOOP ERROR: {e}")

        await asyncio.sleep(CHECK_INTERVAL)


def main():

    app = build_bot(generate_signal)

    loop = asyncio.get_event_loop()
    loop.create_task(auto_signal(app))

    app.run_polling()


if __name__ == "__main__":
    main()
