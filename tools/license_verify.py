#!/usr/bin/env python3
"""Verify the distributed package license state and runtime dependency posture."""

from __future__ import annotations

import argparse
import json
import tomllib
from datetime import UTC, datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()

    root = Path.cwd()
    errors: list[str] = []

    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    if project.get("license") != "Apache-2.0":
        errors.append("pyproject.toml must declare Apache-2.0")

    license_files = set(project.get("license-files", []))
    if not {"LICENSE", "NOTICE"}.issubset(license_files):
        errors.append("pyproject.toml must include LICENSE and NOTICE in license-files")

    runtime_dependencies = project.get("dependencies", [])
    if runtime_dependencies:
        errors.append("runtime dependencies exist and require an explicit dependency-license review")

    license_path = root / "LICENSE"
    notice_path = root / "NOTICE"
    if not license_path.is_file():
        errors.append("LICENSE is missing")
    else:
        license_text = license_path.read_text(encoding="utf-8")
        if "Apache License" not in license_text or "Version 2.0, January 2004" not in license_text:
            errors.append("LICENSE does not contain the expected Apache License 2.0 text")

    if not notice_path.is_file() or not notice_path.read_text(encoding="utf-8").strip():
        errors.append("NOTICE is missing or empty")

    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "result": "Passed" if not errors else "Failed",
        "errors": errors,
        "projectLicense": project.get("license"),
        "runtimeDependencyCount": len(runtime_dependencies),
        "runtimeDependencies": runtime_dependencies,
        "licenseFiles": sorted(license_files),
        "scope": "distributed project license and runtime dependencies",
        "limitations": [
            "Development-only tool dependencies are not distributed as Bonfim SDK runtime dependencies and are outside this runtime-license gate."
        ],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = root / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
