# Publication Review Checklist

This checklist separates technical readiness from the repository owner's publication decision. Completion of automated checks does not authorize visibility changes, merge, tagging, release or package publication.

## Exact candidate

- [ ] Record the final candidate commit SHA.
- [ ] Review every changed file against `main`.
- [ ] Confirm that no unreviewed commit was added after CI completed.
- [ ] Confirm that the candidate is still private.

## Security

- [ ] All mandatory CI jobs passed on the exact candidate.
- [ ] Full-history Gitleaks scan passed.
- [ ] Bandit passed with the documented threshold.
- [ ] Threat model matches the implementation.
- [ ] No credential, token, private key, personal data or confidential artifact is present.
- [ ] Imported-component and in-process execution risks are presented prominently.
- [ ] Security reporting instructions are appropriate for a public repository.

## Legal, authorship and privacy

- [ ] Apache-2.0 license text is correct.
- [ ] `NOTICE` accurately describes copyright and trademark boundaries.
- [ ] All code and documentation are owned by or licensed to the publisher.
- [ ] Third-party Actions and tools are attributed through their repository configuration and licenses.
- [ ] No Panos.AI, employer, customer or internship material is included.
- [ ] No private governance record, personal identifier or proprietary strategy is exposed unintentionally.

## Product and recruiter presentation

- [ ] README is accurate, concise and free of unsupported claims.
- [ ] The project is clearly labeled pre-alpha.
- [ ] The ten-minute review path is technically accurate.
- [ ] Commands are copy-safe and reproducible.
- [ ] Limitations are not hidden by promotional language.
- [ ] The repository demonstrates the intended skills without overstating production maturity.

## Package and release

- [ ] Wheel and sdist pass `twine check`.
- [ ] Wheel contains `LICENSE`, `NOTICE`, templates and `py.typed`.
- [ ] SHA-256 checksums were generated and verified.
- [ ] Clean-environment installation succeeded.
- [ ] Installed CLI smoke tests succeeded.
- [ ] CycloneDX SBOM was generated for the exact candidate.
- [ ] Release notes and migration implications are reviewed.
- [ ] Package publication remains separately authorized.

## Owner decisions

These decisions must be explicit and separate:

- [ ] Approve the exact diff for merge.
- [ ] Approve repository visibility change.
- [ ] Approve creation of a release tag.
- [ ] Approve GitHub Release publication.
- [ ] Approve package-registry publication, if any.
- [ ] Approve pinning the repository on the public GitHub profile.

## Current decision

**Not authorized for public release until the repository owner completes this checklist and issues an explicit publication instruction.**
