from datetime import datetime, timezone

from pydantic import BaseModel


class FieldErrorItem(BaseModel):
    campo: str
    mensagem: str


class ErrorResponse(BaseModel):
    model_config = {"json_schema_extra": {"example": {
        "timestamp": "2026-10-05T18:00:00+00:00",
        "status": 404,
        "error": "Not Found",
        "message": "Sensor não encontrado para a tag: M-999",
        "path": "/v1/sensores/M-999/leitura-atual",
    }}}

    timestamp: datetime
    status: int
    error: str
    message: str
    path: str
    field_errors: list[FieldErrorItem] | None = None

    @classmethod
    def of(cls, status: int, error: str, message: str, path: str) -> "ErrorResponse":
        return cls(
            timestamp=datetime.now(timezone.utc),
            status=status,
            error=error,
            message=message,
            path=path,
        )

    @classmethod
    def of_fields(
        cls, status: int, error: str, message: str, path: str, field_errors: list[FieldErrorItem]
    ) -> "ErrorResponse":
        response = cls.of(status, error, message, path)
        return response.model_copy(update={"field_errors": field_errors})
