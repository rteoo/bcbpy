# Changelog

## [v1.0.0] - 2026-04-13

### Added
- **`bcb_sgs` Python package** — full client for the BCB SGS (Sistema Gerenciador de Series Temporais) API
- **115 curated series codes** organized in 14 categories:
  - Exchange Rates (6), Interest Rates (10), Inflation (17), IPCA Breakdown (11), IPCA Categories (9)
  - GDP (13), Employment (7), Industrial Production (7), Financial Markets (7)
  - Savings (2), Confidence (4), Economic Activity (1), Basic Basket (16), Exchange Rate Index (5)
- **API client functions:**
  - `fetch_series(code, start_date, end_date)` — fetch a full time series as DataFrame
  - `fetch_last(code, n)` — fetch last N observations
  - `fetch_multiple(codes_dict, start_date, end_date)` — fetch and merge multiple series
  - `list_codes(category)` — list available series codes by category
  - `search_codes(keyword)` — search codes by keyword
- **Date handling** — accepts both `YYYY-MM-DD` and `DD/MM/YYYY` formats, with 10-year range validation
- **Error handling** — `SGSError`, `SGSRateLimitError`, `SGSEmptyResponseError` exceptions
- **Test suite** — 50 tests (43 unit tests with mocked API, 7 integration tests against live BCB API)
- `BCB_API_REFERENCE.md` — comprehensive SGS API developer reference with all endpoint patterns and series codes
- `README.md` — full documentation with quick start, API reference, and usage examples
- `main.py` — CLI demo script
