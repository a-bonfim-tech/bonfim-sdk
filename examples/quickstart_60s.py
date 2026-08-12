"""60-second Bonfim SDK demo using only synthetic, local data."""

from __future__ import annotations

import json

from bonfim import Provenance, SkillRegistry, SkillRunner
from security_evidence_collector import SecurityEvidenceCollector


def stage(name: str, detail: str) -> None:
    print(f"{name:<24} {detail}")


def main() -> None:
    registry = SkillRegistry()

    # REGISTER
    identifier = registry.register(SecurityEvidenceCollector)
    stage("REGISTER", identifier)

    # VALIDATE
    errors = SecurityEvidenceCollector.validate()
    if errors:
        raise SystemExit("Validation failed: " + "; ".join(errors))
    stage("VALIDATE", "PASS")

    # EXECUTE through the governed registry/runner boundary.
    provenance = Provenance(
        origin="Synthetic local demo",
        producer="Bonfim SDK quickstart",
        collection_method="Caller-supplied in-memory input",
        environment="Local development environment",
        artifact="synthetic-auth.log",
        repository="a-bonfim-tech/bonfim-sdk",
        branch="demo",
        commit="local-demo",
        issue="Not Applicable",
        pull_request="Not Applicable",
    )
    result = SkillRunner(registry).run(
        identifier,
        {"artifacts": ["synthetic-auth.log"], "requirement_id": "DEMO-REQ-001"},
        provenance=provenance,
        requested_by="Human operator",
    )
    stage("EXECUTE", result.status.upper())

    # AUDIT: expose traceability and quality-gate evidence from the governed result.
    passed = sum(gate.state == "Pass" for gate in result.quality_gates)
    failed = sum(gate.state == "Fail" for gate in result.quality_gates)
    stage("AUDIT", f"quality_gates_passed={passed} failed={failed}")

    # HUMAN REVIEW: execution does not become autonomous decision authority.
    payload = result.to_dict()
    stage("HUMAN REVIEW", payload["decision_status"])

    # VERIFIED EVIDENCE: verify the result contract locally, not artifact authenticity.
    evidence_ids = [item["identifier"] for item in payload["evidence"]]
    contract_verified = (
        result.status == "Succeeded"
        and failed == 0
        and payload["decision_status"] == "Human decision required"
        and bool(evidence_ids)
    )
    stage("VERIFIED EVIDENCE", f"contract={str(contract_verified).upper()} ids={','.join(evidence_ids)}")

    print("\nRESULT")
    print(
        json.dumps(
            {
                "skill_id": payload["skill_id"],
                "status": payload["status"],
                "execution_id": payload["execution_id"],
                "evidence_ids": evidence_ids,
                "decision_status": payload["decision_status"],
                "final_verdict": payload["final_verdict"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
