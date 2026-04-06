import json
from datetime import datetime, timedelta
from .finnhub_common import _make_api_request


def get_news(symbol: str, start_date: str = None, end_date: str = None) -> str:
    """
    Returns company-specific news from Finnhub.

    Args:
        symbol: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format (optional, defaults to 7 days ago)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)

    Returns:
        JSON string with news articles
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    data = _make_api_request("/company-news", {
        "symbol": symbol.upper(),
        "from": start_date,
        "to": end_date
    })

    # Format response
    articles = []
    for item in data[:50]:  # Limit to 50 articles
        articles.append({
            "headline": item.get("headline"),
            "summary": item.get("summary"),
            "source": item.get("source"),
            "url": item.get("url"),
            "datetime": datetime.fromtimestamp(item.get("datetime", 0)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": item.get("category"),
        })

    return json.dumps(articles, indent=2)


def get_global_news(category: str = "general") -> str:
    """
    Returns market-wide news from Finnhub.

    Args:
        category: News category (general, forex, crypto, merger)

    Returns:
        JSON string with news articles
    """
    data = _make_api_request("/news", {
        "category": category
    })

    # Format response
    articles = []
    for item in data[:50]:  # Limit to 50 articles
        articles.append({
            "headline": item.get("headline"),
            "summary": item.get("summary"),
            "source": item.get("source"),
            "url": item.get("url"),
            "datetime": datetime.fromtimestamp(item.get("datetime", 0)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": item.get("category"),
        })

    return json.dumps(articles, indent=2)
