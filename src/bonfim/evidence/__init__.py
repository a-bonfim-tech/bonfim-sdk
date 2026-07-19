"""Evidence-domain contracts."""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Evidence


@dataclass(frozen=True)
class EvidenceBundle:
    identifier: str
    evidence: tuple[Evidence, ...]
    purpose: str
    limitations: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.identifier.strip() or not self.purpose.strip():
            errors.append("Evidence bundle identifier and purpose are required")
        if not self.evidence:
            errors.append("Evidence bundle must contain at least one Evidence record")
        identifiers = tuple(item.identifier for item in self.evidence)
        if len(set(identifiers)) != len(identifiers):
            errors.append("Evidence identifiers must be unique within a bundle")
        return tuple(errors)


__all__ = ["Evidence", "EvidenceBundle"]
