# Interfaces and Shared Models

## Interfaces

Every Framework, Skill, Agent and Automation implements:

| Interface | Contract |
|---|---|
| `Executable` | Execute through a governed pipeline |
| `Validatable` | Return declaration errors without external state change |
| `Traceable` | Produce component/execution identity |
| `Governable` | Expose classification, evidence level, approval status and origin |
| `Versionable` | Enforce Semantic Versioning |
| `Documentable` | Return machine-readable component documentation |

## Shared models

| Model | Purpose |
|---|---|
| `Finding` | Evidence-backed issue or noteworthy conclusion |
| `Evidence` | Observed artifact with origin, validation and confidence |
| `Risk` | Uncertainty/event and its likelihood, impact, treatment and owner |
| `Limitation` | Explicit boundary affecting interpretation |
| `Recommendation` | Proposed next action with priority and rationale |
| `Decision` | Human decision state and rationale |
| `Confidence` | `High`, `Medium`, `Low` or `Unknown` |
| `Traceability` | Component, version, execution and parent/requirement relationships |
| `Requirement` | Source-linked expected outcome |
| `Observation` | Timestamped runtime observation |
| `OutputContract` | Ecosystem-wide serializable result envelope |

Models are immutable dataclasses. Mapping fields are copied into read-only views, and `to_dict()` produces JSON-compatible values.

`SkillResult` remains available as a compatibility-specific universal Skill result. Agents and Automations use `OutputContract`; future migration may unify them after downstream compatibility review.
