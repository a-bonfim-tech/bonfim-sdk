# Contributing

Bonfim SDK is pre-alpha software with explicit security and governance constraints. Contributions are evaluated for correctness, testability, traceability and security impact.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Required validation

Run the complete local validation before submitting a change:

```bash
python -m compileall -q src examples tests
PYTHONPATH=src python -m coverage run -m unittest discover -s tests -v
python -m coverage report --fail-under=90
python -m ruff check src tests examples
python -m mypy -p bonfim
python -m bandit -r src -q -lll -iii
```

## Contribution requirements

Every change should:

- have a narrowly defined purpose;
- preserve backward compatibility or document the break;
- include tests for success, failure and boundary behavior;
- avoid silently increasing authority or external side effects;
- preserve human-review requirements;
- document security implications and residual risk;
- avoid credentials, personal data and proprietary evidence;
- update user-facing documentation when behavior changes;
- update `CHANGELOG.md` when the change is externally relevant.

## Component requirements

New Skills, Agents, Automations and Frameworks must declare stable identifiers, semantic versions, scope, limitations and activation conditions. Domain behavior must remain separate from SDK infrastructure behavior.

## Security-sensitive changes

Changes affecting any of the following require explicit security review:

- plugin or entry-point discovery;
- secret detection;
- serialization;
- provenance and traceability;
- concurrency;
- retries and rollback;
- filesystem or network access;
- release workflows;
- authentication, authorization or connector permissions.

Do not include vulnerability details in a public issue. Follow [SECURITY.md](SECURITY.md).

## Pull request evidence

A reviewable change should include:

1. problem statement;
2. design decision and alternatives considered;
3. test evidence;
4. security impact;
5. compatibility impact;
6. limitations and unresolved work;
7. documentation changes.

## Commit quality

Use focused commits with imperative messages, for example:

```text
fix: preserve step-specific inputs during rollback
test: cover parallel agent exception handling
docs: clarify trusted plugin boundary
```

Generated artifacts should only be committed when they are part of the defined evidence or release process.

## Publication authority

A merged contribution does not authorize public release, tagging, package publication or production use. Those remain separate human decisions.
