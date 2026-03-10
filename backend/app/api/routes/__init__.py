from .documents import router as documents_router
from .equations import router as equations_router
from .chat import router as chat_router

__all__ = ["documents_router", "equations_router", "chat_router"]
