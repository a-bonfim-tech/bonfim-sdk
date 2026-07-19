"""Governed Skill template method and compatibility adapter."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from typing import Any

from ..base import Executable, GovernedComponent
from ..exceptions import ExecutionError, RegistrationError
from ..models import (
    FAILURE_CATEGORIES,
    Evidence,
    Provenance,
    QualityGate,
    SkillContext,
    SkillFailure,
    SkillOutput,
    SkillResult,
    SkillSpecification,
    utc_now,
)
from ..security import sensitive_paths
from ..utils import require_semver


class SkillExecutionError(ExecutionError):
    """An expected, safely reportable Skill failure."""

    def __init__(self, category: str, message: str, operational_impact: str) -> None:
        if category not in FAILURE_CATEGORIES:
            raise ValueError(f"unsupported failure category: {category}")
        super().__init__(message)
        self.category = category
        self.operational_impact = operational_impact


class Skill(GovernedComponent, Executable):
    """Base class that owns validation, execution and governed output.

    New Skills implement :meth:`perform`. Pre-0.2 subclasses that implemented
    ``run(context)`` are adapted at class creation so ``run(inputs)`` now calls
    the complete infrastructure pipeline.
    """

    skill_id = ""
    name = ""
    version = ""
    mission = ""
    description = ""
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
    failure_modes = tuple(sorted(FAILURE_CATEGORIES))
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

    def __init_subclass__(cls, **kwargs: Any) -> None:
        legacy_run = cls.__dict__.get("run")
        super().__init_subclass__(**kwargs)
        if legacy_run is not None and legacy_run is not Skill.run:
            cls.perform = legacy_run  # type: ignore[method-assign]
            cls.run = Skill.run  # type: ignore[method-assign]
        cls.component_id = getattr(cls, "skill_id", "")
        cls.description = getattr(cls, "mission", "")
        if cls.auto_register and cls.component_id and not cls.validate():
            from ..registry import skill_registry

            with suppress(RegistrationError, ValueError):
                skill_registry.register(cls)

    @classmethod
    def validate(cls) -> tuple[str, ...]:
        errors = list(super().validate())
        if not cls.skill_id:
            errors.append(f"{cls.__name__}.skill_id must be declared")
        for field_name in ("scope", "out_of_scope", "activation_conditions", "required_inputs", "optional_inputs"):
            value = getattr(cls, field_name, None)
            if not isinstance(value, tuple) or not all(isinstance(item, str) and item.strip() for item in value):
                errors.append(f"{cls.__name__}.{field_name} must be a tuple of non-empty strings")
        if not cls.scope:
            errors.append(f"{cls.__name__}.scope must not be empty")
        if not cls.activation_conditions:
            errors.append(f"{cls.__name__}.activation_conditions must not be empty")
        if cls.perform is Skill.perform:
            errors.append(f"{cls.__name__}.perform must be implemented")
        return tuple(dict.fromkeys(errors))

    @classmethod
    def _validate_declaration(cls) -> None:
        errors = cls.validate()
        if errors:
            raise ValueError("; ".join(errors))
        require_semver(cls.version, f"{cls.__name__}.version")

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

    def perform(self, context: SkillContext) -> SkillOutput:
        """Implement only the domain-specific behavior."""

        raise NotImplementedError

    def check_activation(self, context: SkillContext) -> tuple[bool, str]:
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

    def run(
        self,
        inputs: Mapping[str, Any],
        *,
        provenance: Provenance | None = None,
        requested_by: str = "Unknown",
    ) -> SkillResult:
        return self.execute(inputs, provenance=provenance, requested_by=requested_by)

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
                started_at,
                provenance,
                "not-started",
                inputs if isinstance(inputs, Mapping) else {},
                "Input Failure",
                f"Invalid Skill declaration or input contract: {type(exc).__name__}",
                "Execution did not start.",
            )

        missing = tuple(name for name in specification.required_inputs if name not in context.inputs)
        if missing:
            return self._failure_result(
                started_at,
                provenance,
                context.execution_id,
                context.inputs,
                "Input Failure",
                "Required inputs are missing.",
                "Skill-specific execution did not start.",
                missing,
            )

        try:
            activated, activation_reason = self.check_activation(context)
            if not activated:
                raise SkillExecutionError(
                    "Operational Failure", "Activation conditions were not satisfied.", activation_reason
                )
            output = self.perform(context)
            if not isinstance(output, SkillOutput):
                raise SkillExecutionError(
                    "Validation Failure",
                    "perform() must return SkillOutput.",
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
                started_at,
                provenance,
                context.execution_id,
                context.inputs,
                exc.category,
                str(exc),
                exc.operational_impact,
            )
        except Exception as exc:
            return self._failure_result(
                started_at,
                provenance,
                context.execution_id,
                context.inputs,
                "Unknown Failure",
                f"Unhandled {type(exc).__name__}; details withheld.",
                "Execution stopped and no Skill output is valid.",
            )

        unknown_provenance = tuple(
            name for name in provenance.__dataclass_fields__ if getattr(provenance, name) == "Unknown"
        )
        limitations = list(output.limitations)
        if unknown_provenance:
            limitations.append("Provenance unavailable for: " + ", ".join(unknown_provenance) + ".")
        gates = self._quality_gates(output, missing, unknown_provenance, activation_reason)
        failed_gate = any(gate.state == "Fail" for gate in gates)
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
            confidence="Unknown" if failed_gate else output.confidence,
            confidence_justification=("One or more mandatory quality gates failed. " if failed_gate else "")
            + output.confidence_justification,
            recommendation=output.recommendation,
            final_verdict="Unable to Assess" if failed_gate else output.final_verdict,
            follow_up_actions=output.follow_up_actions,
            quality_gates=gates,
            provenance=provenance,
            data=output.data,
        )

    def __call__(self, inputs: Mapping[str, Any]) -> dict[str, Any]:
        return self.run(inputs).to_dict()

    def _quality_gates(
        self,
        output: SkillOutput,
        missing: tuple[str, ...],
        unknown_provenance: tuple[str, ...],
        activation_reason: str,
    ) -> tuple[QualityGate, ...]:
        validation_missing = bool(output.evidence) and any(item.validation == "Unknown" for item in output.evidence)
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
                "Fail" if validation_missing else "Pass" if output.evidence else "Not Applicable",
                "Evidence validation is recorded."
                if output.evidence and not validation_missing
                else "One or more evidence records lack validation."
                if output.evidence
                else "No evidence validation was applicable.",
            ),
            QualityGate("Risk Disclosure", "Pass", f"{len(output.risks)} risk(s) disclosed."),
            QualityGate(
                "Limitation Disclosure", "Pass", f"{len(output.limitations)} specialized limitation(s) disclosed."
            ),
            QualityGate("Security", "Pass", "No sensitive output pattern was detected."),
            QualityGate("Reproducibility", "Pass", activation_reason),
        )

    def _failure_result(
        self,
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
