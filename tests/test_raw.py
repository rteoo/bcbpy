"""Tests for the warehouse raw-result API (mocked, no network calls)."""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from unittest.mock import patch, MagicMock

import pytest

from bcbpy import PARSER_VERSION, RawResult, __version__
from bcbpy.client import (
    _date_partitions,
    _validate_date_range,
    fetch_raw,
    fetch_raw_range,
    fetch_series,
    SGSRateLimitError,
)
from bcbpy.constants import BASE_URL


PAYLOAD = b'[{"data":"10/04/2026","valor":"0.054"}]'
EMPTY_PAYLOAD = b"[]"
MALFORMED_PAYLOAD = b'{"error":"bad"}'


def _transport(payload, status_code=200, headers=None, calls=None):
    def getter(url, params=None, timeout=30):
        if calls is not None:
            calls.append({"url": url, "params": dict(params or {}), "timeout": timeout})
        resp = MagicMock()
        resp.status_code = status_code
        resp.content = payload
        resp.headers = headers or {"Content-Type": "application/json"}
        resp.raise_for_status = MagicMock()

        def _json():
            return json.loads(payload.decode("utf-8"))

        resp.json.side_effect = _json
        return resp

    return getter


class TestFetchRaw:
    def test_returns_raw_result_metadata(self):
        result = fetch_raw(12, start_date="2026-04-10", end_date="2026-04-12", transport=_transport(PAYLOAD))
        assert isinstance(result, RawResult)
        assert result.payload == PAYLOAD
        assert result.series_code == 12
        assert result.source_url == BASE_URL.format(code=12)
        assert result.params["formato"] == "json"
        assert result.params["dataInicial"] == "10/04/2026"
        assert result.params["dataFinal"] == "12/04/2026"
        assert result.http_headers["content-type"] == "application/json"
        assert result.library_version == __version__
        assert result.parser_version == PARSER_VERSION
        assert result.status_code == 200
        assert result.byte_size == len(PAYLOAD)
        assert result.sha256 == hashlib.sha256(PAYLOAD).hexdigest()
        assert result.fetched_at.tzinfo is not None
        assert result.retry_after is None

    def test_transport_is_used_instead_of_requests(self):
        with patch("bcbpy.client.requests.get") as mock_get:
            fetch_raw(12, start_date="2026-01-01", end_date="2026-01-31", transport=_transport(PAYLOAD))
            mock_get.assert_not_called()

    def test_empty_body_is_returned(self):
        result = fetch_raw(12, start_date="2026-01-01", end_date="2026-01-31", transport=_transport(EMPTY_PAYLOAD))
        assert result.payload == EMPTY_PAYLOAD

    def test_malformed_body_is_returned(self):
        result = fetch_raw(12, start_date="2026-01-01", end_date="2026-01-31", transport=_transport(MALFORMED_PAYLOAD))
        assert result.payload == MALFORMED_PAYLOAD

    def test_long_range_still_rejected(self):
        calls = []
        with pytest.raises(ValueError, match="10-year API limit"):
            fetch_raw(
                12,
                start_date="2010-01-01",
                end_date="2025-01-01",
                transport=_transport(PAYLOAD, calls=calls),
            )
        assert calls == []

    def test_429_exposes_retry_after(self):
        transport = _transport(b"", status_code=429, headers={"Retry-After": "7"})
        with pytest.raises(SGSRateLimitError) as excinfo:
            fetch_raw(12, start_date="2026-01-01", end_date="2026-01-31", transport=transport)
        assert excinfo.value.retry_after == 7.0
        assert excinfo.value.status_code == 429
        assert excinfo.value.headers["retry-after"] == "7"

    def test_429_parses_http_date_retry_after(self):
        when = datetime.now(timezone.utc) + timedelta(seconds=30)
        transport = _transport(b"", status_code=429, headers={"Retry-After": format_datetime(when)})
        with pytest.raises(SGSRateLimitError) as excinfo:
            fetch_raw(12, start_date="2026-01-01", end_date="2026-01-31", transport=transport)
        assert excinfo.value.retry_after is not None
        assert 0 <= excinfo.value.retry_after <= 30 + 2

    def test_fetch_series_accepts_transport(self):
        df = fetch_series(12, start_date="2026-04-10", end_date="2026-04-12", transport=_transport(PAYLOAD))
        assert len(df) == 1
        assert df["valor"].iloc[0] == 0.054


class TestFetchRawRange:
    def test_short_range_is_one_partition(self):
        calls = []
        results = fetch_raw_range(
            12,
            start_date="2024-01-01",
            end_date="2024-12-31",
            transport=_transport(PAYLOAD, calls=calls),
        )
        assert len(results) == 1
        assert len(calls) == 1
        assert calls[0]["params"]["dataInicial"] == "01/01/2024"
        assert calls[0]["params"]["dataFinal"] == "31/12/2024"

    def test_long_range_splits_on_ten_year_boundary(self):
        start = datetime(2010, 1, 1)
        end = datetime(2020, 1, 2)
        calls = []
        results = fetch_raw_range(
            433,
            start_date=start.date(),
            end_date=end.date(),
            transport=_transport(PAYLOAD, calls=calls),
        )
        assert len(results) == 2
        assert len(calls) == 2
        first_end = datetime.strptime(calls[0]["params"]["dataFinal"], "%d/%m/%Y")
        second_start = datetime.strptime(calls[1]["params"]["dataInicial"], "%d/%m/%Y")
        assert second_start == first_end + timedelta(days=1)
        assert calls[0]["params"]["dataInicial"] == "01/01/2010"
        assert calls[1]["params"]["dataFinal"] == end.strftime("%d/%m/%Y")
        for call in calls:
            _validate_date_range(call["params"]["dataInicial"], call["params"]["dataFinal"])

    def test_exact_max_span_is_one_call(self):
        start = datetime(2015, 1, 1)
        end = datetime(2025, 1, 1)
        calls = []
        results = fetch_raw_range(
            12,
            start_date=start.date(),
            end_date=end.date(),
            transport=_transport(PAYLOAD, calls=calls),
        )
        assert len(results) == 1
        assert len(calls) == 1

    def test_duplicate_boundary_dates_are_not_requested(self):
        windows = list(_date_partitions("01/01/2010", "01/01/2025"))
        seen = []
        for start, end in windows:
            seen.append(start)
            seen.append(end)
        assert len(seen) == len(set(seen))
        for i in range(len(windows) - 1):
            left = datetime.strptime(windows[i][1], "%d/%m/%Y")
            right = datetime.strptime(windows[i + 1][0], "%d/%m/%Y")
            assert right == left + timedelta(days=1)

    def test_leap_day_partition_uses_february_28_anniversary(self):
        windows = list(_date_partitions("29/02/2012", "01/03/2022"))
        assert windows == [("29/02/2012", "28/02/2022"), ("01/03/2022", "01/03/2022")]

    def test_empty_partition_is_kept(self):
        payloads = [EMPTY_PAYLOAD, PAYLOAD]
        calls = []

        def getter(url, params=None, timeout=30):
            calls.append(params)
            body = payloads[len(calls) - 1]
            resp = MagicMock()
            resp.status_code = 200
            resp.content = body
            resp.headers = {}
            resp.raise_for_status = MagicMock()
            return resp

        start = datetime(2010, 1, 1)
        end = datetime(2020, 1, 2)
        results = fetch_raw_range(12, start_date=start.date(), end_date=end.date(), transport=getter)
        assert len(results) == 2
        assert results[0].payload == EMPTY_PAYLOAD
        assert results[1].payload == PAYLOAD

    def test_inverted_range_never_calls_transport(self):
        calls = []
        with pytest.raises(ValueError, match="is before start_date"):
            fetch_raw_range(
                12,
                start_date="2024-12-31",
                end_date="2024-01-01",
                transport=_transport(PAYLOAD, calls=calls),
            )
        assert calls == []

    def test_fetch_series_still_rejects_composed_span(self):
        with pytest.raises(ValueError, match="10-year API limit"):
            fetch_series(12, start_date="2010-01-01", end_date="2025-01-01", transport=_transport(PAYLOAD))
