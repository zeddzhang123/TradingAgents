import os
import requests
import time
from datetime import datetime

API_BASE_URL = "https://finnhub.io/api/v1"

# Rate limiting: 60 calls/min for free tier
_last_request_time = 0
_min_request_interval = 1.0  # 1 second between requests to stay safe


class FinnhubRateLimitError(Exception):
    """Exception raised when Finnhub API rate limit is exceeded."""
    pass


def get_api_key() -> str:
    """Retrieve the API key for Finnhub from environment variables."""
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        raise ValueError("FINNHUB_API_KEY environment variable is not set.")
    return api_key


def _rate_limit_wait():
    """Enforce rate limiting between API requests."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < _min_request_interval:
        time.sleep(_min_request_interval - elapsed)
    _last_request_time = time.time()


def _make_api_request(endpoint: str, params: dict = None) -> dict:
    """
    Make a request to the Finnhub API.

    Args:
        endpoint: API endpoint (e.g., "/stock/candle")
        params: Query parameters

    Returns:
        JSON response as dict

    Raises:
        FinnhubRateLimitError: When API rate limit is exceeded
    """
    _rate_limit_wait()

    if params is None:
        params = {}

    params["token"] = get_api_key()

    url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(url, params=params)

    if response.status_code == 429:
        raise FinnhubRateLimitError("Finnhub rate limit exceeded")

    response.raise_for_status()
    return response.json()


def date_to_timestamp(date_str: str) -> int:
    """Convert date string (YYYY-MM-DD) to Unix timestamp."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp())


def timestamp_to_date(ts: int) -> str:
    """Convert Unix timestamp to date string (YYYY-MM-DD)."""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
