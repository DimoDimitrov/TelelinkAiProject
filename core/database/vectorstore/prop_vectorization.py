"""
Vectorization of the property documents is done in this file.

The documents are plain `.txt` files. We simply:

- read the raw text from each file,
- get an embedding vector for that text via `Embedder`,
- store it in Chroma via `ChromaOperator`.

You can test Chroma persistence with either a single file or an entire
directory of property files.
"""

import argparse
import os
from typing import List

from core.database.embedder import Embedder
from core.database.vectorstore.prop_chroma import ChromaOperator


# Use raw string to avoid invalid escape sequences on Windows paths
CHROMA_LOCATION = r"D:\Codes\Projects\TelelinkAiProject\TelelinkAiProject\persist_gemini\properties"
CHROMA_COLLECTION_NAME = "properties"


def vectorize_file(file_path: str) -> None:
    """
    Read a single .txt file as raw text, embed it, and upsert into Chroma.
    One Chroma document = one file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        return

    embedder = Embedder("gemini-embedding-001")
    chroma = ChromaOperator(
        location=CHROMA_LOCATION,
        collection_name=CHROMA_COLLECTION_NAME,
    )

    file_id = os.path.basename(file_path)
    ids: List[str] = [file_id]
    documents: List[str] = [text]
    metadatas: List[dict] = [
        {
            "source": file_path,
            "filename": file_id,
        }
    ]

    embeddings = embedder.embed_texts(documents)

    chroma.upsert_vectors(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def vectorize_directory(directory_path: str) -> None:
    """
    Read all `.txt` files in a directory, embed each whole file, and upsert
    them into Chroma. One Chroma document per file.
    """
    embedder = Embedder("gemini-embedding-001")
    chroma = ChromaOperator(
        location=CHROMA_LOCATION,
        collection_name=CHROMA_COLLECTION_NAME,
    )

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[dict] = []

    for file_name in os.listdir(directory_path):
        if not file_name.lower().endswith(".txt"):
            continue
        full_path = os.path.join(directory_path, file_name)

        with open(full_path, "r", encoding="utf-8") as f:
            text = f.read()

        if not text.strip():
            continue

        ids.append(file_name)
        documents.append(text)
        metadatas.append(
            {
                "source": full_path,
                "filename": file_name,
            }
        )

    if not documents:
        return

    embeddings = embedder.embed_texts(documents)

    chroma.upsert_vectors(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def main() -> None:
    """
    Simple entrypoint to test Chroma persistence.

    For now this is hard-wired to:
    - create/get the `properties` collection
    - vectorize a single test file (p1.txt)
    """
    co = ChromaOperator(CHROMA_LOCATION, CHROMA_COLLECTION_NAME)
    co.client_create()  # safe even if already created
    co.get_or_create_collection()

    # file_path = r"D:\Codes\Projects\TelelinkAiProject\TelelinkAiProject\documents\properties\p1.txt"
    file_path =r""
    dir_path=r"D:\Codes\Projects\TelelinkAiProject\TelelinkAiProject\documents\properties"

    # vectorize_file(file_path)
    vectorize_directory(dir_path)


if __name__ == "__main__":
    main()
    # To RUN:
    # python -m core.database.vectorstore.prop_vectorization
