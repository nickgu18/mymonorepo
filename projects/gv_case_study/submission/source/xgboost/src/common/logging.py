from __future__ import annotations

import logging
from logging import Logger
from src.common.config import LoggingConfig


def init_logging(cfg: LoggingConfig) -> Logger:
    """Configure root logging once for scripts and notebooks."""

    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    handler.setFormatter(formatter)

    root.addHandler(handler)
    root.setLevel(cfg.level.upper())
    root.propagate = False
    return root
