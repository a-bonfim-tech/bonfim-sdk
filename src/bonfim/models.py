"""Immutable public contracts for Bonfim Skills."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4


CONFIDENCE_LEVELS = frozenset({"High", "Medium", "Low", "Unknown"})
GATE_STATES = frozenset({"Pass", "Fail", "Not Assessed", "Not Applicable"})
RESULT_STATUSES = frozenset({"Succeeded", "Failed"})
FAILURE_CATEGORIES = frozenset(
    {
        "Input Failure",
        "Evidence Failure",
        "Execution Failure",
        "Validation Failure",
        "Operational Failure",
        "Documentation Failure",
        "Security Failure",
        "Unknown Failure",
    }
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(value))


@dataclass(frozen=True)
class Provenance:
    """SOF provenance fields; unavailable facts remain explicitly Unknown."""

    origin: str = "Unknown"
    producer: str = "Unknown"
    collection_method: str = "Unknown"
    timestamp: str = field(default_factory=utc_now)
    environment: str = "Unknown"
    artifact: str = "Unknown"
    repository: str = "Unknown"
    branch: str = "Unknown"
    commit: str = "Unknown"
    issue: str = "Unknown"
    pull_request: str = "Unknown"

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"provenance.{name} must be a non-empty string")


@dataclass(frozen=True)
class Evidence:
    identifier: str
    summary: str
    category: str
    origin: str
    validation: str
    confidence: str = "Unknown"
    limitations: tuple[str, ...] = ()
    traceability: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("identifier", "summary", "category", "origin", "validation"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"evidence.{name} must be a non-empty string")
        if self.confidence not in CONFIDENCE_LEVELS:
            raise ValueError(f"unsupported confidence: {self.confidence}")
        for field_name in ("limitations", "traceability"):
            value = getattr(self, field_name)
            if not isinstance(value, tuple) or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                raise ValueError(f"evidence.{field_name} must contain non-empty strings")


@dataclass(frozen=True)
class SkillContext:
    inputs: Mapping[str, Any]
    provenance: Provenance
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    requested_by: str = "Unknown"

    def __post_init__(self) -> None:
        if not isinstance(self.inputs, Mapping):
            raise TypeError("inputs must be a mapping")
        if not all(isinstance(key, str) and key.strip() for key in self.inputs):
            raise ValueError("input keys must be non-empty strings")
        object.__setattr__(self, "inputs", _freeze_mapping(self.inputs))


@dataclass(frozen=True)
class SkillOutput:
    """Specialized output returned by Skill.run()."""

    executive_summary: str
    evidence: tuple[Evidence, ...] = ()
    findings: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    confidence: str = "Unknown"
    confidence_justification: str = "Not established"
    recommendation: str = "No recommendation"
    final_verdict: str = "Unable to Assess"
    follow_up_actions: tuple[str, ...] = ()
    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.executive_summary, str) or not self.executive_summary.strip():
            raise ValueError("executive_summary must be a non-empty string")
        if self.confidence not in CONFIDENCE_LEVELS:
            raise ValueError(f"unsupported confidence: {self.confidence}")
        if not self.confidence_justification.strip():
            raise ValueError("confidence_justification must not be empty")
        if not isinstance(self.evidence, tuple) or not all(
            isinstance(item, Evidence) for item in self.evidence
        ):
            raise ValueError("evidence must be a tuple of Evidence records")
        for field_name in ("findings", "risks", "limitations", "follow_up_actions"):
            value = getattr(self, field_name)
            if not isinstance(value, tuple) or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                raise ValueError(f"{field_name} must be a tuple of non-empty strings")
        object.__setattr__(self, "data", _freeze_mapping(self.data))


@dataclass(frozen=True)
class QualityGate:
    name: str
    state: str
    justification: str

    def __post_init__(self) -> None:
        if self.state not in GATE_STATES:
            raise ValueError(f"unsupported gate state: {self.state}")
        if not self.name.strip() or not self.justification.strip():
            raise ValueError("quality gate name and justification must not be empty")


@dataclass(frozen=True)
class SkillFailure:
    category: str
    message: str
    operational_impact: str

    def __post_init__(self) -> None:
        if self.category not in FAILURE_CATEGORIES:
            raise ValueError(f"unsupported failure category: {self.category}")
        if not self.message.strip() or not self.operational_impact.strip():
            raise ValueError("failure message and operational impact must not be empty")


@dataclass(frozen=True)
class SkillSpecification:
    """The universal SOF structure plus SDK implementation metadata."""

    identifier: str
    name: str
    version: str
    mission: str
    scope: tuple[str, ...]
    out_of_scope: tuple[str, ...]
    activation_conditions: tuple[str, ...]
    required_inputs: tuple[str, ...]
    optional_inputs: tuple[str, ...]
    workflow: tuple[str, ...]
    evidence_model: str
    confidence_model: str
    risk_register: tuple[str, ...]
    limitation_register: tuple[str, ...]
    quality_gates: tuple[str, ...]
    failure_modes: tuple[str, ...]
    security_policy: str
    human_review_policy: str
    output_contract: str
    internal_checklist: tuple[str, ...]
    framework: str = "BL-SOF-001@2.0.0"
    knowledge_category: str = "Category C — Architectural Proposals"
    evidence_level: str = "Level D — Internal Proposal or Convention"
    approval_status: str = "Proposta"


@dataclass(frozen=True)
class SkillResult:
    skill_id: str
    skill_version: str
    execution_id: str
    status: str
    started_at: str
    completed_at: str
    executive_summary: str
    inputs_used: tuple[str, ...]
    missing_inputs: tuple[str, ...]
    evidence: tuple[Evidence, ...]
    findings: tuple[str, ...]
    risks: tuple[str, ...]
    limitations: tuple[str, ...]
    confidence: str
    confidence_justification: str
    recommendation: str
    final_verdict: str
    follow_up_actions: tuple[str, ...]
    quality_gates: tuple[QualityGate, ...]
    provenance: Provenance
    data: Mapping[str, Any] = field(default_factory=dict)
    failure: SkillFailure | None = None

    def __post_init__(self) -> None:
        if self.status not in RESULT_STATUSES:
            raise ValueError(f"unsupported result status: {self.status}")
        if self.confidence not in CONFIDENCE_LEVELS:
            raise ValueError(f"unsupported confidence: {self.confidence}")
        if self.status == "Failed" and self.failure is None:
            raise ValueError("failed results require a failure record")
        object.__setattr__(self, "data", _freeze_mapping(self.data))

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation for runtime adapters."""

        def evidence_dict(item: Evidence) -> dict[str, Any]:
            return {
                "identifier": item.identifier,
                "summary": item.summary,
                "category": item.category,
                "origin": item.origin,
                "validation": item.validation,
                "confidence": item.confidence,
                "limitations": list(item.limitations),
                "traceability": list(item.traceability),
            }

        return {
            "skill_id": self.skill_id,
            "skill_version": self.skill_version,
            "execution_id": self.execution_id,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "executive_summary": self.executive_summary,
            "inputs_used": list(self.inputs_used),
            "missing_inputs": list(self.missing_inputs),
            "evidence": [evidence_dict(item) for item in self.evidence],
            "findings": list(self.findings),
            "risks": list(self.risks),
            "limitations": list(self.limitations),
            "confidence": self.confidence,
            "confidence_justification": self.confidence_justification,
            "recommendation": self.recommendation,
            "final_verdict": self.final_verdict,
            "follow_up_actions": list(self.follow_up_actions),
            "quality_gates": [
                {"name": gate.name, "state": gate.state, "justification": gate.justification}
                for gate in self.quality_gates
            ],
            "provenance": {
                name: getattr(self.provenance, name) for name in self.provenance.__dataclass_fields__
            },
            "data": dict(self.data),
            "failure": None
            if self.failure is None
            else {
                "category": self.failure.category,
                "message": self.failure.message,
                "operational_impact": self.failure.operational_impact,
            },
            "decision_status": "Human decision required",
        }
