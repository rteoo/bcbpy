"""Warehouse-facing SGS raw-result descriptors. Public; does not import Strateo Markets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RawResult:
    """Checksummed SGS response body plus request metadata for warehouse registration."""

    payload: bytes
    source_url: str
    params: dict
    http_headers: dict
    fetched_at: datetime
    series_code: object
    library_version: str
    parser_version: str
    sha256: str
    byte_size: int
    status_code: int = 200
    retry_after: float | None = None
