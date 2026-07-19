from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from bonfim import Framework, FrameworkRegistry, SkillRegistry
from bonfim.exceptions import DiscoveryError, RegistrationError


class BaseFramework(Framework):
    framework_id = "TEST-FW-BASE"
    name = "Test Base Framework"
    version = "1.0.0"
    description = "Base fixture."


class ChildFramework(Framework):
    framework_id = "TEST-FW-CHILD"
    name = "Test Child Framework"
    version = "1.0.0"
    description = "Child fixture."
    dependencies = ("TEST-FW-BASE",)


class FrameworkTests(unittest.TestCase):
    def test_load_mapping_validate_register_and_resolve(self) -> None:
        loaded = Framework.load(
            {
                "framework_id": "TEST-FW-LOADED",
                "name": "Loaded",
                "version": "1.2.3",
                "description": "Loaded fixture.",
                "dependencies": [],
            }
        )
        self.assertEqual(loaded.validate(), ())
        registry = FrameworkRegistry()
        self.assertEqual(loaded.register(registry), "TEST-FW-LOADED")
        self.assertEqual(loaded.resolve_dependencies(registry), ("TEST-FW-LOADED",))
        self.assertEqual(loaded.execute({"value": 1}).status, "Succeeded")

    def test_load_json_file_and_reject_other_formats(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "framework.json"
            path.write_text(
                json.dumps(
                    {"framework_id": "TEST-FW-JSON", "name": "JSON", "version": "1.0.0", "description": "JSON fixture."}
                ),
                encoding="utf-8",
            )
            self.assertEqual(Framework.load(path).framework_id, "TEST-FW-JSON")
            yaml_path = Path(temporary) / "framework.yaml"
            yaml_path.write_text("name: test", encoding="utf-8")
            with self.assertRaises(ValueError):
                Framework.load(yaml_path)
        with self.assertRaises(ValueError):
            Framework.load({"name": "missing fields"})

    def test_dependency_order_and_cycle_detection(self) -> None:
        registry = FrameworkRegistry()
        registry.register(BaseFramework)
        registry.register(ChildFramework)
        self.assertEqual(registry.dependency_order("TEST-FW-CHILD"), ("TEST-FW-BASE", "TEST-FW-CHILD"))

        class CycleA(Framework):
            framework_id = "TEST-CYCLE-A"
            name = "Cycle A"
            version = "1.0.0"
            description = "Cycle fixture."
            dependencies = ("TEST-CYCLE-B",)

        class CycleB(Framework):
            framework_id = "TEST-CYCLE-B"
            name = "Cycle B"
            version = "1.0.0"
            description = "Cycle fixture."
            dependencies = ("TEST-CYCLE-A",)

        registry.register(CycleA)
        registry.register(CycleB)
        with self.assertRaises(RegistrationError):
            registry.dependency_order("TEST-CYCLE-A")

    def test_invalid_framework_returns_failed_output(self) -> None:
        invalid = Framework()
        self.assertEqual(invalid.execute({}).status, "Failed")


class GenericRegistryTests(unittest.TestCase):
    def test_registry_lifecycle_and_constructor_arguments(self) -> None:
        registry = FrameworkRegistry()
        registry.register(BaseFramework)
        self.assertIsInstance(registry.get("TEST-FW-BASE", specification={"x": 1}), BaseFramework)
        registry.unregister("TEST-FW-BASE")
        with self.assertRaises(KeyError):
            registry.unregister("TEST-FW-BASE")
        registry.register(BaseFramework())
        with self.assertRaises(TypeError):
            registry.get("TEST-FW-BASE", specification={})
        registry.clear()
        self.assertEqual(registry.identifiers(), ())

    def test_registration_errors_and_replace(self) -> None:
        registry = SkillRegistry()
        with self.assertRaises(RegistrationError):
            registry.register(object())

        class OtherBase(BaseFramework):
            framework_id = "TEST-FW-BASE"
            name = "Replacement"

        frameworks = FrameworkRegistry()
        frameworks.register(BaseFramework)
        with self.assertRaises(RegistrationError):
            frameworks.register(OtherBase)
        frameworks.register(OtherBase, replace=True)
        self.assertIsInstance(frameworks.get("TEST-FW-BASE"), OtherBase)

    def test_allowlisted_entry_point_discovery(self) -> None:
        registry = FrameworkRegistry()
        allowed = Mock(name="allowed")
        allowed.name = "approved"
        allowed.load.return_value = BaseFramework
        denied = Mock(name="denied")
        denied.name = "unapproved"
        points = Mock()
        points.select.return_value = (allowed, denied)
        with patch("bonfim.registry.metadata.entry_points", return_value=points):
            self.assertEqual(registry.discover("bonfim.frameworks", allowlist=("approved",)), ("TEST-FW-BASE",))
            self.assertEqual(registry.discover("bonfim.frameworks", allowlist=()), ())

        allowed.load.side_effect = RuntimeError("unsafe details")
        registry.clear()
        with (
            patch("bonfim.registry.metadata.entry_points", return_value=points),
            self.assertRaises(DiscoveryError),
        ):
            registry.discover("bonfim.frameworks", allowlist=("approved",))


if __name__ == "__main__":
    unittest.main()
