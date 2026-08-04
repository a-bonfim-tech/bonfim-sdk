# End-to-End Quickstart

This tutorial creates, validates and executes a governed Skill in a clean local environment. It uses synthetic data and performs no network request or external mutation.

## 1. Create the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
bonfim doctor
```

Expected result: `python_supported` and `templates` are `true`.

## 2. Generate a Skill

```bash
mkdir -p demo
bonfim new skill HeaderReview --id DEMO-HEADER-001 --directory demo
```

The CLI creates `demo/header_review.py` and refuses to overwrite it.

## 3. Implement deterministic behavior

Replace the generated `perform()` body with:

```python
headers = context.inputs["headers"]
missing = tuple(name for name in ("content-security-policy", "x-content-type-options") if name not in headers)
return self.output(
    "Synthetic HTTP header review completed.",
    findings=(f"Missing headers: {', '.join(missing) if missing else 'none'}",),
    risks=("Missing browser security headers may increase client-side exposure.",) if missing else (),
    limitations=("Only caller-supplied synthetic headers were reviewed.",),
    confidence="Medium",
    confidence_justification="The check is deterministic; source authenticity was not verified.",
    recommendation="Review the result before changing any deployed service.",
    final_verdict="Review Required" if missing else "No Missing Header Detected",
)
```

Set the declaration fields:

```python
skill_id = "DEMO-HEADER-001"
name = "Header Review"
version = "0.1.0"
mission = "Review caller-supplied HTTP security headers."
scope = ("Synthetic header review",)
out_of_scope = ("Network requests", "Configuration changes")
activation_conditions = ("Explicit local invocation",)
required_inputs = ("headers",)
```

## 4. Validate the module

```bash
PYTHONPATH=. bonfim validate --module demo.header_review
```

Expected result:

```json
{
  "valid": true,
  "errors": []
}
```

## 5. Run the Skill

```bash
PYTHONPATH=. bonfim run DEMO-HEADER-001 \
  --module demo.header_review \
  --inputs '{"headers":{"x-content-type-options":"nosniff"}}'
```

The JSON output should include:

- a stable Skill identifier and version;
- execution timestamps and ID;
- findings, risk and limitations;
- confidence with justification;
- quality-gate results;
- provenance fields marked `Unknown` where unavailable;
- `decision_status: Human decision required`.

## 6. Verify fail-closed behavior

Run without the required input:

```bash
PYTHONPATH=. bonfim run DEMO-HEADER-001 --module demo.header_review --inputs '{}'
```

The command should return a failed result without executing domain behavior.

## 7. Run repository quality checks

```bash
python -m compileall -q src examples tests
PYTHONPATH=src python -m coverage run -m unittest discover -s tests -v
python -m coverage report --fail-under=90
python -m ruff check src tests examples
python -m mypy -p bonfim
python -m bandit -r src -q -lll -iii
```

## Interpretation

This tutorial demonstrates contract enforcement and transparent uncertainty. It does not establish production suitability, compliance, correctness of caller-supplied evidence or authorization for external action.
