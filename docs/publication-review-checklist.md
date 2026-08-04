# Publication Review Checklist

This checklist separates completed source-publication decisions from release and package-distribution decisions that remain unauthorized.

## Exact candidate

- [x] Record the final candidate commit SHA.
- [x] Review every changed file against `main`.
- [x] Confirm that no unreviewed commit was added after CI completed.
- [x] Record the public `main` integration commit.

Validated candidate: `c0d4c74c302c854b9e4bd628c7ebd0d4ef33ca5e`  
Final candidate CI run: `30951318722`  
Public `main` integration: `4783513fb8b875848ac9aafb40a506b477891755`

## Security

- [x] All mandatory CI jobs passed on the exact candidate.
- [x] Full-history Gitleaks scan passed.
- [x] Bandit passed with the documented threshold.
- [x] Threat model matches the implementation.
- [x] No credential, token, private key, personal data or confidential artifact was identified by the publication review and automated controls.
- [x] Imported-component and in-process execution risks are presented prominently.
- [x] Security reporting instructions are appropriate for a public repository.

## Legal, authorship and privacy

- [x] Apache-2.0 license text is present.
- [x] `NOTICE` records copyright and trademark boundaries.
- [x] Copyright attribution identifies André Luiz Vieira Bonfim.
- [x] No Panos.AI, employer, customer or internship material was identified in the publication candidate.
- [x] No private governance record, personal identifier or proprietary strategy was identified as unintentionally exposed.

The owner authorized source publication and Apache-2.0 licensing. No independent legal opinion or certification is represented by this checklist.

## Product and recruiter presentation

- [x] README is accurate, concise and free of unsupported production claims.
- [x] The project is clearly labeled pre-alpha.
- [x] The ten-minute review path is technically accurate.
- [x] Commands are copy-safe and reproducible.
- [x] Limitations are not hidden by promotional language.
- [x] The repository demonstrates the intended skills without overstating production maturity.

## Package and release evidence

- [x] Wheel and sdist pass `twine check`.
- [x] Wheel contains `LICENSE`, `NOTICE`, templates and `py.typed`.
- [x] SHA-256 checksums were generated and verified.
- [x] Clean-environment installation succeeded.
- [x] Installed CLI smoke tests succeeded.
- [x] CycloneDX SBOM was generated for the exact candidate.
- [x] Public `main` workflow includes build provenance attestation for distribution checksums.

## Owner decisions

- [x] Approve the exact candidate for merge.
- [x] Approve repository source visibility change.
- [x] Approve Apache-2.0 source licensing and copyright attribution.
- [ ] Approve creation of a release tag.
- [ ] Approve GitHub Release publication.
- [ ] Approve package-registry publication.
- [ ] Approve pinning the repository on the public GitHub profile.

## Current decision

**Public source publication completed on 2026-08-04.**

Release tags, GitHub Releases, package-registry publication and profile pinning remain separate, unauthorized decisions.
