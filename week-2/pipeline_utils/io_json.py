import json
from pathlib import Path
from typing import Any


def write_json(path: Path, data: Any, indent: int = 2) -> None:
    """`default=str` is a fallback: if `data` contains something JSON can't natively
    represent (like a `datetime` or `date`), json.dump calls str() on it instead of
    crashing. JSON itself has no date type — this is the standard workaround."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)


def read_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
