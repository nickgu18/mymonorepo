"""Domain-specific exceptions for pipeline clarity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class CaseStudyError(RuntimeError):
    """Base exception to make catching errors easier."""


class ConfigurationError(CaseStudyError):
    pass


@dataclass(slots=True)
class DataLoadError(CaseStudyError):
    path: str
    message: str | None = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        base = self.message or "Failed to load data"
        return f"{base} (path={self.path})"


@dataclass(slots=True)
class SchemaMismatchError(CaseStudyError):
    expected: Any
    received: Any

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Schema mismatch. expected={self.expected} received={self.received}"


@dataclass(slots=True)
class ModelLoadError(CaseStudyError):
    artifact_path: str
    message: str | None = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        base = self.message or "Unable to load model artifacts"
        return f"{base} (artifact={self.artifact_path})"

