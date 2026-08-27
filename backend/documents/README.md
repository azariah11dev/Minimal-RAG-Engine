# 📘 RAG Backend — Document Ingestion & Vector Storage

A minimal **Retrieval-Augmented Generation (RAG)** backend focused on document ingestion and vector storage.

This service accepts uploaded documents, extracts their text, splits the content into chunks, generates embeddings using `sentence-transformers`, and stores the resulting vectors in a persistent local **Qdrant** database.

This project serves as the foundation for a larger RAG system, with future components such as retrieval, reranking, and LLM-powered generation added in later stages.

---

## 🚀 Features

* Upload documents through a FastAPI endpoint
* Support for multiple document formats:

  * `.txt`
  * `.pdf`
  * `.docx`
* Text extraction based on file type
* Naive fixed-size chunking baseline
* Embeddings generated with `all-MiniLM-L6-v2`
* Local persistent Qdrant vector database
* Automatic metadata storage for document chunks
* Temporary uploaded file cleanup after ingestion

---

## 📂 Project Structure

```text
backend/
│
├── models/
│   ├── documents/              # Temporary uploaded files
│   └── qdrant_db/              # Local persistent Qdrant storage
│
├── src/
│   └── services/
│       └── rag/
│           └── document_handler.py
│
└── routes/
    └── document_uploader.py
```

---

## 🔧 Document Upload Endpoint

### `POST /document_uploader/upload`

Uploads a document and triggers the ingestion pipeline.

### Request Body

```json
{
  "file_name": "example.pdf",
  "file_content": "<raw file content as string>"
}
```

### Response

```json
{
  "message": "Document uploaded and processed successfully."
}
```

---

## 🧠 Document Ingestion Pipeline

The `DocumentHandler` class is responsible for processing documents and storing them in Qdrant.

### 1. File Loading

Text is extracted depending on the uploaded file type:

* **`.txt`** → Direct text reading
* **`.pdf`** → Text extraction using `pypdf`
* **`.docx`** → Text extraction using `python-docx`

---

### 2. Chunking

The extracted document text is divided into fixed-size character chunks.

Default chunk size:

```text
400 characters
```

This is intentionally a simple baseline implementation and does not currently include semantic chunking or chunk overlap.

---

### 3. Embedding Generation

Each document chunk is converted into a vector embedding using:

```python
SentenceTransformer("all-MiniLM-L6-v2")
```

The generated vectors are normalized to support cosine similarity search.

---

### 4. Qdrant Ingestion

The ingestion pipeline:

1. Creates the Qdrant collection if it does not already exist.
2. Generates an embedding for each document chunk.
3. Stores the vector and associated metadata in Qdrant.

Each stored point includes metadata such as:

```text
text    → Raw document chunk
source  → Original file name
```

Qdrant is initialized with a local persistent storage path:

```python
qdrant = QdrantClient(
    path="<project_root>/models/qdrant_db"
)
```

This allows vectors and metadata to persist between application restarts.

---

## 📦 Qdrant Storage

Qdrant manages the local vector database automatically.

A typical storage structure may look like:

```text
qdrant_db/
│
└── collections/
    └── documents/
        ├── config.json
        ├── segments/
        ├── payload/
        └── vectors/
```

The database stores:

* Vector embeddings
* Document chunk text
* Source file metadata
* Collection configuration

---

## 🛠 Requirements

Install the required dependencies:

```bash
pip install fastapi uvicorn sentence-transformers qdrant-client pypdf python-docx numpy
```

---

## ▶️ Running the Backend

Start the FastAPI application:

```bash
uvicorn main:app --reload
```

The document upload endpoint will then be available at:

```text
POST /document_uploader/upload
```

---

## 📌 Current Limitations

This project currently focuses only on the **document ingestion and vector storage layer**.

The following features have not yet been implemented:

* No retrieval or similarity search endpoint
* No LLM generation
* No reranking
* No chunk overlap
* No semantic chunking
* No OCR support for scanned PDFs
* No document deduplication
* No advanced text preprocessing
* No metadata filtering

These limitations are intentional for the current baseline implementation.

---

## 🗺️ Future Improvements

Planned additions to the RAG pipeline include:

* Vector similarity search and retrieval
* Metadata filtering
* Chunk overlap and improved chunking strategies
* Semantic chunking
* Hybrid search
* Reranking
* Query expansion
* LLM-powered answer generation
* Source citations
* OCR support for scanned documents
* Document deduplication and preprocessing

---

## 🎯 Project Goal

The goal of this backend is to establish a simple, understandable foundation for a complete RAG system.

The current pipeline follows the basic flow:

```text
Document Upload
      ↓
Text Extraction
      ↓
Text Chunking
      ↓
Embedding Generation
      ↓
Qdrant Vector Storage
```

Future stages will extend this into a complete retrieval pipeline:

```text
User Query
    ↓
Query Embedding
    ↓
Vector Retrieval
    ↓
Optional Reranking
    ↓
Relevant Context
    ↓
LLM Generation
    ↓
Grounded Response
```

This incremental approach makes it easier to evaluate and improve each component of the RAG system independently.
