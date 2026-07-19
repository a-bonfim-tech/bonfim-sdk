"""Thread-safe central registries with import-time and allowlisted discovery."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from importlib import metadata
from threading import RLock
from typing import Any, Generic, TypeVar, cast

from .exceptions import DiscoveryError, RegistrationError
from .models import Provenance, SkillResult

T = TypeVar("T")


class ComponentRegistry(Generic[T]):
    """Store component classes or instances under stable governed identifiers."""

    def __init__(self, kind: str, identifier_attributes: Iterable[str]) -> None:
        self.kind = kind
        self.identifier_attributes = tuple(identifier_attributes)
        self._components: dict[str, type[T] | T] = {}
        self._lock = RLock()

    def _identifier(self, component: type[T] | T) -> str:
        for attribute in self.identifier_attributes:
            value = getattr(component, attribute, None)
            if isinstance(value, str) and value.strip():
                return value
        raise RegistrationError(f"{self.kind} must declare one of {self.identifier_attributes}")

    def register(self, component: type[T] | T, *, replace: bool = False) -> str:
        identifier = self._identifier(component)
        definition = component if isinstance(component, type) else type(component)
        validator = getattr(definition, "validate", None)
        if callable(validator):
            errors = tuple(validator())
            if errors:
                raise RegistrationError("; ".join(errors))
        else:
            specification = getattr(definition, "specification", None)
            if callable(specification):
                specification()

        with self._lock:
            existing = self._components.get(identifier)
            if existing is not None and existing is not component and not replace:
                existing_definition = existing if isinstance(existing, type) else type(existing)
                if existing_definition is not definition:
                    raise RegistrationError(f"{self.kind} already registered: {identifier}")
                raise ValueError(f"{self.kind} already registered: {identifier}")
            self._components[identifier] = component
        return identifier

    def unregister(self, identifier: str) -> None:
        with self._lock:
            if identifier not in self._components:
                raise KeyError(f"Unknown {self.kind}: {identifier}")
            del self._components[identifier]

    def definition(self, identifier: str) -> type[T] | T:
        with self._lock:
            try:
                return self._components[identifier]
            except KeyError as exc:
                raise KeyError(f"Unknown {self.kind}: {identifier}") from exc

    def get(self, identifier: str, **constructor_kwargs: Any) -> T:
        component = self.definition(identifier)
        if isinstance(component, type):
            return component(**constructor_kwargs)
        if constructor_kwargs:
            raise TypeError("constructor arguments cannot be used with a registered instance")
        return component

    def identifiers(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._components))

    def clear(self) -> None:
        with self._lock:
            self._components.clear()

    def discover(
        self,
        group: str,
        *,
        allowlist: Iterable[str],
    ) -> tuple[str, ...]:
        """Load only explicitly allowlisted package entry points."""

        allowed = frozenset(allowlist)
        if not allowed:
            return ()
        discovered: list[str] = []
        entry_points = metadata.entry_points()
        selected = entry_points.select(group=group)
        for entry_point in selected:
            if entry_point.name not in allowed:
                continue
            try:
                component = entry_point.load()
                discovered.append(self.register(component))
            except Exception as exc:
                raise DiscoveryError(f"Failed to load allowlisted {self.kind} entry point: {entry_point.name}") from exc
        return tuple(sorted(discovered))


class SkillRegistry(ComponentRegistry[Any]):
    def __init__(self) -> None:
        super().__init__("Skill", ("skill_id", "component_id"))


class AgentRegistry(ComponentRegistry[Any]):
    def __init__(self) -> None:
        super().__init__("Agent", ("agent_id", "component_id"))


class AutomationRegistry(ComponentRegistry[Any]):
    def __init__(self) -> None:
        super().__init__("Automation", ("automation_id", "component_id"))


class FrameworkRegistry(ComponentRegistry[Any]):
    def __init__(self) -> None:
        super().__init__("Framework", ("framework_id", "component_id"))

    def dependency_order(self, framework_id: str) -> tuple[str, ...]:
        ordered: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(identifier: str) -> None:
            if identifier in visiting:
                raise RegistrationError(f"Framework dependency cycle includes: {identifier}")
            if identifier in visited:
                return
            visiting.add(identifier)
            framework = self.get(identifier)
            for dependency in getattr(framework, "dependencies", ()):
                visit(dependency)
            visiting.remove(identifier)
            visited.add(identifier)
            ordered.append(identifier)

        visit(framework_id)
        return tuple(ordered)


skill_registry = SkillRegistry()
agent_registry = AgentRegistry()
automation_registry = AutomationRegistry()
framework_registry = FrameworkRegistry()


class SkillRunner:
    def __init__(self, registry: SkillRegistry | None = None) -> None:
        self.registry = registry or SkillRegistry()

    def run(
        self,
        skill_id: str,
        inputs: Mapping[str, Any],
        *,
        provenance: Provenance | None = None,
        requested_by: str = "Unknown",
    ) -> SkillResult:
        return cast(
            SkillResult,
            self.registry.get(skill_id).execute(
                inputs,
                provenance=provenance,
                requested_by=requested_by,
            ),
        )


__all__ = [
    "AgentRegistry",
    "AutomationRegistry",
    "ComponentRegistry",
    "FrameworkRegistry",
    "SkillRegistry",
    "SkillRunner",
    "agent_registry",
    "automation_registry",
    "framework_registry",
    "skill_registry",
]
