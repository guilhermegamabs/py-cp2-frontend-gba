import logging
import time
import uuid
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from core.enums.feature import Feature
from core.enums.processing_status import ProcessingStatus
from core.model.request_processing import RequestProcessing
from core.observability import call_context
from core.repository.request_processing_repository import RequestProcessingRepository

logger = logging.getLogger(__name__)

# Rotas de infraestrutura ficam fora: não são uso da solução.
_IGNORED_PATHS = {"/docs", "/redoc", "/openapi.json", "/favicon.ico", "/saude"}


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, repository: RequestProcessingRepository | None = None) -> None:
        super().__init__(app)
        self._repository = repository or RequestProcessingRepository()

    async def dispatch(self, request: Request, call_next):
        if request.url.path in _IGNORED_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        processing = RequestProcessing(
            call_id=str(uuid.uuid4()),
            # Sessão ausente vira `sem-sessao`: falta de instrumentação é achado, não erro.
            session_id=request.headers.get("X-Session-Id") or "sem-sessao",
            feature=Feature.from_header(request.headers.get("X-Feature")).value,
            method=request.method,
            path=request.url.path,
            started_at=datetime.now(timezone.utc),
        )
        call_context.bind(processing)
        self._safe_start(processing)

        # perf_counter, não time(): é monotônico e imune a ajuste de relógio durante a chamada.
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            self._close(processing, ProcessingStatus.FAILED, 500, started, repr(exc)[:500])
            raise

        status = ProcessingStatus.DONE if response.status_code < 400 else ProcessingStatus.FAILED
        self._close(processing, status, response.status_code, started)
        # Devolve o id ao cliente para correlacionar a chamada com a linha do relatório.
        response.headers["X-Call-Id"] = processing.call_id
        return response

    def _close(self, processing, status, http_status, started, error=None) -> None:
        processing.processing_status = status
        processing.http_status = http_status
        processing.finished_at = datetime.now(timezone.utc)
        processing.latency_ms = round((time.perf_counter() - started) * 1000, 2)
        processing.error_message = error
        self._safe_finish(processing)

    def _safe_start(self, processing) -> None:
        try:
            self._repository.start(processing)
        except Exception:
            # Perder o rastro é ruim; devolver 500 por causa dele é pior.
            logger.exception("Falha ao abrir registro de processamento %s", processing.call_id)

    def _safe_finish(self, processing) -> None:
        try:
            self._repository.finish(processing)
        except Exception:
            logger.exception("Falha ao fechar registro de processamento %s", processing.call_id)
