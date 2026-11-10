# bcbpy to bcb-data: migration and release preparation

The repository and PyPI distribution are `bcb-data`; the Python import package
is `bcb_data`. Install with `pip install bcb-data` and import with
`from bcb_data import ...`.
The prepared release is **2.5.0**. It has not been published by preparing this patch.

## Applications

After publication, install `bcb-data` and change imports:

```python
from bcb_data import fetch_series, RawResult, SGSRateLimitError
```

The public API, numeric SGS codes, date handling, exception hierarchy, and parser
version are unchanged by this rename. Raw artifacts report the new library version.

The separately built `bcbpy` 2.5.0 distribution depends on `bcb-data==2.5.0`.
It aliases all public exports and the `bcbpy.client`, `bcbpy.codes`,
`bcbpy.constants`, and `bcbpy.artifacts` module paths to the canonical objects.
Existing imports, exception catches, monkeypatch targets, and raw-result pickles
continue to work. New applications should import `bcb_data` directly.

Do not bundle the compatibility namespace inside the `bcb-data` wheel: the two
distributions own separate import directories and can be installed together.
Keep all previous `bcbpy` releases and tags. PyPI release history and download
counts remain attached to the old project; this is a new project, not an
in-place PyPI rename.

## GitHub

Rename `rteoo/bcbdata` to `rteoo/bcb-data`. The intended rollback is renaming the
same repository back to `bcbdata`; preserve the repository ID, visibility, refs,
branch protection, and GitHub environments. Do not create a replacement at the
old GitHub path, which would interfere with redirects.

Update each existing checkout's origin to `https://github.com/rteoo/bcb-data.git`.
Local checkout directories need not move. Existing README artwork remains
reachable at `docs/bcbpy-icon.svg` and `docs/bcbdata-icon.svg`; new READMEs use `docs/bcb-data-icon.svg`.

## PyPI Trusted Publishing prerequisites

Before publishing, configure and verify these mappings in the appropriate
PyPI account. No token is required by the workflows.

| Project | Owner | Repository | Workflow | Environment |
|---|---|---|---|---|
| `bcb-data` (new pending publisher) | `rteoo` | `bcb-data` | `publish.yml` | `pypi` |
| `bcbpy` (existing project) | `rteoo` | `bcb-data` | `publish.yml` | `pypi` |

The repository rename changes the OIDC repository identity; the old publisher
configuration must be updated rather than assumed to follow GitHub redirects.
Preserve the environment's existing protection and approval rules. Configure
equivalent mappings on TestPyPI for `test-publish.yml` and `testpypi` if staging
is used. A pending publisher does not reserve a PyPI name.

## Build and publish order

```bash
python -m pytest -m "not integration"
python -m build --outdir dist/bcb-data
python -m build compat/bcbpy --outdir dist/bcbpy
python -m twine check --strict dist/bcb-data/* dist/bcbpy/*
```

The CI package job installs both wheels in a fresh environment and imports them
outside the checkout. The release build additionally requires both distribution
versions and the compatibility dependency to match the tag.

After the patch is reviewed and merged, validate the configured Trusted
Publishers, run the full hosted test matrix, and dry-run `release.py` against
the merged `v2.5.0` source. A separately authorized GitHub Release triggers
`publish.yml`: publish `bcb-data` first, then the dependent `bcbpy` distribution.
No bare branch push or tag push publishes to PyPI.

If the compatibility publication fails after `bcb-data` succeeds, rerun only the
failed compatibility job after resolving its cause. Do not delete, replace,
or re-upload a successful immutable release.
