"""Explicit Skill registration and execution without dynamic imports."""

from __future__ import annotations

from threading import RLock
from typing import Any, Mapping

from .models import Provenance, SkillResult
from .skill import Skill


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}
        self._lock = RLock()

    def register(self, skill: Skill) -> None:
        if not isinstance(skill, Skill):
            raise TypeError("registry accepts Skill instances only")
        specification = skill.specification()
        with self._lock:
            if specification.identifier in self._skills:
                raise ValueError(f"Skill already registered: {specification.identifier}")
            self._skills[specification.identifier] = skill

    def get(self, skill_id: str) -> Skill:
        with self._lock:
            try:
                return self._skills[skill_id]
            except KeyError as exc:
                raise KeyError(f"Unknown Skill: {skill_id}") from exc

    def identifiers(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._skills))


class SkillRunner:
    def __init__(self, registry: SkillRegistry | None = None) -> None:
        self.registry = registry or SkillRegistry()

    def run(
        self,
        skill_id: str,
        inputs: Mapping[str, Any],
        *,
        provenance: Provenance | None = None,
        requested_by: str = "Unknown",
    ) -> SkillResult:
        return self.registry.get(skill_id).execute(
            inputs,
            provenance=provenance,
            requested_by=requested_by,
        )
