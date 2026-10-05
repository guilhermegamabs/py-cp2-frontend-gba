from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config.settings import settings

# Headers de contexto que o front envia e o navegador precisa ter autorização para mandar.
CONTEXT_HEADERS = ["X-Session-Id", "X-Feature"]


def configure_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["Content-Type", *CONTEXT_HEADERS],
        # Expor o header: sem ele o front não correlaciona a chamada com o registro.
        expose_headers=["X-Call-Id"],
        max_age=3600,
    )
