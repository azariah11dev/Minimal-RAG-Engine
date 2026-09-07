# 📘 Minimal RAG Engine

A lightweight, modular **Retrieval-Augmented Generation (RAG) application** that lets users upload documents, search their contents semantically, and interact with the retrieved information through a streaming LLM interface.

The project is split into two components:

* **Frontend** — lightweight HTML/CSS/JavaScript interface served through Express
* **Backend** — FastAPI service responsible for document ingestion, vector search, reranking, and LLM generation

The system uses **Qdrant** for persistent vector storage, **BAAI/bge-m3** for embeddings, **BAAI/bge-reranker-base** for reranking, and **Ollama** for local LLM inference.

---

# 🎯 Overview

The project demonstrates a complete RAG pipeline:

```text
                         MINIMAL RAG ENGINE

┌──────────────────────────────────────────────────────────┐
│                       FRONTEND                           │
│                                                          │
│  Document Upload              Question / Chat Interface  │
│         │                              │                 │
└─────────┼──────────────────────────────┼─────────────────┘
          │                              │
          │ HTTP                         │ HTTP Streaming
          ▼                              ▼
┌──────────────────────────────────────────────────────────┐
│                       FASTAPI                            │
│                                                          │
│  Document Ingestion              Response Generation     │
│         │                              │                 │
│         ▼                              ▼                 │
│  Text Extraction                Query Rewriting          │
│         │                              │                 │
│         ▼                              ▼                 │
│  Recursive Chunking             Dense Retrieval          │
│         │                              │                 │
│         ▼                              ▼                 │
│  BGE-M3 Embeddings              Cross-Encoder Reranking  │
│         │                              │                 │
│         ▼                              ▼                 │
│       Qdrant  ◄──────────── Context Assembly             │
│                                        │                 │
│                                        ▼                 │
│                                     Ollama               │
└────────────────────────────────────────┬─────────────────┘
                                         │
                                         ▼
                                  Streamed Answer
```

The application separates **document processing**, **retrieval**, **reranking**, and **generation** so each stage can be independently modified or improved.

---

# 🚀 Features

## 📄 Document Ingestion

* Upload documents through the web interface
* Supports:

  * PDF
  * DOCX
  * TXT
* File-specific text extraction
* Recursive document chunking
* Persistent local copies of uploaded documents
* Automatic embedding generation
* Vector storage in Qdrant

## 🔍 Retrieval

* Semantic dense-vector search
* Query embedding with `BAAI/bge-m3`
* Persistent Qdrant vector database
* Cross-encoder reranking
* Source metadata associated with retrieved chunks

## 🤖 Generation

* Query rewriting
* Retrieval-augmented context assembly
* Local LLM inference through Ollama
* Streaming responses to the frontend

## 🌐 Frontend

* Lightweight HTML/CSS/JavaScript UI
* No React or frontend framework
* No build system
* Document upload interface
* Query/chat interface
* Live streamed LLM responses
* Express static server

---

# 🧠 RAG Pipeline

The application consists of two major pipelines: **ingestion** and **question answering**.

## Document Ingestion

When a document is uploaded:

```text
Document
    ↓
File Storage
    ↓
Text Extraction
    ↓
Recursive Chunking
    ↓
BGE-M3 Embedding
    ↓
Qdrant
```

The resulting vector records contain both the embedding and metadata about the source document.

Example payload:

```json
{
  "text": "Document chunk text...",
  "source": "example.pdf"
}
```

---

## Question Answering

When a user asks a question:

```text
User Question
      ↓
Query Rewriting
      ↓
BGE-M3 Embedding
      ↓
Qdrant Dense Search
      ↓
Candidate Chunks
      ↓
BGE Reranker
      ↓
Relevant Context
      ↓
Ollama
      ↓
Streamed Answer
```

The frontend receives the generated response incrementally rather than waiting for the entire answer to be generated.

---

# 🏗️ System Architecture

The project is intentionally divided into independent application layers.

```text
┌─────────────────────┐
│      Browser        │
│                     │
│ HTML / CSS / JS     │
└──────────┬──────────┘
           │
           │ HTTP
           ▼
┌─────────────────────┐
│   Express Server    │
│      :3000          │
└─────────────────────┘


           │
           │ API Requests
           ▼


┌────────────────────────────────┐
│          FastAPI               │
│             :8000              │
│                                │
│ ┌────────────┐ ┌────────────┐ │
│ │ Ingestion  │ │ Generation │ │
│ └─────┬──────┘ └──────┬─────┘ │
│       │               │        │
│       ▼               ▼        │
│   Embeddings       Retrieval   │
│                       │        │
│                       ▼        │
│                   Reranking    │
│                       │        │
│                       ▼        │
│                   Ollama      │
└────────┬───────────────────────┘
         │
         ▼
   ┌───────────┐
   │  Qdrant   │
   │   :6333   │
   └───────────┘
```

---

# 🧩 Project Components

The project is organized into separate frontend and backend applications.

```text
minimal-rag/
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   ├── server.js
│   ├── styles.css
│   ├── package.json
│   └── documents/
│
└── backend/
    ├── src/
    │   ├── endpoints/
    │   ├── models/
    │   ├── schemas/
    │   └── services/
    │
    ├── documents/
    ├── docker-compose.yml
    ├── dockerfile
    ├── main.py
    ├── pyproject.toml
    └── uv.lock
```

For a detailed explanation of each component, see:

* [Frontend README](./frontend/README.md)
* [Backend README](./backend/README.md)

---

# 🔌 API

The frontend communicates with the backend through two primary endpoints.

| Method | Endpoint                      | Purpose                                         |
| ------ | ----------------------------- | ----------------------------------------------- |
| `POST` | `/document_uploader/upload`   | Upload and process a document                   |
| `POST` | `/response_generation/answer` | Submit a question and receive a streamed answer |

---

## Upload a Document

```bash
curl -X POST "http://localhost:8000/document_uploader/upload" \
  -F "file=@example.pdf"
```

Response:

```json
{
  "message": "Document uploaded and processed successfully."
}
```

---

## Ask a Question

```json
{
  "question": "What does the document say about quantum entanglement?"
}
```

The response is streamed back as plain text.

---

# 🛠️ Technology Stack

| Layer                 | Technology               |
| --------------------- | ------------------------ |
| Frontend              | HTML / CSS / JavaScript  |
| Frontend Server       | Node.js / Express        |
| Backend               | Python / FastAPI         |
| Dependency Management | `uv`                     |
| Vector Database       | Qdrant                   |
| Embedding Model       | `BAAI/bge-m3`            |
| Reranker              | `BAAI/bge-reranker-base` |
| LLM Runtime           | Ollama                   |
| PDF Processing        | `pypdf`                  |
| DOCX Processing       | `python-docx`            |
| Containerization      | Docker / Docker Compose  |

---

# ▶️ Running the Project

## Prerequisites

Install:

* Node.js 18+
* npm
* Python
* `uv`
* Docker
* Docker Compose
* Ollama

---

## 1. Start the Backend Infrastructure

From the backend directory:

```bash
docker compose up -d
```

This starts the Qdrant service.

---

## 2. Start the FastAPI Backend

Install Python dependencies:

```bash
uv sync
```

Start FastAPI:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

## 3. Start the Frontend

From the frontend directory:

```bash
npm install
```

Start the Express server:

```bash
node server.js
```

The application will be available at:

```text
http://localhost:3000
```

Open the application in a browser and upload a document to begin.

---

# 🔄 Example Workflow

A typical user interaction looks like this:

### 1. Upload

```text
User
 ↓
Select PDF/DOCX/TXT
 ↓
Frontend
 ↓
FastAPI
```

### 2. Ingest

```text
FastAPI
 ↓
Extract Text
 ↓
Chunk Document
 ↓
Generate BGE-M3 Embeddings
 ↓
Qdrant
```

### 3. Ask

```text
User
 ↓
"What does the document say about X?"
 ↓
Frontend
 ↓
FastAPI
```

### 4. Retrieve

```text
Question
 ↓
Query Rewrite
 ↓
Embedding
 ↓
Qdrant
 ↓
Candidate Results
 ↓
Cross-Encoder Reranking
```

### 5. Generate

```text
Reranked Context
       +
User Question
       ↓
     Ollama
       ↓
Streamed Response
       ↓
     Browser
```

---

# 💡 Design Philosophy

The project is intentionally **minimal and modular**.

The frontend does not attempt to implement the RAG system itself. It acts as a thin client responsible for user interaction and API communication.

The backend similarly separates the major RAG components rather than hiding the entire process behind a single abstraction.

This makes it possible to experiment with individual parts of the pipeline:

```text
┌──────────────┐
│  Chunking    │  ← Experiment with strategies
└──────────────┘

┌──────────────┐
│  Embeddings  │  ← Compare embedding models
└──────────────┘

┌──────────────┐
│  Retrieval   │  ← Test search approaches
└──────────────┘

┌──────────────┐
│  Reranking   │  ← Improve relevance
└──────────────┘

┌──────────────┐
│  Generation  │  ← Experiment with LLMs
└──────────────┘
```

The result is a small system that can evolve without requiring the entire application to be rewritten.

---

# ⚠️ Current Limitations

The current implementation is intentionally a baseline RAG system.

Known limitations include:

* No OCR for scanned PDFs
* No sparse/BM25 retrieval
* No hybrid search
* No document deduplication
* Basic text cleaning
* Basic recursive chunking
* No retrieval evaluation framework
* No automated RAG quality metrics
* No authentication
* No persistent conversation history
* Limited document management
* Localhost-oriented configuration

---

# 🛣️ Future Development

Potential improvements include:

### Document Processing

* OCR support
* Semantic chunking
* Improved document structure preservation
* Table extraction
* Duplicate detection

### Retrieval

* Hybrid dense + BM25 search
* Metadata filtering
* Query expansion
* Improved retrieval strategies
* Recall@K / Precision@K evaluation

### RAG Quality

* Context compression
* Improved reranking
* Citation generation
* Answer faithfulness evaluation
* Hallucination detection

### Application

* Chat history
* Document management
* Source/citation visualization
* Authentication
* Background ingestion jobs
* Production deployment

---

# 📊 Project Scope

This project is primarily an **engineering and experimentation platform for RAG** rather than a production-ready document assistant.

The goal is to have a complete, understandable pipeline that makes it possible to investigate questions such as:

* How does chunk size affect retrieval?
* Which embedding model performs best?
* How much does reranking improve retrieval quality?
* Does query rewriting improve recall?
* How does retrieval quality affect generation?
* How can RAG responses be evaluated systematically?

Because the system separates these stages, individual components can be replaced and evaluated independently.

---

# 📚 Documentation

The repository contains detailed documentation for each part of the application.

### Frontend

[Read the Frontend README →](./frontend/README.md)

Covers:

* Frontend architecture
* HTML/CSS/JavaScript implementation
* Document upload
* Streaming responses
* Express server
* Frontend/backend integration

### Backend

[Read the Backend README →](./backend/README.md)

Covers:

* Document ingestion
* Text extraction
* Recursive chunking
* Embedding generation
* Qdrant storage
* Dense retrieval
* Cross-encoder reranking
* Query rewriting
* LLM generation
* Docker infrastructure

---

# 🎯 Project Goal

The **Minimal RAG Engine** demonstrates a complete end-to-end RAG application while keeping the underlying architecture understandable.

It combines:

```text
Simple Frontend
       +
FastAPI Backend
       +
Document Processing
       +
Vector Search
       +
Reranking
       +
Local LLM
       ↓
Complete RAG Application
```

The project provides a foundation for experimenting with increasingly sophisticated retrieval and generation techniques while keeping each stage of the system visible, modular, and replaceable.

---

## 📌 Status

**Functional RAG application — ongoing development**

The core document ingestion → retrieval → reranking → generation pipeline is implemented, with the frontend providing a browser-based interface for interacting with the system.
