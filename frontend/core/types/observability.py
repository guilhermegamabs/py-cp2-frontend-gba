from typing import TypedDict


class ProcessingRecord(TypedDict):
    id_chamada: str
    sessao: str
    funcionalidade: str
    metodo: str
    rota: str
    tag: str | None
    status_processamento: str
    status_http: int | None
    iniciado_em: str
    finalizado_em: str | None
    latencia_ms: float | None
    severidade: str | None
    freshness_segundos: float | None
    taxa_completude: float | None
    pontos: int | None
    erro: str | None


class Indicator(TypedDict):
    codigo: str
    rotulo: str
    valor: float | None
    unidade: str
    limiar: float | None
    operador: str
    conforme: bool | None
    grafico_sugerido: str
    acao_ao_estourar: str


class ObservabilityReport(TypedDict):
    gerado_em: str
    total_chamadas: int
    registros_retornados: int
    indicadores: list[Indicator]
    chamadas_por_funcionalidade: dict[str, int]
    chamadas_por_sessao: dict[str, int]
    registros: list[ProcessingRecord]
