import ccxt
import pandas as pd

exchange = ccxt.binance()

def get_ohlcv(symbol, timeframe, limit=200):
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    df = pd.DataFrame(
        bars,
        columns=["time","open","high","low","close","volume"]
    )

    return df
