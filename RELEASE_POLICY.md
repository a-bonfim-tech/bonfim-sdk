# Release Policy

Bonfim SDK is public source software in pre-alpha status. Source visibility, candidate readiness, release authorization, release tagging, GitHub Release publication and package-registry distribution are separate decisions.

## Release authority

Only the repository owner may authorize:

- a version change;
- a release-candidate build;
- approval of the BQA/BRE publication gates;
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
- frozen release notes and migration impact;
- the licensing and attribution state;
- the distribution scope;
- the explicit owner authorization required for publication.

## Mandatory technical gates

Before a release decision, the exact candidate must pass:

1. tests on Python 3.11, 3.12, 3.13 and 3.14;
2. branch-aware coverage of at least 90%;
3. Ruff linting;
4. mypy strict;
5. deterministic formatting verification;
6. Bandit at the configured blocking threshold;
7. full-history Gitleaks scanning;
8. runtime-license and distributed-license verification;
9. a conservative registry performance regression baseline;
10. CycloneDX SBOM generation;
11. wheel and source-distribution build;
12. `twine check`;
13. package-content and metadata verification;
14. SHA-256 checksum generation and verification over release distributions and evidence assets;
15. clean-environment installation and CLI smoke testing;
16. BQA/BRE **candidate-readiness** validation;
17. build-provenance attestation for the final candidate asset checksum set.

## Candidate readiness versus publication authorization

Candidate validation and publication authorization are intentionally separate gates.

`BQA --mode candidate` and `BRE --mode candidate` answer only whether the exact source and generated evidence are technically ready for human release review. They do **not** approve publication and they do not alter the owner-controlled release fields in the repository manifests.

After a candidate passes, the owner reviews the evidence and may make a separate publication decision. Only after that decision is retained may `BQA --mode release` and `BRE --mode release` pass.

This ordering prevents circular authority: technical evidence must be complete before the human is asked to authorize publication.

## Release-candidate workflow

The manual release-candidate workflow validates an exact source ref and preserves artifacts. It does not create a tag, GitHub Release or package-registry publication.

The operator must provide the expected version. The workflow fails when the value does not match `VERSION`, `pyproject.toml`, `bonfim.__version__`, the corresponding `CHANGELOG.md` section and frozen version-specific release notes.

The exact candidate is tested on Python 3.11, 3.12, 3.13 and 3.14. Technical evidence, distributions, SBOM, checksums and candidate provenance are generated before BRE candidate-readiness is evaluated.

## GitHub Release workflow

An explicitly created annotated `vMAJOR.MINOR.PATCH` tag is the human release trigger. The tag workflow must fail closed unless the tag points to the exact protected `main` HEAD and all source version declarations and changelog metadata agree.

The final GitHub Release workflow repeats the release compatibility matrix and technical assurance gates, generates the release artifacts, then requires the retained BQA/BRE **release authorization** state before publication. It produces provenance attestation and attaches the verified release artifacts to the GitHub Release.

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
- candidate BQA/BRE evidence;
- whether public distribution is appropriate.

## Prohibited implicit actions

The following must never happen merely because CI or release-candidate validation passes:

- automatic version bumping;
- automatic approval of BQA/BRE publication fields;
- automatic tag creation;
- automatic GitHub Release publication without an explicitly created release tag;
- automatic PyPI publication;
- production-readiness claims;
- removal of documented limitations.

## Current distribution state

- Public source repository: authorized.
- Source hardening candidate: `0.2.1`.
- Exact release-candidate validation for `0.2.1`: passed for commit `1dc0ecbe34428d482e06856b00253bb453e37432` in workflow run `31638386310`.
- Human BQA/BRE publication approval: approved by the repository owner for GitHub Release `v0.2.1`.
- Git tag `v0.2.1`: authorized; not yet created.
- GitHub Release `v0.2.1`: authorized; not yet published.
- PyPI publication: not authorized.
- Project maturity: pre-alpha.
