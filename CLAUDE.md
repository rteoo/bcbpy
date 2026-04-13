# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python package (`bcb_sgs/`) for fetching economic and financial time series from the Banco Central do Brasil SGS API. Covers 120+ curated series: exchange rates, interest rates (Selic, CDI), inflation (IPCA, IGP-M), GDP, employment, industrial production, and more.

## Running

```bash
pip install -r requirements.txt
python main.py
```

## Dependencies

- pandas
- requests

## Architecture

```
bcb_sgs/
├── __init__.py      # Public API exports
├── constants.py     # Base URLs, date format, API config
├── codes.py         # 120+ series codes organized in 14 category dicts
└── client.py        # API client: fetch_series, fetch_last, fetch_multiple, list_codes, search_codes
```

- `codes.py` — categorized dicts (EXCHANGE_RATES, INTEREST_RATES, INFLATION, etc.) mapping readable names to SGS numeric codes. `ALL_CODES` merges everything for flat lookup. `CATEGORIES` maps category names to their dicts.
- `client.py` — handles HTTP requests, date format conversion (accepts YYYY-MM-DD or DD/MM/YYYY), 10-year range validation, and DataFrame construction. Custom exceptions: `SGSError`, `SGSRateLimitError`, `SGSEmptyResponseError`.
- `main.py` — CLI entry point demonstrating all client functions.
- `bcb_ptax_selic.py` — original legacy script (superseded by the package).

## API Details

- SGS dates use **DD/MM/YYYY** (Brazilian format) but the client accepts **YYYY-MM-DD** too.
- Date range queries are capped at **10 years** (BCB limit since March 2025).
- Rate limiting returns HTTP 429 (no official limit documented).
- Reference guide: `BCB_API_REFERENCE.md`
