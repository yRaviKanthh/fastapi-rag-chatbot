
## Overview

This project is a FastAPI-based backend service that allows users to:

- Register and login using JWT authentication
- Upload TXT and PDF documents
- Process uploaded documents using embeddings
- Ask questions from uploaded documents using a RAG (Retrieval-Augmented Generation) pipeline
- Generate answers using a local LLM (Ollama + Llama3)

---

## Tech Stack

- FastAPI
- SQLite
- SQLAlchemy
- JWT Authentication
- SentenceTransformers
- FAISS Vector Store
- Ollama (Llama3)
- PyPDF2

---

## Features

### Authentication

- User Registration
- User Login
- JWT Token Authentication
- Protected APIs

### Document Upload

- Upload TXT/PDF files
- Text extraction from documents
- Embedding generation
- Vector storage using FAISS

### Chat / Q&A

- Semantic search over uploaded documents
- Context-based answer generation
- Handles missing answers gracefully

---

## Project Structure

```text
app/
├── models/
├── routes/
├── schemas/
├── utils/
├── main.py
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/yRaviKanthh/fastapi-rag-chatbot.git
cd renote-ai-backend
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment (Windows)

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Install Ollama

Download and install Ollama from:

https://ollama.com/

### Run Llama3 Model

```bash
ollama run llama3
```

---

## Run Application

```bash
uvicorn app.main:app --reload
```

---

## Swagger Documentation

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Endpoint   | Description        |
|--------|------------|--------------------|
| POST   | /register  | Register user      |
| POST   | /login     | Login user         |
| GET    | /profile   | Get user profile   |
| POST   | /upload    | Upload document    |
| GET    | /chat      | Ask questions      |

---

## Design Decisions

- Used FAISS for fast vector similarity search
- Used SentenceTransformers for lightweight embeddings
- Used Ollama with Llama3 to avoid paid API usage
- SQLite used for simplicity and local execution
- FastAPI chosen for speed and clean API development

---

## Example Workflow

1. Register user
2. Login and get JWT token
3. Authorize using Swagger or Postman
4. Upload TXT/PDF document
5. Ask questions using `/chat`

---

## Postman Collection

The repository includes a Postman collection file for testing all APIs:

```text
FastAPI RAG Chatbot.postman_collection.json
```

## Notes

- Each user can access only their own uploaded documents
- Uploaded files are stored separately per user
- The system uses semantic similarity search before generating answers
- If no relevant answer is found, the system responds gracefully
