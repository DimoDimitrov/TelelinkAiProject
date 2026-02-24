"""
The interaction with the 'Must' requirements agent can be done here.

"""

import os
from dotenv import load_dotenv
from google import genai
from langsmith import wrappers
# from google.colab import userdata


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

    # Make a traced Gemini call
    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents="Explain how AI works in a few words"
    )

    print(response.text)


if __name__ == "__main__":
    main()