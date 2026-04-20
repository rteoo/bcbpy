"""Integration tests — hit the live BCB SGS API.

Run with: pytest tests/test_integration.py -m integration
Skip with: pytest -m "not integration"
"""

import pytest
import pandas as pd

from bcbpy import (
    fetch_series,
    fetch_last,
    fetch_multiple,
    INTEREST_RATES,
    EXCHANGE_RATES,
    INFLATION,
    GDP,
)

pytestmark = pytest.mark.integration


class TestFetchSeriesLive:
    def test_cdi_daily(self):
        df = fetch_series(INTEREST_RATES["CDI_DAILY"], start_date="2024-01-01", end_date="2024-01-31")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "valor" in df.columns
        assert df.index.name == "data"
        assert df["valor"].dtype == float

    def test_ipca_monthly(self):
        df = fetch_series(INFLATION["IPCA"], start_date="2024-01-01", end_date="2024-12-31")
        assert len(df) == 12  # monthly data, 12 months

    def test_usd_daily(self):
        df = fetch_series(EXCHANGE_RATES["USD_SALE_DAILY"], start_date="2024-06-01", end_date="2024-06-30")
        assert len(df) > 15  # ~22 business days in June


class TestFetchLastLive:
    def test_last_5_cdi(self):
        df = fetch_last(INTEREST_RATES["CDI_DAILY"], n=5)
        assert len(df) == 5

    def test_last_10_usd(self):
        df = fetch_last(EXCHANGE_RATES["USD_SALE_DAILY"], n=10)
        assert len(df) == 10

    def test_last_1(self):
        df = fetch_last(INFLATION["IPCA"], n=1)
        assert len(df) == 1


class TestFetchMultipleLive:
    def test_cdi_and_selic(self):
        df = fetch_multiple(
            {"CDI": INTEREST_RATES["CDI_DAILY"], "SELIC": INTEREST_RATES["SELIC_DAILY"]},
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert "CDI" in df.columns
        assert "SELIC" in df.columns
        assert len(df) > 0
