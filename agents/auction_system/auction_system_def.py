"""
Auction system definition.

This module wires together:
- The orchestrator agent
- Multiple buyer agents
- A shared STATE object that tracks the entire auction

The current implementation is a plain Python orchestration loop that is
*LangGraph-ready*: each of the methods here can be plugged into LangGraph
nodes later. For now, this gives you a working, testable auction system
with explicit STATE passing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agents.auction_system.buyer_agent import BuyerAgent, BuyerConfig
from agents.auction_system.orchestrator_agent import OrchestratorAgent
from core.state.state import State


@dataclass
class AuctionState:
    """
    Shared state for a single auction run.
    """

    conversation: State = field(default_factory=State)

    orchestrator_state: State = field(default_factory=State)
    buyer_states: Dict[str, State] = field(default_factory=dict)

    property_id: Optional[str] = None
    property_text: Optional[str] = None
    round: int = 0
    status: str = "not_started"

    current_highest_bid: Optional[float] = None
    current_highest_bidder: Optional[str] = None

    history: List[Dict[str, Any]] = field(default_factory=list)


class AuctionSystem:
    """
    High-level auction system: orchestrator + buyer agents + shared state.

    This is intentionally simple and explicit so it can be migrated to a
    LangGraph `StateGraph` later with minimal changes.
    """

    def __init__(
        self,
        orchestrator: OrchestratorAgent,
        buyers: Dict[str, BuyerAgent],
        state: Optional[AuctionState] = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.buyers = buyers
        self.state = state or AuctionState()

        for name in buyers.keys():
            self.state.buyer_states.setdefault(name, State())

    def run_single_auction(self, property_id: str, property_text: str) -> AuctionState:
        """
        Run a full auction for a single property until completion.

        - Sets up the state
        - Lets the orchestrator start the auction
        - Runs bidding rounds where each buyer may bid or pass
        - Stops when the orchestrator determines the auction is closed
        """
        self.state.property_id = property_id
        self.state.property_text = property_text
        self.state.round = 0
        self.state.status = "not_started"
        self.state.current_highest_bid = None
        self.state.current_highest_bidder = None
        self.state.history.clear()

        self.orchestrator.start_auction(self.state)

        while self.state.status == "in_progress":
            self.state.round += 1

            for buyer_name, buyer in self.buyers.items():
                buyer_state = self.state.buyer_states[buyer_name]
                action = buyer.decide_action(
                    state=self.state,
                    buyer_state=buyer_state,
                )

                record: Dict[str, Any] = {
                    "round": self.state.round,
                    "buyer": buyer_name,
                    "action": action["action"],
                    "amount": action.get("amount"),
                    "reason": action.get("reason"),
                }
                self.state.history.append(record)

                if action["action"] == "BID" and action.get("amount") is not None:
                    amount = float(action["amount"])
                    if (
                        self.state.current_highest_bid is None
                        or amount > self.state.current_highest_bid
                    ):
                        self.state.current_highest_bid = amount
                        self.state.current_highest_bidder = buyer_name

            self.orchestrator.update_after_round(self.state)

        return self.state
