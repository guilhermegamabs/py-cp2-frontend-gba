from datetime import datetime

from pydantic import BaseModel, Field


class ProcessingRecordResponse(BaseModel):
    id_chamada: str
    sessao: str = Field(description="Valor recebido no header X-Session-Id.")
    funcionalidade: str = Field(description="Valor recebido no header X-Feature.")
    metodo: str
    rota: str
    tag: str | None = None
    status_processamento: str = Field(
        description="EM_PROCESSAMENTO, CONCLUIDA ou FALHA. Linha presa no primeiro "
                    "estado indica requisição que morreu no meio."
    )
    status_http: int | None = None
    iniciado_em: datetime
    finalizado_em: datetime | None = None
    latencia_ms: float | None = None
    severidade: str | None = None
    freshness_segundos: float | None = None
    taxa_completude: float | None = None
    pontos: int | None = Field(default=None, description="Pontos devolvidos na resposta.")
    erro: str | None = None


class IndicatorResponse(BaseModel):
    codigo: str
    rotulo: str
    valor: float | None
    unidade: str
    limiar: float | None
    operador: str = Field(description="Comparação aplicada ao limiar: '<=' ou '>='.")
    conforme: bool | None
    grafico_sugerido: str = Field(description="Camada gráfica recomendada para o indicador.")
    acao_ao_estourar: str = Field(description="O que fazer quando o limiar é estourado.")


class ObservabilityResponse(BaseModel):
    gerado_em: datetime
    total_chamadas: int = Field(description="Total de registros na janela, antes da paginação.")
    registros_retornados: int
    indicadores: list[IndicatorResponse]
    chamadas_por_funcionalidade: dict[str, int]
    chamadas_por_sessao: dict[str, int]
    registros: list[ProcessingRecordResponse]
