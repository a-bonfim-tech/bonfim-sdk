"""Bounded deterministic multi-Skill orchestration."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import suppress
from typing import Any

from ..base import Executable, GovernedComponent
from ..exceptions import RegistrationError
from ..models import (
    Confidence,
    Decision,
    Finding,
    Limitation,
    OutputContract,
    Provenance,
    Recommendation,
    Risk,
    Traceability,
    utc_now,
)
from ..security import sensitive_paths

CONFIDENCE_RANK = {"Unknown": 0, "Low": 1, "Medium": 2, "High": 3}


class Agent(GovernedComponent, Executable):
    agent_id = ""
    skill_ids: tuple[str, ...] = ()
    max_workers = 4
    allow_parallel = True
    failure_strategy = "collect-all"

    def __init__(self, registry: Any | None = None) -> None:
        if registry is None:
            from ..registry import skill_registry

            registry = skill_registry
        self.registry = registry

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.component_id = getattr(cls, "agent_id", "")
        if cls.auto_register and cls.component_id and not cls.validate():
            from ..registry import agent_registry

            with suppress(RegistrationError, ValueError):
                agent_registry.register(cls)

    @classmethod
    def validate(cls) -> tuple[str, ...]:
        errors = list(super().validate())
        if not cls.agent_id:
            errors.append(f"{cls.__name__}.agent_id must be declared")
        if not isinstance(cls.skill_ids, tuple) or not all(
            isinstance(item, str) and item.strip() for item in cls.skill_ids
        ):
            errors.append(f"{cls.__name__}.skill_ids must contain non-empty Skill identifiers")
        if not isinstance(cls.max_workers, int) or not 1 <= cls.max_workers <= 8:
            errors.append(f"{cls.__name__}.max_workers must be between 1 and 8")
        if cls.failure_strategy not in {"collect-all", "fail-fast"}:
            errors.append(f"{cls.__name__}.failure_strategy is unsupported")
        return tuple(dict.fromkeys(errors))

    def select_skills(self, inputs: Mapping[str, Any]) -> tuple[str, ...]:
        """Return an explicit allowlisted plan; subclasses may narrow it."""

        requested = inputs.get("skill_ids")
        if requested is None:
            return self.skill_ids
        if isinstance(requested, (str, bytes)) or not isinstance(requested, Sequence):
            raise TypeError("skill_ids must be a sequence of identifiers")
        requested_ids = tuple(requested)
        if not all(isinstance(identifier, str) and identifier.strip() for identifier in requested_ids):
            raise ValueError("skill_ids must contain non-empty string identifiers")
        unauthorized = tuple(identifier for identifier in requested_ids if identifier not in self.skill_ids)
        if unauthorized:
            raise ValueError("Agent cannot select one or more undeclared Skills")
        return requested_ids

    def run(
        self,
        inputs: Mapping[str, Any],
        *,
        provenance: Provenance | None = None,
        requested_by: str = "Unknown",
        parallel: bool | None = None,
    ) -> OutputContract:
        return self.execute(inputs, provenance=provenance, requested_by=requested_by, parallel=parallel)

    def execute(
        self,
        inputs: Mapping[str, Any],
        *,
        provenance: Provenance | None = None,
        requested_by: str = "Unknown",
        parallel: bool | None = None,
    ) -> OutputContract:
        started = utc_now()
        errors = self.validate()
        if errors or not isinstance(inputs, Mapping):
            return self._failed(
                started, "Invalid Agent declaration or inputs.", errors or ("inputs must be a mapping",)
            )
        try:
            selected = self.select_skills(inputs)
            if not selected:
                raise ValueError("Agent selected no Skills")
            skill_inputs = inputs.get("skill_inputs", {})
            if not isinstance(skill_inputs, Mapping):
                raise TypeError("skill_inputs must be a mapping")
            use_parallel = self.allow_parallel if parallel is None else bool(parallel)
            results = self._execute_plan(selected, skill_inputs, provenance, requested_by, use_parallel)
        except (KeyError, TypeError, ValueError) as exc:
            return self._failed(
                started,
                "Agent orchestration failed safely.",
                (f"{type(exc).__name__}; input or registry contract was rejected.",),
            )
        except Exception as exc:
            return self._failed(
                started,
                "Agent orchestration failed safely.",
                (f"Unhandled {type(exc).__name__}; details withheld.",),
            )

        finding_values = tuple((skill_id, text) for skill_id, result in results for text in result.findings)
        risk_values = tuple(text for _, result in results for text in result.risks)
        limitation_values = tuple(text for _, result in results for text in result.limitations)
        findings = tuple(
            Finding(f"{self.agent_id}-F-{index:03d}", f"Finding from {skill_id}", text)
            for index, (skill_id, text) in enumerate(finding_values, start=1)
        )
        risks = tuple(Risk(f"{self.agent_id}-R-{index:03d}", text) for index, text in enumerate(risk_values, start=1))
        limitations = tuple(
            Limitation(f"{self.agent_id}-L-{index:03d}", text) for index, text in enumerate(limitation_values, start=1)
        )
        evidence = tuple(item for _, result in results for item in result.evidence)
        failed = tuple(skill_id for skill_id, result in results if result.status != "Succeeded")
        confidence_value = min(
            (result.confidence for _, result in results),
            key=lambda value: CONFIDENCE_RANK.get(str(value), 0),
        )
        status = (
            "Partial" if failed and len(failed) < len(results) else "Failed" if failed else "Waiting for Human Review"
        )
        contract = OutputContract(
            component_id=self.agent_id,
            component_type="Agent",
            component_version=self.version,
            status=status,
            summary=f"Agent coordinated {len(results)} Skill execution(s).",
            confidence=Confidence(confidence_value),
            findings=findings,
            evidence=evidence,
            risks=risks,
            limitations=limitations
            + (Limitation(f"{self.agent_id}-AUTH", "No institutional decision or external mutation is authorized."),),
            recommendations=(
                Recommendation(f"{self.agent_id}-REC-001", "Review the aggregated result before any external action."),
            ),
            decisions=(Decision(f"{self.agent_id}-DEC-001", "Human decision required"),),
            trace=Traceability(self.agent_id, self.version, self.traceability().execution_id, self.origin),
            started_at=started,
            metadata={"skills": list(selected), "failed_skills": list(failed), "parallel": use_parallel},
            error="SkillFailure" if failed else None,
        )
        if sensitive_paths(contract):
            return self._failed(
                started, "Agent output was blocked by the sensitive-data guard.", ("Security review required",)
            )
        return contract

    def _execute_plan(
        self,
        selected: tuple[str, ...],
        skill_inputs: Mapping[str, Any],
        provenance: Provenance | None,
        requested_by: str,
        parallel: bool,
    ) -> tuple[tuple[str, Any], ...]:
        def execute_one(identifier: str) -> Any:
            inputs = skill_inputs.get(identifier, {})
            if not isinstance(inputs, Mapping):
                raise TypeError("individual Skill inputs must be a mapping")
            return self.registry.get(identifier).execute(inputs, provenance=provenance, requested_by=requested_by)

        if not parallel or len(selected) == 1:
            results: list[tuple[str, Any]] = []
            for identifier in selected:
                result = execute_one(identifier)
                results.append((identifier, result))
                if self.failure_strategy == "fail-fast" and result.status != "Succeeded":
                    break
            return tuple(results)

        indexed: dict[str, Any] = {}
        with ThreadPoolExecutor(
            max_workers=min(self.max_workers, len(selected)), thread_name_prefix="bonfim-agent"
        ) as executor:
            futures = {executor.submit(execute_one, identifier): identifier for identifier in selected}
            for future in as_completed(futures):
                identifier = futures[future]
                indexed[identifier] = future.result()
        return tuple((identifier, indexed[identifier]) for identifier in selected)

    def _failed(self, started: str, summary: str, errors: tuple[str, ...]) -> OutputContract:
        return OutputContract(
            component_id=self.agent_id or type(self).__name__,
            component_type="Agent",
            component_version=self.version or "0.0.0",
            status="Failed",
            summary=summary,
            confidence=Confidence.UNKNOWN,
            limitations=tuple(
                Limitation(f"AGENT-ERR-{index:03d}", error) for index, error in enumerate(errors, start=1)
            ),
            started_at=started,
            error="AgentExecutionError",
        )
