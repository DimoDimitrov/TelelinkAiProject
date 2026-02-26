import os, sys
from dotenv import load_dotenv
from google import genai
from langsmith import wrappers

from agents.must.must_agent import MustAgent, MustAgentConfig
from core.database.vectorstore.prop_vectorization import (
    CHROMA_LOCATION,
    CHROMA_COLLECTION_NAME,
)
from core.database.vectorstore.prop_retriever import PropertyRetriever

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def main():
    load_dotenv()
    gemini_key = os.getenv("GOOGLE_API_KEY")

    # genai.Client() reads GOOGLE_API_KEY / GEMINI_API_KEY from the environment
    gemini_client = genai.Client(api_key=gemini_key)

    # Wrap the Gemini client to enable LangSmith tracing
    client = wrappers.wrap_gemini(
        gemini_client,
        tracing_extra={
            "tags": ["gemini", "python"],
            "metadata": {
                "integration": "google-genai",
            },
        },
    )

    retriever = PropertyRetriever(
        location=CHROMA_LOCATION,
        collection_name=CHROMA_COLLECTION_NAME,
    )

    agent = MustAgent(
        client,
        retriever=retriever,
        config=MustAgentConfig(
            model="gemini-2.5-flash",
            max_state_messages=6,
            use_rag=True,
            rag_top_k=3,
        ),
    )

    print("Agent ready. Enter a question (empty to exit).")
    while True:
        question = input("User > ").strip()
        if not question:
            break
        answer = agent.ask(question)
        print("Agent > " + answer)
        print()


if __name__ == "__main__":
    main()

# TO RUN: 
# python -m exec.main_must_agent