from __future__ import annotations

import logging
from logging import Logger
from pythonjsonlogger import jsonlogger

from src.common.config import LoggingConfig


def init_logging(cfg: LoggingConfig) -> Logger:
    """Configure root logging once for scripts and notebooks."""

    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler()
    if cfg.format.lower() == "json":
        formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    handler.setFormatter(formatter)

    root.addHandler(handler)
    root.setLevel(cfg.level.upper())
    root.propagate = False
    return root
