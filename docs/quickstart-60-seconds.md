# 60-Second Governed Execution Demo

This demonstration is the shortest executable path through the Bonfim SDK's implemented governance boundary. It uses only synthetic local input, performs no network request and makes no external change.

```text
REGISTER → VALIDATE → EXECUTE → AUDIT → HUMAN REVIEW REQUIRED → VERIFIED EVIDENCE
```

The ordering is intentional. In the current `0.2.1` architecture, human review is a mandatory property of the result; it is **not** a pre-execution authorization gate. The demo therefore does not claim a capability the SDK has not implemented.

## Run it

From a clean clone:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python examples/quickstart_60s.py
```

No third-party runtime dependency or network access is required after the repository is available locally.

## What each stage proves

| Stage | Demonstrated behavior |
| --- | --- |
| `REGISTER` | A governed Skill is admitted through `SkillRegistry` under a stable identifier. |
| `VALIDATE` | The Skill declaration satisfies the SDK contract before use. |
| `EXECUTE` | `SkillRunner` invokes the SDK-owned execution pipeline over explicit synthetic inputs and provenance. |
| `AUDIT` | The result exposes quality-gate states, execution identity, provenance and structured evidence. |
| `HUMAN REVIEW` | The serialized result explicitly states `Human decision required`; execution is not decision authority. |
| `VERIFIED EVIDENCE` | The demo verifies that the local result contract succeeded, mandatory gates did not fail and evidence identifiers were emitted. |

## Expected shape

The exact execution UUID and timestamps vary. The stable progression should resemble:

```text
REGISTER                 SEC-001-SDK-EXAMPLE
VALIDATE                 PASS
EXECUTE                  SUCCEEDED
AUDIT                    quality_gates_passed=9 failed=0
HUMAN REVIEW             Human decision required
VERIFIED EVIDENCE        contract=TRUE ids=EVD-001
```

A compact JSON result follows with the Skill identifier, execution status, execution ID, evidence identifiers, human-decision status and final verdict.

## Security and assurance boundary

`VERIFIED EVIDENCE` means the **SDK result contract** was verified locally for this synthetic execution. It does not mean the underlying artifact is authentic, externally corroborated, compliant, certified or suitable as a basis for an autonomous decision. The example Skill deliberately records that caller-supplied artifact authenticity was not independently verified.

Bonfim SDK remains pre-alpha and is not a sandbox. Imported Python components execute in-process and must be trusted.

For the longer tutorial, including fail-closed missing-input behavior and repository quality commands, continue with [End-to-End Quickstart](quickstart-tutorial.md).
