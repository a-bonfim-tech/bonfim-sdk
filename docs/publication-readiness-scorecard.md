# Publication Readiness Scorecard

This scorecard defines the conditions required before Bonfim SDK can be recommended for public visibility. A repository being technically functional is not sufficient; every category must have objective evidence and no unresolved critical gate.

## Scoring model

Each category is scored from 0 to 10. Public release requires:

- every category at 10/10;
- no open critical or high-severity security finding;
- all mandatory CI jobs passing on the exact candidate commit;
- explicit human approval of the exact diff and publication scope;
- successful legal, privacy and intellectual-property review;
- confirmed absence of credentials, personal data and proprietary material.

A score of 10 means that the defined evidence for the current project scope is complete. It does not mean vulnerability absence, production certification or universal fitness.

## Current candidate assessment

| Category | Current score | 10/10 evidence requirement | Current gap |
|---|---:|---|---|
| Product clarity | 10 | README explains problem, users, capabilities, quick start, limitations and status | Candidate README added; final visual review pending |
| Architecture | 9 | Architecture, interfaces, data flow, trust boundaries and design decisions are documented | Architecture diagrams and ADR summary need final review |
| Code quality | 9 | Strict typing, lint, compile check, maintainable structure and no unresolved major defect | Exact candidate CI has not run yet |
| Testing | 9 | Unit and behavior tests cover success, failure, boundaries, security and compatibility; coverage ≥90% | New tests require hosted validation on candidate commit |
| Security engineering | 9 | Threat model, SAST, secret scanning, output guard, dependency review and documented residual risk | Independent review and candidate scan still pending |
| CI/CD | 9 | Immutable Actions, minimal permissions, test matrix, package verification, SBOM and release gates | Candidate workflow has not run; release gate evidence needs refresh |
| Supply-chain security | 8 | SBOM, pinned tooling, dependency updates, package integrity, provenance and release artifact controls | Signing, attestations and automated license verification are not complete |
| Packaging | 9 | Valid sdist/wheel, complete metadata, typed marker, license files and clean installation test | Clean-environment install and CLI smoke test need candidate evidence |
| Documentation | 9 | README, architecture, security, threat model, API usage, contributing, changelog and release guide are coherent | Terminology and internal governance references require final harmonization |
| Developer experience | 8 | Five-minute quick start, deterministic examples, CLI help, troubleshooting and copy-safe commands | Dedicated troubleshooting and end-to-end tutorial still needed |
| Governance | 9 | Scope, limitations, human authority, versioning and publication decision are explicit | Exact publication approval remains intentionally pending |
| Legal and privacy | 8 | License, notice, authorship, third-party attribution and privacy review completed | Formal final review of marks, artifacts and historical content pending |
| Recruiter value | 9 | Project demonstrates code, security, testing, trade-offs and concise evidence within ten minutes | Recruiter reading path and demo script need final polish |
| Maintenance | 8 | Supported versions, issue templates, dependency cadence, deprecation policy and maintenance expectations exist | Support policy and issue templates need completion |
| Reproducibility | 9 | Clean clone can build, test, lint, scan, package and run documented examples | Exact candidate must be reproduced in clean hosted and local environments |

## Blocking gates

The project must not be made public while any of the following remains unresolved:

1. Candidate CI has not passed on the exact publication commit.
2. Full-history secret scan has not been rerun against the final history.
3. Package build, metadata validation and clean-install smoke test are incomplete.
4. Security review has not assessed the final code and workflow diff.
5. Legal/IP/privacy review has not approved the exact public contents.
6. The repository owner has not reviewed and explicitly approved the final diff.
7. Repository visibility, release tag and package publication have not been separately authorized.

## Required final evidence package

- exact candidate commit SHA;
- complete changed-file list;
- passing CI run identifiers;
- test count and coverage report;
- Ruff, mypy and Bandit results;
- full-history Gitleaks result;
- CycloneDX SBOM artifact and validation result;
- sdist and wheel hashes;
- `twine check` result;
- clean-environment installation and CLI smoke test;
- security review summary;
- legal/privacy/IP review decision;
- final README and documentation review;
- explicit publication approval.

## Publication decision

Current decision: **Not authorized for public release.**

Reason: the private hardening branch is under active development and has not yet produced final hosted validation evidence or received human approval.
