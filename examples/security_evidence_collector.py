"""Minimal specialization: Skill infrastructure remains in the SDK."""

from __future__ import annotations

from collections.abc import Sequence

from bonfim import Evidence, Skill, SkillContext, SkillExecutionError


class SecurityEvidenceCollector(Skill):
    skill_id = "SEC-001-SDK-EXAMPLE"
    name = "Security Evidence Collector"
    version = "0.1.0"
    mission = "Collect supplied security artifacts into traceable evidence records."
    scope = ("Security evidence packaging", "Evidence traceability")
    out_of_scope = ("Compliance certification", "Control implementation", "Approval")
    activation_conditions = ("Caller explicitly requests security evidence collection",)
    required_inputs = ("artifacts",)
    optional_inputs = ("requirement_id",)

    def perform(self, context: SkillContext):
        artifacts = context.inputs["artifacts"]
        if not isinstance(artifacts, Sequence) or isinstance(artifacts, (str, bytes)):
            raise SkillExecutionError(
                "Input Failure",
                "artifacts must be a sequence",
                "No evidence records were created.",
            )

        requirement = str(context.inputs.get("requirement_id", "Unknown"))
        evidence = tuple(
            Evidence(
                identifier=f"EVD-{index:03d}",
                summary=str(artifact),
                category="Security Evidence",
                origin=context.provenance.origin,
                validation="Supplied artifact recorded; independent validation not performed",
                confidence="Low",
                limitations=("Artifact authenticity was not independently verified.",),
                traceability=(requirement,),
            )
            for index, artifact in enumerate(artifacts, start=1)
        )
        return self.output(
            f"Collected {len(evidence)} supplied security artifact(s).",
            evidence=evidence,
            findings=("Artifacts were packaged; control effectiveness was not assessed.",),
            risks=("Unverified artifacts may be incomplete or inauthentic.",),
            limitations=("Read-only packaging only; no security control was tested.",),
            confidence="Low",
            confidence_justification="Artifacts were supplied by the caller without independent validation.",
            recommendation="Validate artifact authenticity before relying on the evidence package.",
            final_verdict="Review Required",
            follow_up_actions=("Perform independent evidence validation.",),
            data={"evidence_count": len(evidence)},
        )
