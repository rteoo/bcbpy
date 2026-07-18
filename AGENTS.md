# AGENTS.md

Canonical agent contract for this repository — it guides Claude Code, Codex, and any other coding agent. `CLAUDE.md` is a single `@AGENTS.md` import so Claude Code auto-loads these rules; make all edits here, never fork guidance into `CLAUDE.md`.

## Project

`bcbpy` is a Python client library for the **BCB SGS** (Banco Central do Brasil — Sistema Gerenciador de Séries Temporais) API. It fetches Brazilian economic/financial time series (FX, interest rates, inflation, GDP, employment, …) as pandas DataFrames, and ships a curated registry of 115 SGS series codes across 14 categories. Public API (`bcbpy/__init__.py`): `fetch_series`, `fetch_last`, `fetch_multiple`, `list_codes`, `search_codes`, plus `SGSError` / `SGSRateLimitError` / `SGSEmptyResponseError`. Library only — no CLI, no `__main__`.

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

Three-module package, layered:

- `bcbpy/constants.py` — `BASE_URL`, `LAST_N_URL`, `DATE_FORMAT`, `MAX_DATE_RANGE_YEARS`.
- `bcbpy/codes.py` — pure data: 115 SGS codes in 14 category dicts + derived `CATEGORIES` / `ALL_CODES`. Hand-curated, not generated.
- `bcbpy/client.py` — all HTTP + DataFrame logic and the public functions/exceptions; imports from both modules.
- `bcbpy/__init__.py` — re-exports the public surface; keep `__all__` in sync when adding/removing exports.

Load-bearing behavior to preserve:
- `_format_date` accepts both `YYYY-MM-DD` and `DD/MM/YYYY` and normalizes to BCB's `DD/MM/YYYY`. Keep the dual-format acceptance and the `DATE_FORMAT` constant.
- `_validate_date_range` enforces a client-side 10-year query limit mirroring the real BCB restriction — do not silently remove it.

## Testing Conventions

pytest under `tests/` (`test_client.py`, `test_codes.py`, `test_integration.py`); classes `Test*`, methods `test_*`. The `integration` marker is registered in `pyproject.toml` and applied module-wide in `test_integration.py` (opt-in via `-m integration`, excluded via `-m "not integration"`). No coverage tooling.

- Unit tests mock `requests.get` (or `bcbpy.client.fetch_series` for `fetch_multiple`) via `unittest.mock.patch`. New client functions get a mocked unit test and, if they hit the network, a matching `@pytest.mark.integration` test.
- Code registry (`codes.py`): keys must be `UPPER_SNAKE_CASE`, values unique positive ints across all categories — enforced by `tests/test_codes.py`. Adding a series code means updating the category dict (`CATEGORIES`/`ALL_CODES` stay auto-derived) and bumping the corresponding `test_category_sizes` count assertion.

## Release & CI

- **No test/lint CI gate exists** — the only workflows (`.github/workflows/publish.yml`, `test-publish.yml`) are build-and-publish. "Tests pass" is verified manually via `pytest`.
- Publishing is CI-driven and OIDC-based (PyPI trusted publishing): a `v*` tag push or a published GitHub Release triggers `publish.yml`; TestPyPI staging is manual `workflow_dispatch` on `test-publish.yml`. **Do not** hand-run `twine upload` or manage PyPI tokens.
- **Version-bump discipline:** a release must update both `pyproject.toml` `version` and `bcbpy/__init__.py` `__version__` together. These are currently out of sync (`pyproject.toml` 2.0.0 vs `__init__.py` 1.2.0) — reconcile opportunistically; `pyproject.toml` is authoritative for packaging.

## Known Drift (don't "fix" into existence)

- README still references `pip install -r requirements.txt` and a `main.py` CLI demo — both were **deleted** (commit `cc4f0aa`). Use the `[dev]` extra; there is no `main.py`.
- `git remote origin` is `github.com/rteoo/bcbpy`, but `pyproject.toml` URLs and CHANGELOG point to `github.com/TeodoroRodrigo/bcbpy`. Confirm which is canonical with a human before propagating either.
- Licensing duality: code is MIT; data fetched via the client remains under ODbL (see `LICENSE`) — relevant to any data-redistribution feature/doc.

## Git

Default branch `main`. Conventional-commit-style messages (`feat:`, `fix:`, `chore:`, `release:`). No AI attribution in commit messages.
