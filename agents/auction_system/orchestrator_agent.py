"""
Orchestrator agent definition.

The orchestrator:
- Starts an auction for a given property
- Monitors each round
- Decides when the auction is closed
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.prompts.prompts import ORCHESTRATOR_AGENT_PROMPT
from core.prompts.prompt_builder import PromptBuilder
from core.state.state import State
from agents.auction_system.auction_system_def import AuctionState


@dataclass
class OrchestratorConfig:
    model: str = "gemini-2.5-flash"


class OrchestratorAgent:
    """
    Simple orchestrator on top of the Gemini client and a prompt template.
    """

    def __init__(
        self,
        client: Any,
        *,
        state: State | None = None,
        config: OrchestratorConfig | None = None,
    ) -> None:
        self.client = client
        self.state = state or State()
        self.config = config or OrchestratorConfig()
        self.prompt_builder = PromptBuilder(ORCHESTRATOR_AGENT_PROMPT)

    def start_auction(self, auction_state: AuctionState) -> None:
        """
        Mark auction as started and create an initial log entry.
        """
        auction_state.status = "in_progress"
        self.state.add_message(
            "assistant",
            f"Starting auction for property {auction_state.property_id or 'unknown'}",
        )

    def update_after_round(self, auction_state: AuctionState) -> None:
        """
        After each full bidding round, decide whether to continue or close.

        For now, the logic is simple:
        - If there is at least one bid in this round, continue to next round (up to a limit)
        - If no new bids appeared in this round, close the auction

        This method can be made more sophisticated later and/or delegated to the LLM.
        """	
        last_round = auction_state.round
        round_events = [h for h in auction_state.history if h["round"] == last_round]
        had_bid = any(e["action"] == "BID" for e in round_events)

        state_text = self.state.conversation_text(max_messages=8)

        if had_bid and last_round < 10:
            auction_state.status = "in_progress"
            summary = (
                f"Round {last_round} completed. "
                f"Highest bid so far: {auction_state.current_highest_bid} "
                f"from {auction_state.current_highest_bidder}."
            )
        else:
            auction_state.status = "closed"
            if auction_state.current_highest_bidder is None:
                summary = (
                    f"Auction closed after round {last_round} with no valid bids. "
                    "Result: no sale."
                )
            else:
                summary = (
                    f"Auction closed after round {last_round}. "
                    f"Winner: {auction_state.current_highest_bidder} "
                    f"with {auction_state.current_highest_bid} EUR."
                )

        question = summary
        prompt = self.prompt_builder.build(state=state_text, question=question)

        response = self.client.models.generate_content(
            model=self.config.model,
            contents=prompt,
        )
        text = getattr(response, "text", "").strip()

        self.state.add_message("user", question)
        self.state.add_message("assistant", text or summary)
