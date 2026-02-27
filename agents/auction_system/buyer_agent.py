"""
Buyer agent definition.

Each buyer agent:
- Has its own STATE memory
- Has a budget and preferences (encoded in its config + prompt)
- Receives the current auction state and decides whether to BID or PASS
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from google import genai 

from core.prompts.prompts import BUYER_AGENT1_PROMPT, BUYER_AGENT2_PROMPT
from core.prompts.prompt_builder import PromptBuilder
from core.state.state import State


@dataclass
class BuyerConfig:
    name: str
    budget: float
    prompt_template: str


class BuyerAgent:
    """
    Generic buyer agent that can be configured via `BuyerConfig`.

    It uses a Gemini client-like object (can be LangSmith-wrapped) that exposes
    `client.models.generate_content(...)`.
    """

    def __init__(
        self,
        client: Any,
        config: BuyerConfig,
    ) -> None:
        self.client = client
        self.config = config
        self.prompt_builder = PromptBuilder(config.prompt_template)

    def _build_question(self, auction_state, buyer_state: State) -> str:
        """
        Build a concise 'question' string describing the current situation for this buyer.
        """
        prop_id = auction_state.property_id or "unknown property"
        current_bid = auction_state.current_highest_bid
        current_bidder = auction_state.current_highest_bidder

        lines = [
            f"You are {self.config.name}. Your budget is {self.config.budget:.0f} EUR.",
            f"Property ID: {prop_id}.",
        ]

        if auction_state.property_text:
            lines.append("Property description:")
            lines.append(auction_state.property_text.strip())

        if current_bid is None:
            lines.append("There is currently no active bid.")
        else:
            who = current_bidder or "unknown buyer"
            lines.append(
                f"The current highest bid is {current_bid:.0f} EUR from {who}."
            )

        lines.append(
            "Decide whether you want to PASS or place a BID within your budget."
        )

        return "\n".join(lines)

    def decide_action(
        self,
        state,
        buyer_state: State,
    ) -> Dict[str, Any]:
        """
        Decide whether to BID or PASS for the current round.

        Returns a dict with at least:
        - action: "BID" or "PASS"
        - amount: float or None
        - reason: short explanation
        """
        state_text = buyer_state.conversation_text(max_messages=8)
        question = self._build_question(state, buyer_state)

        prompt = self.prompt_builder.build(state=state_text, question=question)

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = getattr(response, "text", "").strip()

        action = "PASS"
        amount = None

        upper = text.upper()
        if "BID" in upper:
            import re

            m = re.search(r"(\d[\d\.,]*)", text)
            if m:
                num_str = m.group(1).replace(".", "").replace(",", "")
                try:
                    val = float(num_str)
                    if val <= self.config.budget:
                        action = "BID"
                        amount = val
                except ValueError:
                    pass

        buyer_state.add_message("user", question)
        buyer_state.add_message("assistant", text)

        reason = text if len(text) < 500 else text[:500] + " ..."

        return {
            "action": action,
            "amount": amount,
            "reason": reason,
        }
