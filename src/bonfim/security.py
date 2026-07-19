"""Non-overridable output safety helper used by the Skill execution pipeline."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from typing import Any

SENSITIVE_KEYS = frozenset(
    {
        "password",
        "passwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "private_key",
        "credential",
        "credentials",
    }
)

SENSITIVE_VALUE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*\S+"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
)


def sensitive_paths(value: Any, path: str = "output") -> tuple[str, ...]:
    """Return paths that appear sensitive without reproducing their values."""

    matches: list[str] = []

    def walk(current: Any, current_path: str) -> None:
        if is_dataclass(current):
            for item in fields(current):
                walk(getattr(current, item.name), f"{current_path}.{item.name}")
            return
        if isinstance(current, Mapping):
            for key, item in current.items():
                key_text = str(key).lower()
                child_path = f"{current_path}.{key}"
                normalized_key = key_text.replace("-", "_").replace(".", "_")
                sensitive_key = (
                    normalized_key in SENSITIVE_KEYS
                    or normalized_key.endswith(("_password", "_secret", "_token", "_private_key", "_credential"))
                    or normalized_key.startswith(("password_", "secret_", "private_key_"))
                )
                if sensitive_key:
                    matches.append(child_path)
                else:
                    walk(item, child_path)
            return
        if isinstance(current, (list, tuple, set, frozenset)):
            for index, item in enumerate(current):
                walk(item, f"{current_path}[{index}]")
            return
        if isinstance(current, str) and any(pattern.search(current) for pattern in SENSITIVE_VALUE_PATTERNS):
            matches.append(current_path)

    walk(value, path)
    return tuple(sorted(set(matches)))
