#!/usr/bin/env python3
"""Measure and enforce a conservative registry-operation performance baseline."""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

from bonfim.registry import SkillRegistry


class _BenchmarkSkill:
    skill_id = "BENCHMARK-SKILL-001"

    @classmethod
    def validate(cls) -> tuple[()]:
        return ()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=20_000)
    parser.add_argument("--min-operations-per-second", type=float, default=5_000.0)
    parser.add_argument("--output")
    args = parser.parse_args()

    if args.iterations < 1:
        raise SystemExit("iterations must be positive")
    if args.min_operations_per_second <= 0:
        raise SystemExit("min-operations-per-second must be positive")

    registry = SkillRegistry()
    started = time.perf_counter()
    for _ in range(args.iterations):
        registry.register(_BenchmarkSkill, replace=True)
        registry.definition(_BenchmarkSkill.skill_id)
        registry.identifiers()
    elapsed = time.perf_counter() - started

    operation_count = args.iterations * 3
    operations_per_second = operation_count / elapsed if elapsed else float("inf")
    passed = operations_per_second >= args.min_operations_per_second

    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "result": "Passed" if passed else "Failed",
        "iterations": args.iterations,
        "operationCount": operation_count,
        "elapsedSeconds": round(elapsed, 6),
        "operationsPerSecond": round(operations_per_second, 2),
        "minimumOperationsPerSecond": args.min_operations_per_second,
        "scope": "single-process SkillRegistry register/definition/identifiers baseline",
        "limitations": [
            "This is a conservative regression guard, not a production capacity or latency SLO.",
            "Network, storage and downstream execution performance are outside the SDK library boundary."
        ],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = Path.cwd() / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
