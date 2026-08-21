"""BCB SGS API Client — fetch time series data from Banco Central do Brasil."""

import hashlib
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import pandas as pd
import requests

from .artifacts import RawResult
from .codes import ALL_CODES, CATEGORIES
from .constants import (
    BASE_URL,
    DATE_FORMAT,
    DEFAULT_FORMAT,
    HTTP_TIMEOUT,
    LAST_N_URL,
    MAX_DATE_RANGE_YEARS,
    PARSER_VERSION,
)


class SGSError(Exception):
    """Base exception for SGS API errors."""


class SGSRateLimitError(SGSError):
    """Raised when the API returns HTTP 429.

    ``retry_after`` is seconds parsed from ``Retry-After`` when present.
    Callers retry; this client does not swallow the failure.
    """

    def __init__(self, message="BCB API rate limit exceeded. Wait and retry.", retry_after=None, status_code=429, headers=None):
        super().__init__(message)
        self.retry_after = retry_after
        self.status_code = status_code
        self.headers = headers if headers is not None else {}


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
    if end > _calendar_anniversary(start, MAX_DATE_RANGE_YEARS):
        raise ValueError(
            f"Date range exceeds {MAX_DATE_RANGE_YEARS}-year API limit. "
            f"Split your query into smaller ranges."
        )


def _calendar_anniversary(value, years):
    """Return ``value`` moved by calendar years, preserving valid month/day.

    February 29 has no counterpart in a non-leap target year.  Treating it as
    February 28 keeps the range boundary deterministic and matches the API's
    calendar-year limit rather than approximating years as 366-day windows.
    """
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        # The only invalid replacement for a date is February 29 in a
        # non-leap target year.
        return value.replace(year=value.year + years, day=28)


def _bound_dates(start_date, end_date):
    """Normalize dates; default end to today when only start is given."""
    start = _format_date(start_date)
    end = _format_date(end_date) if end_date else (
        _format_date(date.today()) if start_date else None
    )
    return start, end


def _headers_map(headers):
    """Lowercased header dict. Ignores mock objects that are not real mappings."""
    if headers is None:
        return {}
    try:
        size = len(headers)
    except Exception:
        return {}
    if not isinstance(size, int) or size < 0 or size > 10000:
        return {}
    mapped = {}
    try:
        for key, value in headers.items():
            mapped[str(key).lower()] = str(value)
    except Exception:
        return {}
    return mapped


def _retry_after_seconds(headers):
    """Parse Retry-After as seconds. HTTP-date values become a remaining delay."""
    mapped = _headers_map(headers)
    raw = mapped.get("retry-after")
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(raw)
        remaining = when.timestamp() - datetime.now(timezone.utc).timestamp()
        return max(remaining, 0.0)
    except (TypeError, ValueError, OverflowError):
        return None


def _handle_response(resp):
    """Check response status and raise appropriate errors."""
    if resp.status_code == 429:
        headers = getattr(resp, "headers", None)
        raise SGSRateLimitError(
            "BCB API rate limit exceeded. Wait and retry.",
            retry_after=_retry_after_seconds(headers),
            status_code=429,
            headers=_headers_map(headers),
        )
    if resp.status_code == 404:
        raise SGSError("Series not found (HTTP 404). Check the series code.")
    resp.raise_for_status()


def _http_get(url, params, transport=None):
    getter = requests.get if transport is None else transport
    return getter(url, params=params, timeout=HTTP_TIMEOUT)


def _request(url, params, transport=None):
    resp = _http_get(url, params, transport=transport)
    _handle_response(resp)
    return resp


def _response_payload(resp):
    content = getattr(resp, "content", None)
    if isinstance(content, bytes):
        return content
    if isinstance(content, str):
        return content.encode("utf-8")
    text = getattr(resp, "text", None)
    if isinstance(text, str):
        return text.encode("utf-8")
    raise SGSError("Response has no body.")


def _series_request(code, start_date, end_date):
    start, end = _bound_dates(start_date, end_date)
    url = BASE_URL.format(code=code)
    params = {"formato": DEFAULT_FORMAT}
    if start:
        params["dataInicial"] = start
    if end:
        params["dataFinal"] = end
    return start, end, url, params


def _date_partitions(start, end):
    """Inclusive DD/MM/YYYY windows that each satisfy the 10-year single-call limit.

    Adjacent windows do not share a calendar day, so composed ranges do not
    duplicate the boundary observation.
    """
    start_dt = datetime.strptime(start, DATE_FORMAT)
    end_dt = datetime.strptime(end, DATE_FORMAT)
    cursor = start_dt
    while cursor <= end_dt:
        chunk_end = min(_calendar_anniversary(cursor, MAX_DATE_RANGE_YEARS), end_dt)
        yield cursor.strftime(DATE_FORMAT), chunk_end.strftime(DATE_FORMAT)
        if chunk_end >= end_dt:
            return
        cursor = chunk_end + timedelta(days=1)


def _library_version():
    from . import __version__
    return __version__


def _raw_result(code, url, params, resp):
    payload = _response_payload(resp)
    headers = _headers_map(getattr(resp, "headers", None))
    return RawResult(
        payload=payload,
        source_url=url,
        params=dict(params),
        http_headers=headers,
        fetched_at=datetime.now(timezone.utc),
        series_code=code,
        library_version=_library_version(),
        parser_version=PARSER_VERSION,
        sha256=hashlib.sha256(payload).hexdigest(),
        byte_size=len(payload),
        status_code=getattr(resp, "status_code", 200) or 200,
        retry_after=_retry_after_seconds(getattr(resp, "headers", None)),
    )


def _build_dataframe(data, code):
    """Convert an SGS JSON payload into a validated, date-indexed DataFrame.

    Raises SGSError on a structurally invalid payload (non-list, or missing
    the expected 'data'/'valor' fields) and SGSEmptyResponseError on an empty
    series, rather than letting an opaque pandas error surface.
    """
    if not isinstance(data, list):
        raise SGSError(
            f"Unexpected response for series {code}: expected a JSON list, "
            f"got {type(data).__name__}."
        )
    if not data:
        raise SGSEmptyResponseError(f"No data returned for series {code}.")

    df = pd.DataFrame(data)
    missing = {"data", "valor"} - set(df.columns)
    if missing:
        raise SGSError(
            f"Malformed response for series {code}: missing field(s) "
            f"{', '.join(sorted(missing))}."
        )

    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df.set_index("data", inplace=True)
    return df


def fetch_series(code, start_date=None, end_date=None, transport=None):
    """
    Fetch a full time series from SGS.

    Args:
        code: SGS series numeric code (e.g. 12 for CDI).
        start_date: Optional start date (YYYY-MM-DD, DD/MM/YYYY, or date object).
        end_date: Optional end date. Defaults to today if start_date is provided.
        transport: Optional GET callable ``(url, params=, timeout=)`` for tests.

    Returns:
        pandas DataFrame indexed by date with a 'valor' column.

    The 10-year single-call limit still applies. Use ``fetch_raw_range`` to
    compose longer windows as multiple bounded requests.
    """
    start, end, url, params = _series_request(code, start_date, end_date)
    _validate_date_range(start, end)
    resp = _request(url, params, transport=transport)
    return _build_dataframe(resp.json(), code)


def fetch_last(code, n=10, transport=None):
    """
    Fetch the last N observations of a series.

    Args:
        code: SGS series numeric code.
        n: Number of most recent observations (default 10). Must be a
           positive integer.
        transport: Optional GET callable ``(url, params=, timeout=)`` for tests.

    Returns:
        pandas DataFrame indexed by date.
    """
    # bool is an int subclass; reject it explicitly so fetch_last(code, True)
    # doesn't silently become n=1.
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError(f"n must be a positive integer, got {n!r}.")

    url = LAST_N_URL.format(code=code, n=n)
    params = {"formato": DEFAULT_FORMAT}

    resp = _request(url, params, transport=transport)
    return _build_dataframe(resp.json(), code)


def fetch_multiple(codes_dict, start_date=None, end_date=None, transport=None):
    """
    Fetch multiple series and merge into a single DataFrame.

    Args:
        codes_dict: Dict mapping column names to SGS codes.
                    Example: {"CDI": 12, "SELIC": 11}
        start_date: Optional start date.
        end_date: Optional end date.
        transport: Optional GET callable forwarded to ``fetch_series``.

    Returns:
        pandas DataFrame with one column per series, indexed by date.
    """
    if not codes_dict:
        raise ValueError("codes_dict is empty; provide at least one {name: code} pair.")

    frames = {}
    for name, code in codes_dict.items():
        try:
            df = fetch_series(code, start_date, end_date, transport=transport)
            frames[name] = df["valor"]
        except SGSEmptyResponseError:
            print(f"Warning: no data for {name} (code {code}), skipping.")
    if not frames:
        raise SGSEmptyResponseError("No data returned for any of the requested series.")
    return pd.DataFrame(frames)


def fetch_raw(code, start_date=None, end_date=None, transport=None):
    """
    Fetch one SGS window as a ``RawResult`` (payload bytes + request metadata).

    Honors the same 10-year single-call limit as ``fetch_series``. Does not
    parse the body: HTTP 200 with ``[]`` or malformed JSON is returned so a
    warehouse can register the bytes.
    """
    start, end, url, params = _series_request(code, start_date, end_date)
    _validate_date_range(start, end)
    resp = _request(url, params, transport=transport)
    return _raw_result(code, url, params, resp)


def fetch_raw_range(code, start_date=None, end_date=None, transport=None):
    """
    Fetch a date window as one or more bounded ``RawResult`` partitions.

    Ranges longer than the SGS 10-year limit are split. Adjacent partitions
    start the day after the previous end so boundary dates are not duplicated.
    Empty partition bodies are returned, not skipped.
    """
    start, end = _bound_dates(start_date, end_date)
    if start and end:
        start_dt = datetime.strptime(start, DATE_FORMAT)
        end_dt = datetime.strptime(end, DATE_FORMAT)
        if end_dt < start_dt:
            raise ValueError(f"end_date ({end}) is before start_date ({start})")
        windows = list(_date_partitions(start, end))
    else:
        windows = [(start, end)]
    return [
        fetch_raw(code, start_date=part_start, end_date=part_end, transport=transport)
        for part_start, part_end in windows
    ]


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
    if not keyword:
        print("No codes matching ''.")
        return {}
    results = {name: code for name, code in ALL_CODES.items() if keyword in name}
    if not results:
        print(f"No codes matching '{keyword}'.")
    else:
        print(f"Found {len(results)} match(es):")
        for name, code in results.items():
            print(f"  {code:>6}  {name}")
    return results
