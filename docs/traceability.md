# BSD-001 Traceability Matrix

| Delivery | Implementation | Validation |
|---|---|---|
| Repository structure | `src/bonfim/*`, `tests`, `examples`, `templates`, `docs` | source-tree and build checks |
| Framework base | `framework/base.py` | load, validate, register, dependency/cycle tests |
| Skill base | `skill/base.py` | creation, validation, execution, security and compatibility tests |
| Agent base | `agent/base.py` | parallel, sequential, partial and fail-fast tests |
| Automation base | `automation/base.py` | trigger, retry, rollback and monitoring tests |
| Six interfaces | `base/interfaces.py` | interface inheritance tests |
| Eleven shared models | `models.py`, `schemas/__init__.py` | serialization and immutability tests |
| Four registries | `registry.py` | lifecycle, duplicate, replace and allowlist tests |
| Five templates | root and packaged `templates` | render, compile/JSON and no-overwrite tests |
| CLI | `cli.py`, `__main__.py` | new, validate, run, doctor, version and error tests |
| Four references | `examples/*.py` | direct execution tests |
| Coverage | `pyproject.toml` | `coverage report --fail-under=90` |

BSD-001 is implemented as repository code but remains Category C / Level D / `Proposta`. This traceability matrix does not record Founder approval or production readiness.
