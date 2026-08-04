# Publication Readiness Evidence

This document records the measurable technical evidence used for the public source publication of Bonfim SDK. It does not authorize a release tag, GitHub Release, package-registry publication or production-readiness claim.

## Publication identity

| Field | Value |
|---|---|
| Repository | `a-bonfim-tech/bonfim-sdk` |
| Validated candidate branch | `release/publication-readiness-v1` |
| Validated candidate commit | `c0d4c74c302c854b9e4bd628c7ebd0d4ef33ca5e` |
| Successful final candidate run | `30951318722` |
| Public `main` integration commit | `4783513fb8b875848ac9aafb40a506b477891755` |
| Visibility | Public — authorized and completed on 2026-08-04 |
| Environment | GitHub-hosted Ubuntu 24.04 runners |

The final candidate run completed successfully before the reviewed candidate was integrated into `main`.

## Test and compatibility evidence

The validated candidate passed:

- 58 tests on Python 3.11;
- 58 tests on Python 3.12;
- 58 tests on Python 3.13;
- 58 tests on Python 3.14;
- source and test compilation on all four supported Python versions.

## Coverage and static quality

The quality job reported:

- 958 statements;
- 43 missed statements;
- 188 branches;
- 30 partial branches;
- 93% total coverage;
- Ruff: all checks passed;
- mypy strict: no issues in 27 source files;
- Bandit: no finding at the configured high-severity/high-confidence failure threshold.

## Security and supply-chain evidence

The validated candidate passed:

- full-history Gitleaks scanning;
- CycloneDX SBOM generation and artifact preservation;
- third-party GitHub Actions pinned to immutable commit SHAs;
- read-only default workflow permissions;
- governance quality and release baseline checks;
- package-content inspection;
- Apache-2.0 metadata validation;
- SHA-256 checksum generation and verification.

The public `main` workflow also includes build provenance attestation for wheel and source-distribution checksums on direct pushes to `main`.

## Packaging and reproducibility evidence

The package job successfully:

1. built the wheel and source distribution;
2. passed `twine check`;
3. verified required package files, including `LICENSE`, `NOTICE` and `py.typed`;
4. verified `License-Expression: Apache-2.0` and `Requires-Python: >=3.11`;
5. generated and verified `SHA256SUMS`;
6. created a clean virtual environment;
7. installed the wheel without runtime dependencies;
8. executed `bonfim version` and `bonfim doctor`;
9. imported the installed package;
10. verified packaged templates and typing marker.

## Preserved workflow artifacts

The final candidate run preserved:

| Artifact | Digest |
|---|---|
| Distribution package and checksums | `sha256:102e2b08f951e36dbf3c72673f53205bb24fa827bb9ce67e801df97c09ff3349` |
| Gitleaks SARIF | `sha256:5b576c2066580ba8240a749dfbb7ceec84ced9228a325571802aaf3139f2a56d` |
| CycloneDX SBOM | `sha256:bbb89d39da9fc13773f406e216b78f0bd089eb7f6723393c91f4a8e170dbeaa5` |
| Governance evidence | `sha256:30e061f533d533238ddae950e1a159cd83c8408f8b4f16fbb6c5b4e72c6dcde5` |

## Security review findings resolved during preparation

Two material robustness defects were identified and corrected:

1. Automation rollback previously received the global workflow input rather than the exact input used by the completed step. The implementation now records and reuses the step-specific mapping.
2. Unexpected component or registry exceptions could escape Agent orchestration. The implementation now returns a structured failed result and withholds exception details.

Additional hardening validates Skill selection, individual Skill inputs, Framework inputs and rollback failure reporting.

## Residual risks

The following are intentional boundaries, not undisclosed defects:

- components execute in-process and must be trusted;
- the output detector is not a complete DLP control;
- nested input objects are not recursively frozen;
- rollback cannot prove reversal of external effects;
- package/plugin publisher identity is not cryptographically enforced;
- no durable audit store, scheduler, sandbox or network connector is included;
- the SDK cannot certify compliance, correctness or authorization.

## Publication decision

Public source visibility was explicitly authorized by the repository owner and completed on 2026-08-04 under Apache License 2.0.

This decision does not authorize:

- a release tag;
- a GitHub Release;
- PyPI or another package registry;
- a production-readiness claim;
- removal of the pre-alpha designation.
