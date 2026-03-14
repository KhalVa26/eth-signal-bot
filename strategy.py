import pandas as pd
import ta

def check_signal(exchange):

    # ===== 15M DATA (signal) =====
    ohlcv = exchange.fetch_ohlcv("ETH/USDT", "15m", limit=200)
    df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])

    # indicators
    df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["ema200"] = ta.trend.ema_indicator(df["close"], window=200)
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)
    df["vol_ma"] = df["volume"].rolling(20).mean()
    df["atr"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=14)

    last = df.iloc[-1]
    price = last["close"]
    atr = last["atr"]

    volume_ok = last["volume"] > last["vol_ma"]

    # ===== 1H DATA (trend) =====
    ohlcv1h = exchange.fetch_ohlcv("ETH/USDT", "1h", limit=200)
    df1h = pd.DataFrame(ohlcv1h, columns=["time","open","high","low","close","volume"])

    df1h["ema200"] = ta.trend.ema_indicator(df1h["close"], window=200)

    trend1h = "bull" if df1h.iloc[-1]["close"] > df1h.iloc[-1]["ema200"] else "bear"

    # ===== 5M DATA (entry) =====
    ohlcv5m = exchange.fetch_ohlcv("ETH/USDT", "5m", limit=100)
    df5m = pd.DataFrame(ohlcv5m, columns=["time","open","high","low","close","volume"])

    df5m["rsi"] = ta.momentum.rsi(df5m["close"], window=14)

    entry_ok = 40 < df5m.iloc[-1]["rsi"] < 60

    # ===== VOLATILITY FILTER =====
    if atr < price * 0.002:
        return None

    # ===== LONG =====
    if (
        last["ema50"] > last["ema200"]
        and 40 < last["rsi"] < 60
        and volume_ok
        and trend1h == "bull"
        and entry_ok
    ):

        return {
            "type": "LONG",
            "entry": round(price,2),
            "stop": round(price - atr * 1.5,2),
            "take": round(price + atr * 3,2)
        }

    # ===== SHORT =====
    if (
        last["ema50"] < last["ema200"]
        and 40 < last["rsi"] < 60
        and volume_ok
        and trend1h == "bear"
        and entry_ok
    ):

        return {
            "type": "SHORT",
            "entry": round(price,2),
            "stop": round(price + atr * 1.5,2),
            "take": round(price - atr * 3,2)
        }

    return None
