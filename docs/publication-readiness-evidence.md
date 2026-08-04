# Publication Readiness Evidence

This document records the measurable technical evidence generated for the private Bonfim SDK publication candidate. It does not authorize merge, repository visibility changes, tagging, GitHub Release creation or package-registry publication.

## Candidate identity

| Field | Value |
|---|---|
| Repository | `a-bonfim-tech/bonfim-sdk` |
| Branch | `release/publication-readiness-v1` |
| Validation workflow | `Continuous Integration` |
| Reference successful run | `30951071469` |
| Reference candidate commit | `73a5143b8842ac2eeca3806716766d3e9f7ec02c` |
| Environment | GitHub-hosted Ubuntu 24.04 runners |

The README and this evidence document were added after the reference run. A final workflow run is therefore required on the new exact head commit before publication review is complete.

## Test and compatibility evidence

The reference candidate passed:

- 58 tests on Python 3.11;
- 58 tests on Python 3.12;
- 58 tests on Python 3.13;
- 58 tests on Python 3.14;
- source and test compilation on all four Python versions.

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

The reference candidate passed:

- full-history Gitleaks scanning;
- CycloneDX SBOM generation and artifact preservation;
- third-party GitHub Actions pinned to immutable commit SHAs;
- read-only default workflow permissions;
- governance quality and release baseline checks;
- package-content inspection;
- Apache-2.0 metadata validation;
- SHA-256 checksum generation and verification.

GitHub artifact attestations are not generated while this repository remains private on a non-Enterprise plan. GitHub makes private-repository attestations available through Enterprise Cloud; public repositories can use them on current Free, Pro and Team plans. If public visibility is later approved, build provenance attestation should be added to the release pipeline and verified before package distribution.

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

The reference run preserved:

| Artifact | Digest |
|---|---|
| Distribution package and checksums | `sha256:92055d71069b9a6e26c542b97c3de8fe46dc07ef4c63da22e54b8cc4b9b1d23c` |
| Gitleaks SARIF | `sha256:c4fb560cf960153753529a0a761e0f24a5f3e586d31e5fa2a50c780a07ddf146` |
| CycloneDX SBOM | `sha256:76dcd5c3de76078b7fd53e33c47624f3c9de2cf6ad349a741ca9c418cc7f797e` |
| Governance evidence | `sha256:5e234ff8faf990995dfb3d95ed33c240e0585567f31509b31563861e4ac620bd` |

## Security review findings resolved during preparation

Two material robustness defects were identified and corrected:

1. Automation rollback previously received the global workflow input rather than the exact input used by the completed step. The candidate now records and reuses the step-specific mapping.
2. Unexpected component or registry exceptions could escape Agent orchestration. The candidate now returns a structured failed result and withholds exception details.

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

## Final technical gate

The project is technically publication-ready only when the final CI run passes on the exact current head commit and no later commit is added.

## Human publication gates

Even after technical readiness, the following remain separate owner decisions:

- exact diff approval;
- legal, authorship, trademark and privacy approval;
- merge approval;
- public visibility approval;
- release-tag approval;
- GitHub Release approval;
- package-registry publication approval;
- public profile pinning approval.
