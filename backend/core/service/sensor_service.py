from datetime import datetime, timezone

from core.enums.metric import Metric
from core.exception.exceptions import SensorNotFoundException
from core.model.sensor import Sensor
from core.model.sensor_reading import MetricReading, RawSample, SensorReading
from core.observability import call_context
from core.repository.sensor_repository import SensorRepository
from core.service.severity_classifier import SeverityClassifier


class SensorService:
    def __init__(
        self,
        repository: SensorRepository | None = None,
        classifier: SeverityClassifier | None = None,
    ) -> None:
        self._repository = repository or SensorRepository()
        self._classifier = classifier or SeverityClassifier()

    def list_sensors(self) -> list[Sensor]:
        return self._repository.find_all()

    def get_current_reading(self, tag: str) -> SensorReading:
        sensor = self._require_sensor(tag)
        moment, samples = self._repository.read_current(sensor.tag, datetime.now(timezone.utc))
        reading = self._build_reading(sensor, moment, samples)

        self._describe(sensor.tag, [reading])
        return reading

    def get_history(
        self, tag: str, hours: int, interval_minutes: int
    ) -> tuple[Sensor, list[SensorReading]]:
        sensor = self._require_sensor(tag)
        points = self._repository.read_history(
            sensor.tag, hours, interval_minutes, datetime.now(timezone.utc)
        )
        readings = [self._build_reading(sensor, moment, samples) for moment, samples in points]

        self._describe(sensor.tag, readings)
        return sensor, readings

    def _require_sensor(self, tag: str) -> Sensor:
        sensor = self._repository.find_by_tag(tag)
        if sensor is None:
            raise SensorNotFoundException(tag)
        return sensor

    def _build_reading(
        self, sensor: Sensor, moment: datetime, samples: list[RawSample]
    ) -> SensorReading:
        metrics = [
            MetricReading(
                metric=sample.metric,
                value=sample.value,
                collected_at=sample.collected_at,
                severity=self._classifier.classify(sensor, Metric(sample.metric), sample.value),
            )
            for sample in samples
        ]
        return SensorReading(
            tag=sensor.tag,
            name=sensor.name,
            area=sensor.area,
            reference_at=moment,
            metrics=metrics,
            severity=self._classifier.worst([m.severity for m in metrics]),
        )

    def _describe(self, tag: str, readings: list[SensorReading]) -> None:
        if not readings:
            return
        completeness = sum(r.completeness_ratio for r in readings) / len(readings)
        freshness = sum(r.freshness_seconds for r in readings) / len(readings)
        call_context.describe(
            tag=tag,
            severity=readings[-1].severity.value,
            completeness_ratio=round(completeness, 4),
            freshness_seconds=round(freshness, 2),
            points=len(readings),
        )
