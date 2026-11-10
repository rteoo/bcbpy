# Migrating from bcbpy to bcb-data

The repository and PyPI distribution are `bcb-data`; the Python import package
is `bcb_data`. Install with `pip install bcb-data` and import with
`from bcb_data import ...`.
Both `bcb-data` 2.5.0 and the final `bcbpy` 2.5.0 compatibility release are
published on PyPI. Future releases use only `bcb-data`.

## Applications

Install `bcb-data` and change imports:

```python
from bcb_data import fetch_series, RawResult, SGSRateLimitError
```

The public API, numeric SGS codes, date handling, exception hierarchy, and parser
version are unchanged by this rename. Raw artifacts report the new library version.

The frozen `bcbpy` 2.5.0 distribution depends on `bcb-data==2.5.0`.
It aliases all public exports and the `bcbpy.client`, `bcbpy.codes`,
`bcbpy.constants`, and `bcbpy.artifacts` module paths to the canonical objects.
Existing imports, exception catches, monkeypatch targets, and raw-result pickles
continue to work. New applications should import `bcb_data` directly.

`bcbpy` receives no further releases or dependency updates. Its version and
exact dependency stay at 2.5.0 even when `bcb-data` advances. Archiving the
legacy PyPI project preserves existing installations and download history;
it prevents new uploads. Future fixes and features require migrating to
`bcb-data` directly. Keep `compat/bcbpy` unchanged as the final release source.

Do not bundle the compatibility namespace inside the `bcb-data` wheel: the two
distributions own separate import directories and can be installed together.
Keep all previous `bcbpy` releases and tags. PyPI release history and download
counts remain attached to the old project; this is a new project, not an
in-place PyPI rename.

## GitHub

The repository is `rteoo/bcb-data`. Keep the existing repository ID, visibility,
refs, branch protection, and GitHub environments. Do not create a replacement
at an old GitHub path, which would interfere with redirects.

Update each existing checkout's origin to `https://github.com/rteoo/bcb-data.git`.
Local checkout directories need not move. Existing README artwork remains
reachable at `docs/bcbpy-icon.svg` and `docs/bcbdata-icon.svg`; new READMEs use `docs/bcb-data-icon.svg`.

## Publishing future bcb-data releases

The active Trusted Publisher mapping is:

| Project | Owner | Repository | Workflow | Environment |
|---|---|---|---|---|
| `bcb-data` | `rteoo` | `bcb-data` | `publish.yml` | `pypi` |

Preserve the environment's existing protection and approval rules. TestPyPI
staging uses only `bcb-data`, with `test-publish.yml` and `testpypi`.
Neither workflow builds or uploads `bcbpy`; an archived legacy project cannot
block a new canonical release. No account permissions are changed by this policy.

## Build and release checks

```bash
python -m pytest -m "not integration"
python -m build --outdir dist/bcb-data
python -m twine check --strict dist/bcb-data/*
```

The CI package job installs only the canonical wheel in a fresh environment and
imports it outside the checkout. Legacy import and pickle unit checks remain,
and the compatibility metadata is checked against its fixed 2.5.0 release.

For a future release, update only the canonical version, add its changelog entry,
and merge the reviewed change. Run the hosted test matrix and dry-run `release.py`
against the matching merged version. A separately authorized final GitHub Release
triggers `publish.yml` to publish only `bcb-data`. A bare push or tag publishes
nothing.

Keep the completed `v2.5.0` release and its historical workflow unchanged.
Do not rerun its legacy publication after archival, and do not delete, replace,
or re-upload a successful immutable release.
