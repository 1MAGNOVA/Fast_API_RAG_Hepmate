import chromadb 
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
    )

# Load the knowledge-base document
with open("knowledge_base.txt", "r") as f:
    text = f.read()

# break the chunks into paragraphs -   
chunks = [chunk.strip() for chunk in text.split('\n\n')]
print(f"Loaded {len(chunks)} chunks from knowledge_abse.text")


#init chromadb with ollama embeddings

client = chromadb.PersistentClient(path="./chroma_db")

#now we'll connect to Ollama's embedding model to conevert into vectors
ef = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434",  # Ollama's default local address
)

# Create (or reuse) a collection - like a table in a database
collection = client.get_or_create_collection(
    name="Hepmate_questions",
    embedding_function=ef,  # Tells ChromaDB how to convert text to vectors
)  


# Add chunks to the collection - ChromaDB automatically generates embeddings
collection.add(
    ids=[f"chunk{i}" for i in range(len(chunks))],  # Unique ID for each chunk
    documents=chunks,  # The actual text content
    metadatas=[{"source": "questions", "chunk_index": i} for i in range(len(chunks))],
)

print(f"Added {len(chunks)} chunks to the 'hepmate_questions' collection.")
print("Knowledge base built successfully!")