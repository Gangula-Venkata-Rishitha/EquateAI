# EquateAI — AI Scientific Equation Parsing & Reasoning Platform

An AI-powered system that reads scientific documents (PDF/DOCX), extracts and parses mathematical equations, builds dependency and knowledge graphs, and provides an AI assistant for explanations.

## Features

- **Document processing**: Upload PDF or DOCX; extract text and equation-like expressions
- **Equation parsing**: Lexer → Parser → AST with syntax error detection
- **Semantic analysis**: Variable roles (defined / used / undefined), conflict detection
- **Dependency graph**: Variable dependencies (e.g. F → m, F → a for F = m*a)
- **Knowledge graph**: Triples (subject, predicate, object) for scientific relationships
- **Symbolic reasoning**: SymPy for simplify, solve, differentiate, integrate
- **AI assistant**: Ollama-based explanations and document Q&A

## Tech stack

- **Frontend**: Next.js 15, TypeScript, TailwindCSS, React Flow
- **Backend**: FastAPI, Python 3.11+
- **Database**: SQLite (default) or PostgreSQL
- **AI**: Ollama (Qwen, DeepSeek models)

## Repository structure

```
EquateAI/
├── frontend/          # Next.js app
├── backend/           # FastAPI app
│   └── app/
│       ├── agents/    # Document reader, lexer, parser, semantic, dependency, LLM
│       ├── api/       # REST routes
│       ├── db/        # SQLAlchemy models and DB
│       ├── services/  # Document processing service
│       └── core/      # Config
├── data/              # uploads, processed files (created at runtime)
└── docs/
```

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

Create `backend/.env` (optional):

```
DATABASE_URL=sqlite:///./data/equateai.db
OLLAMA_HOST=http://localhost:11434
```

Run:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:3000

### 3. Ollama (for AI explanations and chat)

Install [Ollama](https://ollama.ai) and pull a model:

```bash
ollama pull qwen2.5:7b
```

Keep Ollama running so the backend can call it.

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/upload` | Upload PDF/DOCX |
| POST | `/api/documents/{id}/process` | Run full pipeline |
| GET | `/api/documents` | List documents |
| GET | `/api/documents/{id}/summary` | Document summary |
| GET | `/api/documents/{id}/equations` | Detected equations |
| GET | `/api/documents/{id}/dependency-graph` | Dependency graph JSON |
| GET | `/api/documents/{id}/knowledge-graph` | Knowledge graph JSON |
| POST | `/api/equations/{id}/explain` | LLM explanation |
| POST | `/api/chat` | Chat with assistant |

## Processing pipeline

1. **Document reader** (PyMuPDF / python-docx) → text lines  
2. **Preprocessing** → normalize symbols (×→*, ÷→/, etc.)  
3. **Equation detection** → confidence-scored candidates  
4. **Lexer** → tokens (VAR, OP, NUMBER, etc.)  
5. **Parser** → AST, syntax errors  
6. **Semantic analysis** → defined/used/undefined variables  
7. **Conflict detection** → multiple definitions  
8. **Dependency analysis** → variable dependencies  
9. **Dependency graph** (NetworkX) → JSON for frontend  
10. **Knowledge graph** → triples  
11. **LLM** → explanations and chat  

## Environment variables (backend)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data/equateai.db` | Database URL |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API base |
| `DEBUG` | `false` | Enable debug logging |

## License

MIT
