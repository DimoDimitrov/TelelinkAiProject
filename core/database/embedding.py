"""
This file is responsible for the embedding process for the documents.
Reader is handled by appropriate classes that will be used with this class.

"""

import google.generativeai as genai
from config import GEMIMINI_API_KEY

# Use reader to get all the info into the needed format

genai.configure(api_key=GEMIMINI_API_KEY)

# Embedding the content
result = genai.embed_content(
    model="models/text-embedding-004",
    content="Your text here",
    task_type="retrieval_document"  # or retrieval_query, classification, etc.
)

embedding = result['embedding']  # 768-dim vector


#  Example
# model = SentenceTransformer("all-MiniLM-L6-v2")

# docs = [
#     "The sky is blue",
#     "The grass is green",
#     "Cats love naps"
# ]

# embeddings = model.encode(docs).tolist()

# collection.add(
#     documents=docs,
#     embeddings=embeddings,
#     ids=["doc1", "doc2", "doc3"]
# )