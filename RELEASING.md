# Release Process

> Category C — Architectural Proposal · Evidence Level D · Status: `Proposta` · Origin: Bonfim Labs.

This repository follows Semantic Versioning using tags in the form `vMAJOR.MINOR.PATCH`.

## Version rules

- `MAJOR`: incompatible change to a documented public contract.
- `MINOR`: backward-compatible capability.
- `PATCH`: backward-compatible fix, security hardening or documentation correction.
- During `0.y.z`, breaking changes increment `MINOR`; compatible changes and fixes increment `PATCH`.
- Pre-releases require a separately approved process because Python PEP 440 and npm encode them differently; the initial workflow publishes stable SemVer tags only.

A public contract includes import paths, schemas, CLI commands, HTTP endpoints, configuration names and documented behavior intended for consumers.

## Required evidence

A release requires:

1. An approved change merged into `main`.
2. Green repository validation and dependency review.
3. Updated `VERSION`, package manifest and `CHANGELOG.md`.
4. Confirmed compatibility classification.
5. No known exposed secrets or generated credentials.
6. Human maintainer approval.
7. Passing BQA and BRE release gates with preserved evidence.
8. Approved release notes, migration guidance, SBOM, checksums and license information.
9. A separate, explicit public-release authorization. A tag or green CI run is not authorization.

The candidate CI must also preserve evidence from the mandatory Bandit SAST,
full-history Gitleaks scan, and CycloneDX SBOM jobs. A generated SBOM is an
inventory artifact, not proof that every component is safe or legally usable.

## Procedure

```bash
VERSION=X.Y.Z
git switch main
git pull --ff-only
# Update VERSION, manifest and CHANGELOG before committing.
git commit -S -m "chore(release): prepare v$VERSION"
git tag -s "v$VERSION" -m "Release v$VERSION"
git push origin main
git push origin "v$VERSION"
```

The tag workflow validates the version and changelog, requires an annotated tag and creates the GitHub Release. Publishing to PyPI, npm or another package registry is a separate decision and is not implicit.

## Rollback and correction

Published tags are immutable. Do not move or reuse a tag. Correct an erroneous release with a new patch version; mark the affected GitHub Release as deprecated when necessary and record the reason in the changelog.
