# Bonfim SDK

## Executive Summary

`bonfim-sdk` provides the reusable Python infrastructure required to build
Bonfim Labs Skills as specializations of the approved `BL-SOF-001 v2.0.0`.

The intended API is available:

```python
from bonfim import Skill


class SecurityEvidenceCollector(Skill):
    ...
```

New Skills declare their identity, mission, scope, activation conditions, and
inputs, then implement only `run()`. The SDK supplies the common execution
pipeline, provenance, quality gates, security checks, failures, output contract,
registry, runner, and runtime adapter.

## Knowledge Classification

| Field | Value |
|---|---|
| Knowledge category | Category C — Architectural Proposals |
| Evidence level | Level D — Internal Proposal or Convention |
| Approval status | Proposta |
| Artifact state | Implementado |
| Origin | Founder instruction dated 2026-07-14 |
| Justification | Avoid duplicating Skill infrastructure across Bonfim Labs |
| Version | 0.1.0 |

`BL-SOF-001 v2.0.0` is an approved Category B internal convention. The SDK is a
new Category C implementation proposal derived from it; the SDK is not an
international standard and has not been approved for production use.

## Create a Skill

```python
from bonfim import Evidence, Skill, SkillContext


class SecurityEvidenceCollector(Skill):
    skill_id = "SEC-001"
    name = "Security Evidence Collector"
    version = "0.1.0"
    mission = "Package supplied security artifacts as traceable evidence."
    scope = ("Security evidence packaging",)
    out_of_scope = ("Compliance certification", "Control implementation")
    activation_conditions = ("Explicit evidence-collection request",)
    required_inputs = ("artifacts",)

    def run(self, context: SkillContext):
        evidence = tuple(
            Evidence(
                identifier=f"EVD-{index:03d}",
                summary=str(artifact),
                category="Security Evidence",
                origin=context.provenance.origin,
                validation="Recorded but not independently validated",
                confidence="Low",
            )
            for index, artifact in enumerate(context.inputs["artifacts"], start=1)
        )
        return self.output(
            f"Collected {len(evidence)} artifact(s).",
            evidence=evidence,
            confidence="Low",
            confidence_justification="Independent validation was not performed.",
            recommendation="Validate authenticity before relying on the package.",
            final_verdict="Review Required",
        )
```

A fuller executable example is available in
[`examples/security_evidence_collector.py`](examples/security_evidence_collector.py).

## Execute Directly

```python
from bonfim import Provenance

result = SecurityEvidenceCollector().execute(
    {"artifacts": ["test output", "configuration snapshot"]},
    provenance=Provenance(
        origin="local validation",
        producer="security engineer",
        collection_method="direct observation",
        environment="development",
        artifact="evidence bundle",
        repository="example/repository",
        branch="main",
        commit="abc123",
        issue="SEC-100",
        pull_request="Not Applicable",
    ),
)

assert result.status == "Succeeded"
```

## Register and Run

```python
from bonfim import SkillRegistry, SkillRunner

registry = SkillRegistry()
registry.register(SecurityEvidenceCollector())

runner = SkillRunner(registry)
result = runner.run("SEC-001", {"artifacts": ["test output"]})
```

`Skill` instances are also callable and return dictionaries, allowing direct
registration with callable-based runtime executors without coupling this SDK to
one runtime implementation.

## Installation

Python 3.11 or newer is required.

```sh
python3 -m pip install -e .
```

There are no third-party runtime dependencies.

## Validation

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Architecture and Traceability

- [Architecture](docs/architecture.md)
- [Traceability matrix](docs/traceability.md)

## Risks and Limitations

- Skill code runs in-process and is not sandboxed.
- Output secret detection is defense in depth, not a complete DLP control.
- The explicit registry does not automatically discover installed plugins.
- Persistence, remote execution, signing, package publication, and trust-policy
  enforcement are not implemented.
- Skills support human review and cannot certify, approve, audit, or replace an
  accountable decision authority.

## Next Logical Step

Perform independent API, security, and SOF-conformance review. Then define the
signed package-distribution and runtime-isolation model before accepting
third-party Skills.
