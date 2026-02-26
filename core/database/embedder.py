"""
This is an embedding module that can turn one or more text strings into
numerical embeddings using Google's Gemini text-embedding model.
"""

from typing import Iterable, List
import os
import time

from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv


class Embedder:
    def __init__(self, model: str = "gemini-embedding-001") -> None:
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY environment variable is not set.")

        self._client = genai.Client(api_key=api_key)
        self.model = model

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        """
        Embed a sequence of plain text strings, returning one vector per string.
        Sends all texts in a single API call. Falls back to smaller chunks
        with retries if rate-limited.
        """
        clean_texts = [t for t in texts if t and t.strip()]
        if not clean_texts:
            return []

        try:
            result = self._client.models.embed_content(
                model=self.model,
                contents=clean_texts,
            )
            # print(f"[Embedder] Done. {len(result.embeddings)} vectors generated.")
            return [getattr(emb, "values", emb) for emb in result.embeddings]

        except genai_errors.ClientError as e:
            if "429" not in str(e) and "RESOURCE_EXHAUSTED" not in str(e):
                raise

            print(
                "[Embedder] Rate limit hit on full batch.\n"
                "  Falling back to chunks of 5 with 15s delay between them.\n"
                "  If every chunk fails, your daily quota is exhausted.\n"
                "  Fix: create a new API key at aistudio.google.com/apikey\n"
                "       under a DIFFERENT Google account."
            )

        # Fallback: chunks of 5 with delays and retries
        all_vectors: List[List[float]] = []
        chunk_size = 5

        for i in range(0, len(clean_texts), chunk_size):
            chunk = clean_texts[i: i + chunk_size]
            attempts = 0

            while attempts < 3:
                try:
                    result = self._client.models.embed_content(
                        model=self.model,
                        contents=chunk,
                    )
                    all_vectors.extend(
                        getattr(emb, "values", emb) for emb in result.embeddings
                    )
                    print(
                        f"[Embedder] Chunk {i // chunk_size + 1} done "
                        f"({len(all_vectors)}/{len(clean_texts)} vectors)."
                    )
                    break

                except genai_errors.ClientError as e:
                    if "429" not in str(e) and "RESOURCE_EXHAUSTED" not in str(e):
                        raise
                    attempts += 1
                    wait = 30 * attempts  # 30s, 60s, 90s
                    print(f"[Embedder] Rate limited. Waiting {wait}s (attempt {attempts}/3)...")
                    time.sleep(wait)
            else:
                raise RuntimeError(
                    "Rate limit persisted after 3 retries. Daily quota is exhausted.\n"
                    "Fix: create a new API key at aistudio.google.com/apikey\n"
                    "     under a DIFFERENT Google account, then update GOOGLE_API_KEY in .env"
                )

            if i + chunk_size < len(clean_texts):
                time.sleep(15)

        return all_vectors