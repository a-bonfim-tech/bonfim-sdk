# SDK Traceability Matrix

| Requirement | Source | Implementation | Validation |
|---|---|---|---|
| `from bonfim import Skill` | Founder instruction | `src/bonfim/__init__.py` | `tests/test_sdk.py` |
| New Skills specialize shared infrastructure | BL-SOF-001 Authority and Adoption Rule | `src/bonfim/skill.py` | Inheritance and minimal-subclass tests |
| Universal Skill Structure | BL-SOF-001 section 4 | `SkillSpecification` and inherited declarations | Specification tests |
| Evidence and confidence | BL-SOF-001 sections 5–7 | `Evidence`, `SkillOutput`, `SkillResult` | Evidence tests |
| Quality gates | BL-SOF-001 section 8 | `Skill._quality_gates()` | Gate tests |
| Fail safely | BL-SOF-001 section 9 | `SkillExecutionError` and failure boundary | Failure tests |
| Security by default | BL-SOF-001 section 10 | `security.sensitive_paths()` | Secret-blocking tests |
| Preserve human authority | BL-SOF-001 section 11 | Result contract and SDK limitations | Serialization tests |
| Universal output | BL-SOF-001 section 12 | `SkillResult` | Result-contract tests |
| Semantic versioning | BL-SOF-001 section 14 | Declaration validation | Invalid-version test |

The SDK implementation is `Implementado` as a repository artifact. Its
architecture remains Category C / Level D / `Proposta` until explicit approval.
