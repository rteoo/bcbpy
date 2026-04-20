"""
bcbpy — Python client for the BCB SGS (Sistema Gerenciador de Series) API.

Usage:
    from bcbpy import fetch_series, fetch_last, fetch_multiple, INTEREST_RATES

    # Fetch CDI daily rate for 2024
    cdi = fetch_series(INTEREST_RATES["CDI_DAILY"], start_date="2024-01-01")

    # Last 10 observations of USD/BRL
    from bcbpy import EXCHANGE_RATES
    usd = fetch_last(EXCHANGE_RATES["USD_SALE_DAILY"], n=10)

    # Multiple series at once
    df = fetch_multiple({"CDI": 12, "SELIC": 11}, start_date="2024-01-01")
"""

__version__ = "1.2.0"

from .client import (
    fetch_series,
    fetch_last,
    fetch_multiple,
    list_codes,
    search_codes,
    SGSError,
    SGSRateLimitError,
    SGSEmptyResponseError,
)

from .codes import (
    EXCHANGE_RATES,
    INTEREST_RATES,
    INFLATION,
    IPCA_BREAKDOWN,
    IPCA_CATEGORIES,
    GDP,
    EMPLOYMENT,
    INDUSTRIAL_PRODUCTION,
    FINANCIAL_MARKETS,
    SAVINGS,
    CONFIDENCE,
    ECONOMIC_ACTIVITY,
    BASIC_BASKET,
    EXCHANGE_RATE_INDEX,
    CATEGORIES,
    ALL_CODES,
)

__all__ = [
    "__version__",
    "fetch_series",
    "fetch_last",
    "fetch_multiple",
    "list_codes",
    "search_codes",
    "SGSError",
    "SGSRateLimitError",
    "SGSEmptyResponseError",
    "EXCHANGE_RATES",
    "INTEREST_RATES",
    "INFLATION",
    "IPCA_BREAKDOWN",
    "IPCA_CATEGORIES",
    "GDP",
    "EMPLOYMENT",
    "INDUSTRIAL_PRODUCTION",
    "FINANCIAL_MARKETS",
    "SAVINGS",
    "CONFIDENCE",
    "ECONOMIC_ACTIVITY",
    "BASIC_BASKET",
    "EXCHANGE_RATE_INDEX",
    "CATEGORIES",
    "ALL_CODES",
]
