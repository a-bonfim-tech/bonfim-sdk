from __future__ import annotations

import json
import unittest

from bonfim import (
    Confidence,
    Decision,
    Evidence,
    Finding,
    Limitation,
    Observation,
    OutputContract,
    Recommendation,
    Requirement,
    Risk,
    Traceability,
)
from bonfim.documentation import DocumentationArtifact
from bonfim.evidence import EvidenceBundle
from bonfim.governance import GovernanceRecord
from bonfim.utils import freeze_mapping, require_semver, serialize


def evidence(identifier: str = "EVD-001") -> Evidence:
    return Evidence(identifier, "Observed output", "Test", "unit test", "asserted", "High")


class SharedModelTests(unittest.TestCase):
    def test_output_contract_serializes_every_shared_model(self) -> None:
        contract = OutputContract(
            component_id="COMP-001",
            component_type="Test",
            component_version="1.0.0",
            status="Waiting for Human Review",
            summary="Structured output.",
            confidence=Confidence.HIGH,
            findings=(Finding("F-1", "Finding", "Description", evidence_ids=("EVD-001",)),),
            evidence=(evidence(),),
            risks=(Risk("R-1", "Risk statement"),),
            limitations=(Limitation("L-1", "Limitation"),),
            recommendations=(Recommendation("REC-1", "Review"),),
            decisions=(Decision("D-1", "Human decision"),),
            observations=(Observation("O-1", "Observed", "test"),),
            requirements=(Requirement("REQ-1", "Must work", "BSD-001"),),
            trace=Traceability("COMP-001", "1.0.0", "EXEC-1", "unit test"),
            metadata={"nested": ("a", "b")},
        )
        serialized = contract.to_dict()
        self.assertEqual(serialized["confidence"], "High")
        self.assertEqual(serialized["trace"]["execution_id"], "EXEC-1")
        self.assertEqual(serialized["decision_status"], "Human decision required")
        json.dumps(serialized)

    def test_output_contract_validates_status_and_required_text(self) -> None:
        with self.assertRaises(ValueError):
            OutputContract("ID", "Test", "1.0.0", "Invalid", "summary")
        with self.assertRaises(ValueError):
            OutputContract("", "Test", "1.0.0", "Succeeded", "summary")

    def test_confidence_accepts_string_values(self) -> None:
        result = OutputContract("ID", "Test", "1.0.0", "Succeeded", "summary", confidence="Low")
        self.assertIs(result.confidence, Confidence.LOW)

    def test_serialization_helpers_are_deterministic(self) -> None:
        frozen = freeze_mapping({"value": 1})
        with self.assertRaises(TypeError):
            frozen["value"] = 2
        self.assertEqual(
            serialize({"confidence": Confidence.MEDIUM, "items": (1, 2)}), {"confidence": "Medium", "items": [1, 2]}
        )

    def test_semantic_version_helper(self) -> None:
        self.assertEqual(require_semver("1.2.3-alpha.1+build.9"), "1.2.3-alpha.1+build.9")
        with self.assertRaises(ValueError):
            require_semver("01.2.3")


class DomainContractTests(unittest.TestCase):
    def test_evidence_bundle_validation(self) -> None:
        valid = EvidenceBundle("BUNDLE-1", (evidence(),), "Test evidence")
        self.assertEqual(valid.validate(), ())
        duplicate = EvidenceBundle("BUNDLE-2", (evidence(), evidence()), "Test")
        self.assertIn("Evidence identifiers must be unique within a bundle", duplicate.validate())
        empty = EvidenceBundle("", (), "")
        self.assertEqual(len(empty.validate()), 2)

    def test_governance_never_authorizes_external_action(self) -> None:
        record = GovernanceRecord("COMP-001")
        self.assertFalse(record.can_authorize_external_action())
        self.assertEqual(record.approval_status, "Proposta")

    def test_documentation_artifact_is_immutable_and_validated(self) -> None:
        artifact = DocumentationArtifact("DOC-1", "Title", "Content", metadata={"owner": "test"})
        self.assertEqual(artifact.metadata["owner"], "test")
        with self.assertRaises(TypeError):
            artifact.metadata["owner"] = "changed"
        with self.assertRaises(ValueError):
            DocumentationArtifact("", "Title", "Content")


if __name__ == "__main__":
    unittest.main()
