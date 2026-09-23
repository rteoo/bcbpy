# AGENTS.md

Canonical agent contract for this repository — it guides Claude Code, Codex, and any other coding agent. `CLAUDE.md` is a single `@AGENTS.md` import so Claude Code auto-loads these rules; make all edits here, never fork guidance into `CLAUDE.md`.

## Project

`bcbpy` is a Python client library for the **BCB SGS** (Banco Central do Brasil — Sistema Gerenciador de Séries Temporais) API. It fetches Brazilian economic/financial time series (FX, interest rates, inflation, GDP, employment, …) as pandas DataFrames, and ships a curated registry of 114 SGS series codes across 14 categories. Public API (`bcbpy/__init__.py`): `fetch_series`, `fetch_last`, `fetch_multiple`, `fetch_raw`, `fetch_raw_range`, `RawResult`, `list_codes`, `search_codes`, plus `SGSError` / `SGSHTTPError` / `SGSRateLimitError` / `SGSEmptyResponseError`. Library only — no CLI, no `__main__`.

## Stack

- Python `>=3.10` (classifiers cover 3.10–3.13). Runtime deps: `pandas>=1.5`, `requests>=2.28`.
- Packaging: PEP 621 `pyproject.toml`, setuptools + wheel build backend. Dev extra (`.[dev]`): `pytest>=7.0`, `build>=1.0`, `twine>=4.0`.
- No lint / formatter / type-checker tooling exists (no ruff/flake8/black/mypy config or deps). The code uses no type hints. Don't assume or invent these conventions; if adding one is in scope, note it's currently absent by design.

## Commands

```bash
pip install -e ".[dev]"                              # local dev setup (there is NO requirements.txt)
pytest                                               # full suite
pytest -m "not integration"                          # offline/CI-safe subset (unit only)
pytest tests/test_integration.py -m integration      # live-API tests — network, opt-in, may be slow
python -m build                                      # build sdist+wheel (release pipeline)
```

- The BCB SGS API is public/unauthenticated — no API key needed to use the library.
- Integration tests hit the **live** BCB API. Exclude them by default; never run them during automated/agentic edits without explicit instruction.

## Architecture

Four-module package, layered:

- `bcbpy/constants.py` — `BASE_URL`, `LAST_N_URL`, `DATE_FORMAT`, `MAX_DATE_RANGE_YEARS`, `PARSER_VERSION`.
- `bcbpy/codes.py` — pure data: 114 SGS codes in 14 category dicts + derived `CATEGORIES` / `ALL_CODES`. Hand-curated, not generated.
- `bcbpy/artifacts.py` — public `RawResult` descriptor (payload bytes, URL, params, headers, fetch time, series identity, library/parser version).
- `bcbpy/client.py` — HTTP, DataFrame conversion, raw fetch, and bounded range composition; imports from the other modules.
- `bcbpy/__init__.py` — re-exports the public surface; keep `__all__` in sync when adding/removing exports.

Load-bearing behavior to preserve:
- `_format_date` accepts both `YYYY-MM-DD` and `DD/MM/YYYY` and normalizes to BCB's `DD/MM/YYYY`. Keep the dual-format acceptance and the `DATE_FORMAT` constant.
- `_validate_date_range` enforces a client-side 10-year query limit mirroring the real BCB restriction — do not silently remove it from `fetch_series` / `fetch_raw`. Longer windows belong on `fetch_raw_range`.
- `SGSRateLimitError` exposes `retry_after` / response headers. Do not auto-retry or swallow 429.
- Other HTTP error statuses raise `SGSHTTPError`, which subclasses both `SGSError` and `requests.HTTPError`. Keep both bases so either `except` style keeps working.

## Testing Conventions

pytest under `tests/` (`test_client.py`, `test_raw.py`, `test_codes.py`, `test_package.py`, `test_version.py`, `test_integration.py`); classes `Test*`, methods `test_*`. The `integration` marker is registered in `pyproject.toml` and applied module-wide in `test_integration.py` (opt-in via `-m integration`, excluded via `-m "not integration"`). No coverage tooling.

- Unit tests mock `requests.get` (or inject a `transport=` callable, or `bcbpy.client.fetch_series` for `fetch_multiple`) via `unittest.mock.patch`. New client functions get a mocked unit test and, if they hit the network, a matching `@pytest.mark.integration` test.
- Code registry (`codes.py`): keys must be `UPPER_SNAKE_CASE`, values unique positive ints across all categories — enforced by `tests/test_codes.py`. Adding a series code means updating the category dict (`CATEGORIES`/`ALL_CODES` stay auto-derived) and bumping the corresponding `test_category_sizes` count assertion. Verify a new or changed code against its SGS series name first: the registry has shipped mislabeled codes before (fixed in 2.2.0).

## Release & CI

- **Test CI:** `.github/workflows/tests.yml` runs the unit subset (`pytest -m "not integration"`) on Python 3.10–3.13 for every push and PR to `main`. Integration tests stay out of CI (live API). No lint/type-check gate exists.
- Publishing is CI-driven and OIDC-based (PyPI trusted publishing): a `v*` tag push or a published GitHub Release triggers `publish.yml`; TestPyPI staging is manual `workflow_dispatch` on `test-publish.yml`. **Do not** hand-run `twine upload` or manage PyPI tokens.
- **Version-bump discipline:** the packaged version is dynamic — `pyproject.toml` reads it from `bcbpy/__init__.py` `__version__` via `[tool.setuptools.dynamic]`, so `__version__` is the single source of truth. A release bumps only `__version__`, adds a `CHANGELOG.md` entry, and pushes a matching `v*` tag.

## Known Drift (don't "fix" into existence)

- `requirements.txt` and the `main.py` CLI demo were **deleted** (commit `cc4f0aa`). Use the `[dev]` extra; there is no `main.py`. Only old `CHANGELOG.md` entries still mention them.
- Some registry keys don't match their SGS series names (`AVG_NOMINAL_INCOME` is real habitual income, `REER_EUR` is the Deutsche mark index, `SELIC_OVERNIGHT_ANNUAL` / `CDI_OVERNIGHT` are monthly-accumulated annualized rates). Renaming them is a breaking change, so they stay until a major release.
- Canonical repo is `github.com/rteoo/bcbpy` (the live remote, the `pyproject.toml` URLs, and the PyPI project all agree). Older `CHANGELOG.md` entries reference the former `github.com/TeodoroRodrigo/bcbpy` path — that is historical and must stay as written.
- Licensing duality: code is MIT; data fetched via the client remains under ODbL (see `LICENSE`) — relevant to any data-redistribution feature/doc.

## Git

Default branch `main`. Conventional-commit-style messages (`feat:`, `fix:`, `chore:`, `release:`). No AI attribution in commit messages.
