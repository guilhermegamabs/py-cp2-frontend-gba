from dataclasses import dataclass, field


@dataclass
class FieldError:
    campo: str
    mensagem: str


@dataclass
class ApiError(Exception):
    status: int
    message: str
    path: str = ""
    error: str = ""
    timestamp: str = ""
    field_errors: list[FieldError] = field(default_factory=list)

    def __str__(self) -> str:
        return self.message
