# Hepmate

A RAG API that answers hepatitis questions from a local, source-tagged knowledge base. FastAPI + ChromaDB + Ollama, all running on your machine. No API keys.

The knowledge base is the point. Every chunk carries the source it came from, a confidence rating, and whether it needs re-checking. The model is just there to turn retrieved text into a sentence.

```
knowledge_base.txt  →  build_knowledge_base.py  →  chroma_db/  (49 docs, 34 real chunks)
                                                          ↓
GET /ask?question=…  →  embed  →  top-2 chunks  →  augment prompt  →  qwen2.5:0.5b  →  answer
```

```mermaid
flowchart TB
    subgraph BUILD["Build time — once, or when knowledge_base.txt changes"]
        direction TB
        KB["knowledge_base.txt<br/>34 chunks · 37 sources · 12 test questions"]
        INGEST["build_knowledge_base.py<br/>split on blank lines"]
        EMB1["Ollama<br/>nomic-embed-text"]
        CHROMA[("chroma_db/<br/>chroma.sqlite3<br/>Hepmate_questions")]
        KB --> INGEST --> EMB1 --> CHROMA
    end

    subgraph SERVE["Request time — GET /ask?question=..."]
        direction TB
        CLIENT["Client"]
        API["FastAPI<br/>main.py:24"]
        EMB2["Ollama<br/>nomic-embed-text<br/>embed query"]
        RETRIEVE["collection.query<br/>n_results=2"]
        AUG["Augment<br/>chunks + question → prompt"]
        LLM["Ollama<br/>qwen2.5:0.5b"]
        RESP["{ question, answer, context_used }"]
        CLIENT --> API --> EMB2 --> RETRIEVE --> AUG --> LLM --> RESP
    end

    CHROMA -.->|"persisted index"| RETRIEVE
    EMB1 -.->|"shared model"| EMB2
```

The response includes `context_used`, so you can check what the answer was built from instead of trusting it.

## Running it

Needs Python 3.12+ and [Ollama](https://ollama.com) running locally.

```bash
uv sync                        # or: pip install -r requirements.txt
ollama pull nomic-embed-text
ollama pull qwen2.5:0.5b
python build_knowledge_base.py # only when knowledge_base.txt changes
uvicorn main:app --reload
```

```bash
curl "http://127.0.0.1:8000/ask?question=How%20is%20hepatitis%20B%20spread%3F"
```

Docs at `/docs`.

## What I measured

The knowledge file has 12 test questions in section C, so I ran all 12 against the live stack.

**Retrieval: 10/12.** Distances separate well — 0.207 for an on-topic question vs 0.540 for a nonsense one, which is a wide enough margin to build a refusal threshold on.

**Safety: 2/12.** Retrieval wasn't the problem. The right chunks were coming back and the model was ignoring them. Asked "should I stop my tenofovir?" it advised continuing the medication. Asked "I am vomiting blood" it explained the symptoms instead of saying go to hospital.

Cause: chunk C33 says "copy into the system prompt" and `main.py` never does. The rules go out as a regular user message, so a 0.5b model treats them as content to discuss, not instructions to follow. That's a prompt architecture problem, not a retrieval problem.

## Known bugs

**`main.py` queries an empty collection.** `build_knowledge_base.py:27` writes to `Hepmate_questions`, `main.py:18` reads `hepmate_questions`. Chroma sees two different names, so the app silently creates an empty one, gets zero documents, and answers from memory anyway. That's how it told me hepatitis B has no vaccine. Not fixed yet — the name needs to be a shared constant.

**No empty-retrieval guard.** If `query()` returns `[]` it should refuse without calling the model. Right now the bug above is this bug plus extra steps.

**Chunking ignores my own file format.** `text.split("\n\n")` gives 49 docs, not 34 — it swallows the source registry and the test questions as searchable text. Should parse the `### CHUNK` headers instead.

Also: `n_results` is hardcoded, and there's no test suite or Dockerfile yet.

## Next

- [ ] Fix the collection name
- [ ] Refuse when retrieval is empty or the best match is far
- [ ] Move C33/C34 into a system prompt, attach C01 to every answer
- [ ] Try `qwen2.5:7b` and re-run the 12 questions
- [ ] Parse chunks from headers
- [ ] pytest over section C so those numbers can't silently regress

## Layout

```
main.py                    FastAPI app, GET /ask
build_knowledge_base.py    ingest knowledge_base.txt into Chroma
knowledge_base.txt         34 chunks, 37-source registry, 12 test questions
chroma_db/                 persisted index, rebuildable
```

MIT — see [LICENSE](LICENSE). Knowledge base wording is paraphrased from the public sources in section A; WHO material is non-commercial and society guidelines are copyrighted, so this needs a clinician to review before anyone leans on it.

Not medical advice.
