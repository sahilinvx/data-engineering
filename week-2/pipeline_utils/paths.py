"""
Pathlib topic.

`pathlib.Path` replaces old-style string path manipulation (os.path.join, manual
string concatenation with '/'). Paths become objects with methods, and the `/`
operator joins them in a way that works correctly on both Linux and Windows.
"""

from pathlib import Path


def find_csv_files(directory: str | Path) -> list[Path]:
    """Return every .csv file directly inside `directory`, sorted for a deterministic order."""
    directory = Path(directory)
    return sorted(directory.glob("*.csv"))


def ensure_dir(directory: str | Path) -> Path:
    """Create `directory` (and any missing parent folders) if it doesn't already exist."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
