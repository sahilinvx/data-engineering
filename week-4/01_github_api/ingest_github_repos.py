from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.http_client import build_auth_headers, get_paginated
from common.logging_setup import get_logger

load_dotenv()
logger = get_logger(__name__)

OUTPUT_DIR = Path(__file__).parent / "output"
GITHUB_API = "https://api.github.com"


def parse_repo(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "name": raw["name"],
        "full_name": raw["full_name"],
        "private": raw["private"],
        "html_url": raw["html_url"],
        "description": raw.get("description"),
        "language": raw.get("language"),
        "stargazers_count": raw["stargazers_count"],
        "forks_count": raw["forks_count"],
        "open_issues_count": raw["open_issues_count"],
        "default_branch": raw.get("default_branch"),
        "created_at": raw["created_at"],
        "updated_at": raw["updated_at"],
        "pushed_at": raw.get("pushed_at"),
    }


def fetch_org_repos(org: str, token: str | None, max_pages: int | None = None) -> list[dict]:
    url = f"{GITHUB_API}/orgs/{org}/repos"
    headers = build_auth_headers(token)
    params = {"per_page": 30, "type": "public", "sort": "updated"}

    repos: list[dict] = []
    for page in get_paginated(url, headers=headers, params=params, max_pages=max_pages):
        repos.extend(parse_repo(r) for r in page)

    return repos


def main() -> None:
    org = sys.argv[1] if len(sys.argv) > 1 else "octokit"
    token = os.getenv("GITHUB_TOKEN") or None

    if not token:
        logger.info("No GITHUB_TOKEN set -- running unauthenticated (60 req/hr limit).")

    logger.info("Fetching public repos for org '%s'...", org)
    repos = fetch_org_repos(org, token, max_pages=5)
    logger.info("Fetched %d repos across pagination.", len(repos))

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f"{org}_repos.json"
    out_path.write_text(json.dumps(repos, indent=2))
    logger.info("Wrote %s", out_path)


if __name__ == "__main__":
    main()
