"""BCB SGS API Client — fetch time series data from Banco Central do Brasil."""

from datetime import datetime, date, timedelta

import pandas as pd
import requests

from .constants import BASE_URL, LAST_N_URL, DATE_FORMAT, DEFAULT_FORMAT, MAX_DATE_RANGE_YEARS
from .codes import ALL_CODES, CATEGORIES


class SGSError(Exception):
    """Base exception for SGS API errors."""


class SGSRateLimitError(SGSError):
    """Raised when the API returns HTTP 429."""


class SGSEmptyResponseError(SGSError):
    """Raised when the API returns no data."""


def _format_date(d):
    """Convert a date-like input to DD/MM/YYYY string."""
    if d is None:
        return None
    if isinstance(d, str):
        # Accept YYYY-MM-DD or DD/MM/YYYY
        for fmt in ("%Y-%m-%d", DATE_FORMAT):
            try:
                return datetime.strptime(d, fmt).strftime(DATE_FORMAT)
            except ValueError:
                continue
        raise ValueError(f"Invalid date format: {d}. Use YYYY-MM-DD or DD/MM/YYYY.")
    if isinstance(d, (date, datetime)):
        return d.strftime(DATE_FORMAT)
    raise TypeError(f"Expected str or date, got {type(d).__name__}")


def _validate_date_range(start_date, end_date):
    """Ensure date range does not exceed the 10-year API limit."""
    if start_date is None or end_date is None:
        return
    start = datetime.strptime(start_date, DATE_FORMAT)
    end = datetime.strptime(end_date, DATE_FORMAT)
    if end < start:
        raise ValueError(f"end_date ({end_date}) is before start_date ({start_date})")
    max_delta = timedelta(days=MAX_DATE_RANGE_YEARS * 366)
    if (end - start) > max_delta:
        raise ValueError(
            f"Date range exceeds {MAX_DATE_RANGE_YEARS}-year API limit. "
            f"Split your query into smaller ranges."
        )


def _handle_response(resp):
    """Check response status and raise appropriate errors."""
    if resp.status_code == 429:
        raise SGSRateLimitError("BCB API rate limit exceeded. Wait and retry.")
    if resp.status_code == 404:
        raise SGSError(f"Series not found (HTTP 404). Check the series code.")
    resp.raise_for_status()


def fetch_series(code, start_date=None, end_date=None):
    """
    Fetch a full time series from SGS.

    Args:
        code: SGS series numeric code (e.g. 12 for CDI).
        start_date: Optional start date (YYYY-MM-DD, DD/MM/YYYY, or date object).
        end_date: Optional end date. Defaults to today if start_date is provided.

    Returns:
        pandas DataFrame indexed by date with a 'valor' column.
    """
    start = _format_date(start_date)
    end = _format_date(end_date) if end_date else (
        _format_date(date.today()) if start_date else None
    )
    _validate_date_range(start, end)

    url = BASE_URL.format(code=code)
    params = {"formato": DEFAULT_FORMAT}
    if start:
        params["dataInicial"] = start
    if end:
        params["dataFinal"] = end

    resp = requests.get(url, params=params, timeout=30)
    _handle_response(resp)

    data = resp.json()
    if not data:
        raise SGSEmptyResponseError(f"No data returned for series {code}.")

    df = pd.DataFrame(data)
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df.set_index("data", inplace=True)
    return df


def fetch_last(code, n=10):
    """
    Fetch the last N observations of a series.

    Args:
        code: SGS series numeric code.
        n: Number of most recent observations (default 10).

    Returns:
        pandas DataFrame indexed by date.
    """
    url = LAST_N_URL.format(code=code, n=n)
    params = {"formato": DEFAULT_FORMAT}

    resp = requests.get(url, params=params, timeout=30)
    _handle_response(resp)

    data = resp.json()
    if not data:
        raise SGSEmptyResponseError(f"No data returned for series {code}.")

    df = pd.DataFrame(data)
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df.set_index("data", inplace=True)
    return df


def fetch_multiple(codes_dict, start_date=None, end_date=None):
    """
    Fetch multiple series and merge into a single DataFrame.

    Args:
        codes_dict: Dict mapping column names to SGS codes.
                    Example: {"CDI": 12, "SELIC": 11}
        start_date: Optional start date.
        end_date: Optional end date.

    Returns:
        pandas DataFrame with one column per series, indexed by date.
    """
    frames = {}
    for name, code in codes_dict.items():
        try:
            df = fetch_series(code, start_date, end_date)
            frames[name] = df["valor"]
        except SGSEmptyResponseError:
            print(f"Warning: no data for {name} (code {code}), skipping.")
    if not frames:
        raise SGSEmptyResponseError("No data returned for any of the requested series.")
    return pd.DataFrame(frames)


def list_codes(category=None):
    """
    Print available series codes, optionally filtered by category.

    Args:
        category: Category name (e.g. "INTEREST_RATES"). None lists all.
    """
    if category:
        cat_upper = category.upper()
        if cat_upper not in CATEGORIES:
            print(f"Unknown category: {category}")
            print(f"Available: {', '.join(CATEGORIES.keys())}")
            return
        cats = {cat_upper: CATEGORIES[cat_upper]}
    else:
        cats = CATEGORIES

    for cat_name, codes in cats.items():
        print(f"\n{'='*60}")
        print(f"  {cat_name} ({len(codes)} series)")
        print(f"{'='*60}")
        for name, code in codes.items():
            print(f"  {code:>6}  {name}")


def search_codes(keyword):
    """
    Search series codes by keyword (case-insensitive).

    Args:
        keyword: Search term to match against code names.

    Returns:
        Dict of matching {name: code} pairs.
    """
    keyword = keyword.upper()
    results = {name: code for name, code in ALL_CODES.items() if keyword in name}
    if not results:
        print(f"No codes matching '{keyword}'.")
    else:
        print(f"Found {len(results)} match(es):")
        for name, code in results.items():
            print(f"  {code:>6}  {name}")
    return results
