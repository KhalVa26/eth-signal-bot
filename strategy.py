import ta
from market import get_ohlcv


# ✅ АДАПТИВНЕ ОКРУГЛЕННЯ
def format_price(price):
    if price < 1:
        return round(price, 4)
    elif price < 100:
        return round(price, 3)
    else:
        return round(price, 2)


def calculate_indicators(df):

    df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["ema200"] = ta.trend.ema_indicator(df["close"], window=200)
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)

    df["vol_ma"] = df["volume"].rolling(20).mean()

    df["atr"] = ta.volatility.average_true_range(
        df["high"], df["low"], df["close"], window=14
    )

    return df


def check_signal(df, symbol):

    df = calculate_indicators(df)
    last = df.iloc[-1]

    atr = last["atr"]
    volume_ok = last["volume"] > last["vol_ma"]
    price = last["close"]

    # ===== ФІЛЬТР ФЛЕТУ =====
    ema50 = last["ema50"]
    ema200 = last["ema200"]

    trend_strength = abs(ema50 - ema200) / price

    if trend_strength < 0.002:
        return None

    # ===== 1H TREND =====
    df1h = get_ohlcv(symbol, "1h")
    if df1h is None or df1h.empty:
        return None

    df1h["ema50"] = ta.trend.ema_indicator(df1h["close"], window=50)

    trend = "bull" if df1h.iloc[-1]["close"] > df1h.iloc[-1]["ema50"] else "bear"

    # ===== 5M ENTRY =====
    df5m = get_ohlcv(symbol, "5m")
    if df5m is None or df5m.empty:
        return None

    df5m["rsi"] = ta.momentum.rsi(df5m["close"], window=14)

    curr_rsi = df5m.iloc[-1]["rsi"]

    entry_long = curr_rsi > 45
    entry_short = curr_rsi < 55

    # ===== ВХІД НЕ В СЕРЕДИНІ =====
    recent_high = df["high"].rolling(20).max().iloc[-1]
    recent_low = df["low"].rolling(20).min().iloc[-1]

    in_upper_zone = price > recent_high * 0.995
    in_lower_zone = price < recent_low * 1.005

    # ===== LONG =====
    if (
        last["ema50"] > last["ema200"]
        and 35 < last["rsi"] < 55
        and volume_ok
        and trend == "bull"
        and entry_long
        and in_lower_zone
    ):

        entry = price
        stop = price - atr * 1.5
        take = price + atr * 3

        # ⛔ захист від однакових цін
        if format_price(entry) == format_price(stop):
            return None

        return {
            "type": "LONG",
            "entry": format_price(entry),
            "stop": format_price(stop),
            "take": format_price(take),
        }

    # ===== SHORT =====
    if (
        last["ema50"] < last["ema200"]
        and 45 < last["rsi"] < 65
        and volume_ok
        and trend == "bear"
        and entry_short
        and in_upper_zone
    ):

        entry = price
        stop = price + atr * 1.5
        take = price - atr * 3

        # ⛔ захист від однакових цін
        if format_price(entry) == format_price(stop):
            return None

        return {
            "type": "SHORT",
            "entry": format_price(entry),
            "stop": format_price(stop),
            "take": format_price(take),
        }

    return None
