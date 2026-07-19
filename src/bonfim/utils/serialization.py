"""Deterministic serialization and immutable mapping helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any


def freeze_mapping(value: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
    """Copy a mapping into a read-only top-level view."""

    return MappingProxyType(dict(value or {}))


def serialize(value: Any) -> Any:
    """Convert SDK records into JSON-compatible Python values."""

    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {item.name: serialize(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): serialize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [serialize(item) for item in value]
    return value
