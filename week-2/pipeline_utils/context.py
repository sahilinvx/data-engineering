"""
Context Managers topic.

`with open(...) as f:` is a context manager you've already used — it guarantees
`f.close()` runs even if an error happens inside the block. `@contextmanager` lets
you write your *own* context manager as a plain function instead of a class: the
code before `yield` is the "setup" (runs on entering the `with` block), and the
code after `yield` is the "teardown" (runs on exiting the block — the `finally`
guarantees it runs even if the block raises an exception).
"""

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

logger = logging.getLogger(__name__)


@contextmanager
def timed_step(step_name: str) -> Iterator[None]:
    """Log the start/end of a pipeline step, plus how long it took — wrap any block with it."""
    start = datetime.now()
    logger.info(f"Starting: {step_name}")
    try:
        yield
    finally:
        elapsed = (datetime.now() - start).total_seconds()
        logger.info(f"Finished: {step_name} ({elapsed:.3f}s)")
