"""Guardrail: the runtime __version__ and the packaged metadata version must agree.

pyproject.toml declares the version dynamically from ``bcbdata.__version__``
(single source of truth), so a build can only ever produce metadata that
matches the module. This test catches a regression where that link is broken
(e.g. someone re-adds a hardcoded ``version =`` to pyproject.toml).
"""

from importlib import metadata

import pytest

import bcbdata


def test_version_matches_package_metadata():
    try:
        dist_version = metadata.version("bcbdata")
    except metadata.PackageNotFoundError:
        pytest.skip("bcbdata is not installed; metadata unavailable")

    assert dist_version == bcbdata.__version__
