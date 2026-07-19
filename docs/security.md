# BSD-001 Security Model

## Trust boundary

Imported component code is trusted in-process Python. Registries constrain identity and discovery but do not provide isolation. A malicious component has the host process privileges.

## Implemented controls

- Explicit imports and allowlisted package entry points.
- Semantic-version and declaration validation.
- Immutable top-level inputs, provenance and shared model mappings.
- Bounded Agent worker count and deterministic result order.
- Bounded Automation retries and observable rollback attempts.
- Secret-like output inspection without reproducing flagged values.
- Withheld unexpected exception details.
- Human decision and no-external-authority statements.
- Bandit SAST fails CI on high-severity, high-confidence findings in `src`.
- Gitleaks 8.30.1 scans the complete Git history and current content in CI.
- Syft 1.48.0 generates a CycloneDX JSON SBOM and preserves it as a workflow artifact.

## CI security gates

| Control | Tool | Failure policy | Evidence |
|---|---|---|---|
| SAST | Bandit 1.9.4 | Fail on high-severity and high-confidence findings | Quality job log |
| Secret scanning | Gitleaks 8.30.1 | Fail when a recognized secret is detected in current or historical content | Dedicated job log and redacted SARIF on findings |
| SBOM | Syft 1.48.0 | Fail when CycloneDX JSON generation or artifact preservation fails | `bonfim-sdk.cdx.json` workflow artifact |

All external GitHub Actions are pinned to immutable commit SHAs. Passing these
controls reduces risk but does not establish vulnerability absence, supply-chain
integrity, license compliance, or production authorization.

## Missing production gates

- Signed component packages and publisher verification.
- Process/container sandbox and resource quotas.
- Capability tokens and connector-specific authorization.
- Durable append-only execution logs and evidence storage.
- Cancellation, deadlines and distributed rate limiting.
- Approved retention, privacy-impact and incident-response procedures.

Until these gates exist, run the SDK locally with authorized components and synthetic or explicitly permitted data only.
