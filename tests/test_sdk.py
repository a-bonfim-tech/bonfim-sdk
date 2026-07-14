from __future__ import annotations

import runpy
import unittest

from bonfim import (
    Evidence,
    Provenance,
    Skill,
    SkillContext,
    SkillExecutionError,
    SkillOutput,
    SkillRegistry,
    SkillRunner,
)


def complete_provenance() -> Provenance:
    return Provenance(
        origin="unit test",
        producer="test_sdk",
        collection_method="direct fixture",
        environment="local",
        artifact="test case",
        repository="bonfim-sdk",
        branch="main",
        commit="test-commit",
        issue="Not Applicable",
        pull_request="Not Applicable",
    )


class DemoSkill(Skill):
    skill_id = "DEMO-001"
    name = "Demo Skill"
    version = "0.1.0"
    mission = "Demonstrate minimal Skill specialization."
    scope = ("Demonstration",)
    out_of_scope = ("Institutional decisions",)
    activation_conditions = ("Explicit invocation",)
    required_inputs = ("value",)

    def run(self, context: SkillContext) -> SkillOutput:
        return self.output(
            "Demo execution completed.",
            evidence=(
                Evidence(
                    identifier="EVD-DEMO-001",
                    summary="Input value was observed.",
                    category="Runtime Evidence",
                    origin=context.provenance.origin,
                    validation="Validated by unit-test assertion",
                    confidence="High",
                    traceability=("TEST-DEMO-001",),
                ),
            ),
            findings=(f"Value is {context.inputs['value']!r}.",),
            risks=(),
            limitations=("Demonstration only.",),
            confidence="High",
            confidence_justification="Deterministic local execution with explicit provenance.",
            recommendation="Review the demonstration output.",
            final_verdict="Review Required",
            follow_up_actions=("Perform human review.",),
            data={"echo": context.inputs["value"], "token_count": 1},
        )


class SecretOutputSkill(DemoSkill):
    skill_id = "SECRET-001"

    def run(self, context: SkillContext) -> SkillOutput:
        return self.output(
            "Unsafe output.",
            confidence_justification="Not applicable.",
            data={"access_token": "must-not-be-returned"},
        )


class ExceptionSkill(DemoSkill):
    skill_id = "EXCEPTION-001"

    def run(self, context: SkillContext) -> SkillOutput:
        raise RuntimeError("password=must-not-leak")


class WrongOutputSkill(DemoSkill):
    skill_id = "WRONG-001"

    def run(self, context: SkillContext):
        return {"not": "SkillOutput"}


class InactiveSkill(DemoSkill):
    skill_id = "INACTIVE-001"

    def check_activation(self, context: SkillContext) -> tuple[bool, str]:
        return False, "The request is outside the declared activation conditions."


class SDKPublicAPITests(unittest.TestCase):
    def test_exact_public_import_is_available(self) -> None:
        from bonfim import Skill as PublicSkill

        self.assertIs(PublicSkill, Skill)

    def test_minimal_subclass_inherits_sof_infrastructure(self) -> None:
        specification = DemoSkill.specification()
        self.assertEqual(specification.framework, "BL-SOF-001@2.0.0")
        self.assertEqual(specification.approval_status, "Proposta")
        self.assertIn("Security scan passed", specification.internal_checklist)

    def test_semantic_version_is_enforced(self) -> None:
        class InvalidVersion(DemoSkill):
            skill_id = "INVALID-001"
            version = "version-one"

        with self.assertRaises(ValueError):
            InvalidVersion.specification()


class SkillExecutionTests(unittest.TestCase):
    def test_successful_execution_returns_universal_contract(self) -> None:
        result = DemoSkill().execute({"value": 42}, provenance=complete_provenance())
        self.assertEqual(result.status, "Succeeded")
        self.assertEqual(result.confidence, "High")
        self.assertEqual(result.final_verdict, "Review Required")
        self.assertEqual(result.data["echo"], 42)
        self.assertTrue(all(gate.state != "Fail" for gate in result.quality_gates))

    def test_missing_required_input_fails_before_run(self) -> None:
        result = DemoSkill().execute({}, provenance=complete_provenance())
        self.assertEqual(result.status, "Failed")
        self.assertEqual(result.failure.category, "Input Failure")
        self.assertEqual(result.missing_inputs, ("value",))

    def test_unknown_provenance_degrades_confidence_and_verdict(self) -> None:
        result = DemoSkill().execute({"value": 42})
        self.assertEqual(result.status, "Succeeded")
        self.assertEqual(result.confidence, "Unknown")
        self.assertEqual(result.final_verdict, "Unable to Assess")
        self.assertIn("Provenance unavailable", " ".join(result.limitations))

    def test_sensitive_output_is_blocked_without_reproducing_value(self) -> None:
        result = SecretOutputSkill().execute({"value": 1}, provenance=complete_provenance())
        serialized = str(result.to_dict())
        self.assertEqual(result.status, "Failed")
        self.assertEqual(result.failure.category, "Security Failure")
        self.assertNotIn("must-not-be-returned", serialized)

    def test_token_count_is_not_misclassified_as_a_secret(self) -> None:
        result = DemoSkill().execute({"value": 1}, provenance=complete_provenance())
        self.assertEqual(result.status, "Succeeded")

    def test_unexpected_exception_details_are_withheld(self) -> None:
        result = ExceptionSkill().execute({"value": 1}, provenance=complete_provenance())
        serialized = str(result.to_dict())
        self.assertEqual(result.failure.category, "Unknown Failure")
        self.assertNotIn("must-not-leak", serialized)
        self.assertIn("RuntimeError", result.failure.message)

    def test_non_contract_output_is_rejected(self) -> None:
        result = WrongOutputSkill().execute({"value": 1}, provenance=complete_provenance())
        self.assertEqual(result.failure.category, "Validation Failure")

    def test_activation_hook_can_fail_closed(self) -> None:
        result = InactiveSkill().execute({"value": 1}, provenance=complete_provenance())
        self.assertEqual(result.failure.category, "Operational Failure")

    def test_callable_adapter_is_serializable(self) -> None:
        result = DemoSkill()({"value": "runtime"})
        self.assertIsInstance(result, dict)
        self.assertEqual(result["decision_status"], "Human decision required")


class RegistryTests(unittest.TestCase):
    def test_registry_and_runner_execute_by_identifier(self) -> None:
        registry = SkillRegistry()
        registry.register(DemoSkill())
        result = SkillRunner(registry).run(
            "DEMO-001", {"value": "registered"}, provenance=complete_provenance()
        )
        self.assertEqual(result.status, "Succeeded")
        self.assertEqual(registry.identifiers(), ("DEMO-001",))

    def test_duplicate_registration_is_rejected(self) -> None:
        registry = SkillRegistry()
        registry.register(DemoSkill())
        with self.assertRaises(ValueError):
            registry.register(DemoSkill())

    def test_unknown_identifier_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            SkillRunner().run("UNKNOWN", {})


class ExampleTests(unittest.TestCase):
    def test_security_evidence_collector_example_is_a_skill(self) -> None:
        namespace = runpy.run_path("examples/security_evidence_collector.py")
        collector = namespace["SecurityEvidenceCollector"]()
        self.assertIsInstance(collector, Skill)
        result = collector.execute(
            {"artifacts": ["test output"], "requirement_id": "REQ-001"},
            provenance=complete_provenance(),
        )
        self.assertEqual(result.status, "Succeeded")
        self.assertEqual(result.data["evidence_count"], 1)


if __name__ == "__main__":
    unittest.main()
