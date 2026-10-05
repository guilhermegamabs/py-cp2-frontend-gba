from enum import Enum


class Feature(str, Enum):
    CURRENT_READING = "leitura-atual"
    HISTORY = "historico"
    OBSERVABILITY = "observabilidade"
    UNKNOWN = "desconhecida"

    @classmethod
    def from_header(cls, value: str | None) -> "Feature":
        # Header fora do contrato vira `desconhecida` e aparece no relatório como lacuna.
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN
