# Changelog

## [v1.2.0] - 2026-04-20

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
