from fastapi import APIRouter, Depends

from core.config.dependencies import get_observability_mapper, get_observability_service
from core.config.settings import settings
from core.dto.request.observability_query import ObservabilityQuery
from core.dto.response.observability_response import IndicatorResponse, ObservabilityResponse
from core.mapper.observability_mapper import ObservabilityMapper
from core.model.indicator import INDICATOR_CATALOG, Indicator
from core.service.observability_service import ObservabilityService

router = APIRouter(prefix="/observabilidade", tags=["Observabilidade"])


@router.get(
    "",
    response_model=ObservabilityResponse,
    summary="Relatório de observabilidade das chamadas registradas",
)
def get_report(
    query: ObservabilityQuery = Depends(),
    service: ObservabilityService = Depends(get_observability_service),
    mapper: ObservabilityMapper = Depends(get_observability_mapper),
) -> ObservabilityResponse:
    return mapper.to_response(*service.report(query))


@router.get(
    "/contrato",
    response_model=list[IndicatorResponse],
    summary="Contrato de observabilidade: indicadores, limiares, gráfico e ação",
)
def get_contract(
    mapper: ObservabilityMapper = Depends(get_observability_mapper),
) -> list[IndicatorResponse]:
    thresholds = {
        "total_chamadas": 1.0,
        "latencia_media_ms": settings.slo.max_latency_ms,
        "latencia_p95_ms": settings.slo.max_latency_ms,
        "taxa_sucesso": settings.slo.min_success_ratio,
        "freshness_medio_s": settings.slo.max_freshness_seconds,
        "taxa_completude_freshness": settings.slo.min_completeness_ratio,
        "cobertura_contexto": settings.slo.min_context_coverage,
    }
    return [
        mapper.to_indicator_response(Indicator(definition, None, thresholds.get(code)))
        for code, definition in INDICATOR_CATALOG.items()
    ]
