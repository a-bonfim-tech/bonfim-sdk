# Ten-Minute Technical Review Path

This path lets a recruiter, security engineer or hiring manager assess the project without reading the entire repository.

## Minute 0–2: Product and scope

Read:

- `README.md`
- `docs/threat-model.md` — trust boundaries and unsupported use

Confirm that the project is a pre-alpha Python SDK, not a compliance product, autonomous authority or sandbox.

## Minute 2–4: Core implementation

Inspect:

- `src/bonfim/skill/base.py` — validation, execution, quality gates and fail-closed output
- `src/bonfim/agent/base.py` — explicit Skill selection, bounded concurrency and deterministic aggregation
- `src/bonfim/automation/base.py` — triggers, retries, rollback and monitored failure handling
- `src/bonfim/security.py` — secret-like output inspection

## Minute 4–6: Tests and failure boundaries

Inspect:

- `tests/test_publication_hardening.py`
- `tests/test_agent_automation.py`
- `tests/test_github_review_skills.py`

The important review question is not only whether success paths work, but whether malformed inputs, unexpected exceptions, failed rollback and sensitive output fail closed.

## Minute 6–8: Engineering and supply chain

Inspect:

- `.github/workflows/ci.yml`
- `pyproject.toml`
- `docs/security.md`

Look for strict typing, linting, coverage, SAST, full-history secret scanning, immutable Action references, SBOM generation, package build validation and clean-install smoke testing.

## Minute 8–10: Governance and trade-offs

Read:

- `docs/architecture.md`
- `docs/publication-readiness-scorecard.md`
- `DEPRECATION.md`
- `SECURITY.md`

Key trade-offs:

- in-process execution is simple but is not isolation;
- allowlisted plugin discovery limits accidental expansion but does not authenticate publishers;
- secret-pattern inspection reduces accidental disclosure but is not DLP;
- rollback is observable compensation, not proof that external effects were reversed;
- automated output always requires human review.

## Evidence summary

The final public candidate must provide passing evidence for the exact reviewed commit: tests on supported Python versions, ≥90% coverage, Ruff, mypy strict, Bandit, Gitleaks, CycloneDX SBOM, wheel/sdist validation, hashes and clean-install CLI smoke tests.
