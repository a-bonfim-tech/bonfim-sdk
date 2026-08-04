# Publication Readiness Scorecard

This scorecard defines the conditions required before Bonfim SDK can be recommended for public visibility. A repository being technically functional is not sufficient; every category requires objective evidence and no unresolved critical gate.

## Scoring model

Each category is scored from 0 to 10. A score of 10 means the defined evidence is complete for the current pre-alpha project scope. It does not mean vulnerability absence, production certification, legal approval or universal fitness.

Public release additionally requires:

- all mandatory CI jobs passing on the exact final candidate commit;
- no unresolved critical or high-severity security finding;
- repository-owner review of the complete diff;
- legal, privacy, authorship and intellectual-property approval;
- separate authorization for merge, visibility, tagging and distribution.

## Technical readiness assessment

| Category | Score | Objective evidence |
|---|---:|---|
| Product clarity | 10/10 | README explains the problem, intended users, capabilities, quick start, limitations, maturity and authority boundary. |
| Architecture | 10/10 | Architecture, execution flow, interfaces, trust boundaries, design decisions and residual risks are documented. |
| Code quality | 10/10 | Maintainable package structure, strict typing, lint, compile checks and resolved execution-boundary defects. |
| Testing | 10/10 | 58 tests cover success, failure, boundaries, security and compatibility; 93% branch-aware coverage. |
| Security engineering | 10/10 | Threat model, fail-closed execution, sensitive-output guard, SAST, full-history secret scan and residual-risk disclosure. |
| CI/CD | 10/10 | Immutable Actions, minimal permissions, Python 3.11–3.14 matrix, governance checks, security checks and package gates. |
| Supply-chain security | 10/10 | Pinned build/security tools, Dependabot, immutable Actions, CycloneDX SBOM, package hashes, metadata inspection and clean-install verification. Attestation is documented as a post-publication release gate because private use requires Enterprise Cloud. |
| Packaging | 10/10 | Valid wheel and sdist, complete PEP 639 metadata, typed marker, license files, templates, `twine check` and clean installation. |
| Documentation | 10/10 | README, architecture, interfaces, security, threat model, quickstart, contributing, support, deprecation, changelog and release guidance are coherent. |
| Developer experience | 10/10 | Five-minute setup, generated templates, CLI, end-to-end tutorial, copy-safe commands, failure demonstration and support guidance. |
| Governance | 10/10 | Scope, limitations, human authority, decision separation, versioning and publication controls are explicit. |
| Legal and privacy preparation | 10/10 | Apache-2.0, NOTICE, PEP 639 metadata, privacy/confidentiality checklist and explicit final owner review gate. This is preparation, not legal certification. |
| Recruiter value | 10/10 | Ten-minute review path demonstrates code, architecture, security, testing, CI, trade-offs and reproducible evidence. |
| Maintenance | 10/10 | Supported versions, issue templates, dependency cadence, support expectations, changelog and deprecation policy exist. |
| Reproducibility | 10/10 | Hosted clean environment builds, tests, scans, packages, installs and runs the CLI; checksums and artifacts are preserved. |

## Verified reference run

The reference workflow run `30951071469` passed every job on candidate commit `73a5143b8842ac2eeca3806716766d3e9f7ec02c`, including:

- tests on Python 3.11, 3.12, 3.13 and 3.14;
- 93% coverage;
- Ruff;
- mypy strict;
- Bandit;
- full-history Gitleaks;
- CycloneDX SBOM;
- governance baseline checks;
- wheel and sdist build;
- metadata and package-content validation;
- SHA-256 checksums;
- clean-install and CLI smoke tests.

The evidence details and artifact digests are recorded in [Publication Readiness Evidence](publication-readiness-evidence.md).

## Current final-CI condition

The README, evidence report and this scorecard were updated after the reference run. These documentation-only changes alter the candidate SHA. Therefore, **all technical scores remain provisional until the final workflow passes on the exact current head commit**.

No code or configuration change may be added after that final successful run without invalidating the exact-candidate evidence.

## Human review gates

Technical 10/10 does not authorize publication. The repository must remain private until the owner explicitly completes the [Publication Review Checklist](publication-review-checklist.md), including:

1. complete diff review;
2. legal, authorship, trademark and privacy review;
3. merge decision;
4. visibility decision;
5. release-tag decision;
6. GitHub Release decision;
7. package-registry decision;
8. profile-pinning decision.

## Publication decision

Current decision: **Not authorized for public release.**

Reason: the technical candidate is awaiting one final exact-head CI run and subsequent repository-owner review. Public visibility and distribution are independent decisions.
