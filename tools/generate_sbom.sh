#!/usr/bin/env bash
set -euo pipefail

SYFT_VERSION="1.48.0"
SYFT_ARCHIVE="syft_${SYFT_VERSION}_linux_amd64.tar.gz"
SYFT_SHA256="6cef9a7f37220d9067eaf9cfaaa2fce986e9f320a8d42cbc36658c99af78ea04"
SYFT_URL="https://github.com/anchore/syft/releases/download/v${SYFT_VERSION}/${SYFT_ARCHIVE}"

OUTPUT="${1:-artifacts/bonfim-sdk.cdx.json}"
TOOL_ROOT="${RUNNER_TEMP:-/tmp}/bonfim-sdk-syft-${SYFT_VERSION}"
ARCHIVE_PATH="${TOOL_ROOT}/${SYFT_ARCHIVE}"
SYFT_BIN="${TOOL_ROOT}/syft"

mkdir -p "${TOOL_ROOT}" "$(dirname "${OUTPUT}")"

curl \
  --fail \
  --location \
  --silent \
  --show-error \
  --proto '=https' \
  --tlsv1.2 \
  --retry 6 \
  --retry-all-errors \
  --retry-delay 2 \
  --connect-timeout 15 \
  --max-time 180 \
  --output "${ARCHIVE_PATH}" \
  "${SYFT_URL}"

printf '%s  %s\n' "${SYFT_SHA256}" "${ARCHIVE_PATH}" | sha256sum --check --strict -

tar -xzf "${ARCHIVE_PATH}" -C "${TOOL_ROOT}" syft
chmod 0755 "${SYFT_BIN}"

"${SYFT_BIN}" version | grep -Fq "${SYFT_VERSION}"
"${SYFT_BIN}" dir:. -o "cyclonedx-json=${OUTPUT}"

test -s "${OUTPUT}"

python3 - "${OUTPUT}" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))

if data.get("bomFormat") != "CycloneDX":
    raise SystemExit("SBOM bomFormat is not CycloneDX")
if data.get("specVersion") != "1.7":
    raise SystemExit(f"unexpected CycloneDX specVersion: {data.get('specVersion')!r}")
if data.get("version") != 1:
    raise SystemExit(f"unexpected CycloneDX document version: {data.get('version')!r}")
if not isinstance(data.get("components", []), list):
    raise SystemExit("CycloneDX components must be a list")

print(
    "validated CycloneDX SBOM: "
    f"format={data['bomFormat']} spec={data['specVersion']} "
    f"components={len(data.get('components', []))}"
)
PY
