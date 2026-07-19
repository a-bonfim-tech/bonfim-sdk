#!/usr/bin/env python3
"""Validate BRE-001 release evidence without authorizing publication."""

from __future__ import annotations

import argparse
import json
import platform
import uuid
from datetime import UTC, datetime
from pathlib import Path

ARTIFACTS = {
    "sourceCode",
    "releaseNotes",
    "changelog",
    "migrationGuide",
    "openapi",
    "documentation",
    "examples",
    "sbom",
    "checksums",
    "licenseInformation",
    "evidencePackage",
    "securityDisclosure",
    "compatibilityPolicy",
}
STATUSES = {"available", "planned", "not_applicable"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "release"), default="baseline")
    parser.add_argument("--output")
    args = parser.parse_args()
    root = Path.cwd()
    manifest: dict[str, object] = {}
    errors: list[str] = []
    gaps: list[str] = []
    try:
        loaded = json.loads((root / "release/bre-manifest.json").read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("manifest root must be an object")
        manifest = loaded
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"manifest unavailable or invalid: {exc}")

    if manifest:
        for field in (
            "schemaVersion",
            "repository",
            "componentVersion",
            "governance",
            "artifacts",
            "bqa",
            "humanReviewStatus",
            "publicReleaseAuthorized",
        ):
            if field not in manifest:
                errors.append(f"missing field: {field}")
        version_path = root / "VERSION"
        if not version_path.is_file():
            errors.append("VERSION is missing")
        elif manifest.get("componentVersion") != version_path.read_text(encoding="utf-8").strip():
            errors.append("componentVersion does not match VERSION")

        governance = manifest.get("governance", {})
        controlled = {"Proposta", "Em Avaliação", "Aprovado", "Implementado", "Revisado"}
        if not isinstance(governance, dict):
            errors.append("governance must be an object")
        else:
            if governance.get("knowledgeCategory") not in {"B", "C"}:
                errors.append("knowledgeCategory must be B or C")
            if governance.get("evidenceLevel") != "D":
                errors.append("evidenceLevel must be D")
            if governance.get("approvalStatus") not in controlled:
                errors.append("approvalStatus is not controlled")

        artifacts = manifest.get("artifacts", {})
        if not isinstance(artifacts, dict) or set(artifacts) != ARTIFACTS:
            errors.append("artifact inventory does not match BRE-001")
        elif isinstance(artifacts, dict):
            for name, control in artifacts.items():
                if not isinstance(control, dict) or control.get("status") not in STATUSES:
                    errors.append(f"invalid artifact declaration: {name}")
                    continue
                status = control["status"]
                if status == "available":
                    path = control.get("path")
                    if not path or not (root / str(path)).exists():
                        errors.append(f"available artifact path is missing: {name}")
                else:
                    if len(str(control.get("justification", ""))) < 20:
                        errors.append(f"artifact requires substantive justification: {name}")
                    if status == "planned":
                        gaps.append(f"artifact:{name}")

        bqa = manifest.get("bqa", {})
        if not isinstance(bqa, dict) or bqa.get("status") != "Approved":
            gaps.append("gate:bqa-approved")
        if manifest.get("humanReviewStatus") != "approved":
            gaps.append("gate:human-review")
        if manifest.get("publicReleaseAuthorized") is not True:
            gaps.append("gate:public-release-authorization")

    result = "Failed" if errors else ("Requires Revision" if gaps else "Passed")
    report = {
        "executionId": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "repository": manifest.get("repository", root.name),
        "version": manifest.get("componentVersion", "unknown"),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "mode": args.mode,
        "result": result,
        "errors": sorted(set(errors)),
        "openGaps": sorted(set(gaps)),
        "publicationPerformed": False,
        "limitations": [
            "This verifier checks declared local evidence; it does not publish, sign, approve or certify a release."
        ],
        "confidence": "high",
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = root / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if errors or (args.mode == "release" and result != "Passed") else 0


if __name__ == "__main__":
    raise SystemExit(main())
