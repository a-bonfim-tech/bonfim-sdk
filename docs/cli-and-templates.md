# CLI and Official Templates

## Generation

```bash
bonfim new skill MySkill --id MY-SKILL-001 --directory src/my_package
bonfim new agent MyAgent --id MY-AGENT-001
bonfim new automation MyAutomation --id MY-AUTOMATION-001
bonfim new framework MyFramework --id MY-FRAMEWORK-001
bonfim new specification MySpecification --id MY-SPEC-001
```

Names must be PascalCase; identifiers must use uppercase letters, digits and hyphens. Existing files are never overwritten.

## Validation and execution

`--module` is an explicit import boundary. It is never derived from untrusted input inside the SDK.

```bash
bonfim validate --module my_package.components
bonfim run MY-SKILL-001 --module my_package.components --inputs @inputs.json
```

Input files are limited to 1 MB and must contain a JSON object.

## Template governance

Root templates are reviewable repository artifacts. Identical packaged copies allow the installed CLI to work without locating the source checkout. CI compiles or parses every rendered template. Template changes are SDK contract changes and must update tests and the changelog.
