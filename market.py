import ccxt
import pandas as pd

exchange = ccxt.binance()

def get_ohlcv(symbol, timeframe, limit=200):
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

df = pd.DataFrame(
    bars,
    columns=["time","open","high","low","close","volume"]
)
df["time"] = pd.to_datetime(df["time"], unit="ms")  # перетворюємо час
df.set_index("time", inplace=True)  # ставимо його як індекс

    return df
