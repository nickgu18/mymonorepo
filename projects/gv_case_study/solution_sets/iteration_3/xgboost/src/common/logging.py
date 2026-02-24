from __future__ import annotations

import logging
from logging import Logger
from typing import Iterable

from pythonjsonlogger import jsonlogger

from src.common.config import LoggingConfig


class _RedactFilter(logging.Filter):
    def __init__(self, fields: Iterable[str]):
        super().__init__(name="gv_redactor")
        self._fields = tuple(fields)

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial mutation
        for field in self._fields:
            if hasattr(record, field):
                setattr(record, field, "***REDACTED***")
        return True


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
    if cfg.redact_fields:
        handler.addFilter(_RedactFilter(cfg.redact_fields))

    root.addHandler(handler)
    root.setLevel(cfg.level.upper())
    root.propagate = False
    return root

