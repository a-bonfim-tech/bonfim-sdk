# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Semantic Versioning.

## [Unreleased]

## [0.2.1] - 2026-08-12

### Added

- Recruiter- and developer-facing README with clear problem statement, architecture, quick start, security boundary and limitations.
- Explicit repository threat model.
- Contribution requirements and security-sensitive review rules.
- Publication-hardening tests for workflow inputs, rollback behavior and framework input validation.
- Package build and metadata validation in CI.
- Test matrix for Python 3.11, 3.12, 3.13 and 3.14.
- Four deterministic GitHub PR evidence, readiness, security and governance Skills.
- BQA/BRE evidence baselines and fail-closed release gates.
- Mandatory Bandit SAST, full-history Gitleaks scanning, and CycloneDX SBOM generation in the SDK CI baseline.
- Security tooling pinned to controlled versions and third-party Actions pinned to immutable commit SHAs.
- Apache-2.0 package metadata with `LICENSE` and `NOTICE` preserved in built wheels.
- Controlled non-publishing release-candidate workflow.
- GitHub build-provenance attestation for public `main` distributions.
- Repository rulesets requiring pull requests, CI checks and CodeQL policy before protected-branch integration.
- Separate BQA/BRE `candidate` readiness modes so technical evidence can be completed before human publication authorization.
- Deterministic formatting, runtime-license and registry performance regression gates with preserved JSON evidence.
- Frozen version-specific release notes and an explicit pre-1.0 compatibility/deprecation policy.
- Non-authorizing candidate evidence manifest included in the candidate asset integrity set.

### Changed

- Automation rollback now receives the same step-specific inputs used during execution.
- Invalid per-step input structures fail closed before the workflow step executes.
- Rollback failures are explicitly recorded as failed outcomes with withheld exception details.
- Framework execution rejects non-mapping inputs through a structured failure result.
- Package metadata now includes classifiers, keywords and project URLs suitable for public distribution.
- CI now uses concurrency cancellation and verifies built distribution metadata and required package contents.
- Public repository governance now includes CODEOWNERS and an explicit release policy separating source visibility, release tags, GitHub Releases and package-registry publication.
- GitHub release automation now performs the release gates against the tagged source, builds and verifies distributions, generates checksums and SBOM evidence, creates provenance attestation, and attaches release artifacts to the GitHub Release.
- Release-candidate and final-release workflows now create technical artifacts before BRE validation, removing the previous circular dependency between evidence generation and publication approval.
- Final BQA/BRE `release` modes remain distinct and require retained human approval before publication can proceed.

### Security

- Unexpected component or registry exceptions are converted into structured failures with implementation details withheld.
- Full-history secret scanning and CodeQL remain required security signals for protected-branch integration.
- Release publication remains human-triggered through an explicitly created annotated version tag; successful CI alone does not create release authority.
- Candidate-readiness evidence explicitly records `publicationAuthorized: false` and cannot satisfy the final release authorization gate.

## [0.2.0] - 2026-07-15

### Added

- BSD-001 base interfaces and shared ecosystem models.
- Framework, Agent and Automation base classes.
- Central automatic-import and allowlisted entry-point registries.
- Official component templates and the `bonfim` CLI.
- Four reference Skills and comprehensive contract tests.

### Changed

- `Skill.run(inputs)` now executes the complete governed pipeline; legacy `run(context)` subclasses are adapted automatically.

## [0.1.0] - 2026-07-14

### Added

- Initial public SDK contract for reusable Bonfim Skills.
- Skill registry, runner, context, provenance and evidence models.
