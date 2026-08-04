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
11. SHA-256 checksum generation and verification;
12. clean-environment installation and CLI smoke testing;
13. build-provenance attestation for public `main` artifacts.

## Release-candidate workflow

The manual release-candidate workflow validates an exact source ref and preserves artifacts. It does not create a tag, GitHub Release or package-registry publication.

The operator must provide the expected version. The workflow fails when the value does not match both `pyproject.toml` and `bonfim.__version__`.

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
- automatic GitHub Release publication;
- automatic PyPI publication;
- production-readiness claims;
- removal of documented limitations.

## Current distribution state

- Public source repository: authorized.
- Git tag for version 0.2.0: not authorized by this policy.
- GitHub Release: not authorized by this policy.
- PyPI publication: not authorized by this policy.
- Project maturity: pre-alpha.
