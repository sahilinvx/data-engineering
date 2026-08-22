"""
Hands-on: read REST API data and save it as JSON.

Demonstrates, using pipeline_utils:
  - Requests     -> iter_users_with_posts() calls a real public API
  - Generators   -> results stream in one user at a time
  - Error handling -> a failed request is caught and logged, not a raw traceback
  - Config/env   -> API base URL, timeout, output dir all come from config.ini,
                     overridable per-environment via .env / real env vars
  - Datetime     -> output is stamped with a timezone-aware fetch timestamp
  - Pathlib      -> output path built with ensure_dir() + the `/` operator
"""

import logging
from datetime import datetime, timezone

import requests

from pipeline_utils import (
    ensure_dir,
    iter_users_with_posts,
    load_settings,
    setup_logging,
    write_json,
)

logger = logging.getLogger(__name__)


def run() -> None:
    settings = load_settings()
    setup_logging(settings.log_level)

    output_dir = ensure_dir(settings.output_dir)
    output_path = output_dir / "api_users_with_posts.json"

    logger.info(f"Fetching users + posts from {settings.api_base_url}")
    try:
        results = list(iter_users_with_posts(settings.api_base_url, timeout=settings.request_timeout))
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed, aborting: {e}")
        return

    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": settings.api_base_url,
        "count": len(results),
        "users": results,
    }
    write_json(output_path, payload)
    logger.info(f"Wrote {len(results)} users (with their posts) to {output_path}")


if __name__ == "__main__":
    run()
