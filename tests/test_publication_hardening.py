from __future__ import annotations

import unittest
from collections.abc import Mapping
from typing import Any

from bonfim import Automation, Framework


class RecordingStep:
    step_id = "record"

    def __init__(self) -> None:
        self.executed_inputs: Mapping[str, Any] | None = None
        self.rollback_inputs: Mapping[str, Any] | None = None

    def execute(self, inputs: Mapping[str, Any], **kwargs: Any) -> Any:
        self.executed_inputs = inputs
        return type("Result", (), {"status": "Succeeded"})()

    def rollback(self, inputs: Mapping[str, Any], result: Any) -> None:
        self.rollback_inputs = inputs


class FailingStep:
    step_id = "fail"

    def execute(self, inputs: Mapping[str, Any], **kwargs: Any) -> Any:
        raise RuntimeError("sensitive implementation detail")


class RollbackFailureStep(RecordingStep):
    step_id = "rollback-failure"

    def rollback(self, inputs: Mapping[str, Any], result: Any) -> None:
        raise RuntimeError("rollback secret")


class PublicationHardeningTests(unittest.TestCase):
    def test_rollback_receives_the_same_step_specific_inputs(self) -> None:
        recording = RecordingStep()

        class Workflow(Automation):
            automation_id = "TEST-PUB-AUTO-001"
            name = "Publication Workflow"
            version = "1.0.0"
            description = "Verify step-specific rollback inputs."
            workflow = (recording, FailingStep())

        expected = {"artifact": "synthetic"}
        result = Workflow().run({"steps": {"record": expected, "fail": {}}})

        self.assertEqual(result.status, "Failed")
        self.assertEqual(recording.executed_inputs, expected)
        self.assertEqual(recording.rollback_inputs, expected)

    def test_invalid_step_input_fails_without_executing_the_step(self) -> None:
        recording = RecordingStep()

        class Workflow(Automation):
            automation_id = "TEST-PUB-AUTO-002"
            name = "Input Validation Workflow"
            version = "1.0.0"
            description = "Reject invalid step input mappings."
            workflow = (recording,)

        result = Workflow().run({"steps": {"record": []}})

        self.assertEqual(result.status, "Failed")
        self.assertIsNone(recording.executed_inputs)
        self.assertNotIn("[]", str(result.to_dict()))

    def test_rollback_failure_is_explicit_and_details_are_withheld(self) -> None:
        rollback_failure = RollbackFailureStep()

        class Workflow(Automation):
            automation_id = "TEST-PUB-AUTO-003"
            name = "Rollback Failure Workflow"
            version = "1.0.0"
            description = "Expose rollback state without exception details."
            workflow = (rollback_failure, FailingStep())

        result = Workflow().run({})

        self.assertEqual(result.status, "Failed")
        self.assertEqual(result.metadata["rollback_errors"], ["rollback-failure"])
        self.assertTrue(any("details were withheld" in item.description for item in result.limitations))
        self.assertNotIn("rollback secret", str(result.to_dict()))

    def test_framework_rejects_non_mapping_inputs_safely(self) -> None:
        class ExampleFramework(Framework):
            framework_id = "TEST-PUB-FRAMEWORK-001"
            name = "Example Framework"
            version = "1.0.0"
            description = "Validate framework inputs."

        result = ExampleFramework().execute([])  # type: ignore[arg-type]

        self.assertEqual(result.status, "Failed")
        self.assertEqual(result.error, "ValidationError")
        self.assertIn("inputs must be a mapping", result.limitations[0].description)


if __name__ == "__main__":
    unittest.main()
