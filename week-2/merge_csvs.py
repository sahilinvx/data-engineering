"""
Hands-on: read 10 CSV files and merge them into one clean output.

Demonstrates, using pipeline_utils:
  - Pathlib      -> find_csv_files() locates every .csv in data/csv_batch/
  - Generators   -> iter_csv_rows() streams rows lazily, one file at a time
  - Context mgrs -> timed_step() logs start/end/duration around each file
  - Error handling -> a broken file (bad encoding, bad delimiter) is logged and
                       skipped, the other 9 files still get merged
  - Config/env   -> load_settings() supplies the output directory
  - Datetime     -> the JSON output is stamped with when the merge ran
  - Typing       -> every function has a real signature
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from pipeline_utils import (
    ensure_dir,
    find_csv_files,
    iter_csv_rows,
    load_settings,
    setup_logging,
    timed_step,
    write_csv_rows,
    write_json,
)
from pipeline_utils.io_csv import sniff_delimiter

logger = logging.getLogger(__name__)

MERGED_FIELDNAMES = ["source_file", "name", "email", "city"]


def merged_rows(files: list[Path]) -> Iterator[dict[str, str]]:
    """Generator: yield validated rows from every file in `files`, in order.

    A broken file (wrong encoding, unreadable) logs an error and is skipped —
    one bad file in a batch of 10 shouldn't take down the whole merge.
    """
    for path in files:
        with timed_step(f"reading {path.name}"):
            row_count = 0
            skipped = 0
            try:
                delimiter = sniff_delimiter(path)
                for row in iter_csv_rows(path, delimiter=delimiter):
                    if not row.get("email"):
                        logger.warning(f"{path.name}: skipping row with no email: {row}")
                        skipped += 1
                        continue
                    row_count += 1
                    yield {
                        "source_file": path.name,
                        "name": row.get("name", ""),
                        "email": row["email"],
                        "city": row.get("city", ""),
                    }
            except UnicodeDecodeError as e:
                logger.error(f"{path.name}: could not decode file, skipping entirely ({e})")
                continue
            except OSError as e:
                logger.error(f"{path.name}: could not read file, skipping entirely ({e})")
                continue
            logger.info(f"{path.name}: merged {row_count} rows, skipped {skipped}")


def run() -> None:
    settings = load_settings()
    setup_logging(settings.log_level)

    csv_dir = Path("data/csv_batch")
    output_dir = ensure_dir(settings.output_dir)

    files = find_csv_files(csv_dir)
    logger.info(f"Found {len(files)} CSV files in {csv_dir}")

    # Materialize the generator ONCE into a list: a generator can only be iterated
    # a single time, and we need the merged data twice below (CSV output, then JSON
    # output). Re-calling merged_rows(files) would work too, but would re-read and
    # re-log every file a second time.
    rows = list(merged_rows(files))

    csv_path = output_dir / "merged_customers.csv"
    write_csv_rows(csv_path, rows, MERGED_FIELDNAMES)
    logger.info(f"Wrote {len(rows)} merged rows to {csv_path}")

    payload = {
        "merged_at": datetime.now(timezone.utc).isoformat(),
        "source_dir": str(csv_dir),
        "file_count": len(files),
        "row_count": len(rows),
        "rows": rows,
    }
    json_path = output_dir / "merged_customers.json"
    write_json(json_path, payload)
    logger.info(f"Wrote merged JSON summary to {json_path}")


if __name__ == "__main__":
    run()
