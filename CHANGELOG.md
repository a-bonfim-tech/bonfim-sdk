# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Semantic Versioning.

## [Unreleased]

### Added

- Four deterministic GitHub PR evidence, readiness, security and governance Skills.
- BQA/BRE evidence baselines and fail-closed release gates.
- Mandatory Bandit SAST, full-history Gitleaks scanning, and CycloneDX SBOM
  generation in the SDK CI baseline.
- Security tooling pinned to controlled versions and third-party Actions pinned
  to immutable commit SHAs.
- Apache-2.0 package metadata with `LICENSE` and `NOTICE` preserved in built
  wheels.

## [0.2.0] - 2026-07-15

### Added

- BSD-001 base interfaces and shared ecosystem models.
- Framework, Agent and Automation base classes.
- Central automatic-import and allowlisted entry-point registries.
- Official component templates and the `bonfim` CLI.
- Four reference Skills and comprehensive contract tests.

### Changed

- `Skill.run(inputs)` now executes the complete governed pipeline; legacy
  `run(context)` subclasses are adapted automatically.

## [0.1.0] - 2026-07-14

### Added

- Initial public SDK contract for reusable Bonfim Skills.
- Skill registry, runner, context, provenance and evidence models.
