"""
pipeline_utils — small reusable helpers for building data pipelines.

This is the "reusable Python utility package" hands-on: instead of scripts each
reinventing file I/O, logging setup, config loading, etc., they import shared,
tested building blocks from here.
"""

from pipeline_utils.logging_setup import setup_logging
from pipeline_utils.paths import find_csv_files, ensure_dir
from pipeline_utils.io_csv import iter_csv_rows, write_csv_rows
from pipeline_utils.io_json import read_json, write_json
from pipeline_utils.config import Settings, load_settings
from pipeline_utils.context import timed_step
from pipeline_utils.http_client import fetch_json, iter_users_with_posts

__all__ = [
    "setup_logging",
    "find_csv_files",
    "ensure_dir",
    "iter_csv_rows",
    "write_csv_rows",
    "read_json",
    "write_json",
    "Settings",
    "load_settings",
    "timed_step",
    "fetch_json",
    "iter_users_with_posts",
]
