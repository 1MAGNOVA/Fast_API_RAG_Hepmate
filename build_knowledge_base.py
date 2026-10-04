import chromadb 
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
    )

# Load the knowledge-base document
with open("profile.txt", "r") as f:
    text = f.read()

# break the chunks into paragraphs -   
