"""
Utilities for building prompts for agents.

`PromptBuilder` takes:
- a prompt template (with placeholders like {state} and {question})
- the current state of the agent / conversation
- the current user question

and returns a single string that can be passed as the `contents` argument
to the Gemini client.
"""

from dataclasses import dataclass

from core.prompts.prompts import MUST_AGENT_PROMPT


@dataclass
class PromptBuilder:
    """
    Simple prompt builder that fills a string template with
    the agent's state and the current question.
    """

    template: str

    def build(self, state: str, question: str) -> str:
        """
        Render the final prompt by formatting the template.

        The template is expected to contain `{state}` and `{question}`
        placeholders (as in `MUST_AGENT_PROMPT`).
        """
        return self.template.format(state=state, question=question)


def make_must_agent_prompt(state: str, question: str) -> str:
    """
    Convenience helper for the Must agent specifically.

    Example usage in the agent:

        prompt = make_must_agent_prompt(state, user_question)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
    """
    builder = PromptBuilder(MUST_AGENT_PROMPT)
    return builder.build(state=state, question=question)