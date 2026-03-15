import logging
import asyncio

from config import CHECK_INTERVAL, SYMBOL, TIMEFRAME, CHAT_ID
from market import get_ohlcv
from strategy import check_signal
from telegram_bot import build_bot

logging.basicConfig(level=logging.INFO)

last_signal = None


def generate_signal():

    global last_signal

    df = get_ohlcv(SYMBOL, TIMEFRAME)

    signal = check_signal(df)

    if signal == last_signal:
        return None

    last_signal = signal

    return signal


async def auto_signal(app):

    while True:

        signal = generate_signal()

        if signal:

            text = f"""
AUTO SIGNAL ⚡

ETH/USDT {signal['type']}

Entry: {signal['entry']}
Stop: {signal['stop']}
Take: {signal['take']}
"""

            await app.bot.send_message(
                chat_id=CHAT_ID,
                text=text
            )

        await asyncio.sleep(CHECK_INTERVAL)


def main():

    app = build_bot(generate_signal)

    loop = asyncio.get_event_loop()
    loop.create_task(auto_signal(app))

    app.run_polling()


if __name__ == "__main__":
    main()
