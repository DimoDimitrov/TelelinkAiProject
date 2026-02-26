import os
from dotenv import load_dotenv
from google import genai
from langsmith import wrappers


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

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Explain how AI works in a few words",
    )
    print("Generation:", response.text)


# prompt builder
# from core.prompts.prompt_builder import make_must_agent_prompt

# state = "...conversation history here..."
# question = "User's current question"

# prompt = make_must_agent_prompt(state, question)

# response = client.models.generate_content(
#     model="gemini-2.0-flash",
#     contents=prompt,
# )

# state


# rag


if __name__ == "__main__":
    main()