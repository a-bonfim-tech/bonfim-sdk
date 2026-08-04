# Architecture

Bonfim SDK provides dependency-light local infrastructure for governed Frameworks, Skills, Agents and Automations. It validates component declarations, controls execution, preserves traceability and returns structured outputs that remain subject to human review.

The SDK does not deploy workloads, schedule persistent jobs, provide remote connectors or confer institutional authority.

## Component model

| Component | Domain extension point | SDK-owned infrastructure |
|---|---|---|
| Framework | definition or specification | JSON loading, validation, registration and dependency ordering |
| Skill | `perform(context)` | input validation, provenance, quality gates, output inspection and result serialization |
| Agent | `select_skills(inputs)` | explicit allowlisting, bounded parallel or sequential execution and deterministic aggregation |
| Automation | workflow-step `execute()` and optional `rollback()` | trigger validation, bounded retry, reverse rollback and observations |

## Execution flow

```text
Caller input
    │
    ▼
Declaration and input validation
    │
    ├── invalid ──► structured failed result
    │
    ▼
Bounded domain execution
    │
    ├── expected failure ──► classified failure
    ├── unexpected failure ──► details withheld
    │
    ▼
Sensitive-output inspection
    │
    ├── suspected secret ──► publication blocked
    │
    ▼
Quality gates and traceability
    │
    ▼
Serializable result requiring human review
```

## Registration and discovery

Valid component subclasses register when their defining module is explicitly imported. This is registration, not arbitrary discovery.

External packages are loaded only through an explicit call such as:

```python
skill_registry.discover("bonfim.skills", allowlist=("approved-package-skill",))
```

The baseline does not walk directories, evaluate source strings or silently import every installed entry point.

## Failure model

- Validation failures stop before domain behavior.
- Expected Skill failures use classified failure records.
- Unexpected exception messages are withheld.
- Agent partial results remain visible and preserve declared Skill order.
- Agent selection is limited to declared identifiers.
- Agent worker count is bounded.
- Automation retries are bounded.
- Rollback receives the exact input mapping used by the completed step.
- Missing and failed rollback operations remain visible as limitations.
- No result represents approval, certification or external-action authority.

## Data model

Inputs and provenance mappings are copied into read-only views. Shared dataclasses model evidence, findings, risks, limitations, recommendations, decisions, observations, requirements and traceability.

Skills return `SkillResult`; Agents, Automations and Framework operations return `OutputContract`. Both are serializable and state that a human decision remains required.

## Trust boundaries

Imported component code runs in the same Python process and with the same operating-system privileges as the host. Registries constrain identity and discovery; they do not provide isolation.

See [Threat Model](threat-model.md) and [Security Model](security.md) for the complete boundary analysis.

## Architectural decisions

| Decision | Benefit | Residual risk |
|---|---|---|
| Standard-library-only runtime | Small dependency and supply-chain surface | Some integrations require downstream adapters |
| In-process component execution | Simple extension and low overhead | Untrusted code can compromise the host process |
| Explicit imports and allowlisted entry points | Predictable plugin loading | Package authenticity is not independently established |
| Immutable top-level inputs | Reduces accidental mutation | Nested mutable values are not recursively frozen |
| Bounded thread parallelism | Controlled concurrency and deterministic aggregation | Components share memory and process state |
| Pattern-based secret blocking | Reduces common accidental disclosures | It is not a complete DLP or taint-analysis control |
| Observable rollback | Makes compensation attempts auditable | External effects may not be reversible |
| Human-review output contract | Prevents silent authority claims | Consumers can still misuse results outside the SDK |

## Compatibility

Version 0.2 adapts pre-0.2 Skill subclasses that implemented `run(context)` by moving that method to the domain execution hook at class creation. The public `run(inputs)` method executes the complete governed pipeline.

Compatibility and removal rules are defined in [DEPRECATION.md](../DEPRECATION.md).
