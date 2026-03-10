"""EquateAI - AI Scientific Equation Parsing & Reasoning Platform."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import init_db
from app.api.routes import documents_router, equations_router, chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    # shutdown if needed


app = FastAPI(
    title=settings.app_name,
    description="AI-powered scientific document and equation parsing, dependency graphs, and reasoning.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router, prefix=settings.api_prefix)
app.include_router(equations_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {"message": "EquateAI API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
