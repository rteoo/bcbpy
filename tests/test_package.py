"""Package-level consistency tests — guard against metadata drift."""

from importlib import metadata

import pytest

import bcbpy


def test_version_matches_installed_distribution():
    # __init__.__version__ drifted behind pyproject once (1.2.0 vs 2.0.0).
    # Compare against the installed distribution metadata (sourced from
    # pyproject at build time) rather than parsing the file, so the check is
    # independent of the working directory and TOML tooling.
    try:
        dist_version = metadata.version("bcbpy")
    except metadata.PackageNotFoundError:
        pytest.skip("bcbpy is not installed as a distribution")
    assert bcbpy.__version__ == dist_version


def test_public_api_is_importable():
    # Everything advertised in __all__ must actually resolve.
    for name in bcbpy.__all__:
        assert hasattr(bcbpy, name), f"{name} listed in __all__ but missing"


def test_exceptions_form_a_hierarchy():
    assert issubclass(bcbpy.SGSRateLimitError, bcbpy.SGSError)
    assert issubclass(bcbpy.SGSEmptyResponseError, bcbpy.SGSError)
