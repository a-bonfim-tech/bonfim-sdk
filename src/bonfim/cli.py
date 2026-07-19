"""Dependency-free command line interface for governed SDK operations."""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from collections.abc import Sequence
from importlib import resources
from pathlib import Path
from typing import Any, cast

from . import __version__
from .base import GovernedComponent
from .registry import agent_registry, automation_registry, framework_registry, skill_registry

COMPONENT_TYPES = ("skill", "agent", "automation", "framework", "specification")
CLASS_NAME = re.compile(r"^[A-Z][A-Za-z0-9]*$")
COMPONENT_ID = re.compile(r"^[A-Z][A-Z0-9-]{2,63}$")


def snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def render_template(kind: str, class_name: str, component_id: str) -> str:
    suffix = "json.tpl" if kind == "specification" else "py.tpl"
    template = resources.files("bonfim.templates").joinpath(f"{kind}.{suffix}").read_text(encoding="utf-8")
    display_name = re.sub(r"(?<!^)(?=[A-Z])", " ", class_name)
    return (
        template.replace("{{ class_name }}", class_name)
        .replace("{{ component_id }}", component_id)
        .replace("{{ display_name }}", display_name)
    )


def create_component(kind: str, class_name: str, component_id: str, directory: Path) -> Path:
    if kind not in COMPONENT_TYPES:
        raise ValueError(f"unsupported component type: {kind}")
    if not CLASS_NAME.fullmatch(class_name):
        raise ValueError("name must be a PascalCase Python class name")
    if not COMPONENT_ID.fullmatch(component_id):
        raise ValueError("id must contain 3-64 uppercase letters, digits, or hyphens")
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    extension = ".json" if kind == "specification" else ".py"
    target = directory / f"{snake_case(class_name)}{extension}"
    with target.open("x", encoding="utf-8") as stream:
        stream.write(render_template(kind, class_name, component_id))
    return target


def import_explicit_module(module_name: str | None) -> None:
    if module_name:
        importlib.import_module(module_name)


def parse_inputs(value: str) -> dict[str, Any]:
    if value.startswith("@"):
        path = Path(value[1:])
        if path.stat().st_size > 1_000_000:
            raise ValueError("input file exceeds 1 MB")
        value = path.read_text(encoding="utf-8")
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("inputs must decode to a JSON object")
    return parsed


def registry_for(kind: str) -> Any:
    return {
        "skill": skill_registry,
        "agent": agent_registry,
        "automation": automation_registry,
        "framework": framework_registry,
    }[kind]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bonfim", description="Bonfim SDK developer CLI")
    subcommands = parser.add_subparsers(dest="command", required=True)

    new = subcommands.add_parser("new", help="Create a component from an official template")
    new.add_argument("kind", choices=COMPONENT_TYPES)
    new.add_argument("name")
    new.add_argument("--id", required=True, dest="component_id")
    new.add_argument("--directory", default=".", type=Path)

    validate = subcommands.add_parser("validate", help="Validate registered components")
    validate.add_argument("--module")

    run = subcommands.add_parser("run", help="Run an imported registered component")
    run.add_argument("identifier")
    run.add_argument("--kind", choices=("skill", "agent", "automation", "framework"), default="skill")
    run.add_argument("--inputs", default="{}")
    run.add_argument("--module")
    run.add_argument("--trigger", default="manual")

    subcommands.add_parser("doctor", help="Check the local SDK environment")
    subcommands.add_parser("version", help="Print the SDK version")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "new":
            target = create_component(arguments.kind, arguments.name, arguments.component_id, arguments.directory)
            print(target)
            return 0
        if arguments.command == "version":
            print(__version__)
            return 0
        if arguments.command == "doctor":
            report = {
                "sdk_version": __version__,
                "python": ".".join(str(item) for item in sys.version_info[:3]),
                "python_supported": sys.version_info >= (3, 11),
                "templates": all(
                    resources.files("bonfim.templates")
                    .joinpath(f"{kind}.{'json.tpl' if kind == 'specification' else 'py.tpl'}")
                    .is_file()
                    for kind in COMPONENT_TYPES
                ),
                "registries": {
                    "skills": len(skill_registry.identifiers()),
                    "agents": len(agent_registry.identifiers()),
                    "automations": len(automation_registry.identifiers()),
                    "frameworks": len(framework_registry.identifiers()),
                },
            }
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if report["python_supported"] and report["templates"] else 1
        if arguments.command == "validate":
            import_explicit_module(arguments.module)
            errors: list[str] = []
            for registry in (skill_registry, agent_registry, automation_registry, framework_registry):
                for identifier in registry.identifiers():
                    definition = registry.definition(identifier)
                    component_type = cast(
                        type[GovernedComponent], definition if isinstance(definition, type) else type(definition)
                    )
                    errors.extend(f"{identifier}: {error}" for error in component_type.validate())
            print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
            return 0 if not errors else 1
        if arguments.command == "run":
            import_explicit_module(arguments.module)
            component = registry_for(arguments.kind).get(arguments.identifier)
            inputs = parse_inputs(arguments.inputs)
            kwargs = {"trigger": arguments.trigger} if arguments.kind == "automation" else {}
            result = component.run(inputs, **kwargs)
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
            return 0 if result.status != "Failed" else 1
    except (FileExistsError, ImportError, KeyError, OSError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.error("unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
