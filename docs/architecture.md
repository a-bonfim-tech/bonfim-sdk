# Bonfim SDK Architecture

## Document control

| Field | Value |
|---|---|
| Identifier | SDK-ARCH-001 |
| Knowledge category | Category C — Architectural Proposals |
| Evidence level | Level D — Internal Proposal or Convention |
| Approval status | Proposta |
| Origin | Founder instruction dated 2026-07-14 |
| Justification | Provide reusable infrastructure for new Bonfim Labs Skills |
| Version | 0.1.0 |

## Objective

Allow a developer to create a new Skill by importing `Skill`, declaring the
specialization, and implementing `run()` without recreating common execution,
governance, evidence, failure, security, registry, or output infrastructure.

## Architecture

```text
BL-SOF-001 v2.0.0 (approved internal framework)
                       |
                     Skill
             +---------+---------+
             |                   |
     Skill specialization   Shared pipeline
          run() only         validation
                             provenance
                             security
                             quality gates
                             output contract
                             failure handling
                                    |
                         SkillRegistry / SkillRunner
```

## Execution flow

1. Resolve a Skill through the explicit registry or instantiate it directly.
2. Build immutable input context and provenance.
3. Validate Skill declaration, semantic version, activation, and required input.
4. Execute only the specialization's `run()` method.
5. Reject outputs that do not implement `SkillOutput`.
6. Block outputs containing likely credentials, tokens, keys, or secrets.
7. Evaluate explicit SOF quality gates.
8. Return `SkillResult` with all universal output sections.

## Dependencies

- Python 3.11 or newer.
- Python standard library at runtime.
- `setuptools` only for package construction.
- No dependency on `bonfim-engineering-runtime`; `Skill.__call__` provides a
  serialization-friendly adapter for callable registries.

## Security implications

- Skill registration is explicit; there is no dynamic import or string evaluation.
- Registered Skill code is trusted in-process code and is not sandboxed.
- Unexpected exception details are withheld from results.
- Inputs are not reproduced automatically; only input field names are recorded.
- Output scanning is defense in depth and cannot guarantee detection of every secret.
- Skills cannot emit institutional approval; every serialized result states that a
  human decision is required.

## Trade-offs

| Option | Advantages | Risks | Complexity | Cost |
|---|---|---|---|---|
| Inheritance with template method | Minimal subclass code; consistent controls | Python subclasses can intentionally bypass conventions | Low | Low |
| Explicit registry | Auditable and deterministic | Manual registration required | Low | Low |
| Automatic plugin discovery | Less wiring for large ecosystems | Supply-chain and import-time execution risk | Medium | Medium |
| Out-of-process sandbox | Stronger isolation | IPC, deployment and observability overhead | High | High |

The implemented baseline uses inheritance plus explicit registration. A
sandbox boundary should be introduced before running untrusted third-party
Skills.
