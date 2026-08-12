# Release Process

> Category C — Architectural Proposal · Evidence Level D · Status: `Proposta` · Origin: Bonfim Labs.

This repository follows Semantic Versioning using tags in the form `vMAJOR.MINOR.PATCH`.

## Version rules

- `MAJOR`: incompatible change to a documented public contract.
- `MINOR`: backward-compatible capability.
- `PATCH`: backward-compatible fix, security hardening or documentation correction.
- During `0.y.z`, breaking changes increment `MINOR`; compatible changes and fixes increment `PATCH`.
- Pre-releases require a separately approved process because Python PEP 440 and npm encode them differently; the current workflow publishes stable SemVer tags only.

A public contract includes import paths, schemas, CLI commands, HTTP endpoints, configuration names and documented behavior intended for consumers.

## Required evidence

A release requires:

1. An approved change merged into protected `main`.
2. Green repository validation and CodeQL policy checks.
3. Updated `VERSION`, package manifest, package `__version__` and `CHANGELOG.md`.
4. Confirmed compatibility classification.
5. No known exposed secrets or generated credentials.
6. Human maintainer approval.
7. Passing BQA and BRE release gates with preserved evidence.
8. Approved release notes, migration guidance, SBOM, checksums and license information.
9. A separate, explicit public-release authorization. A green CI or release-candidate run is not authorization.

The release-candidate workflow must test the exact source ref on Python 3.11, 3.12, 3.13 and 3.14 and preserve evidence from coverage, Ruff, mypy, Bandit, full-history Gitleaks, CycloneDX SBOM, package verification, BQA/BRE, clean installation and provenance attestation.

A generated SBOM is an inventory artifact, not proof that every component is safe or legally usable.

## Candidate validation

Before creating a tag, run the manual `Release Candidate Validation` workflow against the exact intended `main` commit and expected version.

The workflow is non-publishing. It must complete successfully before the owner considers release authorization.

## Publication procedure

After the candidate is reviewed and the owner separately authorizes GitHub Release publication:

```bash
VERSION=X.Y.Z
git switch main
git pull --ff-only

test "$(cat VERSION)" = "$VERSION"

git tag -s "v$VERSION" -m "Release v$VERSION"
git push origin "v$VERSION"
```

Do not create the release tag before the version-preparation commit has already been merged through the protected branch workflow.

The tag workflow requires an annotated version tag pointing to the exact protected `main` HEAD. It then repeats the Python 3.11–3.14 compatibility tests and release assurance gates before publishing.

The GitHub Release attaches the verified wheel, source distribution, CycloneDX SBOM, BQA/BRE evidence and `SHA256SUMS`. The checksum set receives GitHub build-provenance attestation.

Publishing to PyPI or another package registry is a separate decision and is not implicit in the GitHub Release.

## Verification after publication

After a successful release:

```bash
gh release view "v$VERSION" --repo a-bonfim-tech/bonfim-sdk

gh release download "v$VERSION" \
  --repo a-bonfim-tech/bonfim-sdk \
  --dir "/tmp/bonfim-sdk-v$VERSION"

cd "/tmp/bonfim-sdk-v$VERSION"
sha256sum --check SHA256SUMS
```

Where GitHub attestation verification is available, verify the downloaded distributions against the repository provenance before use.

## Rollback and correction

Published tags are immutable. Do not move or reuse a tag. Correct an erroneous release with a new patch version; mark the affected GitHub Release as deprecated when necessary and record the reason in the changelog.
