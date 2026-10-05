from enum import Enum


class Severity(str, Enum):
    OK = "ok"
    WARN = "warn"
    CRIT = "crit"
    OFF = "off"
    # Coleta falha não é `ok`: sem este valor o indicador de completude perde o sentido.
    UNKNOWN = "desconhecida"

    @property
    def label(self) -> str:
        return _LABELS[self]


_LABELS = {
    Severity.OK: "Operando",
    Severity.WARN: "Atenção",
    Severity.CRIT: "Crítico",
    Severity.OFF: "Desligado",
    Severity.UNKNOWN: "Sem dado",
}

# Ordem de gravidade usada para reduzir um snapshot a uma severidade só.
SEVERITY_RANK = {
    Severity.OFF: 0,
    Severity.OK: 1,
    Severity.UNKNOWN: 2,
    Severity.WARN: 3,
    Severity.CRIT: 4,
}
