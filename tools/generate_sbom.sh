#!/usr/bin/env bash
set -euo pipefail

OUTPUT="${1:-artifacts/bonfim-sdk.cdx.json}"
mkdir -p "$(dirname "${OUTPUT}")"

python3 - "${OUTPUT}" <<'PY'
from __future__ import annotations

import json
import pathlib
import re
import sys
import tomllib

output = pathlib.Path(sys.argv[1])
root = pathlib.Path.cwd()

pyproject_path = root / "pyproject.toml"
version_path = root / "VERSION"
source_path = root / "src/bonfim/__init__.py"
license_path = root / "LICENSE"
notice_path = root / "NOTICE"

for required in (pyproject_path, version_path, source_path, license_path, notice_path):
    if not required.is_file():
        raise SystemExit(f"required SBOM input is missing: {required.relative_to(root)}")

pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
project = pyproject.get("project")
if not isinstance(project, dict):
    raise SystemExit("pyproject.toml is missing [project]")

name = project.get("name")
version = project.get("version")
license_expression = project.get("license")
requires_python = project.get("requires-python")
urls = project.get("urls", {})
runtime_dependencies = project.get("dependencies", [])

if name != "bonfim-sdk":
    raise SystemExit(f"unexpected project name: {name!r}")
if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
    raise SystemExit(f"unexpected project version: {version!r}")
if version_path.read_text(encoding="utf-8").strip() != version:
    raise SystemExit("VERSION does not match pyproject.toml")

source = source_path.read_text(encoding="utf-8")
match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', source, re.MULTILINE)
if match is None or match.group(1) != version:
    raise SystemExit("bonfim.__version__ does not match pyproject.toml")

if license_expression != "Apache-2.0":
    raise SystemExit(f"unexpected license expression: {license_expression!r}")
if requires_python != ">=3.11":
    raise SystemExit(f"unexpected Requires-Python: {requires_python!r}")
if not isinstance(runtime_dependencies, list):
    raise SystemExit("project.dependencies must be a list when declared")
if runtime_dependencies:
    raise SystemExit(
        "runtime dependencies are present but this bounded runtime SBOM generator "
        "does not yet model them; update the generator before release"
    )
if not isinstance(urls, dict):
    raise SystemExit("project.urls must be a table")

purl = f"pkg:pypi/{name}@{version}"

reference_types = {
    "Homepage": "website",
    "Documentation": "documentation",
    "Issues": "issue-tracker",
    "Source": "vcs",
}
external_references = []
for key, reference_type in reference_types.items():
    value = urls.get(key)
    if value is not None:
        if not isinstance(value, str) or not value.startswith("https://"):
            raise SystemExit(f"invalid HTTPS project URL for {key}: {value!r}")
        external_references.append({"type": reference_type, "url": value})

component = {
    "type": "library",
    "bom-ref": purl,
    "name": name,
    "version": version,
    "description": str(project.get("description", "")),
    "licenses": [{"license": {"id": license_expression}}],
    "purl": purl,
    "externalReferences": external_references,
    "properties": [
        {"name": "bonfim-sdk:runtime-dependency-count", "value": "0"},
        {"name": "bonfim-sdk:requires-python", "value": requires_python},
        {"name": "bonfim-sdk:maturity", "value": "pre-alpha"},
    ],
}

bom = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.7",
    "version": 1,
    "metadata": {"component": component},
    "components": [],
    "dependencies": [{"ref": purl, "dependsOn": []}],
}

output.write_text(json.dumps(bom, indent=2, sort_keys=True) + "\n", encoding="utf-8")

validated = json.loads(output.read_text(encoding="utf-8"))
if validated.get("bomFormat") != "CycloneDX":
    raise SystemExit("SBOM bomFormat is not CycloneDX")
if validated.get("specVersion") != "1.7":
    raise SystemExit("SBOM specVersion is not 1.7")
if validated.get("version") != 1:
    raise SystemExit("SBOM document version is not 1")
if validated.get("metadata", {}).get("component", {}).get("bom-ref") != purl:
    raise SystemExit("SBOM root component reference is inconsistent")
if validated.get("components") != []:
    raise SystemExit("runtime SBOM unexpectedly contains dependency components")
if validated.get("dependencies") != [{"ref": purl, "dependsOn": []}]:
    raise SystemExit("runtime SBOM dependency graph is inconsistent")

print(
    "validated deterministic CycloneDX runtime SBOM: "
    f"name={name} version={version} spec=1.7 runtime_dependencies=0"
)
PY

test -s "${OUTPUT}"
