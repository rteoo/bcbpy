"""Package-level consistency tests — guard against metadata drift."""

import re
from pathlib import Path

import bcbpy


PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def _pyproject_version():
    """Read the [project] version from pyproject.toml without a TOML lib.

    tomllib is only stdlib on 3.11+, but the package supports 3.10, so parse
    the single line directly.
    """
    text = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert match, "no version field found in pyproject.toml"
    return match.group(1)


def test_version_matches_pyproject():
    # __init__.__version__ drifted behind pyproject once (1.2.0 vs 2.0.0);
    # this locks them together.
    assert bcbpy.__version__ == _pyproject_version()


def test_public_api_is_importable():
    # Everything advertised in __all__ must actually resolve.
    for name in bcbpy.__all__:
        assert hasattr(bcbpy, name), f"{name} listed in __all__ but missing"


def test_exceptions_form_a_hierarchy():
    assert issubclass(bcbpy.SGSRateLimitError, bcbpy.SGSError)
    assert issubclass(bcbpy.SGSEmptyResponseError, bcbpy.SGSError)
