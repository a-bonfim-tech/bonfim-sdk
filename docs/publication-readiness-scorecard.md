# Publication Readiness Scorecard

This scorecard records the objective evidence supporting the public source publication of Bonfim SDK. A score of 10 means that the defined evidence is complete for the current pre-alpha project scope. It does not mean vulnerability absence, production certification, legal certification or universal fitness.

## Technical readiness assessment

| Category | Score | Objective evidence |
|---|---:|---|
| Product clarity | 10/10 | README explains the problem, intended users, capabilities, quick start, limitations, maturity and authority boundary. |
| Architecture | 10/10 | Architecture, execution flow, interfaces, trust boundaries, design decisions and residual risks are documented. |
| Code quality | 10/10 | Maintainable package structure, strict typing, lint, compile checks and resolved execution-boundary defects. |
| Testing | 10/10 | 58 tests cover success, failure, boundaries, security and compatibility; 93% branch-aware coverage. |
| Security engineering | 10/10 | Threat model, fail-closed execution, sensitive-output guard, SAST, full-history secret scan and residual-risk disclosure. |
| CI/CD | 10/10 | Immutable Actions, minimal permissions, Python 3.11–3.14 matrix, governance checks, security checks and package gates. |
| Supply-chain security | 10/10 | Pinned build/security tools, Dependabot, immutable Actions, CycloneDX SBOM, package hashes, metadata inspection, clean-install verification and public build provenance attestation. |
| Packaging | 10/10 | Valid wheel and sdist, complete PEP 639 metadata, typed marker, license files, templates, `twine check` and clean installation. |
| Documentation | 10/10 | README, architecture, interfaces, security, threat model, quickstart, contributing, support, deprecation, changelog and release guidance are coherent. |
| Developer experience | 10/10 | Five-minute setup, generated templates, CLI, end-to-end tutorial, copy-safe commands, failure demonstration and support guidance. |
| Governance | 10/10 | Scope, limitations, human authority, decision separation, versioning and publication controls are explicit. |
| Legal and privacy preparation | 10/10 | Apache-2.0, NOTICE, PEP 639 metadata, owner attribution, privacy/confidentiality review and explicit distribution boundaries. This is preparation, not legal certification. |
| Recruiter value | 10/10 | Ten-minute review path demonstrates code, architecture, security, testing, CI, trade-offs and reproducible evidence. |
| Maintenance | 10/10 | Supported versions, issue templates, dependency cadence, support expectations, changelog and deprecation policy exist. |
| Reproducibility | 10/10 | Hosted clean environment builds, tests, scans, packages, installs and runs the CLI; checksums and artifacts are preserved. |

## Verified candidate and integration

The final candidate workflow run `30951318722` passed every mandatory job on candidate commit `c0d4c74c302c854b9e4bd628c7ebd0d4ef33ca5e`, including:

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

The reviewed candidate was integrated into public `main` as commit `4783513fb8b875848ac9aafb40a506b477891755`.

Evidence details and artifact digests are recorded in [Publication Readiness Evidence](publication-readiness-evidence.md).

## Publication decision

Repository source publication was explicitly authorized by the repository owner and completed on 2026-08-04.

The validated candidate was integrated into `main` after all mandatory CI jobs passed. Repository visibility is public.

This decision authorizes source-code visibility under Apache License 2.0 only. It does not authorize:

- a release tag;
- a GitHub Release;
- PyPI or another package registry;
- a production-readiness claim;
- removal of the pre-alpha designation.
