"""Generated from the official Bonfim Automation template."""

from bonfim import Automation


class {{ class_name }}(Automation):
    automation_id = "{{ component_id }}"
    name = "{{ display_name }}"
    version = "0.1.0"
    description = "Run a trigger-controlled, observable workflow."
    triggers = ("manual",)
    workflow = ()
    max_retries = 0
    rollback_on_failure = True
