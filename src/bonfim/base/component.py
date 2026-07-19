"""Shared metadata behavior for Frameworks, Skills, Agents and Automations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from ..models import Traceability
from ..utils import require_semver
from .interfaces import Documentable, Governable, Traceable, Validatable, Versionable


class GovernedComponent(Validatable, Traceable, Governable, Versionable, Documentable):
    component_id = ""
    name = ""
    version = ""
    description = ""
    knowledge_category = "Category C — Architectural Proposals"
    evidence_level = "Level D — Internal Proposal or Convention"
    approval_status = "Proposta"
    origin = "Bonfim Labs"
    auto_register = True

    @classmethod
    def validate(cls) -> tuple[str, ...]:
        errors: list[str] = []
        for field_name in ("component_id", "name", "version", "description"):
            value = getattr(cls, field_name, None)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{cls.__name__}.{field_name} must be declared")
        try:
            require_semver(cls.version, f"{cls.__name__}.version")
        except ValueError as exc:
            errors.append(str(exc))
        return tuple(errors)

    @classmethod
    def component_version(cls) -> str:
        require_semver(cls.version, f"{cls.__name__}.version")
        return cls.version

    @classmethod
    def governance(cls) -> Mapping[str, str]:
        return {
            "knowledge_category": cls.knowledge_category,
            "evidence_level": cls.evidence_level,
            "approval_status": cls.approval_status,
            "origin": cls.origin,
        }

    @classmethod
    def documentation(cls) -> Mapping[str, Any]:
        return {
            "component_id": cls.component_id,
            "name": cls.name,
            "version": cls.version,
            "description": cls.description,
            "governance": dict(cls.governance()),
        }

    def traceability(self) -> Traceability:
        return Traceability(
            component_id=self.component_id,
            component_version=self.version,
            execution_id=str(uuid4()),
            origin=self.origin,
        )
