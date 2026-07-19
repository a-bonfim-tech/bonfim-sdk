# BSD-COMMIT-PLAN-001 — Candidate Commit Plan

## Control

| Field | Value |
|---|---|
| Knowledge category | Category C — Architectural Proposals |
| Evidence level | Level D — Internal Proposal or Convention |
| Status | Proposta |
| Date | 2026-07-15 |
| Origin | Founder-authorized portfolio P0 execution |
| Justification | Prepare reviewable, reversible commit boundaries without overwriting the pre-existing mixed staging state |

## Constraint

The SDK worktree already contains staged, unstaged, added, renamed, and
untracked work from the 0.2.0 implementation. This plan does not run `git reset`,
rewrite history, or replace the current index. Files containing concerns from
more than one candidate require interactive hunk staging and human diff review.

## Candidate 1 — SDK implementation baseline

**Proposed message:** `feat(sdk): establish governed 0.2 component platform`

Primary scope:

- `src/bonfim/**`
- `tests/**`
- `examples/**`
- `templates/**`
- `docs/architecture.md`
- `docs/cli-and-templates.md`
- `docs/interfaces-and-models.md`
- `docs/traceability.md`
- functional and packaging portions of `README.md` and `pyproject.toml`
- `VERSION`

Acceptance evidence:

- 51 tests pass;
- 93% branch coverage;
- Ruff passes;
- mypy strict passes for 27 source files;
- clean-copy execution passes.

## Candidate 2 — CI security and release evidence

**Proposed message:** `ci(security): enforce SAST secret scanning and SBOM`

Primary scope:

- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `.github/dependabot.yml`
- `quality/**`
- `release/**`
- `tools/**`
- `artifacts/bqa-evidence.json`
- `artifacts/bre-evidence.json`
- `docs/security.md`
- security/release portions of `RELEASING.md`, `CHANGELOG.md`, and
  `pyproject.toml`

Acceptance evidence:

- workflow YAML parses locally;
- every external Action is pinned to a full commit SHA;
- Gitleaks 8.30.1 passes locally for current and historical content;
- BQA removes SAST, SBOM, and secret-detection from its configured-control gaps;
- Bandit 1.9.4 passes locally at the blocking thresholds;
- Syft 1.48.0 produces a valid CycloneDX 1.7 SBOM from a cache-free source copy;
- hosted-runner execution and artifact retention remain mandatory evidence from
  the first remote candidate CI run.

## Candidate 3 — Apache-2.0 licensing

**Proposed message:** `chore(license): adopt Apache-2.0 for bonfim-sdk`

Primary scope:

- `LICENSE`
- `NOTICE`
- licensing portions of `README.md` and `pyproject.toml`
- licensing entry in `CHANGELOG.md`
- `docs/assessments/BSD-VAL-PORT-001_Portfolio_P0_Readiness.md`

Acceptance evidence:

- wheel metadata declares `License-Expression: Apache-2.0`;
- built wheel contains `LICENSE` and `NOTICE`;
- official Apache-2.0 text is preserved;
- `BL-DEC-LIC-001` records the Founder-approved strategy.

## Candidate 4 — Audit and portfolio traceability

**Proposed message:** `docs(portfolio): record sdk P0 readiness evidence`

Primary scope:

- `docs/assessments/BSD-VAL-PORT-001_Portfolio_P0_Readiness.md`
- `docs/assessments/BSD-COMMIT-PLAN-001_Candidate_Commits.md`

This candidate may be folded into Candidate 2 or 3 after human review if the
result remains coherent and independently reversible.

## Separate Decivra candidate

The `decivra` repository must use its own commit:

**Proposed message:** `chore(license): formalize proprietary portfolio terms`

Scope:

- `LICENSE`
- `README.md`

Acceptance evidence: 14 tests pass from a clean copy, Gitleaks reports no
finding, and `BL-DEC-LIC-001` preserves the decision origin.

## Required review before commit creation

1. Inspect every staged and unstaged hunk against the intended candidate.
2. Confirm no user-owned unrelated change is included.
3. Re-run the acceptance evidence after each candidate index is assembled.
4. Record Bandit and SBOM as `Not Verified` until remote CI executes them.
5. Do not push, publish, tag, or create a release without separate authorization.

## Execution decision — 2026-07-19

The SDK candidates are consolidated into one local commit because the inherited
index already mixed staged and unstaged hunks across `README.md`,
`pyproject.toml`, workflows, implementation, release evidence, and governance
documents. Artificially splitting those shared files after the fact would create
intermediate commits with inconsistent metadata or unverifiable gates.

**Executed candidate message:**
`feat(sdk): establish governed 0.2 platform baseline`

The separate Decivra license candidate remains an independent commit in its own
repository. Consolidation does not authorize push, publication, tagging, or
release.
