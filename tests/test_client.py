"""Tests for bcbpy.client — API client functions (mocked, no network calls)."""

from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
import requests

from bcbpy.client import (
    _format_date,
    _validate_date_range,
    _handle_response,
    _build_dataframe,
    fetch_series,
    fetch_last,
    fetch_multiple,
    list_codes,
    search_codes,
    SGSError,
    SGSRateLimitError,
    SGSEmptyResponseError,
)
from bcbpy.constants import MAX_DATE_RANGE_YEARS


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

    def test_bool_raises_type_error(self):
        # bool is an int subclass but is neither a str nor a date.
        with pytest.raises(TypeError, match="Expected str or date"):
            _format_date(True)

    def test_two_digit_year_rejected(self):
        # "24-01-15" must not silently parse to the year 24.
        with pytest.raises(ValueError, match="Invalid date format"):
            _format_date("24-01-15")

    def test_empty_string_rejected(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            _format_date("")

    def test_whitespace_padded_string_rejected(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            _format_date(" 2024-01-15 ")

    def test_impossible_calendar_date_rejected(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            _format_date("2024-02-30")

    def test_iso_roundtrip_is_not_reinterpreted_as_brazilian(self):
        # 03/04 must stay April 3rd (ISO), never be swapped to March 4th.
        assert _format_date("2024-04-03") == "03/04/2024"


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

    def test_same_day_passes(self):
        _validate_date_range("01/01/2024", "01/01/2024")

    def test_boundary_at_max_delta_passes(self):
        # The ceiling is MAX_DATE_RANGE_YEARS * 366 days; the last allowed day
        # must pass and one day beyond must fail (locks the exact boundary).
        start = datetime(2015, 1, 1)
        edge = start + timedelta(days=MAX_DATE_RANGE_YEARS * 366)
        _validate_date_range(start.strftime("%d/%m/%Y"), edge.strftime("%d/%m/%Y"))

    def test_one_day_past_boundary_raises(self):
        start = datetime(2015, 1, 1)
        over = start + timedelta(days=MAX_DATE_RANGE_YEARS * 366 + 1)
        with pytest.raises(ValueError, match="10-year API limit"):
            _validate_date_range(start.strftime("%d/%m/%Y"), over.strftime("%d/%m/%Y"))


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

    def test_500_delegates_to_raise_for_status(self):
        # Non-special error codes must be surfaced via raise_for_status,
        # not swallowed.
        resp = MagicMock()
        resp.status_code = 500
        resp.raise_for_status.side_effect = requests.HTTPError("boom")
        with pytest.raises(requests.HTTPError):
            _handle_response(resp)


# ---- _build_dataframe (malformed payload handling) ----

class TestBuildDataframe:
    def test_non_list_payload_raises_sgs_error(self):
        # BCB occasionally returns an error object instead of a list; this must
        # not surface as an opaque pandas "scalar values" ValueError.
        with pytest.raises(SGSError, match="expected a JSON list"):
            _build_dataframe({"error": "bad request"}, code=12)

    def test_string_payload_raises_sgs_error(self):
        with pytest.raises(SGSError, match="expected a JSON list"):
            _build_dataframe("<html>error</html>", code=12)

    def test_empty_list_raises_empty_response(self):
        with pytest.raises(SGSEmptyResponseError):
            _build_dataframe([], code=12)

    def test_missing_valor_field_raises(self):
        with pytest.raises(SGSError, match="missing field.*valor"):
            _build_dataframe([{"data": "01/01/2024"}], code=12)

    def test_missing_data_field_raises(self):
        with pytest.raises(SGSError, match="missing field.*data"):
            _build_dataframe([{"valor": "1.0"}], code=12)

    def test_non_numeric_valor_coerced_to_nan(self):
        # BCB uses empty/placeholder values for undisclosed observations; those
        # become NaN rather than crashing the whole fetch.
        df = _build_dataframe(
            [{"data": "01/01/2024", "valor": "0.5"},
             {"data": "02/01/2024", "valor": ""}],
            code=12,
        )
        assert df["valor"].iloc[0] == 0.5
        assert pd.isna(df["valor"].iloc[1])

    def test_index_is_datetime_and_named(self):
        df = _build_dataframe([{"data": "15/03/2024", "valor": "1"}], code=12)
        assert df.index.name == "data"
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index[0] == pd.Timestamp("2024-03-15")


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

    @patch("bcbpy.client.requests.get")
    def test_formato_param_always_sent(self, mock_get):
        mock_get.return_value = _mock_response(MOCK_JSON)
        fetch_series(12)
        assert mock_get.call_args[1]["params"]["formato"] == "json"

    @patch("bcbpy.client.requests.get")
    def test_start_only_defaults_end_to_today(self, mock_get):
        # When only start_date is given, end must default to today so the range
        # is bounded — not left open.
        mock_get.return_value = _mock_response(MOCK_JSON)
        fetch_series(12, start_date="2024-01-01")
        params = mock_get.call_args[1]["params"]
        assert params["dataInicial"] == "01/01/2024"
        assert params["dataFinal"] == _format_date(date.today())

    @patch("bcbpy.client.requests.get")
    def test_end_only_sends_no_start_param(self, mock_get):
        mock_get.return_value = _mock_response(MOCK_JSON)
        fetch_series(12, end_date="2024-01-31")
        params = mock_get.call_args[1]["params"]
        assert "dataInicial" not in params
        assert params["dataFinal"] == "31/01/2024"

    @patch("bcbpy.client.requests.get")
    def test_future_start_defaulting_to_today_raises(self, mock_get):
        # start in the future + implicit end=today would be an inverted range;
        # it must fail loudly before hitting the network.
        mock_get.return_value = _mock_response(MOCK_JSON)
        with pytest.raises(ValueError, match="is before start_date"):
            fetch_series(12, start_date="2999-01-01")
        mock_get.assert_not_called()

    @patch("bcbpy.client.requests.get")
    def test_invalid_range_never_calls_network(self, mock_get):
        with pytest.raises(ValueError):
            fetch_series(12, start_date="2024-12-31", end_date="2024-01-01")
        mock_get.assert_not_called()

    @patch("bcbpy.client.requests.get")
    def test_malformed_payload_raises_sgs_error(self, mock_get):
        mock_get.return_value = _mock_response({"error": "bad"})
        with pytest.raises(SGSError, match="expected a JSON list"):
            fetch_series(12, start_date="2024-01-01", end_date="2024-01-31")

    @patch("bcbpy.client.requests.get")
    def test_rate_limit_propagates(self, mock_get):
        mock_get.return_value = _mock_response(MOCK_JSON, status_code=429)
        with pytest.raises(SGSRateLimitError):
            fetch_series(12, start_date="2024-01-01", end_date="2024-01-31")


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

    @patch("bcbpy.client.requests.get")
    def test_default_n_is_10(self, mock_get):
        mock_get.return_value = _mock_response(MOCK_JSON)
        fetch_last(12)
        assert "ultimos/10" in mock_get.call_args[0][0]

    @pytest.mark.parametrize("bad_n", [0, -1, -100])
    @patch("bcbpy.client.requests.get")
    def test_non_positive_n_raises_before_network(self, mock_get, bad_n):
        with pytest.raises(ValueError, match="positive integer"):
            fetch_last(12, n=bad_n)
        mock_get.assert_not_called()

    @pytest.mark.parametrize("bad_n", [2.9, "5", None, 3.0])
    @patch("bcbpy.client.requests.get")
    def test_non_int_n_raises(self, mock_get, bad_n):
        with pytest.raises(ValueError, match="positive integer"):
            fetch_last(12, n=bad_n)
        mock_get.assert_not_called()

    @patch("bcbpy.client.requests.get")
    def test_bool_n_rejected(self, mock_get):
        # True is an int subclass equal to 1; it must not sneak through as n=1.
        with pytest.raises(ValueError, match="positive integer"):
            fetch_last(12, n=True)
        mock_get.assert_not_called()


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

    @patch("bcbpy.client.fetch_series")
    def test_empty_codes_dict_raises_value_error(self, mock_fetch):
        # Empty input is a caller error, not "no data returned".
        with pytest.raises(ValueError, match="empty"):
            fetch_multiple({})
        mock_fetch.assert_not_called()

    @patch("bcbpy.client.fetch_series")
    def test_non_empty_errors_propagate(self, mock_fetch):
        # Only SGSEmptyResponseError is tolerated per-series; a rate-limit must
        # abort the whole batch rather than be silently swallowed.
        mock_fetch.side_effect = SGSRateLimitError("429")
        with pytest.raises(SGSRateLimitError):
            fetch_multiple({"CDI": 12}, start_date="2026-01-01")

    @patch("bcbpy.client.fetch_series")
    def test_column_order_follows_input_dict(self, mock_fetch):
        idx = pd.to_datetime(["2026-04-10"])
        def make(_code, *a, **k):
            df = pd.DataFrame({"valor": [1.0]}, index=idx)
            df.index.name = "data"
            return df
        mock_fetch.side_effect = make
        result = fetch_multiple({"Z": 1, "A": 2, "M": 3}, start_date="2026-04-10")
        assert list(result.columns) == ["Z", "A", "M"]

    @patch("bcbpy.client.fetch_series")
    def test_misaligned_indexes_union_with_nan(self, mock_fetch):
        df1 = pd.DataFrame({"valor": [1.0, 2.0]},
                           index=pd.to_datetime(["2026-04-10", "2026-04-11"]))
        df1.index.name = "data"
        df2 = pd.DataFrame({"valor": [9.0]}, index=pd.to_datetime(["2026-04-11"]))
        df2.index.name = "data"
        mock_fetch.side_effect = [df1, df2]
        result = fetch_multiple({"A": 1, "B": 2}, start_date="2026-04-10")
        assert len(result) == 2
        assert pd.isna(result.loc[pd.Timestamp("2026-04-10"), "B"])
        assert result.loc[pd.Timestamp("2026-04-11"), "B"] == 9.0


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

    def test_empty_keyword_returns_no_matches(self, capsys):
        # An empty query must not report the entire catalog as "matches".
        results = search_codes("")
        assert results == {}
        assert "No codes matching" in capsys.readouterr().out

    def test_returned_codes_are_the_registry_values(self):
        from bcbpy.codes import ALL_CODES
        results = search_codes("IPCA")
        for name, code in results.items():
            assert ALL_CODES[name] == code
