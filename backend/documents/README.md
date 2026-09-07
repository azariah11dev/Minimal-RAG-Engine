# 📘 RAG Backend — Document Ingestion & Vector Storage

A modular **Retrieval-Augmented Generation (RAG) backend** built with **FastAPI, Qdrant, Sentence Transformers, and Ollama**.

The system handles the core RAG pipeline from document ingestion through retrieval and response generation:

```text
Document Upload
      ↓
Text Extraction
      ↓
Recursive Chunking
      ↓
Embedding Generation
      ↓
Qdrant Vector Storage
      ↓
Query Rewriting
      ↓
Dense Retrieval
      ↓
Cross-Encoder Reranking
      ↓
Context Assembly
      ↓
LLM Generation
      ↓
Grounded Answer
```

The project is designed as a foundation for a larger RAG system, with the backend separated into ingestion, retrieval, reranking, and generation components.

---

## 🚀 Features

### Document Ingestion

* Upload documents through a FastAPI endpoint
* Supports:

  * `.txt`
  * `.pdf`
  * `.docx`
* File-type-specific text extraction
* Recursive text chunking
* Default chunk size of **2,000 characters**
* Permanent copies of uploaded files stored locally

### Embeddings & Vector Storage

* Embeddings generated using `BAAI/bge-m3`
* Embeddings normalized for cosine similarity
* Persistent **Qdrant** vector database
* Qdrant runs as a Docker service
* Automatic metadata storage for each document chunk

### Retrieval & Reranking

* Query embedding using the same embedding model
* Dense vector retrieval through Qdrant
* Cross-encoder reranking using:

```python
BAAI/bge-reranker-base
```

* Top-k results ranked by relevance
* Source metadata returned alongside retrieved chunks

### RAG Response Generation

* Query rewriting
* Dense retrieval
* Cross-encoder reranking
* Context assembly
* LLM-powered answer generation
* Streaming responses
* Local LLM inference through **Ollama**

---

## 🏗️ Architecture

The backend is organized into separate layers for API endpoints, schemas, services, and model infrastructure.

```text
                        ┌─────────────────┐
                        │     FastAPI     │
                        └────────┬────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
        Document Upload                    Query / Answer
                 │                               │
                 ▼                               ▼
        Document Handler                 Response Generation
                 │                               │
        ┌────────┴────────┐              ┌───────┴────────┐
        │                 │              │                │
   Text Extraction    Chunking      Query Rewrite    Retrieval
        │                 │              │                │
        └────────┬────────┘              │                ▼
                 │                       │          Qdrant Search
                 ▼                       │                │
          BGE-M3 Embeddings              │                ▼
                 │                       │          Cross-Encoder
                 ▼                       │           Reranking
             Qdrant ◄────────────────────┘                │
                                                         ▼
                                                 Context Assembly
                                                         │
                                                         ▼
                                                      Ollama
                                                         │
                                                         ▼
                                                  Streamed Answer
```

---

## 📂 Project Structure

```text
backend/
│
├── documents/
│   ├── README.md
│   └── docker-commands.txt
│
├── src/
│   │
│   ├── endpoints/
│   │   ├── document_uploader.py
│   │   └── response_generation.py
│   │
│   ├── models/
│   │   └── qdrant_control.ipynb
│   │
│   ├── schemas/
│   │   ├── doc_uploader_valid.py
│   │   ├── env_schema.py
│   │   └── response_generation_valid.py
│   │
│   └── services/
│       │
│       ├── document_generator/
│       │   └── wiki_collection.py
│       │
│       └── rag/
│           ├── document_handler.py
│           ├── document_retrieval.py
│           └── llm.py
│
├── dockerignore
├── .env.example
├── .python-version
├── docker-compose.yml
├── dockerfile
├── main.py
├── pyproject.toml
└── uv.lock
```

---

# 🔧 API Endpoints

## Document Upload

### `POST /document_uploader/upload`

Uploads and processes a document using `multipart/form-data`.

### Request

| Field  | Type         | Description                |
| ------ | ------------ | -------------------------- |
| `file` | `UploadFile` | PDF, DOCX, or TXT document |

### Example

```bash
curl -X POST "http://localhost:8000/document_uploader/upload" \
  -F "file=@example.pdf"
```

### Response

```json
{
  "message": "Document uploaded and processed successfully."
}
```

Once uploaded, the document is:

1. Saved locally
2. Parsed according to its file type
3. Split into chunks
4. Embedded using `BAAI/bge-m3`
5. Stored in Qdrant with associated metadata

---

# 🧠 Document Ingestion Pipeline

The `documentHandler` service is responsible for processing uploaded documents and preparing them for vector search.

## 1. File Storage

Uploaded documents are permanently stored in:

```text
models/files/
```

This provides a local copy of the original source document in addition to the processed vector representation.

---

## 2. Text Extraction

Text extraction is determined by the uploaded file type.

| Format  | Extraction       |
| ------- | ---------------- |
| `.txt`  | Direct file read |
| `.pdf`  | `pypdf`          |
| `.docx` | `python-docx`    |

The extracted text is passed into the chunking pipeline.

---

## 3. Recursive Chunking

Documents are split using recursive chunking.

The current default chunk size is:

```text
2,000 characters
```

Recursive splitting provides a simple baseline for preserving larger text structures compared with blindly splitting at arbitrary character boundaries.

---

## 4. Embedding Generation

Each chunk is converted into a dense vector using:

```python
SentenceTransformer("BAAI/bge-m3")
```

Embeddings are normalized before storage:

```python
normalize_embeddings=True
```

This allows the vectors to be compared using cosine similarity.

---

## 5. Qdrant Storage

Qdrant runs as a Docker container and is accessed by the backend through the Docker network:

```python
qdrant = QdrantClient(
    host="qdrant",
    port=6333
)
```

Each stored point contains both the vector and document metadata.

Example payload:

```json
{
  "text": "Document chunk text...",
  "source": "example.pdf"
}
```

This allows retrieved vectors to be traced back to their original document.

---

# 🔍 Query Retrieval & Reranking

The retrieval layer is implemented through the `queryRetrieval` service.

The retrieval pipeline consists of three primary stages:

```text
User Query
    ↓
Query Embedding
    ↓
Dense Vector Search
    ↓
Cross-Encoder Reranking
    ↓
Top Results
```

## 1. Query Embedding

The user's query is converted into an embedding using the same embedding model used during ingestion.

```python
self.model.encode(
    query,
    normalize_embeddings=True
)
```

Using the same embedding space allows the query vector to be compared against the document vectors stored in Qdrant.

---

## 2. Dense Vector Search

Qdrant performs semantic similarity search using its query API:

```python
qdrant.query_points(...)
```

The initial retrieval stage returns candidate document chunks based on vector similarity.

---

## 3. Cross-Encoder Reranking

Retrieved candidates are subsequently reranked using:

```python
CrossEncoder("BAAI/bge-reranker-base")
```

Unlike the initial embedding search, the cross-encoder evaluates the relationship between the query and retrieved text directly.

```text
Query
  │
  ├── Candidate 1
  ├── Candidate 2
  ├── Candidate 3
  └── Candidate N
          │
          ▼
   Cross-Encoder
          │
          ▼
   Relevance Scores
          │
          ▼
     Ranked Results
```

This creates a two-stage retrieval pipeline:

**Fast candidate retrieval → more precise reranking**

---

# 🤖 Response Generation

## `POST /response_generation/answer`

The response-generation endpoint produces a streamed RAG answer.

The pipeline combines:

* Query rewriting
* Dense retrieval
* Cross-encoder reranking
* Context assembly
* Local LLM generation
* Streaming output

### Request Body

The endpoint expects:

```python
class QueryRequest(BaseModel):
    question: str
```

### Example Request

```json
{
  "question": "What is quantum entanglement?"
}
```

### Response

The response is streamed as plain text.

Example:

```text
Quantum entanglement is a physical phenomenon where...
```

The LLM is accessed through **Ollama**, with the backend running in Docker and communicating with the host through:

```text
host.docker.internal
```

---

# 🐳 Docker Services

The project uses Docker to provide persistent infrastructure for the RAG system.

The primary infrastructure component is:

```text
FastAPI
   │
   └──► Qdrant
          │
          └── Persistent Vector Storage
```

Qdrant can be started with:

```bash
docker compose up -d
```

Check running containers with:

```bash
docker ps
```

---

# ▶️ Running the Backend

## Prerequisites

Install:

* Python
* `uv`
* Docker
* Docker Compose
* Ollama

Clone the repository and install the project dependencies:

```bash
uv sync
```

---

## 1. Configure Environment

Create an environment file from the provided example:

```bash
cp .env.example .env
```

Configure the required environment variables.

---

## 2. Start Qdrant

Start the Docker services:

```bash
docker compose up -d
```

---

## 3. Start FastAPI

Run the development server:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI's interactive documentation is available at:

```text
http://localhost:8000/docs
```

---

# 🔄 End-to-End Example

### Step 1 — Upload a document

```bash
curl -X POST "http://localhost:8000/document_uploader/upload" \
  -F "file=@example.pdf"
```

### Step 2 — Document processing

```text
PDF
 ↓
pypdf
 ↓
Extracted Text
 ↓
Recursive Chunking
 ↓
BGE-M3
 ↓
Qdrant
```

### Step 3 — Ask a question

```json
{
  "question": "What does the document say about X?"
}
```

### Step 4 — Retrieval

```text
Question
   ↓
Query Rewrite
   ↓
BGE-M3
   ↓
Qdrant
   ↓
Candidate Chunks
   ↓
BGE Reranker
   ↓
Relevant Context
```

### Step 5 — Generation

```text
Relevant Context
       +
User Question
       ↓
    Ollama
       ↓
Streamed RAG Answer
```

---

# ⚠️ Current Limitations

This project intentionally represents a relatively minimal RAG implementation. Several areas remain open for future improvement.

* No OCR support for scanned PDFs
* No sparse/BM25 retrieval
* No hybrid search
* No document deduplication
* Limited text cleaning and preprocessing
* No retrieval evaluation metrics
* No automated retrieval-quality benchmarking
* Basic fixed-size chunking baseline

These limitations provide clear opportunities for future iterations of the system.

---

# 🛠️ Potential Improvements

Possible next stages include:

### Retrieval

* Hybrid dense + BM25 retrieval
* Improved metadata filtering
* Query expansion
* Retrieval evaluation
* Recall@K / Precision@K measurements

### Document Processing

* OCR for scanned documents
* Better document structure preservation
* Semantic chunking
* Table extraction
* Duplicate detection

### RAG Quality

* Context compression
* Improved reranking
* Citation generation
* Answer faithfulness evaluation
* Hallucination detection

### Infrastructure

* Authentication
* Background document processing
* Async ingestion jobs
* Production database configuration
* Observability and logging
* Containerized deployment

---

# 🎯 Project Goal

The goal of this project is to build a modular foundation for experimenting with and improving RAG systems.

Rather than treating RAG as a single black-box operation, the architecture separates the major stages of the pipeline:

```text
┌──────────────────────┐
│   Document Upload    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│   Text Extraction    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Recursive Chunking   │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Embedding Generation │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│   Qdrant Storage     │
└──────────┬───────────┘
           │
           │
           ▼
┌──────────────────────┐
│    Query Rewriting   │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  Dense Retrieval     │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│     Reranking        │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  Context Assembly    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│   LLM Generation     │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│   Grounded Answer    │
└──────────────────────┘
```

The project can therefore serve as a foundation for testing different **chunking strategies, embedding models, retrieval methods, rerankers, and generation approaches** without having to rebuild the entire system.

---

## 📌 Tech Stack

| Component             | Technology               |
| --------------------- | ------------------------ |
| API                   | FastAPI                  |
| Language              | Python                   |
| Dependency Management | `uv`                     |
| Vector Database       | Qdrant                   |
| Containerization      | Docker / Docker Compose  |
| Embeddings            | `BAAI/bge-m3`            |
| Reranker              | `BAAI/bge-reranker-base` |
| PDF Processing        | `pypdf`                  |
| DOCX Processing       | `python-docx`            |
| LLM Runtime           | Ollama                   |
| API Validation        | Pydantic                 |

---

## 📚 Project Status

**Status:** Functional RAG backend / ongoing development

The current implementation establishes the core ingestion, retrieval, reranking, and generation pipeline. Future development is focused on improving retrieval quality, document processing, evaluation, and production readiness.
