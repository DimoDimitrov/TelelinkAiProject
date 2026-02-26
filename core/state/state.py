"""
State container for agents.

The project needs a simple, non-complex state:
- internally it's just a dictionary
- plus a small set of helpers for common agent needs (conversation memory)

This state is meant to be injected into prompt templates (e.g. `{state}` in
`core/prompts/prompts.py`).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class State:
    """
    Classic state class (dict-based) with getters/setters.

    By convention we store conversation history in:
        state["messages"] = [{"role": "user"|"assistant", "content": str}, ...]
    """

    def __init__(self, initial: Optional[Dict[str, Any]] = None) -> None:
        self._data: Dict[str, Any] = dict(initial or {})
        self._data.setdefault("messages", [])

    # -------------------------
    # Generic dict operations
    # -------------------------

    def get_state(self) -> Dict[str, Any]:
        return self._data

    def set_state(self, new_state: Dict[str, Any]) -> None:
        self._data = dict(new_state)
        self._data.setdefault("messages", [])

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def update(self, values: Dict[str, Any]) -> None:
        self._data.update(values)
        self._data.setdefault("messages", [])

    # -------------------------
    # Conversation helpers
    # -------------------------

    def add_message(self, role: str, content: str) -> None:
        """
        Append a single message to the conversation memory.
        """
        if role not in ("user", "assistant"):
            raise ValueError("role must be 'user' or 'assistant'")

        messages: List[Dict[str, str]] = self._data.setdefault("messages", [])
        messages.append({"role": role, "content": content})

    def add_turn(self, user: str, assistant: str) -> None:
        """
        Convenience method for adding a user+assistant turn.
        """
        self.add_message("user", user)
        self.add_message("assistant", assistant)

    def conversation_text(self, max_messages: Optional[int] = 12) -> str:
        """
        Render conversation history into a human-readable string for `{state}`.

        `max_messages` limits how many most-recent messages are shown.
        """
        messages: List[Dict[str, str]] = self._data.get("messages", [])
        if not messages:
            return "(no prior conversation)"

        if max_messages is not None and max_messages > 0:
            messages = messages[-max_messages:]

        lines: List[str] = []
        for msg in messages:
            role = msg.get("role", "user")
            content = (msg.get("content") or "").strip()
            if not content:
                continue
            prefix = "User" if role == "user" else "Assistant"
            lines.append(f"{prefix}: {content}")
        return "\n".join(lines) if lines else "(no prior conversation)"
