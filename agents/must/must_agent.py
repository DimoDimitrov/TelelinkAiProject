"""
Must agent implementation.

This agent wires together:
- Gemini client (`google.genai.Client` optionally wrapped by LangSmith)
- Prompt template + builder
- Simple in-memory State (conversation history)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, List

from core.database.vectorstore.prop_retriever import PropertyRetriever, RetrievedProperty
from core.prompts.prompt_builder import make_must_agent_prompt
from core.state.state import State


@dataclass
class MustAgentConfig:
    model: str = "gemini-2.0-flash"
    max_state_messages: int = 6
    use_rag: bool = True
    rag_top_k: int = 3


class MustAgent:
    def __init__(
        self,
        client: Any,
        *,
        state: Optional[State] = None,
        retriever: Optional[PropertyRetriever] = None,
        config: Optional[MustAgentConfig] = None,
    ) -> None:
        """
        `client` is expected to be a Gemini client (or a LangSmith-wrapped client)
        that exposes `client.models.generate_content(...)`.
        """
        self.client = client
        self.state = state or State()
        self.retriever = retriever
        self.config = config or MustAgentConfig()

    def ask(self, question: str) -> str:
        """
        Ask the agent a question and update state with this interaction.
        """
        question = (question or "").strip()
        if not question:
            raise ValueError("question must be a non-empty string")

        state_text = self.state.conversation_text(
            max_messages=self.config.max_state_messages
        )

        # Optional RAG: retrieve relevant properties from Chroma
        if self.retriever and self.config.use_rag:
            retrieved: List[RetrievedProperty] = self.retriever.retrieve(
                query=question,
                n_results=self.config.rag_top_k,
            )
            if retrieved:
                lines = ["Relevant property documents:"]
                for idx, item in enumerate(retrieved, start=1):
                    meta = item.metadata or {}
                    src = meta.get("filename") or meta.get("source") or "unknown source"
                    header = f"[Property {idx}] (source: {src})"
                    lines.append(header)
                    lines.append(item.text.strip())
                    lines.append("")
                context_block = "\n".join(lines).strip()
                state_text = f"{state_text}\n\n{context_block}"
        prompt = make_must_agent_prompt(state=state_text, question=question)

        response = self.client.models.generate_content(
            model=self.config.model,
            contents=prompt,
        )

        answer = getattr(response, "text", None) or str(response)

        # Update conversation memory
        self.state.add_message("user", question)
        self.state.add_message("assistant", answer)

        return answer

