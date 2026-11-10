"""Package-level consistency tests — guard against metadata drift.

The version check lives in test_version.py.
"""

import requests

import bcbdata


def test_public_api_is_importable():
    # Everything advertised in __all__ must actually resolve.
    for name in bcbdata.__all__:
        assert hasattr(bcbdata, name), f"{name} listed in __all__ but missing"


def test_exceptions_form_a_hierarchy():
    assert issubclass(bcbdata.SGSRateLimitError, bcbdata.SGSError)
    assert issubclass(bcbdata.SGSEmptyResponseError, bcbdata.SGSError)
    assert issubclass(bcbdata.SGSHTTPError, bcbdata.SGSError)
    assert issubclass(bcbdata.SGSHTTPError, requests.HTTPError)
