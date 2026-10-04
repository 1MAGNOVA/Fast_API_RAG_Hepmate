from fastapi import FastAPI
import ollama 
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

app = FastAPI() #this creates the fasapi app

client = chromadb.PersistentClient("./chroma_db")

#declaring the embedded function
ef = OllamaEmbeddingFunction(
    model_name ="nomic-embed-text", 
    url="http://localhost:11434",
)
collection = client.get_or_create_collection(
    name="hepmate_questions", 
    embedding_function=ef,
)

@app.get("/ask") # this will create a GET endpoint at /ask

def ask(question: str): #fastapi will read the question directly from the query string
    # RAG =- retrieves, augments and generates the response
    results = collection.query(
        query_texts=[question],
        n_results=2
    ) 

    context = "\n\n".join(results["documents"][0])

    #Augment the prompt

    aug_prompt = f"""Use the following context to answer the question.
                If the context doesn't contain relevant information, say so.

                Context:
                {context}

                Question: {question}"""

    # Step 3: GENERATE - send the augmented prompt to the local LLM
    response = ollama.chat(
                        model="qwen2.5:0.5b",
                        messages=[{"role": "user", "content": aug_prompt}],
                    )

    # Return the answer along with the context so users can verify the source
    return {
                        "question": question,
                        "answer": response["message"]["content"],
                        "context_used": results["documents"][0],
                    }
