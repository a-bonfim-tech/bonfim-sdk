"""Deterministic, read-only Skills for the GitHub PR evidence vertical."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..models import Evidence, SkillContext, SkillOutput
from .base import Skill, SkillExecutionError


def _sequence(inputs: Mapping[str, Any], name: str) -> tuple[Any, ...]:
    value = inputs.get(name, ())
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise SkillExecutionError("Input Failure", f"{name} must be a sequence", "PR review did not start.")
    return tuple(value)


def _identity(context: SkillContext) -> str:
    return f"{context.inputs['repository']}#{context.inputs['pull_request']}@{context.inputs['head_sha']}"


class PullRequestEvidenceCollector(Skill):
    skill_id = "GH-PR-EVIDENCE-001"
    name = "Pull Request Evidence Collector"
    version = "0.1.0"
    mission = "Package caller-supplied PR metadata, checks and changed files as traceable evidence."
    scope = ("PR evidence packaging", "Commit-bound traceability")
    out_of_scope = ("Query GitHub", "Modify GitHub", "Assert artifact authenticity")
    activation_conditions = ("A repository, PR number and immutable head SHA are supplied",)
    required_inputs = ("repository", "pull_request", "head_sha", "checks", "changed_files")

    def perform(self, context: SkillContext) -> SkillOutput:
        checks = _sequence(context.inputs, "checks")
        files = _sequence(context.inputs, "changed_files")
        identity = _identity(context)
        evidence = (
            Evidence(
                "PR-META-001",
                f"PR identity {identity}",
                "PR Metadata",
                context.provenance.origin,
                "Bound to caller-supplied repository, PR number and head SHA",
                "Medium",
                traceability=(identity,),
            ),
            Evidence(
                "PR-CHECKS-001",
                f"{len(checks)} check result(s) supplied",
                "CI Evidence",
                context.provenance.origin,
                "Counted and bound to the assessed PR identity",
                "Medium",
                traceability=(identity,),
            ),
            Evidence(
                "PR-DIFF-001",
                f"{len(files)} changed file(s) supplied",
                "Diff Evidence",
                context.provenance.origin,
                "File names recorded without retrieving file contents",
                "Medium",
                traceability=(identity,),
            ),
        )
        return self.output(
            f"Packaged three evidence records for {identity}.",
            evidence=evidence,
            findings=(f"Observed {len(checks)} checks and {len(files)} changed files in caller-supplied data.",),
            risks=("Caller-supplied evidence may be stale or incomplete.",),
            limitations=("GitHub was not queried; authenticity was not independently verified.",),
            confidence="Medium",
            confidence_justification="All records are deterministic but caller supplied.",
            recommendation="Verify the head SHA against GitHub before a merge decision.",
            final_verdict="Evidence Packaged — Human Verification Required",
            data={"identity": identity, "evidence_records": len(evidence)},
        )


class PullRequestReadinessReviewer(Skill):
    skill_id = "GH-PR-READINESS-001"
    name = "Pull Request Readiness Reviewer"
    version = "0.1.0"
    mission = "Evaluate checks, review threads and approval evidence without making a merge decision."
    scope = ("CI status", "Review readiness", "Approval evidence")
    out_of_scope = ("Approve", "Merge", "Comment", "Push")
    activation_conditions = ("PR evidence is supplied for a fixed head SHA",)
    required_inputs = ("repository", "pull_request", "head_sha", "checks", "changed_files")
    optional_inputs = ("unresolved_threads", "approvals")

    def perform(self, context: SkillContext) -> SkillOutput:
        checks = _sequence(context.inputs, "checks")
        normalized = tuple(item for item in checks if isinstance(item, Mapping))
        invalid = len(checks) - len(normalized)
        passing = sum(item.get("conclusion") == "success" for item in normalized)
        unresolved = int(context.inputs.get("unresolved_threads", 0))
        approvals = int(context.inputs.get("approvals", 0))
        ready = bool(normalized) and invalid == 0 and passing == len(normalized) and unresolved == 0 and approvals > 0
        findings = (
            f"Passing checks: {passing}/{len(normalized)}.",
            f"Unresolved review threads: {unresolved}.",
            f"Recorded approvals: {approvals}.",
        )
        blockers = tuple(item for item in findings if not ready)
        return self.output(
            "PR evidence supports human review." if ready else "PR evidence contains readiness blockers.",
            findings=findings,
            risks=() if ready else ("Merge readiness is not supported by the supplied evidence.",),
            limitations=("Branch protection and current GitHub state were not independently queried.",),
            confidence="Medium" if normalized else "Unknown",
            confidence_justification="The decision rule is deterministic and evidence remains caller supplied.",
            recommendation="A human reviewer must verify repository rules and the current head SHA.",
            final_verdict="Ready for Human Review" if ready else "Not Ready",
            data={"identity": _identity(context), "ready": ready, "blockers": blockers},
        )


class PullRequestSecurityReviewer(Skill):
    skill_id = "GH-PR-SECURITY-001"
    name = "Pull Request Security Change Reviewer"
    version = "0.1.0"
    mission = "Identify security-sensitive changed paths and missing security checks from supplied PR evidence."
    scope = ("Security-sensitive path detection", "Security check presence")
    out_of_scope = ("SAST", "Exploitability determination", "Vulnerability certification")
    activation_conditions = ("Changed file names and CI checks are supplied",)
    required_inputs = ("repository", "pull_request", "head_sha", "checks", "changed_files")

    def perform(self, context: SkillContext) -> SkillOutput:
        files = tuple(str(item) for item in _sequence(context.inputs, "changed_files"))
        checks = tuple(item for item in _sequence(context.inputs, "checks") if isinstance(item, Mapping))
        markers = ("auth", "security", "permission", "policy", "secret", "crypto", "workflow", "docker", "terraform")
        sensitive = tuple(path for path in files if any(marker in path.lower() for marker in markers))
        security_checks = tuple(
            item
            for item in checks
            if any(
                marker in str(item.get("name", "")).lower() for marker in ("security", "sast", "secret", "dependency")
            )
        )
        security_checks_pass = bool(security_checks) and all(
            item.get("conclusion") == "success" for item in security_checks
        )
        risk = bool(sensitive) and not security_checks_pass
        sensitive_label = ", ".join(sensitive) if sensitive else "None detected by path heuristic"
        passing_security_checks = sum(item.get("conclusion") == "success" for item in security_checks)
        return self.output(
            f"Detected {len(sensitive)} security-sensitive path(s) and {len(security_checks)} security check(s).",
            findings=(
                f"Security-sensitive paths: {sensitive_label}.",
                f"Passing security checks: {passing_security_checks}/{len(security_checks)}.",
            ),
            risks=("Security-sensitive changes lack passing security-check evidence.",) if risk else (),
            limitations=("Path heuristics do not inspect code and cannot establish absence of vulnerabilities.",),
            confidence="Low" if sensitive else "Medium",
            confidence_justification="Only file names and check labels were evaluated.",
            recommendation="Route sensitive changes to a qualified security reviewer."
            if sensitive
            else "Preserve security checks in the required CI set.",
            final_verdict="Security Review Required" if risk else "No Evidence-Based Security Blocker",
            data={
                "identity": _identity(context),
                "sensitive_paths": sensitive,
                "security_checks_pass": security_checks_pass,
            },
        )


class PullRequestGovernanceReviewer(Skill):
    skill_id = "GH-PR-GOVERNANCE-001"
    name = "Pull Request Governance Reviewer"
    version = "0.1.0"
    mission = "Evaluate issue, acceptance-criteria and documentation traceability for a pull request."
    scope = ("Change traceability", "Acceptance evidence", "Documentation impact")
    out_of_scope = ("Organizational approval", "Compliance certification", "Merge authorization")
    activation_conditions = ("Governance metadata is supplied with the PR evidence",)
    required_inputs = ("repository", "pull_request", "head_sha", "checks", "changed_files")
    optional_inputs = ("issue", "acceptance_criteria", "documentation_updated")

    def perform(self, context: SkillContext) -> SkillOutput:
        issue = str(context.inputs.get("issue", "")).strip()
        criteria = tuple(str(item) for item in _sequence(context.inputs, "acceptance_criteria"))
        documented = bool(context.inputs.get("documentation_updated", False))
        gaps = tuple(
            label
            for condition, label in (
                (not issue, "No linked issue was supplied."),
                (not criteria, "No acceptance criteria were supplied."),
                (not documented, "Documentation impact was not recorded as updated."),
            )
            if condition
        )
        return self.output(
            "Governance traceability is complete." if not gaps else "Governance traceability contains gaps.",
            findings=gaps or (f"Issue {issue} and {len(criteria)} acceptance criterion/criteria are traceable.",),
            risks=("A change without traceability may be difficult to audit or maintain.",) if gaps else (),
            limitations=("Supplied metadata was not verified against an issue tracker or repository.",),
            confidence="Medium",
            confidence_justification="The completeness rule is deterministic; source truth was not verified.",
            recommendation="Resolve governance gaps before requesting a merge decision."
            if gaps
            else "Preserve the traceability record with the review evidence.",
            final_verdict="Governance Review Required" if gaps else "Governance Evidence Complete",
            data={"identity": _identity(context), "gaps": gaps, "decision_authority": "Human"},
        )


GITHUB_PR_REVIEW_SKILLS = (
    PullRequestEvidenceCollector,
    PullRequestReadinessReviewer,
    PullRequestSecurityReviewer,
    PullRequestGovernanceReviewer,
)

__all__ = [
    "GITHUB_PR_REVIEW_SKILLS",
    "PullRequestEvidenceCollector",
    "PullRequestGovernanceReviewer",
    "PullRequestReadinessReviewer",
    "PullRequestSecurityReviewer",
]
