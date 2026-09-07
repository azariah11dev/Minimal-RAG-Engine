# 📘 Minimal RAG Frontend

A lightweight frontend for interacting with the **Minimal RAG Engine** backend.

The interface provides a simple document-to-answer workflow:

```text
Upload Document
      ↓
RAG Backend
      ↓
Document Ingestion
      ↓
Qdrant
      ↓
Ask Question
      ↓
RAG Retrieval
      ↓
LLM Generation
      ↓
Stream Response
      ↓
Frontend
```

The frontend is intentionally built without a JavaScript framework or build system. The goal is to provide a small, understandable interface that demonstrates the interaction between a browser-based client and a RAG backend.

---

## 🚀 Features

* 📄 Document upload
* Supports:

  * `.pdf`
  * `.docx`
  * `.txt`
* 💬 Natural-language query input
* ⚡ Live streaming of LLM responses
* 🔗 Direct integration with the RAG backend API
* 🌐 Express static server
* 🧩 Pure HTML, CSS, and JavaScript
* 🚫 No React
* 🚫 No frontend build tools
* 🚫 No external UI framework
* 🚫 No client-side state-management library

---

# 🏗️ Architecture

The frontend acts as a thin client over the RAG backend.

```text
┌──────────────────────────┐
│        Browser           │
│                          │
│  ┌────────────────────┐  │
│  │  Document Upload   │  │
│  └─────────┬──────────┘  │
│            │             │
│  ┌─────────▼──────────┐  │
│  │    Query Input     │  │
│  └─────────┬──────────┘  │
│            │             │
│  ┌─────────▼──────────┐  │
│  │ Streaming Response │  │
│  └────────────────────┘  │
└────────────┬─────────────┘
             │
             │ HTTP
             ▼
┌──────────────────────────┐
│     FastAPI Backend      │
│                          │
│  Document Ingestion      │
│  Retrieval               │
│  Reranking               │
│  LLM Generation          │
└────────────┬─────────────┘
             │
             ▼
        ┌──────────┐
        │  Qdrant  │
        └──────────┘
```

The frontend does not perform embedding, retrieval, reranking, or LLM inference itself.

It is responsible for:

1. Sending documents to the backend
2. Sending user questions to the backend
3. Reading streamed responses
4. Updating the UI as response data arrives

---

# 📁 Project Structure

```text
frontend/
│
├── documents/
│   └── README.md
│
├── app.js
├── index.html
├── package-lock.json
├── package.json
├── server.js
└── styles.css
```

## File Overview

| File                  | Purpose                                                          |
| --------------------- | ---------------------------------------------------------------- |
| `index.html`          | Main UI layout containing the document upload and chat interface |
| `styles.css`          | Application styling                                              |
| `app.js`              | Client-side logic for uploads, queries, and streamed responses   |
| `server.js`           | Express server responsible for serving the frontend              |
| `package.json`        | Node.js project metadata and dependencies                        |
| `package-lock.json`   | Locked Node.js dependency versions                               |
| `documents/README.md` | Additional project documentation                                 |

---

# 🔧 Backend Integration

The frontend communicates with two primary backend endpoints.

| Method | Endpoint                      | Purpose                                               |
| ------ | ----------------------------- | ----------------------------------------------------- |
| `POST` | `/document_uploader/upload`   | Upload and process a document                         |
| `POST` | `/response_generation/answer` | Submit a question and receive a streamed RAG response |

The backend is expected to run at:

```text
http://localhost:8000
```

The frontend runs at:

```text
http://localhost:3000
```

---

# 📄 Document Upload

Documents are uploaded using `multipart/form-data`.

The frontend creates a `FormData` object and sends the selected file to the backend.

### Request

```javascript
const formData = new FormData();

formData.append("file", file);

fetch("http://localhost:8000/document_uploader/upload", {
    method: "POST",
    body: formData
});
```

The backend accepts:

* PDF
* DOCX
* TXT

The frontend does not process the document itself. The uploaded file is passed directly to the RAG backend for ingestion.

---

## Backend Processing

Once the backend receives the document, it handles the ingestion pipeline:

```text
File Upload
     ↓
Text Extraction
     ↓
Recursive Chunking
     ↓
Embedding Generation
     ↓
Qdrant Storage
```

The frontend receives the resulting API response:

```json
{
  "message": "Document uploaded and processed successfully."
}
```

---

# 💬 Query Interface

Users can submit natural-language questions through the chat interface.

Questions are sent to:

```text
POST /response_generation/answer
```

The request body contains the user's question:

```json
{
  "question": "What does the document say about quantum entanglement?"
}
```

The backend then performs the RAG pipeline:

```text
User Question
      ↓
Query Rewriting
      ↓
Query Embedding
      ↓
Dense Retrieval
      ↓
Cross-Encoder Reranking
      ↓
Context Assembly
      ↓
LLM Generation
```

---

# ⚡ Streaming Responses

One of the primary purposes of the frontend is demonstrating **streamed LLM output**.

Rather than waiting for the complete answer before updating the interface, the browser reads the response body incrementally.

```javascript
const reader = res.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    responseBox.innerText += decoder.decode(value);
}
```

This produces a progressively updating response:

```text
Quantum
```

```text
Quantum entanglement
```

```text
Quantum entanglement is a physical phenomenon...
```

The result is a more responsive chat experience while the backend LLM is generating the answer.

---

# 🌐 Express Static Server

The frontend uses a minimal Node/Express server to host the static application.

The server serves the project directory using Express's static middleware:

```javascript
app.use(express.static(path.join(__dirname)));
```

This allows the frontend to be served locally without:

* Webpack
* Vite
* React
* Next.js
* Angular
* Vue
* Other frontend build systems

The Express server is simply responsible for making the HTML, CSS, and JavaScript available to the browser.

---

# ▶️ Running the Frontend

## Requirements

* Node.js 18+
* npm
* Modern web browser
* Running RAG backend

The backend should be available at:

```text
http://localhost:8000
```

---

## 1. Install Dependencies

From the frontend directory:

```bash
npm install
```

---

## 2. Start the Server

```bash
node server.js
```

The frontend will be available at:

```text
http://localhost:3000
```

Open the URL in your browser.

---

# 🔄 End-to-End Workflow

The complete application flow is:

### 1. Start the backend

```text
FastAPI
   +
Qdrant
   +
Ollama
```

### 2. Start the frontend

```bash
node server.js
```

### 3. Upload a document

```text
Browser
   ↓
POST /document_uploader/upload
   ↓
FastAPI
   ↓
Document Processing
   ↓
Qdrant
```

### 4. Ask a question

```text
Browser
   ↓
POST /response_generation/answer
   ↓
Query Processing
   ↓
Retrieval
   ↓
Reranking
   ↓
LLM
```

### 5. Stream the answer

```text
LLM
 ↓
FastAPI
 ↓
HTTP Stream
 ↓
Browser
 ↓
Live UI Update
```

---

# 🧩 Design Philosophy

This frontend intentionally avoids unnecessary complexity.

There is no:

* React component hierarchy
* Frontend build pipeline
* Global state management
* UI component library
* Client-side routing
* Complex application framework

Instead, the application consists of:

```text
HTML
 +
CSS
 +
JavaScript
 +
Express
```

This makes the frontend easy to inspect and provides a clear demonstration of the underlying API interactions.

The simplicity also keeps the focus on the actual RAG system rather than the frontend framework.

---

# 📌 Current Limitations

The frontend is intentionally minimal and currently has several limitations:

* No authentication
* No conversation persistence
* No chat history
* No document management interface
* No document deletion
* No progress tracking for large uploads
* No citation/source visualization
* No advanced error handling
* Localhost-oriented configuration
* Backend URL is currently configured directly in the frontend code

These are deliberate tradeoffs for the project's current scope.

---

# 🛠️ Potential Improvements

Future iterations could introduce:

### User Experience

* Chat history
* Markdown rendering
* Code-block formatting
* Source/citation display
* Upload progress indicators
* Drag-and-drop uploads
* Better error messages

### RAG Features

* Display retrieved sources
* Show relevance scores
* Document management
* Conversation-aware retrieval
* Multiple document collections

### Infrastructure

* Configurable backend URL
* Environment-based configuration
* Authentication
* Production deployment
* HTTPS
* Reverse proxy configuration

### Frontend Architecture

If the application grows significantly, the UI could eventually be migrated to a framework such as React or Next.js.

For the current project, however, a framework would add complexity without providing much additional value.

---

# 🎯 Purpose

The **Minimal RAG Frontend** exists primarily as a thin client for the RAG backend.

It demonstrates three fundamental application flows:

```text
┌──────────────────────┐
│   Document Upload    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│   Backend Ingestion  │
└──────────────────────┘
```

```text
┌──────────────────────┐
│     User Query       │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│    RAG Retrieval     │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│    LLM Generation    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  Streamed Response   │
└──────────────────────┘
```

The result is a small, dependency-light frontend that provides a complete browser interface to the **Minimal RAG Engine** while keeping the implementation easy to understand and extend.

---

## 📚 Related Project

This frontend is designed to work with the **Minimal RAG Backend**, which handles:

* Document ingestion
* Text extraction
* Recursive chunking
* Embedding generation
* Qdrant vector storage
* Dense retrieval
* Cross-encoder reranking
* Query rewriting
* LLM response generation
* Streaming responses

Together, the two components form a complete local RAG application:

```text
             MINIMAL RAG SYSTEM

┌──────────────────┐
│  Minimal RAG     │
│    Frontend      │
└────────┬─────────┘
         │ HTTP
         ▼
┌──────────────────┐
│  Minimal RAG     │
│     Backend      │
└────────┬─────────┘
         │
    ┌────┴─────┐
    ▼          ▼
 Qdrant     Ollama
```

**Status:** Functional frontend / ongoing development
