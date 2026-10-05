import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.exception.error_response import ErrorResponse, FieldErrorItem
from core.exception.exceptions import SensorNotFoundException, SensorOfflineException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    # ------------------------------------------------------------------ 404
    @app.exception_handler(SensorNotFoundException)
    async def handle_sensor_not_found(request: Request, exc: SensorNotFoundException):
        return _build(404, "Not Found", str(exc), request)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException):
        # Sem este handler, rota inexistente sairia com corpo diferente do resto da API.
        message = exc.detail if isinstance(exc.detail, str) else "Recurso não encontrado."
        if exc.status_code == 404:
            message = "Rota não encontrada."
        return _build(exc.status_code, "HTTP Error", message, request)

    # ------------------------------------------------------------------ 409
    @app.exception_handler(SensorOfflineException)
    async def handle_sensor_offline(request: Request, exc: SensorOfflineException):
        return _build(409, "Conflict", str(exc), request)

    # ------------------------------------------------------------------ 400
    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError):
        # Devolve todos os campos inválidos, não o primeiro.
        field_errors = [
            FieldErrorItem(
                campo=".".join(str(part) for part in error["loc"][1:]) or str(error["loc"][0]),
                mensagem=error["msg"],
            )
            for error in exc.errors()
        ]
        body = ErrorResponse.of_fields(
            400, "Bad Request", "Parâmetros inválidos na requisição.",
            request.url.path, field_errors,
        )
        return _response(400, body)

    # ------------------------------------------------------------------ 500
    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        # Loga o detalhe e responde genérico: stack trace nunca vaza para o cliente.
        logger.exception("Erro não tratado em %s", request.url.path)
        return _build(500, "Internal Server Error", "Erro interno ao processar a requisição.", request)


def _build(status: int, error: str, message: str, request: Request) -> JSONResponse:
    return _response(status, ErrorResponse.of(status, error, message, request.url.path))


def _response(status: int, body: ErrorResponse) -> JSONResponse:
    return JSONResponse(status_code=status, content=body.model_dump(mode="json", exclude_none=True))
