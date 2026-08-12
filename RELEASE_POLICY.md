# Release Policy

Bonfim SDK is public source software in pre-alpha status. Source visibility, release tagging, GitHub Release publication and package-registry distribution are separate decisions.

## Release authority

Only the repository owner may authorize:

- a version change;
- a release-candidate build;
- creation of a Git tag;
- publication of a GitHub Release;
- publication to PyPI or another package registry;
- removal of the pre-alpha designation.

Passing automation does not grant release authority.

## Required release inputs

A release candidate must define:

- the intended Semantic Version;
- the exact source commit;
- the supported Python versions;
- the release notes and migration impact;
- the licensing and attribution state;
- the distribution scope;
- the explicit owner authorization.

## Mandatory technical gates

Before a release decision, the exact candidate must pass:

1. tests on Python 3.11, 3.12, 3.13 and 3.14;
2. branch-aware coverage of at least 90%;
3. Ruff;
4. mypy strict;
5. Bandit at the configured blocking threshold;
6. full-history Gitleaks scanning;
7. CycloneDX SBOM generation;
8. wheel and source-distribution build;
9. `twine check`;
10. package-content and metadata verification;
11. SHA-256 checksum generation and verification over release distributions and evidence assets;
12. clean-environment installation and CLI smoke testing;
13. BQA and BRE release-gate validation;
14. build-provenance attestation for the final release asset checksum set.

## Release-candidate workflow

The manual release-candidate workflow validates an exact source ref and preserves artifacts. It does not create a tag, GitHub Release or package-registry publication.

The operator must provide the expected version. The workflow fails when the value does not match `VERSION`, `pyproject.toml`, `bonfim.__version__` and the corresponding `CHANGELOG.md` section.

The exact candidate is tested on Python 3.11, 3.12, 3.13 and 3.14 before packaging and assurance evidence are produced.

## GitHub Release workflow

An explicitly created annotated `vMAJOR.MINOR.PATCH` tag is the human release trigger. The tag workflow must fail closed unless the tag points to the exact protected `main` HEAD and all source version declarations and changelog metadata agree.

The final GitHub Release workflow repeats the release compatibility matrix and assurance gates, builds wheel and source distributions, generates the CycloneDX SBOM, BQA/BRE evidence and SHA-256 checksum manifest, produces provenance attestation, and attaches the verified release artifacts to the GitHub Release.

A successful tag workflow authorizes only the GitHub Release associated with the explicitly created tag. It does not authorize PyPI or another package registry.

## Required human review

The owner must review:

- the exact diff since the prior version;
- changelog completeness;
- compatibility and deprecation impact;
- threat-model changes;
- security findings and residual risks;
- package metadata;
- license and NOTICE files;
- generated checksums, SBOM and provenance;
- whether public distribution is appropriate.

## Prohibited implicit actions

The following must never happen merely because CI or release-candidate validation passes:

- automatic version bumping;
- automatic tag creation;
- automatic GitHub Release publication without an explicitly created release tag;
- automatic PyPI publication;
- production-readiness claims;
- removal of documented limitations.

## Current distribution state

- Public source repository: authorized.
- Source hardening candidate: `0.2.1`.
- Release-candidate validation for `0.2.1`: pending merge and exact-candidate execution.
- Git tag `v0.2.1`: not yet authorized for creation by this technical preparation step.
- GitHub Release `v0.2.1`: not yet authorized for publication by this technical preparation step.
- PyPI publication: not authorized.
- Project maturity: pre-alpha.
