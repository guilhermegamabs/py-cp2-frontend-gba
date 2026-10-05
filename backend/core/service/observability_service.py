from collections import Counter
from datetime import datetime, timezone

from core.config.settings import settings
from core.dto.request.observability_query import ObservabilityQuery
from core.enums.feature import Feature
from core.enums.processing_status import ProcessingStatus
from core.model.indicator import INDICATOR_CATALOG, Indicator
from core.model.request_processing import RequestProcessing
from core.repository.request_processing_repository import RequestProcessingRepository

# Indicador precisa da janela inteira, mas sem teto uma base grande derruba a resposta.
_AGGREGATION_LIMIT = 5000


class ObservabilityService:
    def __init__(self, repository: RequestProcessingRepository | None = None) -> None:
        self._repository = repository or RequestProcessingRepository()

    def report(self, query: ObservabilityQuery):
        filters = dict(
            session_id=query.session_id,
            feature=query.feature,
            tag=query.tag.upper() if query.tag else None,
            since=query.since,
        )
        page = self._repository.find_all(**filters, limit=query.limit, offset=query.offset)
        window = self._repository.find_all(**filters, limit=_AGGREGATION_LIMIT, offset=0)
        total = self._repository.count(**filters)

        return (
            page,
            self._build_indicators(window),
            total,
            dict(Counter(record.feature for record in window)),
            dict(Counter(record.session_id for record in window)),
            datetime.now(timezone.utc),
        )

    def _build_indicators(self, records: list[RequestProcessing]) -> list[Indicator]:
        slo = settings.slo
        # Linha em processamento não tem latência; contá-la como falha inventaria erro.
        closed = [r for r in records if r.processing_status is not ProcessingStatus.IN_PROGRESS]
        latencies = [r.latency_ms for r in closed if r.latency_ms is not None]
        with_freshness = [r for r in records if r.freshness_seconds is not None]

        return [
            Indicator(INDICATOR_CATALOG["total_chamadas"], float(len(records)), 1.0),
            Indicator(
                INDICATOR_CATALOG["latencia_media_ms"],
                self._mean(latencies),
                slo.max_latency_ms,
            ),
            Indicator(
                INDICATOR_CATALOG["latencia_p95_ms"],
                self._percentile(latencies, 0.95),
                slo.max_latency_ms,
            ),
            Indicator(
                INDICATOR_CATALOG["taxa_sucesso"],
                self._ratio(closed, lambda r: r.http_status is not None and r.http_status < 400),
                slo.min_success_ratio,
            ),
            Indicator(
                INDICATOR_CATALOG["freshness_medio_s"],
                self._mean([r.freshness_seconds for r in with_freshness]),
                slo.max_freshness_seconds,
            ),
            Indicator(
                INDICATOR_CATALOG["taxa_completude_freshness"],
                self._completeness_freshness_rate(with_freshness),
                slo.min_completeness_ratio,
            ),
            Indicator(
                INDICATOR_CATALOG["cobertura_contexto"],
                self._ratio(records, self._has_context),
                slo.min_context_coverage,
            ),
        ]

    def _completeness_freshness_rate(self, records: list[RequestProcessing]) -> float | None:
        slo = settings.slo
        return self._ratio(
            records,
            lambda r: (
                r.freshness_seconds is not None
                and r.freshness_seconds <= slo.max_freshness_seconds
                and r.completeness_ratio is not None
                and r.completeness_ratio >= slo.min_completeness_ratio
            ),
        )

    @staticmethod
    def _has_context(record: RequestProcessing) -> bool:
        return record.session_id != "sem-sessao" and record.feature != Feature.UNKNOWN.value

    @staticmethod
    def _mean(values: list[float]) -> float | None:
        # Janela vazia devolve None, não zero: zero afirmaria uma medição que não houve.
        return round(sum(values) / len(values), 2) if values else None

    @staticmethod
    def _percentile(values: list[float], fraction: float) -> float | None:
        if not values:
            return None
        ordered = sorted(values)
        # Vizinho mais próximo: interpolar sugeriria precisão que a amostra não tem.
        index = min(len(ordered) - 1, max(0, round(fraction * len(ordered)) - 1))
        return round(ordered[index], 2)

    @staticmethod
    def _ratio(records: list, predicate) -> float | None:
        if not records:
            return None
        return round(sum(1 for record in records if predicate(record)) / len(records), 4)
