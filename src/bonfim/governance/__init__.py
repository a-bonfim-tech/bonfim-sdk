"""Governance metadata and authority-boundary helpers."""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Decision, Requirement


@dataclass(frozen=True)
class GovernanceRecord:
    component_id: str
    knowledge_category: str = "Category C — Architectural Proposals"
    evidence_level: str = "Level D — Internal Proposal or Convention"
    approval_status: str = "Proposta"
    origin: str = "Bonfim Labs"
    requirements: tuple[Requirement, ...] = ()
    decisions: tuple[Decision, ...] = ()

    def can_authorize_external_action(self) -> bool:
        return False


__all__ = ["Decision", "GovernanceRecord", "Requirement"]
