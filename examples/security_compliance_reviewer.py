"""Evidence-to-requirement mapping reference Skill; no certification output."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from bonfim import Skill, SkillContext, SkillExecutionError, SkillOutput


class SecurityComplianceReviewer(Skill):
    skill_id = "SEC-COMPLIANCE-REVIEW-001"
    name = "Security Compliance Reviewer"
    version = "0.1.0"
    mission = "Map supplied evidence coverage to explicit security requirements."
    scope = ("Applicability input", "Evidence-to-requirement mapping", "Gap identification")
    out_of_scope = ("Certification", "Legal advice", "Audit opinion")
    activation_conditions = ("Requirements and evidence mappings are explicitly supplied",)
    required_inputs = ("requirements", "evidence_mappings")
    optional_inputs = ("framework", "assessment_scope")

    def perform(self, context: SkillContext) -> SkillOutput:
        requirements = context.inputs["requirements"]
        mappings = context.inputs["evidence_mappings"]
        if (
            not isinstance(requirements, Sequence)
            or isinstance(requirements, (str, bytes))
            or not isinstance(mappings, Mapping)
        ):
            raise SkillExecutionError(
                "Input Failure", "requirements and evidence_mappings have invalid types", "Assessment did not start."
            )
        identifiers = tuple(str(item) for item in requirements)
        supported = tuple(identifier for identifier in identifiers if mappings.get(identifier))
        missing = tuple(identifier for identifier in identifiers if not mappings.get(identifier))
        return self.output(
            f"Mapped evidence for {len(supported)} of {len(identifiers)} requirement(s).",
            findings=tuple(f"Evidence is missing for {identifier}." for identifier in missing),
            risks=("Evidence coverage does not prove control design or operating effectiveness.",),
            limitations=("No certification, legal conclusion or audit opinion is produced.",),
            confidence="Medium" if identifiers else "Unknown",
            confidence_justification="Coverage was derived from explicit caller-supplied mappings.",
            recommendation="Validate evidence quality and applicability with an accountable assessor.",
            final_verdict="Review Required",
            data={"supported": supported, "missing": missing},
        )
