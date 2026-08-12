# Threat Model

## Scope

This threat model covers the Bonfim SDK package, CLI, registries, governed component execution, generated outputs and GitHub-based development and release pipeline.

It does not cover applications that embed the SDK, external connectors, cloud infrastructure, model providers or third-party components beyond the boundaries explicitly described here.

## Assets

- caller-supplied inputs;
- provenance and traceability metadata;
- evidence, findings, risks and decisions;
- component identifiers and registry integrity;
- package source and release artifacts;
- CI evidence, SBOMs, checksums, attestations and security-scan results;
- developer workstations and GitHub credentials.

## Trust boundaries

### 1. Caller to SDK

Inputs may be malformed, oversized, misleading or contain sensitive information. The SDK validates top-level contracts but domain components remain responsible for semantic validation.

### 2. SDK to component code

Imported component code executes in-process with the privileges of the host Python process. Components are trusted code. Registries constrain identifiers and discovery but do not isolate execution.

### 3. Package entry-point discovery

Installed packages may expose entry points. Discovery is opt-in and requires an explicit allowlist, but package authenticity and publisher identity are not cryptographically verified by the SDK.

### 4. Component output to caller

Outputs may accidentally contain credentials, tokens, keys or sensitive data. The SDK applies pattern-based inspection and blocks recognized secret-like output. This is a defense-in-depth control, not a complete DLP system.

### 5. Repository to CI and release pipeline

GitHub Actions, development dependencies, package registries and release artifacts are supply-chain boundaries. Actions are pinned to immutable commit SHAs; verification tooling is pinned to controlled versions; CI generates SBOM and checksum evidence; public distribution artifacts receive provenance attestation. A compromised upstream dependency, package registry, Action publisher or maintainer credential remains a residual risk.

### 6. Release artifact to consumer

The repository can publish hashes, SBOM and provenance evidence, but consumers are responsible for verifying them. The SDK does not force downstream environments to validate GitHub attestations or package origin before installation.

## Threat actors

- a developer who accidentally passes or returns sensitive data;
- a malicious or compromised third-party component author;
- an attacker who controls malformed component inputs;
- a compromised development dependency, package registry or GitHub Action;
- an unauthorized publisher attempting to create a release;
- a reviewer who mistakes a generated result for an approved decision;
- a consumer who installs an unverified artifact or bypasses documented trust boundaries.

## Primary threats and controls

| Threat | Existing control | Residual risk |
|---|---|---|
| Secret disclosure in output | Recursive key and value-pattern inspection; fail-closed result | Encoded, fragmented or novel secret formats may evade detection |
| Arbitrary untrusted component execution | Explicit imports; allowlisted entry points; documented trust boundary | No sandbox, process isolation or capability restriction |
| Registry collision or substitution | Stable identifiers; duplicate protection; validation before registration | Authorized replacement remains possible when explicitly requested |
| Dependency-cycle denial of service | Framework cycle detection | Extremely large dependency graphs may still consume resources |
| Excessive Agent concurrency | Worker count constrained to 1–8 | In-process components may still consume CPU, memory or shared state |
| Unbounded retry loop | Automation retries constrained to 0–5 | Individual workflow steps may block without external timeout control |
| Exception-detail leakage | Unexpected exception details withheld | Domain components may place sensitive data in normal output fields |
| False authority or compliance claim | Human-review status, limitations and decision statements | Integrators may ignore or remove the statements |
| Supply-chain compromise | Pinned Actions, controlled tool versions, Gitleaks, Bandit, CodeQL policy, CycloneDX SBOM, SHA-256 release checksums and build provenance attestation | Builds are not hermetic/offline; upstream registries remain dependencies; consumer verification is not enforced |
| Unauthorized release | Protected `main`, required CI/CodeQL rulesets, release policy, annotated-tag requirement, exact-main tag binding and release environment | Repository administration or credential compromise can still alter settings or workflows |
| Artifact substitution after release | Immutable tag/release policy, release checksums and provenance attestation | Consumers may fail to verify hashes or attestation before installation |
| Path or file abuse through CLI input | JSON-only input, 1 MB file limit, explicit path | Caller can read any locally accessible file they already have permission to read |

## Security invariants

The following properties are intended to hold:

1. A component with an invalid declaration does not execute domain behavior.
2. Missing required inputs produce a structured failure result.
3. Unexpected exceptions do not expose exception messages to the caller.
4. Recognized secret-like output is blocked before a successful result is returned.
5. Agents cannot select undeclared Skills.
6. Agent execution remains bounded by a configured worker limit.
7. Automation retries remain bounded.
8. Rollback attempts and failures remain observable.
9. Framework dependency cycles are rejected.
10. Generated results retain an explicit human-decision requirement.
11. A release tag must not bypass version, compatibility, security, packaging and evidence gates.
12. PyPI or another registry publication must not occur implicitly from GitHub Release publication.

## Abuse cases requiring additional controls

The SDK is not suitable, without additional isolation, for:

- executing untrusted plugins;
- processing high-sensitivity secrets or regulated production data;
- autonomous infrastructure mutation;
- safety-critical or legally binding decision making;
- multi-tenant execution in a shared process;
- long-running remote workflows requiring cancellation and durable state.

## Future security gates

- process or container isolation for untrusted or semi-trusted component execution;
- resource quotas and execution deadlines;
- signed package and publisher verification enforced by the runtime or consumer policy;
- capability-based connector permissions;
- durable append-only audit logs;
- hermetic or otherwise stronger reproducible build controls;
- automated license and vulnerability policy enforcement at release time;
- structured data classification and stronger output DLP;
- cancellation and distributed rate limiting;
- independent external security review.

## Review rule

A passing CI or release-candidate run reduces known implementation and supply-chain risk but does not prove vulnerability absence, production readiness, compliance or authorization. GitHub Release publication and package-registry publication remain separate human decisions.
