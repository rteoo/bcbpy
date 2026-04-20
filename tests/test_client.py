"""Tests for bcbpy.client — API client functions (mocked, no network calls)."""

import json
from datetime import date, datetime
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from bcbpy.client import (
    _format_date,
    _validate_date_range,
    _handle_response,
    fetch_series,
    fetch_last,
    fetch_multiple,
    list_codes,
    search_codes,
    SGSError,
    SGSRateLimitError,
    SGSEmptyResponseError,
)


# ---- _format_date ----

class TestFormatDate:
    def test_none_returns_none(self):
        assert _format_date(None) is None

    def test_iso_format(self):
        assert _format_date("2024-01-15") == "15/01/2024"

    def test_brazilian_format(self):
        assert _format_date("15/01/2024") == "15/01/2024"

    def test_date_object(self):
        assert _format_date(date(2024, 3, 10)) == "10/03/2024"

    def test_datetime_object(self):
        assert _format_date(datetime(2024, 12, 25, 10, 30)) == "25/12/2024"

    def test_invalid_string_raises(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            _format_date("not-a-date")

    def test_invalid_type_raises(self):
        with pytest.raises(TypeError, match="Expected str or date"):
            _format_date(12345)


# ---- _validate_date_range ----

class TestValidateDateRange:
    def test_none_dates_pass(self):
        _validate_date_range(None, None)
        _validate_date_range("01/01/2024", None)
        _validate_date_range(None, "01/01/2024")

    def test_valid_range_passes(self):
        _validate_date_range("01/01/2020", "31/12/2024")

    def test_end_before_start_raises(self):
        with pytest.raises(ValueError, match="is before start_date"):
            _validate_date_range("01/01/2025", "01/01/2020")

    def test_exceeds_10_years_raises(self):
        with pytest.raises(ValueError, match="10-year API limit"):
            _validate_date_range("01/01/2010", "01/01/2025")

    def test_exactly_10_years_passes(self):
        _validate_date_range("01/01/2015", "31/12/2024")


# ---- _handle_response ----

class TestHandleResponse:
    def test_429_raises_rate_limit(self):
        resp = MagicMock()
        resp.status_code = 429
        with pytest.raises(SGSRateLimitError):
            _handle_response(resp)

    def test_404_raises_sgs_error(self):
        resp = MagicMock()
        resp.status_code = 404
        with pytest.raises(SGSError, match="Series not found"):
            _handle_response(resp)

    def test_200_passes(self):
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        _handle_response(resp)
        resp.raise_for_status.assert_called_once()


# ---- fetch_series ----

MOCK_JSON = [
    {"data": "10/04/2026", "valor": "0.054"},
    {"data": "11/04/2026", "valor": "0.055"},
    {"data": "12/04/2026", "valor": "0.053"},
]


def _mock_response(json_data, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


class TestFetchSeries:
    @patch("bcbpy.client.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(MOCK_JSON)
        df = fetch_series(12, start_date="2026-04-10", end_date="2026-04-12")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert "valor" in df.columns
        assert df.index.name == "data"

    @patch("bcbpy.client.requests.get")
    def test_valor_is_numeric(self, mock_get):
        mock_get.return_value = _mock_response(MOCK_JSON)
        df = fetch_series(12, start_date="2026-04-10", end_date="2026-04-12")
        assert df["valor"].dtype == float

    @patch("bcbpy.client.requests.get")
    def test_empty_response_raises(self, mock_get):
        mock_get.return_value = _mock_response([])
        with pytest.raises(SGSEmptyResponseError):
            fetch_series(99999, start_date="2026-01-01", end_date="2026-01-31")

    @patch("bcbpy.client.requests.get")
    def test_url_contains_code(self, mock_get):
        mock_get.return_value = _mock_response(MOCK_JSON)
        fetch_series(433, start_date="2026-01-01", end_date="2026-04-01")
        url = mock_get.call_args[0][0]
        assert "bcdata.sgs.433" in url

    @patch("bcbpy.client.requests.get")
    def test_date_params_sent(self, mock_get):
        mock_get.return_value = _mock_response(MOCK_JSON)
        fetch_series(12, start_date="2026-01-01", end_date="2026-04-01")
        params = mock_get.call_args[1]["params"]
        assert params["dataInicial"] == "01/01/2026"
        assert params["dataFinal"] == "01/04/2026"

    @patch("bcbpy.client.requests.get")
    def test_no_dates_no_date_params(self, mock_get):
        mock_get.return_value = _mock_response(MOCK_JSON)
        fetch_series(12)
        params = mock_get.call_args[1]["params"]
        assert "dataInicial" not in params
        assert "dataFinal" not in params


# ---- fetch_last ----

class TestFetchLast:
    @patch("bcbpy.client.requests.get")
    def test_returns_n_rows(self, mock_get):
        mock_get.return_value = _mock_response(MOCK_JSON[:2])
        df = fetch_last(12, n=2)
        assert len(df) == 2

    @patch("bcbpy.client.requests.get")
    def test_url_contains_ultimos(self, mock_get):
        mock_get.return_value = _mock_response(MOCK_JSON)
        fetch_last(1, n=5)
        url = mock_get.call_args[0][0]
        assert "ultimos/5" in url

    @patch("bcbpy.client.requests.get")
    def test_empty_response_raises(self, mock_get):
        mock_get.return_value = _mock_response([])
        with pytest.raises(SGSEmptyResponseError):
            fetch_last(99999, n=5)


# ---- fetch_multiple ----

class TestFetchMultiple:
    @patch("bcbpy.client.fetch_series")
    def test_merges_columns(self, mock_fetch):
        df1 = pd.DataFrame({"valor": [0.05, 0.06]}, index=pd.to_datetime(["2026-04-10", "2026-04-11"]))
        df1.index.name = "data"
        df2 = pd.DataFrame({"valor": [0.04, 0.05]}, index=pd.to_datetime(["2026-04-10", "2026-04-11"]))
        df2.index.name = "data"
        mock_fetch.side_effect = [df1, df2]

        result = fetch_multiple({"CDI": 12, "SELIC": 11}, start_date="2026-04-10", end_date="2026-04-11")
        assert list(result.columns) == ["CDI", "SELIC"]
        assert len(result) == 2

    @patch("bcbpy.client.fetch_series")
    def test_all_empty_raises(self, mock_fetch):
        mock_fetch.side_effect = SGSEmptyResponseError("empty")
        with pytest.raises(SGSEmptyResponseError, match="No data returned for any"):
            fetch_multiple({"CDI": 12}, start_date="2026-01-01")

    @patch("bcbpy.client.fetch_series")
    def test_partial_empty_skips(self, mock_fetch):
        df1 = pd.DataFrame({"valor": [0.05]}, index=pd.to_datetime(["2026-04-10"]))
        df1.index.name = "data"
        mock_fetch.side_effect = [df1, SGSEmptyResponseError("empty")]

        result = fetch_multiple({"CDI": 12, "BAD": 99999}, start_date="2026-04-10")
        assert list(result.columns) == ["CDI"]


# ---- list_codes ----

class TestListCodes:
    def test_list_all(self, capsys):
        list_codes()
        output = capsys.readouterr().out
        assert "INTEREST_RATES" in output
        assert "EXCHANGE_RATES" in output
        assert "INFLATION" in output

    def test_list_single_category(self, capsys):
        list_codes("SAVINGS")
        output = capsys.readouterr().out
        assert "SAVINGS" in output
        assert "SAVINGS_RATE" in output
        assert "INTEREST_RATES" not in output

    def test_list_case_insensitive(self, capsys):
        list_codes("interest_rates")
        output = capsys.readouterr().out
        assert "INTEREST_RATES" in output

    def test_unknown_category(self, capsys):
        list_codes("NONEXISTENT")
        output = capsys.readouterr().out
        assert "Unknown category" in output


# ---- search_codes ----

class TestSearchCodes:
    def test_finds_matches(self):
        results = search_codes("CDI")
        assert "CDI_DAILY" in results
        assert "CDI_MONTHLY" in results
        assert results["CDI_DAILY"] == 12

    def test_case_insensitive(self):
        results = search_codes("ipca")
        assert "IPCA" in results

    def test_no_matches(self, capsys):
        results = search_codes("XYZNONEXISTENT")
        assert results == {}
        output = capsys.readouterr().out
        assert "No codes matching" in output

    def test_partial_match(self):
        results = search_codes("SELIC")
        assert len(results) >= 4  # SELIC_DAILY, SELIC_TARGET, SELIC_OVERNIGHT_ANNUAL, SELIC_MONTHLY_ACCUMULATED
