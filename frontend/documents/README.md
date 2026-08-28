# Minimal RAG Engine — Frontend

A lightweight web interface for interacting with the **Minimal RAG Engine**.

The frontend allows users to upload documents and ask questions about their contents through a FastAPI backend. The backend handles document processing, embeddings, vector storage, retrieval, and LLM-powered response generation.

The frontend is intentionally simple:

* **HTML**
* **CSS**
* **Vanilla JavaScript**
* **Express**

No frontend framework, bundler, or build step is required.

---

## 📖 About the Project

The Minimal RAG Engine is a small Retrieval-Augmented Generation (RAG) application designed to demonstrate the core components of a document question-answering system.

The overall workflow is:

```text
Document
    ↓
FastAPI Backend
    ↓
Text Extraction
    ↓
Chunking
    ↓
Embeddings
    ↓
Qdrant
    ↓
User Query
    ↓
Vector Retrieval
    ↓
Context
    ↓
LLM
    ↓
Response
```

This repository contains only the **frontend interface**.

The frontend communicates with the FastAPI backend through HTTP requests.

---

## 🚀 Features

### 📄 Document Upload

Users can upload:

* `.txt`
* `.pdf`
* `.docx`

Uploaded files are sent to:

```http
POST /document_uploader/upload
```

The FastAPI backend is responsible for:

* File handling
* Text extraction
* Document chunking
* Embedding generation
* Vector insertion into Qdrant

The frontend simply handles file selection and submission.

---

### 💬 Chat With Your Documents

Users can enter a natural-language question about their uploaded documents.

Queries are sent to:

```http
POST /query
```

The backend performs:

1. Query embedding
2. Vector similarity search
3. Context retrieval
4. Prompt construction
5. LLM response generation

The generated response is then returned to the frontend and displayed to the user.

---

## 🏗 Architecture

The frontend acts as the presentation layer of the RAG application.

```text
┌──────────────────────────────┐
│          Browser             │
│                              │
│  HTML / CSS / JavaScript     │
└──────────────┬───────────────┘
               │
               │ HTTP
               ▼
┌──────────────────────────────┐
│       FastAPI Backend        │
│                              │
│  Document Processing         │
│  Retrieval                   │
│  Generation                  │
└──────────────┬───────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
┌──────────────┐ ┌──────────────┐
│    Qdrant    │ │     LLM      │
│ Vector Store │ │  Generation  │
└──────────────┘ └──────────────┘
```

### Frontend → Backend

The frontend communicates with the FastAPI application using standard HTTP requests.

### Backend → Qdrant

The backend stores document embeddings and performs vector similarity searches using Qdrant.

### Backend → LLM

Retrieved document context is provided to an LLM to generate the final response.

---

## 📁 Project Structure

```text
frontend/
├── index.html
├── styles.css
├── app.js
├── server.js
└── package.json
```

### `index.html`

The main application interface.

Contains:

* Document upload form
* File selector
* Query input
* Submit button
* Response display area

---

### `styles.css`

Contains the application's basic styling.

The UI is intentionally minimal so that the focus remains on the RAG functionality rather than frontend complexity.

---

### `app.js`

Contains the frontend application logic.

Responsible for:

* Handling document uploads
* Sending files to FastAPI
* Submitting user queries
* Sending HTTP requests
* Processing backend responses
* Rendering responses in the UI

---

### `server.js`

A small Express server used to serve the frontend files.

No frontend compilation or build process is required.

---

## 🛠️ Requirements

Before running the frontend, make sure you have:

* **Node.js**
* **npm**
* A running Minimal RAG Engine FastAPI backend

The frontend currently expects the backend to run at:

```text
http://localhost:8000
```

---

## 🚀 Running the Frontend

### 1. Clone the repository

```bash
git clone <repository-url>
cd frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Start the Express server

```bash
node server.js
```

The frontend will be available at:

```text
http://localhost:3000
```

### 4. Start the FastAPI backend

The backend should be running separately at:

```text
http://localhost:8000
```

Once both services are running, open:

```text
http://localhost:3000
```

---

## 🔌 API Integration

The frontend communicates with two primary FastAPI endpoints.

### Document Upload

```javascript
fetch("http://localhost:8000/document_uploader/upload", {
    method: "POST",
    body: formData
});
```

The request contains the selected document as multipart form data.

The backend then processes the document and stores its embeddings in Qdrant.

---

### Query

```javascript
fetch("http://localhost:8000/query", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({ query })
});
```

The backend receives the user's question and performs the RAG workflow:

```text
Query
  ↓
Embedding
  ↓
Vector Search
  ↓
Relevant Chunks
  ↓
LLM
  ↓
Response
```

---

## 🎨 UI Overview

The interface contains two primary areas.

### Chat Interface

The chat section provides:

* Response display
* Query input
* Submit button

Users can enter questions about information contained in their uploaded documents.

---

### Document Upload

The upload section provides:

* File selector
* Upload button

Supported file types:

```text
.txt
.pdf
.docx
```

---

## 🎯 Design Philosophy

This frontend intentionally avoids unnecessary complexity.

There is:

* No React
* No Next.js
* No TypeScript
* No frontend state-management library
* No bundler
* No build pipeline

The goal is to demonstrate the RAG system itself rather than introduce additional frontend abstractions.

The application can therefore be understood by following a simple flow:

```text
User Action
    ↓
JavaScript
    ↓
HTTP Request
    ↓
FastAPI
    ↓
RAG Pipeline
    ↓
HTTP Response
    ↓
JavaScript
    ↓
UI
```

---

## 🔗 Related Components

This frontend is designed to work with the Minimal RAG Engine backend.

The complete system consists of:

```text
Minimal RAG Engine
│
├── Frontend
│   ├── HTML
│   ├── CSS
│   ├── JavaScript
│   └── Express
│
└── Backend
    ├── FastAPI
    ├── Document Processing
    ├── Chunking
    ├── Embeddings
    ├── Qdrant
    └── LLM
```

---

## 📚 RAG Learning Series

This project is part of a four-part series exploring how to build a RAG application with FastAPI.

### Episode 1 — Store, Chunk & Embed

How documents are transformed into searchable vector data.

**Topics:**

* Document ingestion
* Text extraction
* Chunking
* Embeddings
* Qdrant

### Episode 2 — Retrieval

How the system finds relevant information when a user asks a question.

**Topics:**

* Query embeddings
* Vector similarity search
* Top-K retrieval
* Context selection

### Episode 3 — Augmented Generation

How retrieved information is provided to an LLM to generate a response.

**Topics:**

* Context construction
* Prompt augmentation
* LLM generation
* Grounding
* Source information

### Episode 4 — IntelliDoc

Combining the individual components into a complete document intelligence application.

**Topics:**

* Full-stack architecture
* Document management
* RAG pipeline
* User interface
* End-to-end workflow

---

## 🔮 Future Improvements

Potential improvements include:

* Streaming LLM responses
* Conversation history
* Document management
* Multiple document collections
* Source citations
* Improved error handling
* Authentication
* Upload progress indicators
* Better chat interface
* Retrieval evaluation
* Hybrid search
* Reranking
