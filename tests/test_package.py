"""Package-level consistency tests — guard against metadata drift.

The version check lives in test_version.py.
"""

import requests

import bcb_data


def test_public_api_is_importable():
    # Everything advertised in __all__ must actually resolve.
    for name in bcb_data.__all__:
        assert hasattr(bcb_data, name), f"{name} listed in __all__ but missing"


def test_exceptions_form_a_hierarchy():
    assert issubclass(bcb_data.SGSRateLimitError, bcb_data.SGSError)
    assert issubclass(bcb_data.SGSEmptyResponseError, bcb_data.SGSError)
    assert issubclass(bcb_data.SGSHTTPError, bcb_data.SGSError)
    assert issubclass(bcb_data.SGSHTTPError, requests.HTTPError)
