"""Generated from the official Bonfim Agent template."""

from bonfim import Agent


class {{ class_name }}(Agent):
    agent_id = "{{ component_id }}"
    name = "{{ display_name }}"
    version = "0.1.0"
    description = "Coordinate an explicit allowlist of Skills."
    skill_ids = ("REPLACE-WITH-SKILL-ID",)
    max_workers = 4
    allow_parallel = True
