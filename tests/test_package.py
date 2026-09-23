"""Package-level consistency tests — guard against metadata drift.

The version check lives in test_version.py.
"""

import requests

import bcbpy


def test_public_api_is_importable():
    # Everything advertised in __all__ must actually resolve.
    for name in bcbpy.__all__:
        assert hasattr(bcbpy, name), f"{name} listed in __all__ but missing"


def test_exceptions_form_a_hierarchy():
    assert issubclass(bcbpy.SGSRateLimitError, bcbpy.SGSError)
    assert issubclass(bcbpy.SGSEmptyResponseError, bcbpy.SGSError)
    assert issubclass(bcbpy.SGSHTTPError, bcbpy.SGSError)
    assert issubclass(bcbpy.SGSHTTPError, requests.HTTPError)
