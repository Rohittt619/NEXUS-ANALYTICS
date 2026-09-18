"""
NEXUS-ANALYTICS Structured Logger Module.

Provides color-coded Rich console logging with timestamps and log levels.
"""
from __future__ import annotations

import logging
from rich.console import Console
from rich.logging import RichHandler

console = Console()


def get_logger(name: str = "nexus") -> logging.Logger:
    """
    Configure and return a structured Rich logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            show_time=True,
            show_path=False
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
