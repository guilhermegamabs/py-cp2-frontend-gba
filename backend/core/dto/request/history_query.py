from dataclasses import dataclass

from fastapi import Query


@dataclass
class HistoryQuery:
    hours: int = Query(
        default=24,
        ge=1,
        le=168,
        description="Tamanho da janela em horas. Máximo de 7 dias (168 h).",
    )
    interval_minutes: int = Query(
        default=60,
        ge=5,
        le=1440,
        alias="intervalo_minutos",
        description="Espaçamento entre pontos da série, em minutos.",
    )
