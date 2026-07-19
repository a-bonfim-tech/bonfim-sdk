"""Formal interfaces implemented by every Bonfim component."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class Executable(ABC):
    @abstractmethod
    def execute(self, inputs: Mapping[str, Any]) -> Any:
        """Execute through the component's governed pipeline."""


class Validatable(ABC):
    @classmethod
    @abstractmethod
    def validate(cls) -> tuple[str, ...]:
        """Return validation errors without changing external state."""


class Traceable(ABC):
    @abstractmethod
    def traceability(self) -> Any:
        """Return the component's traceability record."""


class Governable(ABC):
    @classmethod
    @abstractmethod
    def governance(cls) -> Mapping[str, str]:
        """Return immutable knowledge and authority metadata."""


class Versionable(ABC):
    @classmethod
    @abstractmethod
    def component_version(cls) -> str:
        """Return a Semantic Versioning value."""


class Documentable(ABC):
    @classmethod
    @abstractmethod
    def documentation(cls) -> Mapping[str, Any]:
        """Return machine-readable component documentation."""
