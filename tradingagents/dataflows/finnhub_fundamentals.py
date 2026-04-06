import json
from .finnhub_common import _make_api_request


def get_fundamentals(symbol: str) -> str:
    """
    Returns company profile and basic metrics from Finnhub.

    Args:
        symbol: Stock ticker symbol

    Returns:
        JSON string with company fundamentals
    """
    # Get company profile
    profile = _make_api_request("/stock/profile2", {"symbol": symbol.upper()})

    # Get basic financials/metrics
    metrics = _make_api_request("/stock/metric", {
        "symbol": symbol.upper(),
        "metric": "all"
    })

    result = {
        "profile": profile,
        "metrics": metrics.get("metric", {}),
    }

    return json.dumps(result, indent=2)


def get_balance_sheet(symbol: str) -> str:
    """
    Returns balance sheet data from Finnhub.

    Args:
        symbol: Stock ticker symbol

    Returns:
        JSON string with balance sheet data
    """
    data = _make_api_request("/stock/financials", {
        "symbol": symbol.upper(),
        "statement": "bs",  # balance sheet
        "freq": "annual"
    })

    return json.dumps(data, indent=2)


def get_cashflow(symbol: str) -> str:
    """
    Returns cash flow statement from Finnhub.

    Args:
        symbol: Stock ticker symbol

    Returns:
        JSON string with cash flow data
    """
    data = _make_api_request("/stock/financials", {
        "symbol": symbol.upper(),
        "statement": "cf",  # cash flow
        "freq": "annual"
    })

    return json.dumps(data, indent=2)


def get_income_statement(symbol: str) -> str:
    """
    Returns income statement from Finnhub.

    Args:
        symbol: Stock ticker symbol

    Returns:
        JSON string with income statement data
    """
    data = _make_api_request("/stock/financials", {
        "symbol": symbol.upper(),
        "statement": "ic",  # income statement
        "freq": "annual"
    })

    return json.dumps(data, indent=2)


def get_insider_transactions(symbol: str) -> str:
    """
    Returns insider transactions from Finnhub.

    Args:
        symbol: Stock ticker symbol

    Returns:
        JSON string with insider transaction data
    """
    data = _make_api_request("/stock/insider-transactions", {
        "symbol": symbol.upper()
    })

    return json.dumps(data, indent=2)
