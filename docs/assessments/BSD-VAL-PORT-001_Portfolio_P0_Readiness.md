# BSD-VAL-PORT-001 — Portfolio P0 Readiness Assessment

## Control

| Field | Value |
|---|---|
| Knowledge category | Category C — Architectural Proposals |
| Evidence level | Level D — Internal Proposal or Convention |
| Assessment status | Implementado |
| Publication recommendation | Proposta |
| Date | 2026-07-15 |
| Origin | Founder-requested portfolio readiness audit and direct local validation |
| Justification | Record cleanup and reproducibility evidence without treating implementation as publication approval or production readiness |

## Scope

This assessment covers the current `bonfim-sdk` working tree, its existing Git
history, the Python 0.2.0 implementation, tests, quality checks, security scan,
dependency metadata, and release-governance evidence.

## Controlled cleanup record

The following untracked local artifacts were removed after comparison with the
canonical paths. The suffixed files were older divergent copies; their SHA-256
hashes preserve an auditable identification record. No content was merged from
them because the canonical files contained the current 0.2.0 implementation.

| Removed artifact | SHA-256 | Canonical path |
|---|---|---|
| `README 2.md` | `7863db3301c8654cc12f8788323b69a05bc8e5e0eb090d125858c2403e67c10e` | `README.md` |
| `docs/architecture 2.md` | `c3c4f9dc698685a01f54cfe4adcec5b59d80d437808510a016041d68fba814a3` | `docs/architecture.md` |
| `docs/traceability 2.md` | `21d917fe859ab97b4e61cdfa2822c0dfe92849302e6492a206669e1b32fb77a8` | `docs/traceability.md` |
| `src/bonfim/registry 2.py` | `bc13943374f4a9dfce252df19474a63b6077faad0f9b3d3e4aef0a690b4f2808` | `src/bonfim/registry.py` |
| `.coverage` | Generated SQLite coverage database; intentionally not retained | `.gitignore` already excludes `.coverage` |

## Validation evidence

| Check | Result | Evidence and limitations |
|---|---|---|
| Source/example/test compilation | Pass | Python 3.14.6 `compileall` completed without error |
| Unit/contract/integration baseline | Pass | 51 tests passed, 0 failed |
| Branch coverage | Pass | 93%, threshold 90% |
| Ruff | Pass | 0 findings across source, tests, and examples |
| mypy strict | Pass | 0 issues across 27 source files |
| Clean-copy reproducibility | Pass | The same 51 tests, 93% coverage, Ruff, and mypy passed from `/tmp/bonfim-sdk-p0-clean` with caches, `.git`, `.venv`, build output, and duplicate artifacts excluded |
| Full Git-history secret scan | Pass | Gitleaks 8.30.1 scanned the existing commit and approximately 51.14 KB; no leaks found |
| Current-directory secret scan | Pass | Gitleaks 8.30.1 scanned approximately 12.87 MB, including the isolated environment; no leaks found |
| Runtime dependencies | Pass | No third-party runtime dependency declared |
| Development dependency licenses | Pass with limitation | Coverage: Apache-2.0; mypy, mypy-extensions and Ruff: MIT; typing-extensions: PSF-2.0; pathspec: MPL-2.0. This is a metadata review, not legal advice |
| Repository license | Pass with legal-review limitation | Founder approved Apache-2.0 in `BL-DEC-LIC-001`; the official license text, `NOTICE`, package metadata, and built-wheel contents were verified |
| BQA baseline | Requires Revision | SAST, SBOM, and secret scanning are configured; performance, formatting, automated license verification, approval, and human review remain open |
| BRE baseline | Requires Revision | Checksums, compatibility policy, evidence package, migration guide, release notes, SBOM, approval, human review, and public-release authorization remain open |
| GitHub state and CI | Not verified | No `origin` remote is configured and available GitHub CLI authentication was invalid |

## P0 decision

**Result: Cleanup and local quality validation passed; repository publication P0
remains blocked.**

The implementation is locally reproducible and has strong test, coverage, lint,
typing, and secret-scan evidence. Publication remains blocked by:

1. uncommitted candidate content and lack of an intentional candidate commit;
2. no configured remote or verified live CI;
3. BQA/BRE security, supply-chain, release, and human-review gaps;
4. pending full legal/IP and public-disclosure review;
5. pending Founder approval of the exact publication scope.

No commit, publication, push, remote mutation, approval, or release authorization
was performed by this assessment.

## Security-control implementation update

On 2026-07-15, the candidate CI was extended with:

- Bandit 1.9.4 SAST configured to fail on high-severity, high-confidence findings;
- Gitleaks Action v3 pinned to commit
  `e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e`, using Gitleaks 8.30.1 and a
  complete-history checkout;
- Anchore SBOM Action v0.24.0 pinned to commit
  `e22c389904149dbc22b58101806040fa8d37a610`, using Syft 1.48.0 and
  CycloneDX JSON output retained for 30 days.

Local Gitleaks execution passed. Bandit 1.9.4 executed against `src` with the
CI blocking thresholds and returned no high-severity, high-confidence finding.
Syft 1.48.0 generated `artifacts/bonfim-sdk.cdx.json` from a cache-free copy;
the document is valid CycloneDX 1.7, identifies `bonfim-sdk`, and contains eight
components. Remote CI execution remains required to confirm the hosted-runner
path and artifact retention behavior.
