from __future__ import annotations

import io
import json
import runpy
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from bonfim import Skill
from bonfim.cli import create_component, main, parse_inputs, render_template, snake_case


class TemplateTests(unittest.TestCase):
    def test_all_official_templates_render(self) -> None:
        for kind in ("skill", "agent", "automation", "framework", "specification"):
            rendered = render_template(kind, "ExampleComponent", "EXAMPLE-001")
            self.assertNotIn("{{", rendered)
            if kind == "specification":
                self.assertEqual(json.loads(rendered)["approval_status"], "Proposta")
            else:
                compile(rendered, f"{kind}.py", "exec")

    def test_create_component_is_exclusive_and_validated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = create_component("skill", "ExampleSkill", "EXAMPLE-SKILL-001", Path(temporary))
            self.assertEqual(target.name, "example_skill.py")
            with self.assertRaises(FileExistsError):
                create_component("skill", "ExampleSkill", "EXAMPLE-SKILL-001", Path(temporary))
            with self.assertRaises(ValueError):
                create_component("unknown", "ExampleSkill", "EXAMPLE-001", Path(temporary))
            with self.assertRaises(ValueError):
                create_component("skill", "not_pascal", "EXAMPLE-001", Path(temporary))
            with self.assertRaises(ValueError):
                create_component("skill", "ExampleSkill", "bad id", Path(temporary))

    def test_snake_case(self) -> None:
        self.assertEqual(snake_case("SecurityEvidenceCollector"), "security_evidence_collector")


class CLITests(unittest.TestCase):
    def invoke(self, arguments):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(arguments)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_version_doctor_validate_and_new(self) -> None:
        code, output, _ = self.invoke(["version"])
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), "0.2.0")

        code, output, _ = self.invoke(["doctor"])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(output)["templates"])

        code, output, _ = self.invoke(["validate", "--module", "examples.security_evidence_collector"])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(output)["valid"])

        with tempfile.TemporaryDirectory() as temporary:
            code, output, _ = self.invoke(
                ["new", "framework", "TestFramework", "--id", "TEST-FRAMEWORK-001", "--directory", temporary]
            )
            self.assertEqual(code, 0)
            self.assertTrue(Path(output.strip()).is_file())

    def test_run_and_errors(self) -> None:
        code, output, _ = self.invoke(
            [
                "run",
                "SEC-001-SDK-EXAMPLE",
                "--module",
                "examples.security_evidence_collector",
                "--inputs",
                '{"artifacts":["test"]}',
            ]
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["status"], "Succeeded")

        code, _, error = self.invoke(["run", "UNKNOWN", "--inputs", "{}"])
        self.assertEqual(code, 2)
        self.assertIn("Unknown Skill", error)

        code, _, error = self.invoke(["new", "skill", "bad", "--id", "BAD-001"])
        self.assertEqual(code, 2)
        self.assertIn("PascalCase", error)

    def test_parse_inline_and_file_inputs(self) -> None:
        self.assertEqual(parse_inputs('{"value":1}'), {"value": 1})
        with self.assertRaises(ValueError):
            parse_inputs("[]")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "input.json"
            path.write_text('{"from_file":true}', encoding="utf-8")
            self.assertEqual(parse_inputs(f"@{path}"), {"from_file": True})
            path.write_text("x" * 1_000_001, encoding="utf-8")
            with self.assertRaises(ValueError):
                parse_inputs(f"@{path}")


class OfficialExampleTests(unittest.TestCase):
    def test_four_reference_implementations_execute(self) -> None:
        fixtures = (
            ("examples/security_evidence_collector.py", {"artifacts": ["log"]}),
            (
                "examples/github_pr_readiness_reviewer.py",
                {
                    "repository": "Bonfim-Labs/sdk",
                    "pull_request": 1,
                    "head_sha": "abc",
                    "checks": [{"name": "tests", "conclusion": "success"}],
                },
            ),
            (
                "examples/security_compliance_reviewer.py",
                {"requirements": ["GV.OC-01"], "evidence_mappings": {"GV.OC-01": ["EVD-1"]}},
            ),
            (
                "examples/governance_documentation_generator.py",
                {"title": "Decision", "owner": "Founder", "facts": {"state": "Proposta"}},
            ),
        )
        for path, inputs in fixtures:
            namespace = runpy.run_path(path)
            classes = [
                value
                for value in namespace.values()
                if isinstance(value, type) and issubclass(value, Skill) and value is not Skill
            ]
            self.assertEqual(len(classes), 1)
            result = classes[0]().run(inputs)
            self.assertEqual(result.status, "Succeeded")


if __name__ == "__main__":
    unittest.main()
