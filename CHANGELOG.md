# Changelog

## [v2.2.0] - 2026-09-23

### Added
- **`fetch_raw` / `fetch_raw_range` / `RawResult`** — warehouse-facing API returning payload bytes, canonical URL, query params, response headers, fetch time, series identity, SHA-256, and library/parser version (`sgs-json-1`).
- Injectable **`transport=`** GET callable on fetch helpers for deterministic tests.
- **`fetch_raw_range`** splits windows longer than the SGS 10-year limit into bounded partitions without duplicating the boundary date. Empty partition bodies are kept.
- **`SGSRateLimitError.retry_after`** (and response headers) parsed from `Retry-After`. Failures are not swallowed or auto-retried.
- **`SGSHTTPError`** for HTTP error statuses other than 429, carrying BCB's error text (e.g. the HTTP 406 explanation for undated daily queries). It subclasses both `SGSError` and `requests.HTTPError`, so existing handlers still catch it.

### Changed
- `fetch_series`, `fetch_last`, and `fetch_multiple` still return DataFrames and still enforce the 10-year single-call limit. Longer ranges stay on `fetch_raw_range`.
- `fetch_multiple` reports skipped empty series with `warnings.warn` instead of printing to stdout.
- SGS dates are parsed strictly as `DD/MM/YYYY`; an unparseable date raises `SGSError`.

### Removed
- **`INDUSTRIAL_PRODUCTION["PRODUCTION_GENERAL"]` (21858)** — SGS no longer serves this series (it returns an HTML error page after ~30s). The registry now holds 114 codes. Use `PRODUCTION_TOTAL` (21859).

### Fixed
- Ten-year range validation and `fetch_raw_range` partitioning now use a
  calendar anniversary instead of a fixed 366-day approximation. February 29
  uses February 28 in non-leap target years.
- **`IPCA_BREAKDOWN["IPCA_CORE_EX1"]`** pointed to 1621, a discontinued unemployment series. It now points to 16121 (IPCA core EX1).
- **`CONFIDENCE["ICC_FUTURE_EXPECTATIONS"]` / `["ICC_CURRENT_CONDITIONS"]`** were swapped. Future expectations is 4395; current conditions is 4394.
- Non-JSON responses (SGS answers unknown series with an HTML page) raise `SGSError` instead of a raw JSON decode error.
- `end_date=""` is rejected like `start_date=""` instead of silently becoming today.

## [v2.1.1] - 2026-07-18

### Changed
- Documentation only — refreshed `AGENTS.md` to reflect the test CI workflow, dynamic versioning (`__version__` as the single source of truth), and the canonical `rteoo/bcbpy` repository. No library, API, or packaged-code changes.

## [v2.1.0] - 2026-07-18

### Added
- **Adversarial unit test suite** — expanded from 43 to 85 tests covering malformed API payloads, boundary date ranges, invalid `fetch_last` sizes, inverted ranges, and package metadata consistency.
- **CI workflow** (`.github/workflows/tests.yml`) — runs the unit suite on Python 3.10–3.13 for every push and pull request to `main`.

### Fixed
- `fetch_last` now rejects non-positive, non-integer, and boolean `n` with a clear `ValueError` instead of issuing a malformed API request.
- Malformed API responses (non-list payloads, or missing `data`/`valor` fields) now raise a descriptive `SGSError` instead of an opaque pandas error.
- `fetch_multiple({})` raises `ValueError` for empty input instead of a misleading "no data returned" error.
- `search_codes("")` returns no matches instead of the entire code catalog.
- Realigned `__version__`, which had drifted out of sync with the packaged version.

## [v2.0.0] - 2026-04-20

### Changed (breaking)
- **Project renamed from `bcb-sgs` to `bcbpy`.** This is a breaking change for imports and installation:
  - PyPI distribution: `pip install bcb-sgs` → `pip install bcbpy`
  - Python import: `from bcb_sgs import ...` → `from bcbpy import ...`
  - GitHub repository: `TeodoroRodrigo/bcb-sgs` → `TeodoroRodrigo/bcbpy`
- Updated all documentation, examples, project URLs, and GitHub Actions environment targets to reflect the new name

### Migration

```python
# old
from bcb_sgs import fetch_series, INTEREST_RATES

# new
from bcbpy import fetch_series, INTEREST_RATES
```

## [v1.1.1] - 2026-04-20

### Added
- **Two-stage publish pipeline** — separate workflows for staging and production:
  - `.github/workflows/test-publish.yml` — manual dispatch only, publishes to **TestPyPI** (environment: `testpypi`)
  - `.github/workflows/publish.yml` — triggers on `v*` tag push or GitHub release, publishes to **PyPI** (environment: `pypi`)

### Changed
- Trusted publishing now uses distinct GitHub environments for test vs production to prevent accidental cross-publication

## [v1.1.0] - 2026-04-20

### Added
- **PyPI packaging** — `pyproject.toml` with PEP 621 metadata (SPDX license, loose dependency constraints, optional `dev` extras, classifiers, project URLs)
- **MIT License** — `LICENSE` file for the client code (BCB data remains under ODbL, as noted in the license)
- **`__version__`** attribute exported from `bcb_sgs`
- **GitHub Actions workflow** — `.github/workflows/publish.yml` automates PyPI releases on `v*` tag push via trusted publishing (OIDC, no long-lived tokens)
- **`.gitignore`** — standard Python ignore patterns (build artifacts, caches, venvs, secrets)

### Changed
- Minimum Python version raised from **3.8 → 3.10** (Python 3.8 reached end-of-life in October 2024)
- README updates for repository structure and project name

### Removed
- Legacy standalone script `bcb_ptax_selic.py` (superseded by the `bcb_sgs` package since v1.0.0)

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
