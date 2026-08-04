"""Framework loading, validation, registration and dependency resolution."""

from __future__ import annotations

import json
from collections.abc import Mapping
from contextlib import suppress
from pathlib import Path
from typing import Any, cast

from ..base import Executable, GovernedComponent
from ..exceptions import RegistrationError
from ..models import Confidence, Limitation, OutputContract, Traceability, utc_now


class Framework(GovernedComponent, Executable):
    framework_id = ""
    dependencies: tuple[str, ...] = ()
    schema_version = "1.0"

    def __init__(self, specification: Mapping[str, Any] | None = None) -> None:
        self.specification = dict(specification or {})

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.component_id = getattr(cls, "framework_id", "")
        if cls.auto_register and cls.component_id and not cls.validate():
            from ..registry import framework_registry

            with suppress(RegistrationError, ValueError):
                framework_registry.register(cls)

    @classmethod
    def validate(cls) -> tuple[str, ...]:
        errors = list(super().validate())
        if not cls.framework_id:
            errors.append(f"{cls.__name__}.framework_id must be declared")
        if not isinstance(cls.dependencies, tuple) or not all(
            isinstance(item, str) and item.strip() for item in cls.dependencies
        ):
            errors.append(f"{cls.__name__}.dependencies must contain non-empty identifiers")
        if cls.framework_id in cls.dependencies:
            errors.append(f"{cls.__name__} cannot depend on itself")
        return tuple(dict.fromkeys(errors))

    @classmethod
    def load(cls, source: Mapping[str, Any] | str | Path) -> Framework:
        if isinstance(source, Mapping):
            data = dict(source)
        else:
            path = Path(source)
            if path.suffix.lower() != ".json":
                raise ValueError("Framework.load supports JSON files only without optional parsers")
            data = json.loads(path.read_text(encoding="utf-8"))
        required = ("framework_id", "name", "version", "description")
        missing = tuple(name for name in required if not data.get(name))
        if missing:
            raise ValueError("Framework definition missing: " + ", ".join(missing))
        framework_type = cast(
            type[Framework],
            type(
                f"Loaded_{str(data['framework_id']).replace('-', '_')}",
                (cls,),
                {
                    "framework_id": str(data["framework_id"]),
                    "component_id": str(data["framework_id"]),
                    "name": str(data["name"]),
                    "version": str(data["version"]),
                    "description": str(data["description"]),
                    "dependencies": tuple(data.get("dependencies", ())),
                },
            ),
        )
        errors = framework_type.validate()
        if errors:
            raise ValueError("; ".join(errors))
        return framework_type(data)

    def register(self, registry: Any | None = None) -> str:
        if registry is None:
            from ..registry import framework_registry

            registry = framework_registry
        return registry.register(self)

    def resolve_dependencies(self, registry: Any | None = None) -> tuple[str, ...]:
        if registry is None:
            from ..registry import framework_registry

            registry = framework_registry
        return registry.dependency_order(self.framework_id)

    def execute(self, inputs: Mapping[str, Any], **kwargs: Any) -> OutputContract:
        started = utc_now()
        errors = self.validate()
        if not isinstance(inputs, Mapping):
            errors = (*errors, "inputs must be a mapping")
        if errors:
            return OutputContract(
                component_id=self.framework_id or type(self).__name__,
                component_type="Framework",
                component_version=self.version or "0.0.0",
                status="Failed",
                summary="Framework validation failed safely.",
                limitations=(Limitation("FRAMEWORK-INVALID", "; ".join(errors)),),
                confidence=Confidence.UNKNOWN,
                started_at=started,
                error="ValidationError",
            )
        trace = Traceability(self.framework_id, self.version, self.traceability().execution_id, self.origin)
        return OutputContract(
            component_id=self.framework_id,
            component_type="Framework",
            component_version=self.version,
            status="Succeeded",
            summary="Framework is valid and its dependency contract can be resolved.",
            confidence=Confidence.HIGH,
            trace=trace,
            started_at=started,
            metadata={"dependencies": list(self.dependencies), "input_keys": sorted(inputs)},
        )
