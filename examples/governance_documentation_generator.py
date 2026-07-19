"""Governance documentation reference Skill with explicit proposal status."""

from __future__ import annotations

from collections.abc import Mapping

from bonfim import Skill, SkillContext, SkillExecutionError, SkillOutput


class GovernanceDocumentationGenerator(Skill):
    skill_id = "GOV-DOC-GENERATE-001"
    name = "Governance Documentation Generator"
    version = "0.1.0"
    mission = "Generate a bounded governance-document draft from supplied facts and decisions."
    scope = ("Markdown drafting", "Knowledge metadata", "Source traceability")
    out_of_scope = ("Approval", "Publication", "Inventing missing decisions")
    activation_conditions = ("Document owner and source facts are explicitly supplied",)
    required_inputs = ("title", "owner", "facts")
    optional_inputs = ("decisions", "recommendations")

    def perform(self, context: SkillContext) -> SkillOutput:
        facts = context.inputs["facts"]
        if not isinstance(facts, Mapping):
            raise SkillExecutionError("Input Failure", "facts must be a mapping", "No document draft was created.")
        title = str(context.inputs["title"])
        owner = str(context.inputs["owner"])
        lines = [
            f"# {title}",
            "",
            "> Category C · Level D · Status: Proposta",
            "",
            f"Owner: {owner}",
            "",
            "## Verified facts",
            "",
        ]
        lines.extend(f"- **{key}:** {value}" for key, value in sorted(facts.items()))
        lines.extend(
            ("", "## Human review", "", "This draft requires review and does not record organizational approval.")
        )
        content = "\n".join(lines) + "\n"
        return self.output(
            "Governance document draft generated.",
            findings=(f"Draft contains {len(facts)} caller-supplied fact(s).",),
            limitations=(
                "Source facts were not independently validated.",
                "Document remains Proposta until explicit approval.",
            ),
            confidence="Low",
            confidence_justification="The document structure is deterministic; source truth was not validated.",
            recommendation="Route the draft to the named owner and subject-matter reviewers.",
            final_verdict="Draft — Review Required",
            data={"format": "markdown", "content": content},
        )
