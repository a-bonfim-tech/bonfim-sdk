# BSD-001 Architecture

## Document control

| Field | Value |
|---|---|
| Identifier | `BSD-ARCH-001` |
| Knowledge category | Category C — Architectural Proposals |
| Evidence level | Level D — Internal Proposal or Convention |
| Approval status | Proposta |
| Artifact state | Implementado |
| Origin | Founder instruction dated 2026-07-15 |
| Version | 0.2.0 |

## Boundaries

`bonfim-sdk` owns developer-facing abstractions and dependency-free local execution. `bonfim-engineering-runtime` remains the higher-level runtime/integration boundary. The SDK does not deploy workloads, schedule jobs, provide connectors or confer framework authority.

## Component model

| Component | Domain method | Shared infrastructure |
|---|---|---|
| Framework | definition/specification | JSON load, validation, registration, dependency ordering |
| Skill | `perform(context)` | input validation, provenance, quality gates, security, result serialization |
| Agent | `select_skills(inputs)` | bounded parallel/sequential execution and deterministic aggregation |
| Automation | workflow step `execute()`/optional `rollback()` | trigger validation, retry, reverse rollback and observations |

## Registration and discovery

Valid component subclasses are registered when their defining module is imported. This is automatic registration, not arbitrary discovery. External packages require an explicit `discover(group, allowlist=...)` call. No directory walking, `eval`, string execution or silent import of every installed entry point is permitted.

## Failure model

- Validation failures stop before domain execution.
- Expected Skill failures use classified `SkillExecutionError` records.
- Unexpected exception messages are withheld.
- Agent partial results remain visible; aggregation order follows the declared Skill order.
- Automation retry count is bounded to five; rollback runs only for completed steps and reports missing/failed rollback operations.
- No result represents institutional approval.

## Compatibility

SDK 0.2 adapts pre-0.2 subclasses that implemented `run(context)` by moving that method to the domain execution hook at class creation. The public `run(inputs)` method therefore executes the complete pipeline while `execute(inputs)` remains supported for downstream Agents.
