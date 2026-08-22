"""
Requests library topic.

`requests` is the standard third-party HTTP client (not in the stdlib — this is
why we set up a venv and requirements.txt earlier). Two habits that matter for
pipeline code specifically:
  - Always pass `timeout=...` — without it, a hung server can freeze your pipeline
    forever with no error.
  - Always call `response.raise_for_status()` — a 404 or 500 response is NOT a
    Python exception by default, `requests` just hands you the error response like
    it was a success. `raise_for_status()` turns bad HTTP status codes into a real
    `requests.exceptions.HTTPError` you can catch.
"""

import logging
from typing import Any, Iterator

import requests

logger = logging.getLogger(__name__)


def fetch_json(url: str, timeout: int = 10) -> Any:
    """GET a URL and return the parsed JSON body, raising on any HTTP error."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def iter_users_with_posts(base_url: str, timeout: int = 10) -> Iterator[dict[str, Any]]:
    """Generator: fetch all users, then yield each one combined with their own posts —
    one full user+posts record at a time, rather than building the whole result
    before the caller can start using it."""
    users = fetch_json(f"{base_url}/users", timeout=timeout)
    for user in users:
        logger.debug(f"Fetching posts for user {user['id']} ({user['username']})")
        posts = fetch_json(f"{base_url}/users/{user['id']}/posts", timeout=timeout)
        yield {**user, "posts": posts}
