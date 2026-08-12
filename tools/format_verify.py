#!/usr/bin/env python3
"""Verify repository text-formatting invariants without modifying source files."""

from __future__ import annotations

import argparse
import ast
import json
from datetime import UTC, datetime
from pathlib import Path

ROOTS = ("src", "tests", "examples", "tools")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()

    root = Path.cwd()
    errors: list[str] = []
    checked = 0

    for root_name in ROOTS:
        directory = root / root_name
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.py")):
            checked += 1
            relative = path.relative_to(root).as_posix()
            raw = path.read_bytes()
            if b"\r\n" in raw or b"\r" in raw:
                errors.append(f"{relative}: non-LF line ending")
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                errors.append(f"{relative}: invalid UTF-8")
                continue
            if text and not text.endswith("\n"):
                errors.append(f"{relative}: missing final newline")
            for number, line in enumerate(text.splitlines(), start=1):
                if line.rstrip(" \t") != line:
                    errors.append(f"{relative}:{number}: trailing whitespace")
                leading = line[: len(line) - len(line.lstrip(" \t"))]
                if "\t" in leading:
                    errors.append(f"{relative}:{number}: tab indentation")
            try:
                ast.parse(text, filename=relative)
            except SyntaxError as exc:
                errors.append(f"{relative}:{exc.lineno or 0}: syntax error: {exc.msg}")

    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "filesChecked": checked,
        "result": "Passed" if not errors else "Failed",
        "errors": errors,
        "policy": {
            "encoding": "UTF-8",
            "lineEndings": "LF",
            "finalNewline": True,
            "trailingWhitespace": False,
            "tabIndentation": False,
            "pythonSyntax": "parseable",
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = root / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
