# Launch Guide — Adaptive RAG

Step-by-step instructions to get the Adaptive RAG app running locally and verify that it works.

---

## What you are launching

This project has two parts:

| Component | Port | Purpose |
|-----------|------|---------|
| **FastAPI backend** | `8000` | RAG pipeline, document upload, chat API |
| **Streamlit frontend** | `8501` | User-friendly chat UI with document upload |

You also need **MongoDB** (chat history) running on port `27017`.

> **Note:** The Streamlit UI talks directly to the FastAPI backend. No separate auth server is required.

---

## Prerequisites

- **Python 3.9+** (3.11 or 3.13 tested)
- **Docker Desktop** (recommended, for MongoDB) — or a local MongoDB install
- API keys:
  - **OpenAI** — required for all queries
  - **Tavily** — required only for web-search queries

---

## 1. Clone and enter the project

```bash
git clone
cd Adaptive-Rag
```

If you already have the repo locally:

```bash
cd /path/to/Adaptive-Rag
```

---

## 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pypdf               # required for PDF uploads
```

Activate the venv in every new terminal before running commands.

---

## 3. Configure environment variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here

# Optional — Qdrant is not used by default (FAISS in-memory is active)
# QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=
# QDRANT_CODE_COLLECTION=code_documents
# QDRANT_DOCS_COLLECTION=documents
```

### Where to get API keys

| Key | Where to get it |
|-----|-----------------|
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| `TAVILY_API_KEY` | [tavily.com](https://tavily.com) — free tier available, no card required |

Never commit `.env` to git.

---

## 4. Start MongoDB

### Option A — Docker (recommended)

Make sure Docker Desktop is running, then:

```bash
docker run -d --name adaptive-rag-mongo -p 27017:27017 mongo:7
```

On subsequent runs, start the existing container:

```bash
docker start adaptive-rag-mongo
```

### Option B — Local MongoDB

If MongoDB is installed via Homebrew:

```bash
brew services start mongodb-community
```

The app expects MongoDB at `mongodb://localhost:27017` (configured in `src/db/mongo_client.py`).

---

## 5. Start the FastAPI backend

Open **Terminal 1** from the project root:

```bash
source venv/bin/activate
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

Verify the backend is up:

- http://localhost:8000 → `{"message":"Adaptive RAG API is running"}`
- http://localhost:8000/docs → interactive API documentation

Leave this terminal running.

---

## 6. Start the Streamlit frontend

Open **Terminal 2** from the project root:

```bash
source venv/bin/activate
streamlit run streamlit_app/home.py
```

You should see:

```
Local URL: http://localhost:8501
```

Open **http://localhost:8501** in your browser.

> If the home page shows a backend error, make sure Terminal 1 (FastAPI) is running, then refresh.

---

## 7. Use the app

### Streamlit UI (recommended)

1. Go to http://localhost:8501
2. Confirm you see **"Backend connected."**
3. Enter a **display name** and click **Start Chat**
4. *(Optional)* In the sidebar, upload a **PDF** or **TXT** file and add a short description (e.g. `My resume`)
5. Ask questions in the chat box

**Example questions:**

| Type | Example |
|------|---------|
| General knowledge | `What is machine learning?` |
| Document-based | `What skills are mentioned in the document?` |
| Web search | `What are today's top AI news headlines?` |

### API docs (alternative)

If you prefer testing without the UI:

1. Open http://localhost:8000/docs
2. Use `POST /rag/documents/upload` to upload a file (set the `X-Description` header)
3. Use `POST /rag/query` with a JSON body:

```json
{
  "query": "What is Python?",
  "session_id": "my_session_1"
}
```

### cURL (alternative)

```bash
# Upload a document
curl -X POST http://localhost:8000/rag/documents/upload \
  -H "X-Description: Sample resume document" \
  -F "file=@/path/to/your/file.pdf"

# Ask a question
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize the document", "session_id": "my_session_1"}'
```

---

## Quick reference

| Service | Start command | URL |
|---------|---------------|-----|
| MongoDB | `docker start adaptive-rag-mongo` | `localhost:27017` |
| Backend | `python -m uvicorn src.main:app --reload --port 8000` | http://localhost:8000 |
| Frontend | `streamlit run streamlit_app/home.py` | http://localhost:8501 |
| API docs | *(auto with backend)* | http://localhost:8000/docs |

---

## Stopping the app

| Service | How to stop |
|---------|-------------|
| FastAPI / Streamlit | `Ctrl+C` in the terminal |
| MongoDB (Docker) | `docker stop adaptive-rag-mongo` |

---

## Troubleshooting

### "Backend is not running" on the Streamlit home page

Start the FastAPI server first (step 5), then refresh http://localhost:8501.

### `Connection refused` on `/rag/query`

- Confirm uvicorn is running on port 8000
- Confirm MongoDB is running: `docker ps` should show `adaptive-rag-mongo`

### Document upload fails for PDFs

Install the PDF dependency:

```bash
pip install pypdf
```

### Web search queries fail

Check that `TAVILY_API_KEY` is set correctly in `.env` and restart the FastAPI server.

### Uploaded documents are forgotten after restart

Documents are stored in an **in-memory FAISS** index by default. Re-upload files after restarting the backend. (Qdrant support exists in the codebase but is not active by default.)

### Port already in use

```bash
# Find what is using the port (example for 8000)
lsof -i :8000

# Or start on a different port
python -m uvicorn src.main:app --reload --port 8001
```

If you change the backend port, set `RAG_API_URL` before starting Streamlit:

```bash
export RAG_API_URL=http://127.0.0.1:8001
streamlit run streamlit_app/home.py
```

---

## Startup checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`requirements.txt` + `pypdf`)
- [ ] `.env` file with `OPENAI_API_KEY` and `TAVILY_API_KEY`
- [ ] MongoDB running on port 27017
- [ ] FastAPI backend running on port 8000
- [ ] Streamlit frontend running on port 8501
- [ ] Home page shows "Backend connected."
- [ ] Test query returns a response

---

*Last updated: June 2026*
