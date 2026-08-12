# Release Process

> Category C — Architectural Proposal · Evidence Level D · Status: `Proposta` · Origin: Bonfim Labs.

This repository follows Semantic Versioning using tags in the form `vMAJOR.MINOR.PATCH`.

## Version rules

- `MAJOR`: incompatible change to a documented public contract.
- `MINOR`: backward-compatible capability.
- `PATCH`: backward-compatible fix, security hardening or documentation correction.
- During `0.y.z`, breaking changes increment `MINOR`; compatible changes and fixes increment `PATCH`.
- Pre-releases require a separately approved process because Python PEP 440 and SemVer encode them differently; the current workflow publishes stable SemVer tags only.

A public contract includes import paths, schemas, CLI commands, configuration names and documented behavior intended for consumers.

See `docs/compatibility.md` for the current pre-1.0 compatibility and deprecation policy.

## Required evidence

A release requires:

1. An approved change merged into protected `main`.
2. Green repository validation and CodeQL policy checks.
3. Updated `VERSION`, package manifest, package `__version__` and `CHANGELOG.md`.
4. Confirmed compatibility classification and frozen version-specific release notes.
5. No known exposed secrets or generated credentials.
6. Exact-candidate validation on Python 3.11, 3.12, 3.13 and 3.14.
7. Coverage, Ruff, mypy, formatting, Bandit, runtime-license and performance regression gates.
8. Full-history Gitleaks scanning and CycloneDX SBOM generation.
9. Verified wheel/source distributions, package metadata and clean installation.
10. Candidate SHA-256 manifest and build-provenance attestation.
11. Passing BQA and BRE **candidate-readiness** evidence.
12. Human maintainer review of the complete candidate evidence.
13. A separate explicit BQA/BRE publication approval and public-release authorization.
14. Passing BQA and BRE **release** gates against the exact final source.

A generated SBOM is an inventory artifact, not proof that every component is safe or legally usable.

## Candidate validation

Before creating a tag, run the manual `Release Candidate Validation` workflow against the exact intended `main` commit and expected version.

The workflow is non-publishing. It must complete successfully before the owner considers release authorization.

Candidate validation deliberately uses `BQA --mode candidate` and `BRE --mode candidate`. These modes validate technical readiness but do not set or infer human approval, public-release authorization, Git tag authority or package-registry authority.

The candidate workflow first creates the evidence needed for review — distributions, SBOM, quality evidence, frozen release notes, candidate evidence and checksums — and only then evaluates BRE candidate readiness. This prevents a circular requirement for approval before evidence exists.

## Human release decision

After candidate validation passes, the owner reviews:

- the exact candidate source commit;
- all candidate checks and generated artifacts;
- changelog and frozen release notes;
- compatibility impact;
- threat-model changes;
- security findings and residual risks;
- license/NOTICE state;
- checksums, SBOM and provenance.

If publication is approved, that decision must be retained separately in the repository governance/release state. Candidate success alone is never publication authority.

## Publication procedure

Only after the candidate passes and the owner separately authorizes GitHub Release publication:

```bash
VERSION=X.Y.Z
git switch main
git pull --ff-only

test "$(cat VERSION)" = "$VERSION"

git tag -s "v$VERSION" -m "Release v$VERSION"
git push origin "v$VERSION"
```

Do not create the release tag before the release-authorization state has already been merged through the protected branch workflow.

The tag workflow requires an annotated version tag pointing to the exact protected `main` HEAD. It repeats Python 3.11–3.14 compatibility tests and technical assurance, creates the release artifacts, then executes `BQA --mode release` and `BRE --mode release`. Those release modes remain fail-closed unless the retained human authorization fields are approved.

The GitHub Release attaches the verified wheel, source distribution, CycloneDX SBOM, candidate/release evidence and `SHA256SUMS`. The checksum set receives GitHub build-provenance attestation.

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
