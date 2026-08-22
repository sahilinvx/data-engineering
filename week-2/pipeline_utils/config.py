"""
Config Files + Environment Variables topics.

Two different jobs, often confused:
  - A config *file* (config.ini here, via the stdlib `configparser`) holds settings
    that are the same for everyone and safe to commit to git — API URLs, timeouts,
    log level.
  - Environment *variables* hold things that differ per machine/environment, or are
    secret (API keys, passwords) — never committed to git. `.env` is a local file
    (gitignored) that `load_dotenv()` reads into the real environment variables for
    you, so you don't have to `export` them by hand every time.

The pattern below: read the config file first as the default, then let an
environment variable override it if one is set. That's how the same code runs
against different settings in dev vs. production without editing the file itself.
"""

import configparser
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Settings:
    api_base_url: str
    request_timeout: int
    log_level: str
    output_dir: Path


def load_settings(config_path: str | Path = "config/config.ini") -> Settings:
    load_dotenv()  # populates os.environ from a local .env file, if one exists

    parser = configparser.ConfigParser()
    parser.read(config_path)

    api_base_url = os.getenv("API_BASE_URL", parser.get("api", "base_url"))
    request_timeout = int(os.getenv("REQUEST_TIMEOUT", parser.get("api", "timeout")))
    log_level = os.getenv("LOG_LEVEL", parser.get("logging", "level"))
    output_dir = Path(os.getenv("OUTPUT_DIR", parser.get("paths", "output_dir")))

    return Settings(
        api_base_url=api_base_url,
        request_timeout=request_timeout,
        log_level=log_level,
        output_dir=output_dir,
    )
