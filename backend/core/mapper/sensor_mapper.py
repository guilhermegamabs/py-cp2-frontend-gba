from core.dto.response.sensor_response import (
    MetricReadingResponse,
    SensorHistoryResponse,
    SensorReadingResponse,
    SensorSummaryResponse,
)
from core.enums.metric import Metric
from core.model.sensor import Sensor
from core.model.sensor_reading import MetricReading, SensorReading


class SensorMapper:
    def to_response(self, reading: SensorReading) -> SensorReadingResponse:
        return SensorReadingResponse(
            tag=reading.tag,
            nome=reading.name,
            area=reading.area,
            observado_em=reading.observed_at,
            severidade=reading.severity,
            rotulo_severidade=reading.severity.label,
            taxa_completude=round(reading.completeness_ratio, 4),
            freshness_segundos=round(reading.freshness_seconds, 2),
            metricas=[self._to_metric_response(reading, m) for m in reading.metrics],
        )

    def to_history_response(
        self,
        sensor: Sensor,
        readings: list[SensorReading],
        hours: int,
        interval_minutes: int,
    ) -> SensorHistoryResponse:
        return SensorHistoryResponse(
            tag=sensor.tag,
            nome=sensor.name,
            janela_horas=hours,
            intervalo_minutos=interval_minutes,
            total_pontos=len(readings),
            pontos=[self.to_response(r) for r in readings],
        )

    def to_summary(self, sensor: Sensor) -> SensorSummaryResponse:
        return SensorSummaryResponse(tag=sensor.tag, nome=sensor.name, area=sensor.area)

    @staticmethod
    def _to_metric_response(
        reading: SensorReading, metric_reading: MetricReading
    ) -> MetricReadingResponse:
        metric = Metric(metric_reading.metric)
        return MetricReadingResponse(
            metrica=metric.value,
            rotulo=metric.label,
            unidade=metric.unit,
            valor=metric_reading.value,
            severidade=metric_reading.severity,
            coletado_em=metric_reading.collected_at,
            idade_segundos=round(reading.age_of(metric_reading), 2),
        )
