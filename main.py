"""
BCB SGS API — Example Usage

Demonstrates the bcbpy package for fetching economic data
from the Banco Central do Brasil.
"""

from bcbpy import (
    fetch_series,
    fetch_last,
    fetch_multiple,
    list_codes,
    search_codes,
    INTEREST_RATES,
    EXCHANGE_RATES,
    INFLATION,
)


def main():
    separator = "- - " * 15

    # --- List all available codes ---
    print("=" * 60)
    print("  ALL AVAILABLE SGS SERIES CODES")
    print("=" * 60)
    list_codes()

    print(f"\n{separator}")

    # --- Search codes by keyword ---
    print("\nSearching for 'IPCA' codes:")
    search_codes("IPCA")

    print(f"\n{separator}")

    # --- Fetch last 5 CDI observations ---
    print("\nLast 5 CDI daily rates:")
    cdi = fetch_last(INTEREST_RATES["CDI_DAILY"], n=5)
    print(cdi)

    print(f"\n{separator}")

    # --- Fetch last 5 USD/BRL rates ---
    print("\nLast 5 USD/BRL (PTAX sale) rates:")
    usd = fetch_last(EXCHANGE_RATES["USD_SALE_DAILY"], n=5)
    print(usd)

    print(f"\n{separator}")

    # --- Fetch IPCA with date range ---
    print("\nIPCA (official inflation) — 2024:")
    ipca = fetch_series(INFLATION["IPCA"], start_date="2024-01-01", end_date="2024-12-31")
    print(ipca)

    print(f"\n{separator}")

    # --- Fetch multiple series at once ---
    print("\nMultiple series (CDI + Selic + IPCA) — last available data:")
    df = fetch_multiple(
        {
            "CDI": INTEREST_RATES["CDI_DAILY"],
            "SELIC": INTEREST_RATES["SELIC_DAILY"],
        },
        start_date="2024-01-01",
        end_date="2024-12-31",
    )
    print(df.tail(10))


if __name__ == "__main__":
    main()
