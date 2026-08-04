# Compatibility and Deprecation Policy

Bonfim SDK is pre-alpha software. The project nevertheless uses an explicit compatibility policy so downstream users can distinguish experimentation from supported behavior.

## Semantic Versioning

The package follows Semantic Versioning.

- Patch releases fix defects without intentionally changing public behavior.
- Minor releases may add APIs and may deprecate existing pre-1.0 APIs.
- Major releases may remove deprecated APIs or introduce incompatible contracts.

Before version 1.0, a minor release may contain an incompatible change when maintaining the previous behavior would preserve a security defect or an unsound contract. Such changes must be documented prominently in `CHANGELOG.md` and the migration guide.

## Deprecation process

A public API is deprecated only when all of the following are provided:

1. a documented replacement or migration path;
2. a changelog entry;
3. a runtime warning when technically appropriate;
4. tests covering the compatibility behavior;
5. a planned removal version.

The default deprecation window is at least one minor release. Security-critical behavior may be removed sooner when retaining it would create material risk.

## Compatibility scope

Compatibility applies to documented public imports, CLI commands and serialized contracts. Internal modules, undocumented attributes, development manifests and experimental governance metadata are not stable APIs.

## Supported Python versions

The candidate supports Python 3.11 through 3.14. A Python version is removed only after it reaches end of upstream security support or when maintaining it prevents required security controls.

## Human authority

Compatibility does not override security or governance gates. No deprecated or compatibility path may bypass validation, sensitive-output blocking, provenance disclosure or required human review.
