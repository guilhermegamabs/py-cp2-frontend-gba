from datetime import datetime

from pydantic import BaseModel, Field

from core.enums.severity import Severity


class MetricReadingResponse(BaseModel):
    metrica: str = Field(description="Código da grandeza (v, i, t, rpm, vib).")
    rotulo: str = Field(description="Nome da grandeza para exibição.")
    unidade: str
    valor: float | None
    severidade: Severity
    coletado_em: datetime
    idade_segundos: float = Field(description="Freshness da grandeza no instante da resposta.")


class SensorReadingResponse(BaseModel):
    tag: str
    nome: str
    area: str
    observado_em: datetime
    severidade: Severity = Field(description="Pior severidade entre as grandezas do snapshot.")
    rotulo_severidade: str
    taxa_completude: float = Field(description="Fração de grandezas efetivamente coletadas.")
    freshness_segundos: float = Field(description="Idade da grandeza mais antiga do snapshot.")
    metricas: list[MetricReadingResponse]


class SensorHistoryResponse(BaseModel):
    tag: str
    nome: str
    janela_horas: int
    intervalo_minutos: int
    total_pontos: int
    pontos: list[SensorReadingResponse]


class SensorSummaryResponse(BaseModel):
    tag: str
    nome: str
    area: str
