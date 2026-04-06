# 1. Project Title

## EquateAI
### AI-Assisted Scientific Equation Parsing, Graph Construction, and Document-Centric Reasoning

# 2. Executive Summary

EquateAI is a full-stack application that ingests scientific documents and extracts equation-like expressions into a structured analysis workflow. The repository contains a FastAPI backend and a Next.js frontend. The backend performs document reading (PDF/DOCX/images), preprocessing, heuristic equation detection, lexical parsing, AST generation, semantic role analysis of variables, dependency analysis, conflict checks, and graph-oriented outputs. The frontend provides upload, document browsing, equation explanation, dependency/knowledge graph visualization, and AI chat interfaces.

The project addresses a practical problem: scientific equations are often embedded in unstructured documents and hard to inspect at scale. EquateAI aims to make equation structure explicit and navigable by converting detected equations into machine-readable representations and graph views, with optional LLM-powered explanations.

The implemented scope is strongest in product workflow and backend pipeline orchestration. It is not a model-training research codebase: no training loop, checkpoint lifecycle, experiment tracker, or benchmark harness exists in this repository. The current system is primarily a deterministic/rule-based pipeline augmented with local LLM inference through Ollama.

# 3. Introduction

Scientific and technical documents mix prose and mathematics, making downstream analysis difficult for students, researchers, and engineers. EquateAI attempts to bridge this gap by extracting equation candidates, parsing them into syntax trees, tracking variable semantics, and projecting relationships as dependency and knowledge graphs.

This matters in both educational and technical contexts:
- educationally, to explain equations and highlight undefined or conflicting variable usage;
- operationally, to map formula dependencies quickly across a document;
- analytically, to surface inconsistencies and graph-level issues (e.g., cycles).

From code evidence, the project objective is application-level utility rather than publication-grade experimentation. It focuses on an end-user workflow from document upload to interactive inspection and assistant chat.

# 4. Objectives

## Main Objective
- Build an end-to-end system that transforms uploaded scientific documents into structured equation data and graph representations.

## Secondary Objectives
- Provide equation-level natural-language explanations (rule-based + LLM fallback).
- Provide document-aware chat assistance.
- Detect multi-definition and symbolic conflicts.
- Detect missing/undefined variables and dependency cycles.
- Offer graph UIs suitable for interactive exploration.

## Deliverables / Intended Outcomes
- Backend REST API for upload, processing, retrieval, explanation, and chat.
- Frontend pages for upload/dashboard/documents/graph/knowledge/chat.
- Persistent storage of extracted equations, variables, dependencies, and conflict/missing-variable artifacts.

# 5. Repository Overview

## High-Level Description

The repository is a two-project monorepo-like structure:
- `backend/`: FastAPI app implementing extraction and analysis pipeline.
- `frontend/`: Next.js App Router application for user interaction and visualization.

No committed tests, CI/CD workflows, Docker setup, notebooks, or experiment framework were found.

## Directory Tree Summary

```text
EquateAI/
├─ README.md
├─ .gitignore
├─ backend/
│  ├─ requirements.txt
│  ├─ .env
│  └─ app/
│     ├─ main.py
│     ├─ core/config.py
│     ├─ db/{database.py,models.py}
│     ├─ api/routes/{documents.py,equations.py,chat.py}
│     ├─ agents/*.py
│     ├─ services/*.py
│     ├─ schemas/*.py
│     └─ utils/ast_serialize.py
└─ frontend/
   ├─ package.json
   ├─ package-lock.json
   ├─ tsconfig.json
   ├─ next.config.mjs
   ├─ tailwind.config.ts
   ├─ postcss.config.mjs
   ├─ .env.local
   ├─ lib/{api.ts,cn.ts}
   ├─ components/AppShell.tsx
   └─ app/** (pages/routes + globals.css)
```

## Important Folders and Roles
- `backend/app/agents/`: core processing stages (reader, preprocessing, detection, parsing, semantic, graph builders, reasoning, LLM assistant).
- `backend/app/services/`: DB-oriented orchestration and derived analysis (document persistence, conflicts, missing variables, classifier, NL conversion).
- `backend/app/api/routes/`: exposed REST interface.
- `frontend/app/`: UI routes and page-level logic.
- `frontend/lib/api.ts`: typed API client and endpoint wrappers.

# 6. Complete Architecture Overview

## System Architecture

```text
[User]
  |
  v
[Next.js Frontend]
  |
  | HTTP (REST)
  v
[FastAPI Backend]
  |
  | orchestrates
  v
[Pipeline Coordinator]
  |--> DocumentReader (PDF/DOCX/OCR)
  |--> Preprocessing
  |--> EquationDetection
  |--> Lexer + Parser (AST)
  |--> SemanticAnalyzer
  |--> ConflictDetector (agent-level)
  |--> DependencyAgent
  |--> GraphBuilder + KnowledgeGraphBuilder
  |
  v
[DocumentService Persistence]
  |--> SQLAlchemy models (SQLite/Postgres URL)
  |--> ConflictDetectionService (symbolic checks)
  |--> SemanticAnalysisService (missing vars, cycles)
  |
  v
[Frontend retrieval: summary/equations/graphs/conflicts/chat]
```

## End-to-End Control and Data Flow

1. Frontend uploads a file via `POST /api/documents/upload`.
2. Backend stores file under configured upload directory and inserts a `Document` row.
3. Frontend triggers `POST /api/documents/{id}/process`.
4. `DocumentService.process_document()` invokes `ProcessingCoordinator.process_document()`.
5. Coordinator returns parsed semantic artifacts and graph JSON.
6. Service persists equations/variables/dependencies; runs higher-level conflict and semantic services.
7. Frontend fetches document summary, equation list, dependency graph, knowledge graph, conflicts, missing variables, dependency cycles.
8. Optional LLM routes provide equation explanation and chat response.

## Training / Inference / Evaluation Architecture
- Training architecture: **Not clearly implemented** (no train scripts/pipeline/checkpoints).
- Inference architecture:
  - deterministic/rule-based parsing stack in backend agents;
  - LLM inference via Ollama in `LLMAssistantAgent` and `LLMClient`.
- Evaluation architecture:
  - no benchmark framework;
  - operational quality signals only (counts, conflicts, missing variables, cycles).

# 7. Tech Stack

## Languages
- Python (backend)
- TypeScript/TSX (frontend)
- CSS (styling)

## Backend Frameworks/Libraries
- FastAPI `0.115.6`
- Uvicorn `0.32.1`
- SQLAlchemy `2.0.36`
- Pydantic `2.10.3` + `pydantic-settings`
- PyMuPDF, python-docx, Pillow, pytesseract (document extraction)
- SymPy (symbolic math and conflict checks)
- NetworkX (graph operations)
- Ollama Python client (LLM calls)

## Frontend Frameworks/Libraries
- Next.js `^16.1.6`
- React `^18.3.1`
- TailwindCSS `^3.4.17`
- `@xyflow/react` (graph rendering)
- `elkjs` (graph layout)
- `katex` (equation rendering in graphs)
- `lucide-react` (icons)

## Storage and Runtime Assumptions
- Default DB: SQLite (`sqlite:///./data/equateai.db`)
- Optional DB URL supports PostgreSQL driver deps (`asyncpg`, `psycopg2-binary` present)
- Local Ollama service expected at `http://localhost:11434`
- Frontend expects backend at `http://localhost:8000/api` via `NEXT_PUBLIC_API_URL`

## Tooling and Quality Infrastructure
- ESLint script exists (`npm run lint`) in frontend.
- No committed test suite or CI/CD pipeline.
- No containerization files detected.

# 8. Environment and Setup

## Environment Files
- `backend/.env`:
  - `OLLAMA_HOST`
  - `OLLAMA_EQUATION_MODEL`
  - `OLLAMA_CHAT_MODEL`
  - `OLLAMA_CODE_MODEL`
  - optional/commented DB and debug variables
- `frontend/.env.local`:
  - `NEXT_PUBLIC_API_URL=http://localhost:8000/api`

## Setup Evidence
- Backend setup and run commands are documented in `README.md` and consistent with code:
  - create venv
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Frontend:
  - `npm install`
  - `npm run dev`

## Hardware/OS Assumptions
- CPU execution is sufficient for deterministic parsing.
- OCR requires local Tesseract runtime installation (package alone may be insufficient).
- LLM features require local Ollama model availability and adequate hardware.
- GPU-specific training assumptions: **Not clearly implemented**.

## Dependency Risks
- `next@^16` with `react@^18.3.1` may need verification for compatibility in target environment.
- OCR quality and availability depend on external Tesseract binary setup.
- Symbolic parsing robustness depends on equation string quality from extraction.

# 9. Methodology

## Baseline Approach (Implemented)
- Heuristic equation candidate scoring from extracted text lines.
- Handwritten lexer/parser for mathematical expressions.
- AST-based variable role extraction.
- Rule-based equation typing and natural-language conversion.
- Graph derivation from variable dependencies.

## Design Philosophy
- Favor deterministic, inspectable transformations first.
- Use LLMs as augmentation for explanation/chat and text-to-equation fallback.
- Persist intermediate semantic structure in relational tables for retrieval.

## Algorithmic Flow

1. **Extract text**
   - PDF via PyMuPDF blocks/lines.
   - DOCX via paragraphs.
   - Images via OCR.
2. **Normalize**
   - Unicode math symbol replacements.
   - noise line filtering (headers/page numbers).
3. **Detect**
   - confidence score based on operators, equality sign, function patterns, numbers.
4. **Parse**
   - tokenize into `VAR/NUMBER/OP/...`.
   - recursive descent parse to AST.
5. **Semantic role assignment**
   - LHS variable considered `defined`.
   - RHS variables considered `used` or `undefined` given prior definitions.
6. **Dependency + graph construction**
   - edges `(defined -> used)` per equation.
   - graph JSON for visualization.
7. **Persistence + higher-level checks**
   - store equations/variables/dependencies.
   - detect multiple-definition + symbolic conflicts.
   - compute missing variables and dependency cycles.

## Training / Inference / Evaluation Strategy
- Training: not implemented.
- Inference:
  - deterministic pipeline + optional LLM calls.
- Evaluation:
  - no formal metrics pipeline; implicit structural checks only.

# 10. Models and Algorithms Used

## DocumentReaderAgent
- **Path**: `backend/app/agents/document_reader.py`
- **Purpose**: extract text lines from PDF, DOCX, images.
- **Input/Output**: file path -> `list[TextLine(content,page,line_no)]`.
- **Role**: initial data acquisition.

## PreprocessingAgent
- **Path**: `backend/app/agents/preprocessing.py`
- **Purpose**: normalize symbols and remove noise lines.
- **Key behavior**: replacements for symbols like `×, ÷, ≤, ≥, π`.

## EquationDetectionAgent
- **Path**: `backend/app/agents/equation_detection.py`
- **Purpose**: heuristic candidate extraction.
- **Key rule**: score threshold `> 0.3` to keep candidate.

## LexerAgent + ParserAgent
- **Paths**: `backend/app/agents/lexer.py`, `backend/app/agents/parser.py`
- **Purpose**: tokenize and parse equation text into AST.
- **Parsing style**: recursive descent with precedence (additive -> multiplicative -> power -> unary -> primary).

## SemanticAnalyzerAgent
- **Path**: `backend/app/agents/semantic.py`
- **Purpose**: classify variables as `defined`, `used`, `undefined`.

## DependencyAgent / ConflictDetectorAgent (agent-level)
- **Paths**: `backend/app/agents/dependency.py`, `backend/app/agents/conflict.py`
- **Purpose**:
  - dependency edges from defined variables to used variables;
  - detect multiple definitions by variable.

## GraphBuilderAgent / KnowledgeGraphBuilder
- **Paths**: `backend/app/agents/graph_builder.py`, `backend/app/agents/knowledge_graph.py`
- **Purpose**: create graph/triple structures for frontend.

## ReasoningAgent (SymPy)
- **Path**: `backend/app/agents/reasoning.py`
- **Capabilities**: simplify, solve, differentiate, integrate.
- **Usage status**: class exists; direct API route integration is limited.

## LLM Components
- **Paths**: `backend/app/agents/llm_assistant.py`, `backend/app/services/llm_client.py`
- **Purpose**:
  - explain equations;
  - chat with optional document context;
  - convert text to equation fallback.
- **Backend dependency**: local Ollama server.

## Persisted State / Checkpoints
- Model checkpoints: **Not clearly implemented**.
- Persisted analytical state: SQL tables (documents/equations/variables/dependencies/conflicts/missing/chat_history).

# 11. Data Pipeline

## Raw Input Sources
- User-uploaded files through `/api/documents/upload`.
- Allowed file types: PDF, DOCX, PNG, JPG, JPEG, BMP, TIF, TIFF, WEBP.

## Loading and Parsing
- File saved to `settings.upload_dir`.
- Reader selects extraction routine by extension.

## Cleaning/Preprocessing
- Symbol normalization and whitespace collapse.
- Noise filtering via regexes for page/header-like lines.

## Structuring
- Equation candidates scored and filtered.
- Candidates converted to token streams and AST.
- Variables extracted and role-tagged.

## Batching/Splits/Augmentation
- Batching: not applicable (single document request flow).
- Dataset splits/augmentation: **Not clearly implemented**.

## Caching/Serialization
- AST serialized to JSON via `ast_to_dict`.
- Derived entities persisted in SQL tables.

## Failure Handling
- Upload endpoint validates extension and filename.
- Process endpoint validates document/file existence.
- Exceptions set document status to `"error"` in service-level flow.
- LLM failures are returned as human-readable fallback strings.

# 12. Datasets

No committed dataset files were found in this repository.

## Dataset-Related Evidence
- `data/` path is referenced in config and README but ignored by `.gitignore`.
- Runtime artifacts expected under:
  - `data/uploads`
  - `data/processed`
  - `data/equateai.db`

## Inferred Dataset Characteristics
- Data is user-provided uploaded documents, not a fixed benchmark corpus.
- Sample counts/splits/labels: **Needs verification from code/results** (not versioned in repo).

## Compatibility Notes
- OCR path quality depends on image quality and Tesseract configuration.
- Multilingual or handwritten support claims in UI copy need verification from results.

# 13. Training Pipeline

No training pipeline is present.

## Verified Status
- No `train.py`, trainer modules, epochs, checkpoints, optimizer/scheduler logic.
- No reproducibility controls (seeds, deterministic flags) for ML training.

## Practical Interpretation
- This is an application pipeline project using deterministic parsing + LLM inference, not supervised model training.

# 14. Inference / Generation Pipeline

## Document Inference Flow
1. Upload document.
2. Trigger processing route.
3. Run full parsing/semantic/graph pipeline.
4. Persist derived structures.
5. Query summary/equations/graphs/conflicts/missing/dependency issues.

## LLM Inference Flow
- Equation explanation route:
  - fetch equation text by ID;
  - call Ollama model with concise explanation prompt.
- Chat route:
  - build document context from up to 50 equations;
  - send message and optional context to Ollama.

## Post-processing and Outputs
- Dependency graph and knowledge graph returned as `nodes/edges` JSON payloads.
- Equation-to-text uses rule-based conversion first, then LLM fallback.

## Runtime Considerations / Failure Points
- Missing Ollama service or model pulls cause LLM fallback error strings.
- OCR depends on external Tesseract availability.
- Equation parsing can produce syntax errors; parser stores error list in `ParsedEquation` but API currently exposes primarily AST/raw.

# 15. Evaluation and Benchmarking

## What Exists
- Conflict detection:
  - `MULTIPLE_DEFINITION`
  - `SYMBOLIC_CONFLICT` via SymPy RHS comparison.
- Semantic checks:
  - missing variable computation;
  - dependency cycle detection via `networkx.simple_cycles`.

## What Does Not Exist
- Benchmark scripts, eval dataset, metric dashboards, ablations, baselines comparison tables.
- Automated quality metrics for extraction precision/recall.

## Interpretation
- Evaluation is currently operational/diagnostic, not research-grade benchmarked.

# 16. Results and Current Status

## Implemented and Operational (Code-Complete)
- End-to-end upload -> process -> inspect workflow.
- Equation extraction/parsing/semantic role storage.
- Dependency and knowledge graph generation and visualization.
- Conflict and missing-variable routes.
- LLM explanation and chat endpoints.

## Partially Implemented / Fragile Areas
- Chat history persistence model exists, but route uses `history = []` with TODO for loading history.
- `ReasoningAgent` is implemented but not surfaced in dedicated API routes.
- Equation classifier enum includes a typo value (`PROPOSITIONIAL_LOGIC` string) and should be verified for downstream impact.

## Incomplete / Missing for Mature Research Pipeline
- No tests, CI, containerization, formal evaluation datasets or scripts.
- No reproducible experiment artifacts (checkpoints/logs/tables).

## Maturity Assessment
- Product prototype / MVP maturity for interactive document reasoning.
- Early-stage research maturity due absent experimental rigor tooling.

# 17. Related Work Context

This project sits at the intersection of:
- scientific document understanding,
- equation parsing/symbolic reasoning,
- graph-based knowledge representation,
- LLM-assisted explanation.

Compared with typical method families:
- **Pure OCR + regex extractors**: EquateAI goes further with AST and semantic role analysis.
- **Formal theorem provers/CAS systems**: EquateAI uses lightweight symbolic checks but is not a full formal verification stack.
- **End-to-end neural document parsers**: repository does not implement trainable deep parsing models; instead combines rule-based pipeline with LLM augmentation.

No bibliography or explicit related-work references are included in the repository; this section is contextual, not citation-backed.

# 18. Code Quality and Engineering Assessment

## Modularity
- Strong separation: agents (pipeline logic), services (DB and higher-level business logic), routes (API layer), schemas (contract layer).

## Readability
- Generally clear class/method naming.
- Docstrings present in most backend files.

## Maintainability
- Positive:
  - typed dataclasses and Pydantic schemas.
  - central config object.
- Risks:
  - some repeated graph-page logic in frontend (`graph` vs `knowledge`) suggests refactor opportunity.
  - limited tests increase regression risk.

## Reproducibility
- Good dependency pinning in backend.
- Weak experiment reproducibility (no datasets/artifacts/scripts).

## Separation of Concerns
- Mostly good.
- API routes occasionally contain manual aggregation loops that could be optimized/service-ized.

## Config Hygiene
- Env defaults and local overrides are clear.
- No production environment templates or secrets-management patterns.

## Technical Debt / Risk Areas
- Missing automated tests and CI checks.
- Chat history TODO indicates incomplete conversational continuity.
- Symbolic conflict parsing can silently skip parse failures.

# 19. Strengths

- Clear end-to-end full-stack architecture with coherent workflow.
- Deterministic pipeline stages are inspectable and explainable.
- Useful graph visualizations with layout and interaction features.
- Practical semantic diagnostics (missing vars, cycles, conflicts).
- Flexible local LLM integration via Ollama without cloud lock-in.
- Dependency versions mostly pinned for backend stability.

# 20. Limitations and Gaps

- No formal training/evaluation pipeline; not a benchmarked ML research repo.
- No automated tests, no CI/CD, no container setup.
- OCR and LLM reliability depend on external local runtime setup.
- Heuristic equation detection/parsing may degrade on complex notation.
- No persisted multi-turn chat context despite schema/table support.
- No versioned dataset corpus or experiment records for reproducibility.

# 21. Future Work

## Architecture
- Consolidate duplicated frontend graph logic into reusable graph workspace components.
- Add async task queue for long document processing and progress events.

## Training/Methodology
- If research direction is desired, add train/eval modules with curated equation datasets and measurable metrics.
- Expand parser grammar coverage (subscripts, matrices, piecewise, LaTeX-like constructs).

## Evaluation
- Add extraction precision/recall benchmarks against labeled corpora.
- Add conflict-detection validation suite with known symbolic equivalents/conflicts.

## Engineering
- Introduce unit/integration/e2e tests.
- Add CI workflows (lint, typecheck, backend tests).
- Add Docker compose for reproducible local setup.

## Documentation
- Add API examples and architecture diagrams to docs.
- Provide troubleshooting guide for Ollama and Tesseract setup.

# 22. Conclusion

EquateAI successfully implements a practical document-to-equation reasoning application with interactive visualization and assistant capabilities. Its core contribution is integrating deterministic equation parsing semantics with graph-centric exploration and optional LLM augmentation in a usable full-stack flow.

The codebase is product-prototype mature but research-pipeline immature. To transition toward thesis-grade reproducibility and scientific validation, the next critical steps are test infrastructure, benchmark design, versioned datasets/artifacts, and explicit evaluation scripts.

# 23. Key Commands / Operational Reference

## Backend (documented and code-aligned)
- `cd backend`
- `python -m venv .venv`
- `.venv\Scripts\activate` (Windows)
- `pip install -r requirements.txt`
- `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## Frontend
- `cd frontend`
- `npm install`
- `npm run dev`
- optional: `npm run build`, `npm run start`, `npm run lint`

## Inference Workflow (API-driven, inferred from routes)
- Upload: `POST /api/documents/upload`
- Process: `POST /api/documents/{id}/process`
- Retrieve:
  - `/api/documents/{id}/summary`
  - `/api/documents/{id}/equations`
  - `/api/documents/{id}/dependency-graph`
  - `/api/documents/{id}/knowledge-graph`
  - `/api/documents/{id}/conflicts`
  - `/api/documents/{id}/missing-variables`
  - `/api/documents/{id}/dependency-issues`

## LLM-Assisted Operations
- Explain equation: `POST /api/equations/{id}/explain`
- Equation to text: `POST /api/equations/{id}/to-text`
- Text to equation: `POST /api/equations/from-text`
- Chat: `POST /api/chat`

## Training / Evaluation Reproduction
- Training commands: **Not clearly implemented**.
- Evaluation commands: **Not clearly implemented** beyond API diagnostics.

# 24. Important Files Reference

| Path | Purpose | Importance |
|---|---|---|
| `README.md` | project intro, quickstart, API overview | High |
| `backend/app/main.py` | FastAPI app creation, router mounting, startup DB init | High |
| `backend/app/core/config.py` | environment-backed settings and paths | High |
| `backend/app/db/models.py` | persistent schema for document/equation artifacts | High |
| `backend/app/services/document_service.py` | orchestrates processing persistence and post-checks | High |
| `backend/app/agents/coordinator.py` | core pipeline orchestration across agents | High |
| `backend/app/agents/document_reader.py` | PDF/DOCX/OCR extraction entry | High |
| `backend/app/agents/parser.py` | recursive descent parser + syntax handling | High |
| `backend/app/services/conflict_detection.py` | symbolic and multi-definition conflict persistence | High |
| `backend/app/services/semantic_analysis.py` | missing vars and cycle checks | High |
| `backend/app/api/routes/documents.py` | primary operational API surface | High |
| `backend/app/api/routes/equations.py` | explain/convert equation APIs | Medium-High |
| `backend/app/api/routes/chat.py` | chat API and document context assembly | Medium-High |
| `frontend/lib/api.ts` | frontend-backend typed API contract | High |
| `frontend/app/upload/page.tsx` | upload-and-process user entry flow | High |
| `frontend/app/documents/[id]/page.tsx` | document analysis hub page | High |
| `frontend/app/documents/[id]/graph/page.tsx` | dependency graph visualization | High |
| `frontend/app/documents/[id]/knowledge/page.tsx` | knowledge graph visualization | High |
| `frontend/app/chat/page.tsx` | user chat interface | Medium-High |
| `backend/requirements.txt` | backend dependency lock list | High |
| `frontend/package.json` | frontend scripts and dependencies | High |

# 25. Open Questions / Needs Verification

- OCR runtime dependency installation (system Tesseract binary path) is not documented in detail.
- UI claims around LaTeX/MathML/handwritten support appear in frontend marketing copy; comprehensive implementation evidence is limited and needs verification from results.
- `docs/` folder content was not discoverable as committed text files; if present locally, it should be reviewed.
- No committed experiment logs/checkpoints/metrics were found; actual prior experiments (if any) need external artifacts.
- Chat history table exists but route does not load history yet; intended conversational persistence behavior needs confirmation.
- Compatibility and stability of `next@^16` with current React/toolchain should be verified in target environment.

