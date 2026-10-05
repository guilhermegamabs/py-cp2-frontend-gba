from core.api import http_client
from core.enums.feature import Feature
from core.types.observability import Indicator, ObservabilityReport


def get_report(
    session_id: str,
    limit: int = 200,
    feature: str | None = None,
    tag: str | None = None,
    only_this_session: bool = False,
) -> ObservabilityReport:
    # Filtro ausente não vai na query: a API trata null como "ignore este filtro".
    params: dict = {"limite": limit}
    if feature:
        params["funcionalidade"] = feature
    if tag:
        params["tag"] = tag
    if only_this_session:
        params["sessao"] = session_id
    return http_client.get("/observabilidade", session_id, Feature.OBSERVABILITY, params=params)


def get_contract(session_id: str) -> list[Indicator]:
    return http_client.get("/observabilidade/contrato", session_id, Feature.OBSERVABILITY)
