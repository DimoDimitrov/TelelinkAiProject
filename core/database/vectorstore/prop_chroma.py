"""
This file's purrpose is to define the ChromaDB vectorstore that will be used for the properties. 
(And other if needed)

"""

import chromadb
from sentence_transformers import SentenceTransformer

class ChromaOperator():
    def __init__():
# I am making a class that would take the whole chroma vectorstore opperations of the project. 
# I need to check if the client persists between runs
# Complete the methods of teh documentation
# Fix the class itself (Constructor, this fields, methods fix)


    def client_create(locaion):
        client = chromadb.PersistentClient(path=location) 

    def create_collection(nameC, client):
        collection = client.create_collection(name=nameC)

    def get_collection(nameC, client):
        collection = client.get_collection(name=nameC)

    def get_or_create_collection(nameC, client):
        collection = client.get_or_create_collection(name=nameC)

    def list_collections(nameC, client):
        print(client.list_collections())

    def delete_collection(nameC, client):
        client.delete_collection(name=nameC)
        return

    # Import embeddings from embedding.py

    def view_vectors(nameC, client):
        # Get everything in the collection
        collection = get_collection(name=nameC)
        results = collection.get(include=["documents", "embeddings", "metadatas"])
        print(results["documents"])     # The text
        print(results["metadatas"])     # Any metadata dicts
        print(results["embeddings"])    # The actual float vectors

        # Get specific items by ID
        results = collection.get(ids=["doc1", "doc2"], include=["documents", "embeddings"])

        # Count items in the collection
        print(collection.count())


def main():
    # Create collection
    chroma = new ChromaOperator()
    client = chroma.client_create(path="D:\Codes\Projects\TelelinkAiProject\TelelinkAiProject\persist_gemini\properties") 







# Database creation
# Vectorization (embeddings)
# Update methods for the vectors
# Clean-up method
# Turnicate method 
# Drop method


