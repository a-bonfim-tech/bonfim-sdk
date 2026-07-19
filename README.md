# Bonfim SDK — BSD-001

Reusable, governed Python infrastructure for Bonfim Frameworks, Skills, Agents and Automations.

> Category C — Architectural Proposals · Evidence Level D · Status: `Proposta` · Artifact state: `Implementado` · Origin: Founder instruction dated 2026-07-15.

Licensed under the [Apache License 2.0](LICENSE). Product names and marks remain
subject to the trademark limitation recorded in [NOTICE](NOTICE).

## Objective

BSD-001 turns the Engineering Runtime contracts into a developer platform. A component author implements domain behavior while the SDK supplies validation, execution, traceability, governance metadata, output construction, registration and classified failure handling.

```python
from bonfim import Skill, SkillContext, SkillOutput


class SecurityEvidenceCollector(Skill):
    skill_id = "SEC-EVD-001"
    name = "Security Evidence Collector"
    version = "0.1.0"
    mission = "Package authorized artifacts as evidence."
    scope = ("Evidence packaging",)
    out_of_scope = ("Certification", "Remediation")
    activation_conditions = ("Explicit evidence request",)
    required_inputs = ("artifacts",)

    def perform(self, context: SkillContext) -> SkillOutput:
        return self.output(
            f"Received {len(context.inputs['artifacts'])} artifact(s).",
            limitations=("Authenticity was not independently validated.",),
            confidence="Low",
            confidence_justification="Only caller-supplied artifacts were observed.",
            final_verdict="Review Required",
        )


collector = SecurityEvidenceCollector()
result = collector.run({"artifacts": ["test.log"]})
print(result.to_dict())
```

The author does not implement registry wiring, provenance degradation, quality gates, secret-output blocking, timestamps, safe failures or serialization.

## Architecture

```text
Developer component
       │
       ├── Framework ── load · validate · register · dependencies
       ├── Skill ────── validate · perform · findings · confidence · output
       ├── Agent ────── select Skills · bounded parallelism · aggregate
       └── Automation ─ trigger · workflow · retry · rollback · monitor
               │
               ▼
Executable · Validatable · Traceable · Governable · Versionable · Documentable
               │
               ▼
Shared models + central registries + security boundary + OutputContract
```

All base components implement the six formal interfaces. Imported valid subclasses register automatically. Installed package plugins are loaded only through an explicitly allowlisted entry-point discovery call.

## Dependencies

- Python 3.11 or newer.
- Python standard library only at runtime.
- `setuptools` for package construction.
- Optional pinned development tools: Coverage, Ruff and mypy.

No network service, database, dynamic filesystem scan or runtime dependency on `bonfim-engineering-runtime` is required.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
bonfim doctor
```

## Formal interfaces

- `Executable`
- `Validatable`
- `Traceable`
- `Governable`
- `Versionable`
- `Documentable`

## Shared models

`Finding`, `Evidence`, `Risk`, `Limitation`, `Recommendation`, `Decision`, `Confidence`, `Traceability`, `Requirement`, `Observation` and `OutputContract` are exported directly from `bonfim` and through `bonfim.schemas`.

## Central registries

```python
from bonfim import skill_registry

assert "SEC-EVD-001" in skill_registry.identifiers()
result = skill_registry.get("SEC-EVD-001").run({"artifacts": []})
```

Available registries:

- `SkillRegistry` / `skill_registry`
- `AgentRegistry` / `agent_registry`
- `AutomationRegistry` / `automation_registry`
- `FrameworkRegistry` / `framework_registry`

Entry-point discovery is opt-in and allowlisted:

```python
skill_registry.discover("bonfim.skills", allowlist=("approved-package-skill",))
```

## CLI

```bash
bonfim new skill SecurityEvidenceCollector --id SEC-EVD-001 --directory src/my_project
bonfim new agent EvidenceAgent --id AGENT-EVD-001
bonfim new automation EvidenceWorkflow --id AUT-EVD-001
bonfim validate --module my_project.skills
bonfim run SEC-EVD-001 --module my_project.skills --inputs '{"artifacts":[]}'
bonfim doctor
bonfim version
```

`new framework` and `new specification` are also supported. Creation is exclusive: the CLI refuses to overwrite an existing component file.

## Official templates

The canonical templates are in [`templates/`](templates/). Packaged copies drive the CLI so installed users receive the exact same contracts.

No component should begin outside these templates without an explicitly recorded exception and review.

## Reference implementations

- [`SecurityEvidenceCollector`](examples/security_evidence_collector.py)
- [`GitHubPRReadinessReviewer`](examples/github_pr_readiness_reviewer.py)
- [`SecurityComplianceReviewer`](examples/security_compliance_reviewer.py)
- [`GovernanceDocumentationGenerator`](examples/governance_documentation_generator.py)

All examples use caller-supplied or synthetic data, remain read-only and require human review.

## Execution flow

1. Import or explicitly load a component.
2. Validate its declaration, Semantic Versioning value and input contract.
3. Resolve it through the appropriate registry or instantiate it directly.
4. Create immutable context and traceability metadata.
5. Execute domain behavior in-process.
6. Reject non-contract or secret-like output.
7. Evaluate quality, evidence, confidence and limitations.
8. Return a serializable governed result requiring human decision.

## Security implications and trade-offs

| Decision | Advantage | Residual risk |
|---|---|---|
| Imported-class auto-registration | Minimal developer wiring; deterministic | Importing code executes trusted package initialization |
| Allowlisted entry points | Controlled ecosystem extension | Package authenticity/signature is not yet enforced |
| In-process execution | Simple and fast | No sandbox for untrusted components |
| Bounded thread parallelism | Lower latency with deterministic aggregation | Shared-process components can interfere with each other |
| Explicit rollback | Observable compensating behavior | Rollback cannot guarantee reversal of every external effect |
| Secret-pattern guard | Blocks common accidental disclosures | Not a complete DLP control |

Never run untrusted third-party components in this baseline. Network exposure, workload identity, signed packages, capability tokens, process isolation and durable tamper-evident audit logs remain future security gates.

## Validation

```bash
python -m compileall -q src examples tests
PYTHONPATH=src python -m coverage run -m unittest discover -s tests -v
python -m coverage report --fail-under=90
python -m ruff check src tests examples
python -m mypy -p bonfim
```

## Documentation

- [Architecture](docs/architecture.md)
- [Interfaces and models](docs/interfaces-and-models.md)
- [CLI and templates](docs/cli-and-templates.md)
- [Security model](docs/security.md)
- [Traceability matrix](docs/traceability.md)

## Limitations

- BSD-001 remains Category C / Level D / `Proposta` until explicit Founder approval.
- Agent aggregation and Automation rollback are local infrastructure baselines, not operational authority.
- No persistence, scheduling, remote execution, connector implementation or package signing is included.
- Successful execution does not prove an external effect, compliance, certification or approval.

## Versioning

The BSD-001 implementation is version `0.2.0` and follows Semantic Versioning. See [CHANGELOG.md](CHANGELOG.md), [RELEASING.md](RELEASING.md) and [SECURITY.md](SECURITY.md).
