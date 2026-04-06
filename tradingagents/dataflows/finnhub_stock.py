import pandas as pd
from io import StringIO
from .finnhub_common import _make_api_request, date_to_timestamp, timestamp_to_date


def get_stock(symbol: str, start_date: str, end_date: str) -> str:
    """
    Returns daily OHLCV data for a stock from Finnhub.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        CSV string containing date, open, high, low, close, volume columns
    """
    params = {
        "symbol": symbol.upper(),
        "resolution": "D",  # Daily
        "from": date_to_timestamp(start_date),
        "to": date_to_timestamp(end_date),
    }

    data = _make_api_request("/stock/candle", params)

    # Check for no data
    if data.get("s") == "no_data" or "t" not in data:
        return "timestamp,open,high,low,close,volume\n"

    # Build DataFrame
    df = pd.DataFrame({
        "timestamp": [timestamp_to_date(t) for t in data["t"]],
        "open": data["o"],
        "high": data["h"],
        "low": data["l"],
        "close": data["c"],
        "volume": data["v"],
    })

    # Sort by date descending (matching Alpha Vantage format)
    df = df.sort_values("timestamp", ascending=False)

    return df.to_csv(index=False)
