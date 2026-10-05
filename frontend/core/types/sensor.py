from typing import TypedDict


class MetricReading(TypedDict):
    metrica: str
    rotulo: str
    unidade: str
    valor: float | None
    severidade: str
    coletado_em: str
    idade_segundos: float


class SensorReading(TypedDict):
    tag: str
    nome: str
    area: str
    observado_em: str
    severidade: str
    rotulo_severidade: str
    taxa_completude: float
    freshness_segundos: float
    metricas: list[MetricReading]


class SensorHistory(TypedDict):
    tag: str
    nome: str
    janela_horas: int
    intervalo_minutos: int
    total_pontos: int
    pontos: list[SensorReading]


class SensorSummary(TypedDict):
    tag: str
    nome: str
    area: str
