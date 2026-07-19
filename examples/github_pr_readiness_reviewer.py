"""Read-only GitHub PR readiness reference Skill using caller-supplied evidence."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from bonfim import Evidence, Skill, SkillContext, SkillExecutionError, SkillOutput


class GitHubPRReadinessReviewer(Skill):
    skill_id = "GH-PR-READINESS-001"
    name = "GitHub PR Readiness Reviewer"
    version = "0.1.0"
    mission = "Assess supplied pull-request evidence without changing GitHub."
    scope = ("PR metadata analysis", "CI and review evidence assessment")
    out_of_scope = ("Approve", "Merge", "Comment", "Push")
    activation_conditions = ("Exact repository, PR number and head SHA are supplied",)
    required_inputs = ("repository", "pull_request", "head_sha", "checks")
    optional_inputs = ("unresolved_threads", "changed_files", "acceptance_criteria")

    def perform(self, context: SkillContext) -> SkillOutput:
        checks = context.inputs["checks"]
        if not isinstance(checks, Sequence) or isinstance(checks, (str, bytes)):
            raise SkillExecutionError(
                "Input Failure", "checks must be a sequence", "No readiness assessment was produced."
            )
        normalized = tuple(item for item in checks if isinstance(item, Mapping))
        passing = bool(normalized) and all(item.get("conclusion") == "success" for item in normalized)
        unresolved = int(context.inputs.get("unresolved_threads", 0))
        ready = passing and unresolved == 0
        identity = f"{context.inputs['repository']}#{context.inputs['pull_request']}@{context.inputs['head_sha']}"
        evidence = tuple(
            Evidence(
                identifier=f"CI-{index:03d}",
                summary=f"{item.get('name', 'Unknown check')}: {item.get('conclusion', 'Unknown')}",
                category="CI Evidence",
                origin=context.provenance.origin,
                validation="Caller-supplied check mapped to the assessed head SHA",
                confidence="Medium",
                traceability=(identity,),
            )
            for index, item in enumerate(normalized, start=1)
        )
        return self.output(
            "Pull-request evidence is ready for human review."
            if ready
            else "Pull-request evidence has readiness blockers.",
            evidence=evidence,
            findings=(
                f"Passing checks: {sum(item.get('conclusion') == 'success' for item in normalized)}/{len(normalized)}.",
                f"Unresolved review threads: {unresolved}.",
            ),
            risks=() if ready else ("Merge readiness is not supported by the supplied evidence.",),
            limitations=(
                "GitHub was not queried; supplied evidence may be stale.",
                "No GitHub mutation is authorized.",
            ),
            confidence="Medium" if normalized else "Unknown",
            confidence_justification="Assessment is deterministic but depends on caller-supplied GitHub evidence.",
            recommendation="Human reviewer should verify the current head SHA and repository rules.",
            final_verdict="Ready for Human Review" if ready else "Not Ready",
            data={"identity": identity, "ready": ready},
        )
