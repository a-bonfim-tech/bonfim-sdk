from __future__ import annotations

import unittest

from bonfim import GITHUB_PR_REVIEW_SKILLS, Provenance


def inputs() -> dict:
    return {
        "repository": "Bonfim-Labs/api",
        "pull_request": 42,
        "head_sha": "abc123",
        "checks": (
            {"name": "tests", "conclusion": "success"},
            {"name": "security", "conclusion": "success"},
        ),
        "changed_files": ("src/auth/policy.py", "tests/test_policy.py", "docs/security.md"),
        "unresolved_threads": 0,
        "approvals": 1,
        "issue": "BL-42",
        "acceptance_criteria": ("Unauthorized requests are denied",),
        "documentation_updated": True,
    }


def provenance() -> Provenance:
    return Provenance(
        origin="deterministic fixture",
        producer="unittest",
        collection_method="direct fixture",
        environment="test",
        artifact="tests/fixtures/pr-42.json",
        repository="Bonfim-Labs/api",
        branch="feature/pr-42",
        commit="abc123",
        issue="BL-42",
        pull_request="42",
    )


class GitHubReviewSkillTests(unittest.TestCase):
    def test_four_official_skills_execute_against_one_pr_contract(self) -> None:
        results = tuple(skill_type().run(inputs(), provenance=provenance()) for skill_type in GITHUB_PR_REVIEW_SKILLS)
        self.assertEqual(len(results), 4)
        self.assertTrue(all(result.status == "Succeeded" for result in results))
        self.assertEqual(
            tuple(result.skill_id for result in results), tuple(item.skill_id for item in GITHUB_PR_REVIEW_SKILLS)
        )
        self.assertEqual(sum(len(result.evidence) for result in results), 3)

    def test_readiness_and_governance_fail_closed_on_missing_evidence(self) -> None:
        value = inputs()
        value.update(
            {"checks": (), "approvals": 0, "issue": "", "acceptance_criteria": (), "documentation_updated": False}
        )
        results = {
            skill_type.skill_id: skill_type().run(value, provenance=provenance())
            for skill_type in GITHUB_PR_REVIEW_SKILLS
        }
        self.assertEqual(results["GH-PR-READINESS-001"].final_verdict, "Not Ready")
        self.assertEqual(results["GH-PR-GOVERNANCE-001"].final_verdict, "Governance Review Required")
        self.assertGreaterEqual(len(results["GH-PR-GOVERNANCE-001"].findings), 3)


if __name__ == "__main__":
    unittest.main()
