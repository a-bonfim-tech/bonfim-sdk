"""Generated from the official Bonfim Framework template."""

from bonfim import Framework


class {{ class_name }}(Framework):
    framework_id = "{{ component_id }}"
    name = "{{ display_name }}"
    version = "0.1.0"
    description = "Define the framework purpose and authority boundary."
    dependencies = ()
