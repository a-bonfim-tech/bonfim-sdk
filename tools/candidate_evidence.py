#!/usr/bin/env python3
"""Generate a non-authorizing evidence manifest for an exact release candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path.cwd()
    target = root / args.output
    target.parent.mkdir(parents=True, exist_ok=True)

    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    source_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    artifacts: list[dict[str, object]] = []
    dist = root / "dist"
    for path in sorted(dist.iterdir() if dist.exists() else ()):
        if not path.is_file() or path == target or path.name == "SHA256SUMS":
            continue
        artifacts.append(
            {
                "name": path.name,
                "size": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    report = {
        "schemaVersion": "1.0",
        "generatedAt": datetime.now(UTC).isoformat(),
        "repository": "a-bonfim-tech/bonfim-sdk",
        "version": version,
        "sourceCommit": source_commit,
        "candidateValidationOnly": True,
        "publicationAuthorized": False,
        "supportedPython": ["3.11", "3.12", "3.13", "3.14"],
        "artifacts": artifacts,
        "limitations": [
            "This manifest records technical candidate evidence only.",
            "It does not approve, publish, sign a Git tag, or authorize a GitHub/PyPI release."
        ],
    }
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(target.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
