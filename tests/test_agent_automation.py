from __future__ import annotations

import unittest

from bonfim import Agent, Automation, Provenance, Skill, SkillContext, SkillOutput, SkillRegistry


def provenance() -> Provenance:
    return Provenance(
        origin="unit test",
        producer="test_agent_automation",
        collection_method="fixture",
        environment="local",
        artifact="test",
        repository="bonfim-sdk",
        branch="main",
        commit="test",
        issue="Not Applicable",
        pull_request="Not Applicable",
    )


class AlphaSkill(Skill):
    skill_id = "TEST-ALPHA-001"
    name = "Alpha"
    version = "1.0.0"
    mission = "Produce alpha output."
    scope = ("Test",)
    out_of_scope = ("External effects",)
    activation_conditions = ("Explicit test",)
    required_inputs = ("value",)

    def perform(self, context: SkillContext) -> SkillOutput:
        return self.output(
            "Alpha completed.",
            findings=(f"Alpha: {context.inputs['value']}",),
            risks=("Synthetic risk",),
            limitations=("Synthetic",),
            confidence="High",
            confidence_justification="Deterministic fixture.",
            final_verdict="Review Required",
        )


class BetaSkill(AlphaSkill):
    skill_id = "TEST-BETA-001"

    def perform(self, context: SkillContext) -> SkillOutput:
        return self.output(
            "Beta completed.",
            findings=(f"Beta: {context.inputs['value']}", "Second finding"),
            confidence="Medium",
            confidence_justification="Deterministic fixture.",
            final_verdict="Review Required",
        )


class FailingSkill(AlphaSkill):
    skill_id = "TEST-FAIL-001"
    required_inputs = ("missing",)


def registry() -> SkillRegistry:
    result = SkillRegistry()
    result.register(AlphaSkill)
    result.register(BetaSkill)
    result.register(FailingSkill)
    return result


class ParallelAgent(Agent):
    agent_id = "TEST-AGENT-001"
    name = "Parallel Agent"
    version = "1.0.0"
    description = "Coordinate test Skills."
    skill_ids = ("TEST-ALPHA-001", "TEST-BETA-001")


class AgentTests(unittest.TestCase):
    def test_parallel_aggregation_is_ordered_and_structured(self) -> None:
        result = ParallelAgent(registry()).run(
            {"skill_inputs": {"TEST-ALPHA-001": {"value": 1}, "TEST-BETA-001": {"value": 2}}},
            provenance=provenance(),
        )
        self.assertEqual(result.status, "Waiting for Human Review")
        self.assertEqual(result.confidence, "Medium")
        self.assertEqual(result.metadata["skills"], ["TEST-ALPHA-001", "TEST-BETA-001"])
        self.assertEqual(
            [item.identifier for item in result.findings],
            ["TEST-AGENT-001-F-001", "TEST-AGENT-001-F-002", "TEST-AGENT-001-F-003"],
        )

    def test_sequential_fail_fast_stops_after_failure(self) -> None:
        class FailFastAgent(ParallelAgent):
            agent_id = "TEST-AGENT-FAIL-FAST"
            skill_ids = ("TEST-FAIL-001", "TEST-ALPHA-001")
            failure_strategy = "fail-fast"

        result = FailFastAgent(registry()).run({"skill_inputs": {}}, provenance=provenance(), parallel=False)
        self.assertEqual(result.status, "Failed")
        self.assertEqual(result.metadata["skills"], ["TEST-FAIL-001", "TEST-ALPHA-001"])
        self.assertEqual(result.metadata["failed_skills"], ["TEST-FAIL-001"])

    def test_partial_result_and_selection_policy(self) -> None:
        class PartialAgent(ParallelAgent):
            agent_id = "TEST-AGENT-PARTIAL"
            skill_ids = ("TEST-ALPHA-001", "TEST-FAIL-001")

        result = PartialAgent(registry()).run(
            {"skill_inputs": {"TEST-ALPHA-001": {"value": 1}}}, provenance=provenance(), parallel=False
        )
        self.assertEqual(result.status, "Partial")
        with self.assertRaises(ValueError):
            ParallelAgent(registry()).select_skills({"skill_ids": ["UNDECLARED"]})

    def test_invalid_agent_inputs_and_plan_fail_closed(self) -> None:
        self.assertEqual(ParallelAgent(registry()).run({"skill_inputs": []}).status, "Failed")
        self.assertEqual(ParallelAgent(registry()).run({"skill_ids": []}).status, "Failed")
        self.assertEqual(ParallelAgent(registry()).run("invalid").status, "Failed")

        class InvalidAgent(Agent):
            agent_id = "TEST-INVALID-AGENT"
            name = "Invalid"
            version = "1.0.0"
            description = "Invalid workers."
            max_workers = 99

        self.assertEqual(InvalidAgent(registry()).run({}).status, "Failed")


class GoodStep:
    step_id = "good"

    def __init__(self) -> None:
        self.rollbacks = 0

    def execute(self, inputs, **kwargs):
        return type("Result", (), {"status": "Succeeded"})()

    def rollback(self, inputs, result):
        self.rollbacks += 1


class FlakyStep:
    step_id = "flaky"

    def __init__(self) -> None:
        self.attempts = 0

    def execute(self, inputs, **kwargs):
        self.attempts += 1
        if self.attempts == 1:
            raise RuntimeError("transient secret details")
        return type("Result", (), {"status": "Succeeded"})()


class BadStep:
    step_id = "bad"

    def execute(self, inputs, **kwargs):
        raise RuntimeError("permanent secret details")


class NoRollbackStep:
    step_id = "no-rollback"

    def execute(self, inputs, **kwargs):
        return type("Result", (), {"status": "Succeeded"})()


class RollbackErrorStep(GoodStep):
    step_id = "rollback-error"

    def rollback(self, inputs, result):
        raise RuntimeError("rollback details")


class AutomationTests(unittest.TestCase):
    def test_successful_workflow_and_retry_monitoring(self) -> None:
        flaky = FlakyStep()

        class RetryAutomation(Automation):
            automation_id = "TEST-AUTO-RETRY"
            name = "Retry Automation"
            version = "1.0.0"
            description = "Retry fixture."
            workflow = (flaky,)
            max_retries = 1

        result = RetryAutomation().run({})
        self.assertEqual(result.status, "Waiting for Human Review")
        self.assertEqual(flaky.attempts, 2)
        self.assertEqual(len(result.observations), 2)

    def test_failure_rolls_back_completed_steps(self) -> None:
        good = GoodStep()

        class FailingAutomation(Automation):
            automation_id = "TEST-AUTO-FAIL"
            name = "Fail Automation"
            version = "1.0.0"
            description = "Failure fixture."
            workflow = (good, BadStep())
            max_retries = 1

        result = FailingAutomation().run({})
        self.assertEqual(result.status, "Failed")
        self.assertEqual(good.rollbacks, 1)
        self.assertEqual(result.metadata["rolled_back_steps"], ["good"])
        self.assertNotIn("secret details", str(result.to_dict()))

    def test_missing_and_failed_rollback_are_reported(self) -> None:
        class RollbackAutomation(Automation):
            automation_id = "TEST-AUTO-ROLLBACK"
            name = "Rollback Automation"
            version = "1.0.0"
            description = "Rollback fixture."
            workflow = (NoRollbackStep(), RollbackErrorStep(), BadStep())

        result = RollbackAutomation().run({})
        self.assertEqual(result.status, "Failed")
        self.assertEqual(result.metadata["rollback_errors"], ["rollback-error"])
        self.assertTrue(any("no rollback" in item.description for item in result.limitations))

    def test_trigger_input_declaration_and_security_fail_closed(self) -> None:
        class EmptyAutomation(Automation):
            automation_id = "TEST-AUTO-EMPTY"
            name = "Empty"
            version = "1.0.0"
            description = "Empty workflow."
            workflow = ()

        self.assertEqual(EmptyAutomation().run({}, trigger="unknown").status, "Failed")
        self.assertEqual(EmptyAutomation().run({"steps": []}).status, "Failed")
        self.assertEqual(EmptyAutomation().run({}, requested_by="token=do-not-return").status, "Failed")

        class InvalidAutomation(Automation):
            automation_id = "TEST-AUTO-INVALID"
            name = "Invalid"
            version = "1.0.0"
            description = "Invalid retries."
            max_retries = 99

        self.assertEqual(InvalidAutomation().run({}).status, "Failed")


if __name__ == "__main__":
    unittest.main()
