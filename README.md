# Bonfim SDK

**A governed Python SDK for building auditable security skills, AI agents and automations with validation, traceability, explicit limitations and human review.**

[![Python](https://img.shields.io/badge/Python-3.11--3.14-3776AB)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Pre--Alpha-orange)](CHANGELOG.md)

Bonfim SDK provides reusable infrastructure for developers who need AI-assisted or security-oriented components to produce structured, reviewable and serializable results without silently claiming authority, compliance or certainty.

The SDK supplies the governance and execution pipeline. A component author implements only the domain-specific behavior.

## Why this project exists

AI agents and security automations often fail in predictable ways:

- inputs are accepted without validation;
- evidence provenance is lost;
- confidence is asserted without justification;
- sensitive output is returned accidentally;
- failures expose implementation details;
- automated results are treated as final decisions;
- plugin discovery expands the trust boundary without control.

Bonfim SDK addresses these problems through explicit contracts and fail-closed behavior.

## What it demonstrates

- Python package and CLI design
- governed component interfaces
- immutable input and provenance models
- deterministic registries and allowlisted plugin discovery
- bounded agent parallelism
- retry and rollback-aware automation workflows
- secret-like output blocking
- structured evidence, findings, risks and limitations
- human-review requirements
- strict typing, linting, SAST, tests and coverage gates
- full-history secret scanning and CycloneDX SBOM generation
- wheel and source-distribution validation with clean-install smoke testing

## Verified candidate evidence

The private publication candidate has been validated on its exact commit by GitHub Actions with:

- 58 passing tests on Python 3.11, 3.12, 3.13 and 3.14;
- 93% branch-aware coverage across 958 statements and 188 branches;
- Ruff with all checks passing;
- mypy strict with no issues across 27 source files;
- Bandit with no finding at the configured high-severity/high-confidence blocking threshold;
- full-history Gitleaks scanning;
- CycloneDX SBOM generation;
- governance baseline validation;
- wheel and source-distribution build;
- `twine check` validation;
- package-content and metadata validation;
- SHA-256 checksum generation and verification;
- clean virtual-environment installation;
- installed CLI and package-resource smoke tests.

See [Publication Readiness Evidence](docs/publication-readiness-evidence.md) and [Publication Review Checklist](docs/publication-review-checklist.md).

## Architecture at a glance

```text
Domain component
      │
      ├── Skill ─────── validate → execute → inspect → quality gates → result
      ├── Agent ─────── select allowlisted Skills → bounded execution → aggregate
      ├── Automation ── validate trigger → execute steps → retry → rollback → report
      └── Framework ─── load → validate → register → resolve dependencies
      │
      ▼
Governed output
      ├── traceability and provenance
      ├── evidence and findings
      ├── risks and limitations
      ├── confidence with justification
      ├── security inspection
      └── explicit human decision requirement
```

See [Architecture](docs/architecture.md), [Security Model](docs/security.md) and [Threat Model](docs/threat-model.md).

## Quick start

### Requirements

- Python 3.11 through 3.14
- No runtime dependencies outside the Python standard library

### Installation for development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
bonfim doctor
```

### Create a governed Skill

```bash
bonfim new skill SecurityEvidenceCollector \
  --id SEC-EVD-001 \
  --directory src/my_project
```

### Minimal example

```python
from bonfim import Skill, SkillContext, SkillOutput


class SecurityEvidenceCollector(Skill):
    skill_id = "SEC-EVD-001"
    name = "Security Evidence Collector"
    version = "0.2.0"
    mission = "Package caller-supplied artifacts for human review."
    scope = ("Evidence packaging",)
    out_of_scope = ("Certification", "Remediation")
    activation_conditions = ("Explicit evidence request",)
    required_inputs = ("artifacts",)

    def perform(self, context: SkillContext) -> SkillOutput:
        artifacts = context.inputs["artifacts"]
        return self.output(
            f"Received {len(artifacts)} artifact(s).",
            limitations=("Artifact authenticity was not independently validated.",),
            confidence="Low",
            confidence_justification="Only caller-supplied artifacts were observed.",
            final_verdict="Review Required",
        )


result = SecurityEvidenceCollector().run({"artifacts": ["test.log"]})
print(result.to_dict())
```

The execution pipeline validates the declaration and inputs, creates traceability metadata, executes the component, blocks secret-like output, evaluates quality gates and returns a serializable result.

For a complete reproducible workflow, follow the [End-to-End Quickstart](docs/quickstart-tutorial.md).

## Core APIs

### Skills

Skills implement domain behavior through `perform(context)` while the SDK owns validation, execution, security inspection and output construction.

### Agents

Agents coordinate an explicit allowlist of Skills. Execution can be sequential or use bounded thread parallelism. Aggregated results preserve order and remain subject to human review.

### Automations

Automations run trigger-controlled workflows with bounded retries, monitoring and observable rollback attempts. Rollback receives the exact input mapping used by the completed step. It is compensating behavior, not a guarantee that external effects were reversed.

### Frameworks

Frameworks can be loaded from JSON, validated, registered and resolved through dependency order with cycle detection.

### Registries

Central registries support explicit imports and opt-in package entry-point discovery. Discovery requires a caller-provided allowlist.

## CLI

```bash
bonfim new skill SecurityEvidenceCollector --id SEC-EVD-001 --directory src/my_project
bonfim new agent EvidenceAgent --id AGENT-EVD-001
bonfim new automation EvidenceWorkflow --id AUT-EVD-001
bonfim validate --module my_project.skills
bonfim run SEC-EVD-001 --module my_project.skills --inputs '{"artifacts": []}'
bonfim doctor
bonfim version
```

The CLI refuses to overwrite existing component files.

## Security model

Implemented safeguards include:

- explicit imports and allowlisted entry points;
- declaration and Semantic Versioning validation;
- immutable top-level inputs and provenance mappings;
- bounded Agent worker count;
- bounded Automation retries;
- secret-like output detection;
- withheld unexpected exception details;
- mandatory human-review statements;
- Bandit SAST;
- full-history Gitleaks scanning;
- CycloneDX SBOM generation;
- GitHub Actions pinned to immutable commit SHAs;
- package hashes and clean-install validation.

Important boundary: imported Python components execute in-process and are trusted. The SDK is not a sandbox. Do not run untrusted third-party components.

See [Security Model](docs/security.md), [Threat Model](docs/threat-model.md) and [Security Policy](SECURITY.md).

## Quality and verification

```bash
python -m compileall -q src examples tests
PYTHONPATH=src python -m coverage run -m unittest discover -s tests -v
python -m coverage report --fail-under=90
python -m ruff check src tests examples
python -m mypy -p bonfim
python -m bandit -r src -q -lll -iii
```

## Repository map

```text
src/bonfim/          SDK implementation
tests/               contract and behavior tests
examples/            read-only reference components
templates/           component templates
docs/                architecture, security and interface documentation
tools/               quality and release verification
quality/             quality baseline manifest
release/             release baseline manifest
.github/workflows/   CI and release gates
```

## Public interfaces

- `Executable`
- `Validatable`
- `Traceable`
- `Governable`
- `Versionable`
- `Documentable`

Shared models include `Evidence`, `Finding`, `Risk`, `Limitation`, `Recommendation`, `Decision`, `Observation`, `Requirement`, `Provenance`, `Traceability` and `OutputContract`.

## Limitations

- Pre-alpha software; APIs may change.
- No process or container isolation for component execution.
- No network connector implementation.
- No persistent scheduler, database or durable audit store.
- No signed plugin verification or package attestation enforcement.
- Secret-pattern inspection is not a complete DLP control.
- Successful execution does not prove an external effect, compliance, certification or approval.

## Project status

Current package version: `0.2.0`.

Technical publication gates are validated on the private candidate. Repository visibility, merge, tagging, GitHub Release creation and package-registry publication remain separate human decisions.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports must follow [SECURITY.md](SECURITY.md).

## License

Licensed under the [Apache License 2.0](LICENSE). Product names and marks remain subject to the limitation recorded in [NOTICE](NOTICE).
