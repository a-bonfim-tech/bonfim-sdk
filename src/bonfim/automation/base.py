"""Trigger-controlled workflows with retries, rollback and monitoring."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from time import sleep
from typing import Any, Protocol

from ..base import Executable, GovernedComponent
from ..exceptions import RegistrationError
from ..models import (
    Confidence,
    Decision,
    Limitation,
    Observation,
    OutputContract,
    Recommendation,
    Traceability,
    utc_now,
)
from ..security import sensitive_paths


class WorkflowStep(Protocol):
    step_id: str

    def execute(self, inputs: Mapping[str, Any], **kwargs: Any) -> Any: ...


class Automation(GovernedComponent, Executable):
    automation_id = ""
    triggers: tuple[str, ...] = ("manual",)
    workflow: tuple[WorkflowStep, ...] = ()
    max_retries = 0
    retry_backoff_seconds = 0.0
    rollback_on_failure = True

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.component_id = getattr(cls, "automation_id", "")
        if cls.auto_register and cls.component_id and not cls.validate():
            from ..registry import automation_registry

            with suppress(RegistrationError, ValueError):
                automation_registry.register(cls)

    @classmethod
    def validate(cls) -> tuple[str, ...]:
        errors = list(super().validate())
        if not cls.automation_id:
            errors.append(f"{cls.__name__}.automation_id must be declared")
        if (
            not isinstance(cls.triggers, tuple)
            or not cls.triggers
            or not all(isinstance(item, str) and item.strip() for item in cls.triggers)
        ):
            errors.append(f"{cls.__name__}.triggers must contain non-empty trigger names")
        if not isinstance(cls.workflow, tuple) or not all(
            hasattr(item, "execute") and hasattr(item, "step_id") for item in cls.workflow
        ):
            errors.append(f"{cls.__name__}.workflow must contain WorkflowStep objects")
        if not isinstance(cls.max_retries, int) or not 0 <= cls.max_retries <= 5:
            errors.append(f"{cls.__name__}.max_retries must be between 0 and 5")
        if not isinstance(cls.retry_backoff_seconds, (int, float)) or not 0 <= cls.retry_backoff_seconds <= 5:
            errors.append(f"{cls.__name__}.retry_backoff_seconds must be between 0 and 5")
        return tuple(dict.fromkeys(errors))

    def run(
        self,
        inputs: Mapping[str, Any],
        *,
        trigger: str = "manual",
        requested_by: str = "Unknown",
    ) -> OutputContract:
        return self.execute(inputs, trigger=trigger, requested_by=requested_by)

    def execute(
        self,
        inputs: Mapping[str, Any],
        *,
        trigger: str = "manual",
        requested_by: str = "Unknown",
    ) -> OutputContract:
        started = utc_now()
        errors = self.validate()
        if errors or not isinstance(inputs, Mapping):
            return self._failed(
                started, "Invalid Automation declaration or inputs.", errors or ("inputs must be a mapping",)
            )
        if trigger not in self.triggers:
            return self._failed(started, "Trigger was rejected.", (f"Unsupported trigger: {trigger}",))

        observations: list[Observation] = []
        limitations: list[Limitation] = []
        completed: list[tuple[WorkflowStep, Any]] = []
        failed_step: str | None = None
        step_input_map = inputs.get("steps", {})
        if not isinstance(step_input_map, Mapping):
            return self._failed(started, "Workflow step inputs are invalid.", ("steps must be a mapping",))
        for sequence, step in enumerate(self.workflow, start=1):
            step_inputs = step_input_map.get(step.step_id, inputs)
            result: Any = None
            last_exception: Exception | None = None
            for attempt in range(self.max_retries + 1):
                try:
                    result = step.execute(step_inputs, requested_by=requested_by)
                    if getattr(result, "status", "Succeeded") == "Failed":
                        raise RuntimeError("step returned a failed result")
                    observations.append(
                        Observation(
                            f"OBS-{sequence:03d}-{attempt + 1}",
                            f"Step {step.step_id} succeeded on attempt {attempt + 1}.",
                            self.automation_id,
                        )
                    )
                    completed.append((step, result))
                    last_exception = None
                    break
                except Exception as exc:
                    last_exception = exc
                    observations.append(
                        Observation(
                            f"OBS-{sequence:03d}-{attempt + 1}",
                            f"Step {step.step_id} failed on attempt {attempt + 1}; details withheld.",
                            self.automation_id,
                        )
                    )
                    if attempt < self.max_retries and self.retry_backoff_seconds:
                        sleep(float(self.retry_backoff_seconds))
            if last_exception is not None:
                failed_step = step.step_id
                limitations.append(
                    Limitation(
                        f"AUTO-FAIL-{sequence:03d}",
                        f"Step {step.step_id} failed after {self.max_retries + 1} attempt(s).",
                    )
                )
                break

        rollback_errors: list[str] = []
        rolled_back: list[str] = []
        if failed_step and self.rollback_on_failure:
            for step, result in reversed(completed):
                rollback = getattr(step, "rollback", None)
                if not callable(rollback):
                    limitations.append(
                        Limitation(f"ROLLBACK-{step.step_id}", f"Step {step.step_id} has no rollback operation.")
                    )
                    continue
                try:
                    rollback(inputs, result)
                    rolled_back.append(step.step_id)
                except Exception:
                    rollback_errors.append(step.step_id)

        status = "Failed" if failed_step else "Waiting for Human Review"
        contract = OutputContract(
            component_id=self.automation_id,
            component_type="Automation",
            component_version=self.version,
            status=status,
            summary=f"Automation completed {len(completed)} of {len(self.workflow)} workflow step(s).",
            confidence=Confidence.UNKNOWN if failed_step else Confidence.HIGH,
            limitations=tuple(limitations),
            recommendations=(
                Recommendation(
                    f"{self.automation_id}-REC-001", "Review monitored outcomes before any external action."
                ),
            ),
            decisions=(Decision(f"{self.automation_id}-DEC-001", "Human decision required"),),
            observations=tuple(observations),
            trace=Traceability(self.automation_id, self.version, self.traceability().execution_id, self.origin),
            started_at=started,
            metadata={
                "trigger": trigger,
                "requested_by": requested_by,
                "completed_steps": [step.step_id for step, _ in completed],
                "failed_step": failed_step,
                "rolled_back_steps": rolled_back,
                "rollback_errors": rollback_errors,
            },
            error="WorkflowFailure" if failed_step else "RollbackFailure" if rollback_errors else None,
        )
        if sensitive_paths(contract):
            return self._failed(
                started, "Automation output was blocked by the sensitive-data guard.", ("Security review required",)
            )
        return contract

    def _failed(self, started: str, summary: str, errors: tuple[str, ...]) -> OutputContract:
        return OutputContract(
            component_id=self.automation_id or type(self).__name__,
            component_type="Automation",
            component_version=self.version or "0.0.0",
            status="Failed",
            summary=summary,
            confidence=Confidence.UNKNOWN,
            limitations=tuple(
                Limitation(f"AUTOMATION-ERR-{index:03d}", error) for index, error in enumerate(errors, start=1)
            ),
            started_at=started,
            error="AutomationExecutionError",
        )
