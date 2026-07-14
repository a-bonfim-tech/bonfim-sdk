"""Template-method implementation of the approved Skill Operational Framework."""

from __future__ import annotations

from abc import ABC, abstractmethod
import re
from typing import Any, Mapping

from .models import (
    Evidence,
    FAILURE_CATEGORIES,
    Provenance,
    QualityGate,
    SkillContext,
    SkillFailure,
    SkillOutput,
    SkillResult,
    SkillSpecification,
    utc_now,
)
from .security import sensitive_paths


SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")


class SkillExecutionError(Exception):
    """An expected, safely reportable Skill failure."""

    def __init__(self, category: str, message: str, operational_impact: str) -> None:
        if category not in FAILURE_CATEGORIES:
            raise ValueError(f"unsupported failure category: {category}")
        super().__init__(message)
        self.category = category
        self.operational_impact = operational_impact


class Skill(ABC):
    """Base class for a reusable Bonfim Skill.

    Subclasses declare their specialization as class attributes and implement
    only ``run``. The base class owns execution, validation, security, quality
    gates, provenance, failure handling, and the universal SOF output contract.
    """

    skill_id = ""
    name = ""
    version = ""
    mission = ""
    scope: tuple[str, ...] = ()
    out_of_scope: tuple[str, ...] = ()
    activation_conditions: tuple[str, ...] = ()
    required_inputs: tuple[str, ...] = ()
    optional_inputs: tuple[str, ...] = ()

    workflow = (
        "Input Assessment",
        "Scope Alignment",
        "Evidence Evaluation",
        "Finding Construction",
        "Risk Evaluation",
        "Output Construction",
        "Quality Validation",
    )
    evidence_model = "BL-SOF-001 v2.0.0 universal evidence chain"
    confidence_model = "High, Medium, Low, or Unknown with explicit justification"
    risk_register = ("Incorrect or incomplete output caused by insufficient inputs",)
    limitation_register = ("A Skill supports human review and is not decision authority",)
    quality_gates = (
        "Objective Clarity",
        "Input Sufficiency",
        "Traceability",
        "Evidence Consistency",
        "Validation Availability",
        "Risk Disclosure",
        "Limitation Disclosure",
        "Security",
        "Reproducibility",
    )
    failure_modes = (
        "Input Failure",
        "Evidence Failure",
        "Execution Failure",
        "Validation Failure",
        "Operational Failure",
        "Documentation Failure",
        "Security Failure",
        "Unknown Failure",
    )
    security_policy = "Block output that appears to expose credentials, tokens, keys, or secrets"
    human_review_policy = "The Skill does not approve, certify, audit, merge, or replace human review"
    output_contract = "BL-SOF-001 v2.0.0 Universal Output Contract"
    internal_checklist = (
        "Activation evaluated",
        "Inputs classified",
        "Outputs structured",
        "Evidence requirements evaluated",
        "Confidence justified",
        "Risks disclosed",
        "Limitations disclosed",
        "Failure modes enforced",
        "Security scan passed",
        "Human authority preserved",
    )

    @classmethod
    def specification(cls) -> SkillSpecification:
        cls._validate_declaration()
        return SkillSpecification(
            identifier=cls.skill_id,
            name=cls.name,
            version=cls.version,
            mission=cls.mission,
            scope=tuple(cls.scope),
            out_of_scope=tuple(cls.out_of_scope),
            activation_conditions=tuple(cls.activation_conditions),
            required_inputs=tuple(cls.required_inputs),
            optional_inputs=tuple(cls.optional_inputs),
            workflow=tuple(cls.workflow),
            evidence_model=cls.evidence_model,
            confidence_model=cls.confidence_model,
            risk_register=tuple(cls.risk_register),
            limitation_register=tuple(cls.limitation_register),
            quality_gates=tuple(cls.quality_gates),
            failure_modes=tuple(cls.failure_modes),
            security_policy=cls.security_policy,
            human_review_policy=cls.human_review_policy,
            output_contract=cls.output_contract,
            internal_checklist=tuple(cls.internal_checklist),
        )

    @classmethod
    def _validate_declaration(cls) -> None:
        required_text = {"skill_id": cls.skill_id, "name": cls.name, "version": cls.version, "mission": cls.mission}
        for field_name, value in required_text.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{cls.__name__}.{field_name} must be declared")
        if not SEMVER.fullmatch(cls.version):
            raise ValueError(f"{cls.__name__}.version must use semantic versioning")
        for field_name in ("scope", "out_of_scope", "activation_conditions", "required_inputs"):
            value = getattr(cls, field_name)
            if not isinstance(value, tuple) or not all(isinstance(item, str) and item.strip() for item in value):
                raise ValueError(f"{cls.__name__}.{field_name} must be a tuple of non-empty strings")
        if not cls.scope:
            raise ValueError(f"{cls.__name__}.scope must not be empty")
        if not cls.activation_conditions:
            raise ValueError(f"{cls.__name__}.activation_conditions must not be empty")

    @abstractmethod
    def run(self, context: SkillContext) -> SkillOutput:
        """Implement only the Skill-specific operational behavior."""

        raise NotImplementedError

    def check_activation(self, context: SkillContext) -> tuple[bool, str]:
        """Specialize when activation depends on machine-verifiable context."""

        return True, "Skill was explicitly invoked by the caller."

    @staticmethod
    def output(
        executive_summary: str,
        *,
        evidence: tuple[Evidence, ...] = (),
        findings: tuple[str, ...] = (),
        risks: tuple[str, ...] = (),
        limitations: tuple[str, ...] = (),
        confidence: str = "Unknown",
        confidence_justification: str = "Not established",
        recommendation: str = "No recommendation",
        final_verdict: str = "Unable to Assess",
        follow_up_actions: tuple[str, ...] = (),
        data: Mapping[str, Any] | None = None,
    ) -> SkillOutput:
        return SkillOutput(
            executive_summary=executive_summary,
            evidence=evidence,
            findings=findings,
            risks=risks,
            limitations=limitations,
            confidence=confidence,
            confidence_justification=confidence_justification,
            recommendation=recommendation,
            final_verdict=final_verdict,
            follow_up_actions=follow_up_actions,
            data=data or {},
        )

    def execute(
        self,
        inputs: Mapping[str, Any],
        *,
        provenance: Provenance | None = None,
        requested_by: str = "Unknown",
    ) -> SkillResult:
        started_at = utc_now()
        provenance = provenance or Provenance()
        try:
            specification = self.specification()
            context = SkillContext(inputs=inputs, provenance=provenance, requested_by=requested_by)
        except (TypeError, ValueError) as exc:
            return self._failure_result(
                started_at=started_at,
                provenance=provenance,
                execution_id="not-started",
                inputs=inputs if isinstance(inputs, Mapping) else {},
                category="Input Failure",
                message=f"Invalid Skill declaration or input contract: {type(exc).__name__}",
                operational_impact="Execution did not start.",
            )

        missing = tuple(name for name in specification.required_inputs if name not in context.inputs)
        if missing:
            return self._failure_result(
                started_at=started_at,
                provenance=provenance,
                execution_id=context.execution_id,
                inputs=context.inputs,
                category="Input Failure",
                message="Required inputs are missing.",
                operational_impact="Skill-specific execution did not start.",
                missing_inputs=missing,
            )

        try:
            activated, activation_reason = self.check_activation(context)
            if not activated:
                raise SkillExecutionError(
                    "Operational Failure",
                    "Activation conditions were not satisfied.",
                    activation_reason,
                )
            output = self.run(context)
            if not isinstance(output, SkillOutput):
                raise SkillExecutionError(
                    "Validation Failure",
                    "run() must return SkillOutput.",
                    "The non-conforming output was rejected.",
                )
            exposed_paths = sensitive_paths(output)
            if exposed_paths:
                raise SkillExecutionError(
                    "Security Failure",
                    "Potential sensitive information detected in Skill output.",
                    f"Publication blocked; inspect {len(exposed_paths)} flagged output path(s).",
                )
        except SkillExecutionError as exc:
            return self._failure_result(
                started_at=started_at,
                provenance=provenance,
                execution_id=context.execution_id,
                inputs=context.inputs,
                category=exc.category,
                message=str(exc),
                operational_impact=exc.operational_impact,
            )
        except Exception as exc:
            return self._failure_result(
                started_at=started_at,
                provenance=provenance,
                execution_id=context.execution_id,
                inputs=context.inputs,
                category="Unknown Failure",
                message=f"Unhandled {type(exc).__name__}; details withheld.",
                operational_impact="Execution stopped and no Skill output is valid.",
            )

        unknown_provenance = tuple(
            name for name in provenance.__dataclass_fields__ if getattr(provenance, name) == "Unknown"
        )
        limitations = list(output.limitations)
        if unknown_provenance:
            limitations.append(
                "Provenance unavailable for: " + ", ".join(unknown_provenance) + "."
            )
        gates = self._quality_gates(output, missing, unknown_provenance, activation_reason)
        failed_gate = any(gate.state == "Fail" for gate in gates)
        confidence = "Unknown" if failed_gate else output.confidence
        confidence_justification = (
            "One or more mandatory quality gates failed. " + output.confidence_justification
            if failed_gate
            else output.confidence_justification
        )
        final_verdict = "Unable to Assess" if failed_gate else output.final_verdict

        return SkillResult(
            skill_id=specification.identifier,
            skill_version=specification.version,
            execution_id=context.execution_id,
            status="Succeeded",
            started_at=started_at,
            completed_at=utc_now(),
            executive_summary=output.executive_summary,
            inputs_used=tuple(sorted(context.inputs)),
            missing_inputs=(),
            evidence=output.evidence,
            findings=output.findings,
            risks=output.risks,
            limitations=tuple(limitations),
            confidence=confidence,
            confidence_justification=confidence_justification,
            recommendation=output.recommendation,
            final_verdict=final_verdict,
            follow_up_actions=output.follow_up_actions,
            quality_gates=gates,
            provenance=provenance,
            data=output.data,
        )

    def __call__(self, inputs: Mapping[str, Any]) -> dict[str, Any]:
        """Adapter compatible with callable-based runtime registries."""

        return self.execute(inputs).to_dict()

    def _quality_gates(
        self,
        output: SkillOutput,
        missing: tuple[str, ...],
        unknown_provenance: tuple[str, ...],
        activation_reason: str,
    ) -> tuple[QualityGate, ...]:
        return (
            QualityGate("Objective Clarity", "Pass", self.mission),
            QualityGate(
                "Input Sufficiency",
                "Fail" if missing else "Pass",
                "Missing: " + ", ".join(missing) if missing else "All required inputs are present.",
            ),
            QualityGate(
                "Traceability",
                "Fail" if unknown_provenance else "Pass",
                "Unknown provenance fields: " + ", ".join(unknown_provenance)
                if unknown_provenance
                else "Provenance fields are populated.",
            ),
            QualityGate(
                "Evidence Consistency",
                "Pass" if output.evidence else "Not Applicable",
                "Evidence records use the SDK contract." if output.evidence else "No evidence was produced.",
            ),
            QualityGate(
                "Validation Availability",
                "Pass"
                if output.evidence and all(item.validation != "Unknown" for item in output.evidence)
                else "Fail"
                if output.evidence
                else "Not Applicable",
                "Evidence validation is recorded."
                if output.evidence and all(item.validation != "Unknown" for item in output.evidence)
                else "One or more evidence records lack validation."
                if output.evidence
                else "No evidence validation was applicable.",
            ),
            QualityGate("Risk Disclosure", "Pass", f"{len(output.risks)} risk(s) disclosed."),
            QualityGate("Limitation Disclosure", "Pass", f"{len(output.limitations)} specialized limitation(s) disclosed."),
            QualityGate("Security", "Pass", "No sensitive output pattern was detected."),
            QualityGate("Reproducibility", "Pass", activation_reason),
        )

    def _failure_result(
        self,
        *,
        started_at: str,
        provenance: Provenance,
        execution_id: str,
        inputs: Mapping[str, Any],
        category: str,
        message: str,
        operational_impact: str,
        missing_inputs: tuple[str, ...] = (),
    ) -> SkillResult:
        return SkillResult(
            skill_id=self.skill_id or type(self).__name__,
            skill_version=self.version or "Unknown",
            execution_id=execution_id,
            status="Failed",
            started_at=started_at,
            completed_at=utc_now(),
            executive_summary="Skill execution failed safely.",
            inputs_used=tuple(sorted(str(key) for key in inputs)),
            missing_inputs=missing_inputs,
            evidence=(),
            findings=(message,),
            risks=(operational_impact,),
            limitations=("No Skill-specific result is valid for this execution.",),
            confidence="Unknown",
            confidence_justification="Execution failure prevents a supported confidence assessment.",
            recommendation="Resolve the classified failure and run the Skill again.",
            final_verdict="Unable to Assess",
            follow_up_actions=("Review failure category and required inputs.",),
            quality_gates=(QualityGate("Execution", "Fail", operational_impact),),
            provenance=provenance,
            failure=SkillFailure(category, message, operational_impact),
        )
