"""Generated from the official Bonfim Skill template."""

from bonfim import Skill, SkillContext, SkillOutput


class {{ class_name }}(Skill):
    skill_id = "{{ component_id }}"
    name = "{{ display_name }}"
    version = "0.1.0"
    mission = "Describe the bounded capability."
    scope = ("Declare allowed work",)
    out_of_scope = ("External mutation", "Institutional decisions")
    activation_conditions = ("Explicit invocation",)
    required_inputs = ("value",)

    def perform(self, context: SkillContext) -> SkillOutput:
        return self.output(
            "Execution completed; human review is required.",
            findings=(f"Input was observed: {context.inputs['value']!r}.",),
            limitations=("Generated template; domain validation is not implemented.",),
            confidence="Low",
            confidence_justification="Only structural validation was performed.",
            final_verdict="Review Required",
        )
