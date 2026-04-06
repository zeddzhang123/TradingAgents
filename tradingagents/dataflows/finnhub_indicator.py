import pandas as pd
from io import StringIO
from .finnhub_common import _make_api_request, date_to_timestamp, timestamp_to_date


def get_indicators(symbol: str, start_date: str, end_date: str) -> str:
    """
    Returns technical indicators calculated from OHLCV data.

    Finnhub provides /indicator endpoint for technical indicators.
    We fetch common indicators: SMA, EMA, RSI, MACD.

    Args:
        symbol: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        CSV string with technical indicators
    """
    from_ts = date_to_timestamp(start_date)
    to_ts = date_to_timestamp(end_date)

    # Fetch candle data first
    candle_params = {
        "symbol": symbol.upper(),
        "resolution": "D",
        "from": from_ts,
        "to": to_ts,
    }
    candle_data = _make_api_request("/stock/candle", candle_params)

    if candle_data.get("s") == "no_data" or "t" not in candle_data:
        return "timestamp,close,sma_20,ema_20,rsi_14\n"

    # Build base DataFrame
    df = pd.DataFrame({
        "timestamp": [timestamp_to_date(t) for t in candle_data["t"]],
        "close": candle_data["c"],
    })

    # Calculate indicators locally (Finnhub indicator endpoint requires premium)
    df = df.sort_values("timestamp", ascending=True).reset_index(drop=True)

    # SMA 20
    df["sma_20"] = df["close"].rolling(window=20).mean()

    # EMA 20
    df["ema_20"] = df["close"].ewm(span=20, adjust=False).mean()

    # RSI 14
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi_14"] = 100 - (100 / (1 + rs))

    # Sort descending and round values
    df = df.sort_values("timestamp", ascending=False)
    df = df.round(4)

    return df.to_csv(index=False)
