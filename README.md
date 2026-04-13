# BCG SGS

Python client for the **BCB SGS** (Sistema Gerenciador de Series Temporais) API from the [Banco Central do Brasil](https://dadosabertos.bcb.gov.br/).

Fetch Brazilian economic and financial time series as pandas DataFrames with a simple, Pythonic interface. Includes **115 curated series codes** covering exchange rates, interest rates, inflation, GDP, employment, and more.

## Installation

```bash
git clone https://github.com/TeodoroRodrigo/BCB.git
cd BCB
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- pandas
- requests

## Quick Start

```python
from bcb_sgs import fetch_series, fetch_last, fetch_multiple, INTEREST_RATES, EXCHANGE_RATES

# Last 10 CDI daily rates
cdi = fetch_last(INTEREST_RATES["CDI_DAILY"], n=10)
print(cdi)

# USD/BRL exchange rate for 2024
usd = fetch_series(EXCHANGE_RATES["USD_SALE_DAILY"], start_date="2024-01-01", end_date="2024-12-31")
print(usd)

# Multiple series merged into one DataFrame
df = fetch_multiple(
    {"CDI": INTEREST_RATES["CDI_DAILY"], "SELIC": INTEREST_RATES["SELIC_DAILY"]},
    start_date="2024-01-01",
    end_date="2024-12-31",
)
print(df.tail())
```

## API Reference

### Functions

#### `fetch_series(code, start_date=None, end_date=None)`

Fetch a time series by its SGS numeric code. Returns a pandas DataFrame indexed by date.

```python
from bcb_sgs import fetch_series

# Accepts YYYY-MM-DD or DD/MM/YYYY date formats
ipca = fetch_series(433, start_date="2023-01-01", end_date="2024-12-31")
```

#### `fetch_last(code, n=10)`

Fetch the last N observations of a series.

```python
from bcb_sgs import fetch_last

selic = fetch_last(11, n=5)
```

#### `fetch_multiple(codes_dict, start_date=None, end_date=None)`

Fetch multiple series and merge them into a single DataFrame, one column per series.

```python
from bcb_sgs import fetch_multiple

df = fetch_multiple({"CDI": 12, "SELIC": 11, "TR": 226}, start_date="2024-01-01")
```

#### `list_codes(category=None)`

Print all available series codes. Pass a category name to filter.

```python
from bcb_sgs import list_codes

list_codes()                        # all 115 codes across 14 categories
list_codes("INTEREST_RATES")        # only interest rate codes
```

#### `search_codes(keyword)`

Search codes by keyword (case-insensitive). Returns a dict of matches.

```python
from bcb_sgs import search_codes

results = search_codes("IPCA")      # finds 15 IPCA-related codes
results = search_codes("USD")       # finds USD exchange rate codes
```

### Exceptions

| Exception | When |
|-----------|------|
| `SGSError` | Base exception for all API errors |
| `SGSRateLimitError` | API returns HTTP 429 (too many requests) |
| `SGSEmptyResponseError` | No data returned for the given query |

### Error Handling

```python
from bcb_sgs import fetch_series, SGSRateLimitError, SGSEmptyResponseError

try:
    df = fetch_series(433, start_date="2024-01-01")
except SGSRateLimitError:
    print("Rate limited — wait and retry")
except SGSEmptyResponseError:
    print("No data for this date range")
```

## Available Series Codes

115 curated codes organized in 14 categories:

| Category | Series | Examples |
|----------|--------|----------|
| `EXCHANGE_RATES` | 6 | USD/BRL daily sale/purchase, monthly averages |
| `INTEREST_RATES` | 10 | Selic, CDI, TR, TBF, TJLP |
| `INFLATION` | 17 | IPCA, INPC, IGP-M, IGP-DI, IPC-Fipe |
| `IPCA_BREAKDOWN` | 11 | Tradeable, non-tradeable, durables, services, cores |
| `IPCA_CATEGORIES` | 9 | Food, housing, transport, health, education |
| `GDP` | 13 | GDP current/constant/USD, per capita, quarterly components |
| `EMPLOYMENT` | 7 | Unemployment rate, labor force, income |
| `INDUSTRIAL_PRODUCTION` | 7 | Manufacturing, mining, capital/intermediate/consumer goods |
| `FINANCIAL_MARKETS` | 7 | Gold, Bovespa, IMA-B |
| `SAVINGS` | 2 | Savings rate and return |
| `CONFIDENCE` | 4 | Consumer (ICC) and business (ICEI) confidence |
| `ECONOMIC_ACTIVITY` | 1 | IBC-Br (GDP proxy, seasonally adjusted) |
| `BASIC_BASKET` | 16 | Cost of living by capital city |
| `EXCHANGE_RATE_INDEX` | 5 | Real effective exchange rate (USD, EUR, JPY, ARS) |

Use any code directly by number or via the category dictionaries:

```python
from bcb_sgs import INFLATION, GDP

# These are equivalent:
fetch_series(433)
fetch_series(INFLATION["IPCA"])
```

## API Limits

- **Date range:** max 10 years per query (BCB restriction since March 2025)
- **Rate limiting:** HTTP 429 on excessive requests (no official limit documented)
- **Date formats:** the client accepts both `YYYY-MM-DD` and `DD/MM/YYYY`

## Project Structure

```
BCB/
├── bcb_sgs/
│   ├── __init__.py      # Public API exports
│   ├── client.py        # API client functions and exceptions
│   ├── codes.py         # 115 curated series codes in 14 categories
│   └── constants.py     # Base URLs and API configuration
├── main.py              # CLI demo script
├── requirements.txt
├── BCB_API_REFERENCE.md # Full SGS + Olinda API reference guide
└── README.md
```

## Data Source

All data is fetched from the [BCB Open Data Portal](https://dadosabertos.bcb.gov.br/) under the [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/).

## License

This project uses open data provided by the Banco Central do Brasil.
