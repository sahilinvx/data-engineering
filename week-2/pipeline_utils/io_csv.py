"""
Generators topic, plus File Handling revisited.

A normal function that returns a list builds the *whole* result in memory before
giving it back. A generator function (any function containing `yield`) instead
produces values one at a time, lazily, as the caller asks for the next one — it
pauses at each `yield` and resumes right there next time. For pipelines, this
matters a lot: `iter_csv_rows` below can stream a 50GB CSV one row at a time
without ever holding the whole file in memory, because a `for` loop over a
generator only ever has one row "alive" at once.

One gotcha worth knowing: a generator can only be iterated *once*. After a `for`
loop has drained it, it's empty — you'd need to call the generator function again
to get a fresh one.
"""

import csv
import logging
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)


def iter_csv_rows(path: Path, delimiter: str = ",") -> Iterator[dict[str, str]]:
    """Lazily yield each row of a CSV file as a dict. Nothing is read until iterated."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            yield row


def write_csv_rows(path: Path, rows: Iterator[dict[str, str]], fieldnames: list[str]) -> int:
    """Write any iterable of dicts (a list, or a generator) to a CSV file. Returns row count."""
    count = 0
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def sniff_delimiter(path: Path, default: str = ",") -> str:
    """Detect whether a CSV uses ',' or ';' by sampling its first line (csv.Sniffer)."""
    with open(path, encoding="utf-8") as f:
        sample = f.readline()
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;").delimiter
    except csv.Error:
        return default
