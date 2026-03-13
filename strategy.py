import ta

def calculate_indicators(df):

    df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["ema200"] = ta.trend.ema_indicator(df["close"], window=200)
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)

    df["vol_ma"] = df["volume"].rolling(20).mean()

    return df


def check_signal(df):

    df = calculate_indicators(df)
    last = df.iloc[-1]
    volume_ok = last["volume"] > last["vol_ma"]

    price = last["close"]

    if last["ema50"] > last["ema200"] and 40 < last["rsi"] < 50 and volume_ok:

        return {
            "type": "LONG",
            "entry": round(price,2),
            "stop": round(price * 0.99,2),
            "take": round(price * 1.02,2)
        }

    if last["ema50"] < last["ema200"] and 50 < last["rsi"] < 60:

        return {
            "type": "SHORT",
            "entry": round(price,2),
            "stop": round(price * 1.01,2),
            "take": round(price * 0.98,2)
        }

    return None
