#!/usr/bin/env python3
"""Validate the repository BQA declaration and emit auditable JSON evidence."""

from __future__ import annotations

import argparse
import json
import platform
import uuid
from datetime import UTC, datetime
from pathlib import Path

CATEGORIES = {
    "unit",
    "integration",
    "contract",
    "regression",
    "e2e",
    "performance",
    "load",
    "stress",
    "chaos",
    "security",
    "accessibility",
    "documentation",
    "governance",
    "schema",
    "api",
}
TARGETS = {
    "unitCoverage": 90,
    "integrationCoverage": 80,
    "criticalWorkflows": 100,
    "criticalSecurityControls": 100,
    "publicApiContracts": 100,
    "frameworkValidation": 100,
    "evidenceGeneration": 100,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "candidate", "release"), default="baseline")
    parser.add_argument("--output")
    args = parser.parse_args()
    root = Path.cwd()
    errors: list[str] = []
    gaps: list[str] = []
    manifest: dict[str, object] = {}
    try:
        manifest = json.loads((root / "quality/bqa-manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"manifest unavailable or invalid: {exc}")
    if manifest:
        for field in (
            "schemaVersion",
            "repository",
            "componentVersion",
            "governance",
            "targets",
            "categories",
            "staticChecks",
            "release",
        ):
            if field not in manifest:
                errors.append(f"missing field: {field}")
        version_file = root / "VERSION"
        if (
            version_file.is_file()
            and manifest.get("componentVersion") != version_file.read_text(encoding="utf-8").strip()
        ):
            errors.append("componentVersion does not match VERSION")
        governance = manifest.get("governance", {})
        controlled_statuses = {"Proposta", "Em Avaliação", "Aprovado", "Implementado", "Revisado"}
        if (
            not isinstance(governance, dict)
            or governance.get("knowledgeCategory") not in {"B", "C"}
            or governance.get("evidenceLevel") != "D"
            or governance.get("approvalStatus") not in controlled_statuses
        ):
            errors.append("governance must declare Category B/C, Level D and a controlled approval status")
        targets = manifest.get("targets", {})
        for key, minimum in TARGETS.items():
            if (
                not isinstance(targets, dict)
                or not isinstance(targets.get(key), (int, float))
                or targets[key] < minimum
            ):
                errors.append(f"target {key} must be at least {minimum}")
        categories = manifest.get("categories", {})
        if not isinstance(categories, dict) or set(categories) != CATEGORIES:
            errors.append("category inventory does not match BQA-001")
        elif isinstance(categories, dict):
            for name, control in categories.items():
                if not isinstance(control, dict) or control.get("status") not in {
                    "required",
                    "planned",
                    "not_applicable",
                }:
                    errors.append(f"invalid category declaration: {name}")
                    continue
                if control["status"] == "required":
                    if not control.get("command") or not control.get("evidence"):
                        errors.append(f"required category lacks command or evidence: {name}")
                    for evidence in control.get("evidence", []):
                        if not (root / str(evidence)).exists():
                            errors.append(f"missing evidence path for {name}: {evidence}")
                elif len(str(control.get("justification", ""))) < 20:
                    errors.append(f"missing substantive justification: {name}")
                if control["status"] == "planned":
                    gaps.append(f"category:{name}")
        static_checks = manifest.get("staticChecks", {})
        if not isinstance(static_checks, dict) or not static_checks:
            errors.append("staticChecks must be a non-empty object")
        else:
            for name, control in static_checks.items():
                if not isinstance(control, dict) or control.get("status") not in {
                    "required",
                    "planned",
                    "not_applicable",
                }:
                    errors.append(f"invalid static check: {name}")
                    continue
                if control["status"] == "required":
                    if not control.get("command") or not control.get("evidence"):
                        errors.append(f"required static check lacks command or evidence: {name}")
                    for evidence in control.get("evidence", []):
                        if not (root / str(evidence)).exists():
                            errors.append(f"missing static-check evidence path for {name}: {evidence}")
                elif control["status"] == "planned":
                    gaps.append(f"static:{name}")
                elif len(str(control.get("justification", ""))) < 20:
                    errors.append(f"missing substantive static-check justification: {name}")
        release = manifest.get("release", {})
        if not isinstance(release, dict) or release.get("certification") != "human-review-required":
            errors.append("release certification must require human review")
        elif args.mode == "release":
            if release.get("humanReviewStatus") != "approved":
                gaps.append("release:human-review")
            if release.get("approvalStatus") != "Aprovado":
                gaps.append("release:bqa-approval")
            if release.get("releaseDecision") != "approved":
                gaps.append("release:decision")

    result = "Failed" if errors else ("Requires Revision" if gaps else "Passed")
    report = {
        "executionId": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "repository": manifest.get("repository", root.name),
        "version": manifest.get("componentVersion", "unknown"),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "mode": args.mode,
        "executedChecks": [
            "manifest",
            "version",
            "governance",
            "applicability",
            "evidence-paths",
            "technical-readiness",
            "release-gate" if args.mode == "release" else "publication-gate-not-executed",
        ],
        "result": result,
        "errors": sorted(set(errors)),
        "openGaps": sorted(set(gaps)),
        "publicationAuthorized": False,
        "limitations": [
            "Declared commands execute in separate CI steps; this verifier validates their contract and evidence paths.",
            "Candidate mode establishes technical readiness only and does not approve or authorize publication.",
        ],
        "confidence": "high",
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = root / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if errors:
        return 1
    if args.mode in {"candidate", "release"} and result != "Passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
