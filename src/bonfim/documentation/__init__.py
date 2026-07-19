"""Documentation artifact contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from ..utils import freeze_mapping


@dataclass(frozen=True)
class DocumentationArtifact:
    identifier: str
    title: str
    content: str
    format: str = "markdown"
    status: str = "Proposta"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("identifier", "title", "content", "format", "status"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be a non-empty string")
        object.__setattr__(self, "metadata", freeze_mapping(self.metadata))


__all__ = ["DocumentationArtifact"]
