from dataclasses import dataclass
from datetime import datetime

from fastapi import Query


@dataclass
class ObservabilityQuery:
    session_id: str | None = Query(
        default=None, alias="sessao", description="Filtra por identificador de sessão."
    )
    feature: str | None = Query(
        default=None, alias="funcionalidade", description="Filtra por funcionalidade de origem."
    )
    tag: str | None = Query(
        default=None, description="Filtra pelo ativo consultado na chamada."
    )
    since: datetime | None = Query(
        default=None,
        alias="desde",
        description="Considera apenas chamadas a partir deste instante (ISO-8601).",
    )
    limit: int = Query(
        default=200, ge=1, le=1000, alias="limite",
        description="Quantidade de registros retornados. Teto de 1000 por chamada.",
    )
    offset: int = Query(default=0, ge=0, alias="deslocamento", description="Paginação.")
