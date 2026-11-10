"""The legacy distribution must forward to the canonical client without forks."""

import importlib
import pickle
import re
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import bcb_data
import bcbpy
import pytest


def test_legacy_public_exports_are_identical():
    assert bcbpy.__all__ == bcb_data.__all__
    for name in bcb_data.__all__:
        assert getattr(bcbpy, name) is getattr(bcb_data, name)


@pytest.mark.parametrize("name", ["client", "codes", "constants", "artifacts"])
def test_legacy_module_paths_share_identity(name):
    assert importlib.import_module(f"bcbpy.{name}") is importlib.import_module(f"bcb_data.{name}")


def test_legacy_monkeypatch_reaches_canonical_fetch():
    with patch("bcbpy.client.fetch_series", return_value="same client"):
        assert bcb_data.client.fetch_series(433) == "same client"


def test_legacy_raw_result_pickle_is_readable():
    result = bcb_data.RawResult(
        payload=b"[]", source_url="https://example.test", params={}, http_headers={},
        fetched_at=datetime(2024, 1, 1, tzinfo=timezone.utc), series_code=433,
        library_version=bcb_data.__version__, parser_version=bcb_data.PARSER_VERSION,
        sha256="digest", byte_size=2,
    )
    # Protocol 0 encodes the original module path in a human-readable GLOBAL opcode.
    legacy = pickle.dumps(result, protocol=0).replace(b"bcb_data.artifacts", b"bcbpy.artifacts")
    assert pickle.loads(legacy) == result


@pytest.mark.parametrize("canonical_version", ["2.5.0", "2.6.0"])
def test_compatibility_release_is_frozen(monkeypatch, canonical_version):
    monkeypatch.setattr(bcb_data, "__version__", canonical_version)
    root = Path(__file__).parents[1]
    metadata = (root / "compat/bcbpy/pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r'^version = "([^"]+)"', metadata, re.M).group(1) == "2.5.0"
    assert 'dependencies = ["bcb-data==2.5.0"]' in metadata
