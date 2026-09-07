"""
Minimal REST client with two things every real-world ingestion script needs:
authentication headers and pagination handling.
"""
from __future__ import annotations

import time
from typing import Any, Iterator

import requests

from common.logging_setup import get_logger

logger = get_logger(__name__)


def build_auth_headers(token: str | None) -> dict[str, str]:
    """Bearer-token auth. With no token, requests are sent unauthenticated
    (GitHub still serves public data, just at a much lower rate limit)."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_paginated(
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    max_pages: int | None = None,
) -> Iterator[list[dict]]:
    """
    Follows GitHub's Link-header pagination style (RFC 5988):
    the response carries a `Link: <url>; rel="next"` header pointing at the
    next page instead of the client having to guess page numbers.

    Yields one page (a list of JSON records) at a time so the caller can
    process/write incrementally instead of holding everything in memory.
    """
    page_num = 0
    next_url: str | None = url
    next_params: dict[str, Any] | None = params

    while next_url:
        page_num += 1
        response = requests.get(next_url, headers=headers, params=next_params, timeout=30)

        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining is not None:
            logger.info("page %d -> %s (rate limit remaining: %s)", page_num, response.status_code, remaining)
        else:
            logger.info("page %d -> %s", page_num, response.status_code)

        if response.status_code == 403 and remaining == "0":
            reset_at = response.headers.get("X-RateLimit-Reset")
            wait = max(int(reset_at) - int(time.time()), 0) if reset_at else 60
            raise RuntimeError(
                f"GitHub rate limit exhausted. Resets in ~{wait}s. "
                f"Set GITHUB_TOKEN in .env to raise the limit from 60/hr to 5000/hr."
            )

        response.raise_for_status()
        yield response.json()

        # Params only apply to the *first* request; the Link header's next
        # URL already has query params baked in.
        next_params = None

        if max_pages and page_num >= max_pages:
            break

        next_url = response.links.get("next", {}).get("url")
