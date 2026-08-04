# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Semantic Versioning.

## [Unreleased]

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

### Changed

- Automation rollback now receives the same step-specific inputs used during execution.
- Invalid per-step input structures fail closed before the workflow step executes.
- Rollback failures are explicitly recorded as failed outcomes with withheld exception details.
- Framework execution rejects non-mapping inputs through a structured failure result.
- Package metadata now includes classifiers, keywords and project URLs suitable for public distribution.
- CI now uses concurrency cancellation and verifies built distribution metadata and required package contents.

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
