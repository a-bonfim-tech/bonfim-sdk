# Compatibility Policy

Bonfim SDK is currently **pre-alpha** and versioned with Semantic Versioning. The `0.x` series is an initial-development line, so compatibility commitments are intentionally narrower than they will be at `1.0.0`.

## Supported Python versions for 0.2.1

The exact `0.2.1` candidate is validated in CI on:

- CPython 3.11;
- CPython 3.12;
- CPython 3.13;
- CPython 3.14.

The package is pure Python, but the release assurance baseline is executed on GitHub-hosted Ubuntu runners. Other operating systems may work but are not independently certified by this release process.

## Versioning policy

### Patch releases (`0.2.x`)

Patch releases are intended for backward-compatible defect fixes, security hardening, documentation, packaging, governance and release-engineering improvements. They must not intentionally remove a documented public API.

### Minor releases (`0.x.0` before 1.0)

Minor pre-1.0 releases may introduce incompatible API or behavior changes when necessary. Any intentional incompatibility must be recorded in the changelog and accompanied by explicit migration guidance before release authorization.

### 1.0 and later

A `1.0.0` release would establish a stronger public compatibility contract and requires a separate maturity decision. Nothing in the `0.x` line implies production readiness or long-term API stability.

## Deprecation policy

When practical in the pre-1.0 line, a public API scheduled for removal should first be documented as deprecated and remain available for at least one subsequent minor release. Security defects or unsafe behavior may require a faster change, but the reason and impact must be documented.

## 0.2.1 migration impact

`0.2.1` does not intentionally remove a documented public API. The release focuses on fail-closed behavior, packaging, supply-chain controls, release assurance, documentation and repository governance. A version-specific migration guide is therefore not required for this patch release.

## Distribution boundary

Compatibility validation does not authorize publication. Git tagging, GitHub Release publication, PyPI publication and removal of the pre-alpha designation remain separate owner decisions under `RELEASE_POLICY.md`.
