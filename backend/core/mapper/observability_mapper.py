from datetime import datetime

from core.dto.response.observability_response import (
    IndicatorResponse,
    ObservabilityResponse,
    ProcessingRecordResponse,
)
from core.model.indicator import Indicator
from core.model.request_processing import RequestProcessing


class ObservabilityMapper:
    def to_response(
        self,
        records: list[RequestProcessing],
        indicators: list[Indicator],
        total_calls: int,
        calls_by_feature: dict[str, int],
        calls_by_session: dict[str, int],
        generated_at: datetime,
    ) -> ObservabilityResponse:
        return ObservabilityResponse(
            gerado_em=generated_at,
            total_chamadas=total_calls,
            registros_retornados=len(records),
            indicadores=[self.to_indicator_response(i) for i in indicators],
            chamadas_por_funcionalidade=calls_by_feature,
            chamadas_por_sessao=calls_by_session,
            registros=[self.to_record_response(r) for r in records],
        )

    @staticmethod
    def to_record_response(record: RequestProcessing) -> ProcessingRecordResponse:
        return ProcessingRecordResponse(
            id_chamada=record.call_id,
            sessao=record.session_id,
            funcionalidade=record.feature,
            metodo=record.method,
            rota=record.path,
            tag=record.tag,
            status_processamento=record.processing_status.value,
            status_http=record.http_status,
            iniciado_em=record.started_at,
            finalizado_em=record.finished_at,
            latencia_ms=record.latency_ms,
            severidade=record.severity,
            freshness_segundos=record.freshness_seconds,
            taxa_completude=record.completeness_ratio,
            pontos=record.points,
            erro=record.error_message,
        )

    @staticmethod
    def to_indicator_response(indicator: Indicator) -> IndicatorResponse:
        definition = indicator.definition
        return IndicatorResponse(
            codigo=definition.code,
            rotulo=definition.label,
            valor=indicator.value,
            unidade=definition.unit,
            limiar=indicator.threshold,
            operador=definition.operator,
            conforme=indicator.compliant,
            grafico_sugerido=definition.suggested_chart,
            acao_ao_estourar=definition.breach_action,
        )
