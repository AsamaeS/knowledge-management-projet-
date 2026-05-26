# NEXUS - AI Knowledge Chatbot

RAG system built with FastAPI, React, embeddings, and pgvector-ready storage.

## Features

- Document ingestion for PDF, TXT, and JSON files
- Text chunking and embedding generation
- Semantic retrieval over document chunks
- Chat endpoint with contextual answers and sources
- Lightweight chunk similarity graph
- In-memory fallback when PostgreSQL/pgvector is unavailable

## Run Backend

```bash
cd backend
uvicorn main:app --reload
```

Open:

```text
http://localhost:8000/api/health
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## API Smoke Tests

```bash
curl http://localhost:8000/api/health
```

```bash
curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What is this system?\"}"
```

## Docker

```bash
docker compose up --build
```
