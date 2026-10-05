from dataclasses import dataclass
from datetime import datetime

from core.enums.severity import Severity


@dataclass(frozen=True)
class RawSample:
    metric: str
    value: float | None
    collected_at: datetime


@dataclass(frozen=True)
class MetricReading:
    metric: str
    value: float | None
    collected_at: datetime
    severity: Severity


@dataclass(frozen=True)
class SensorReading:
    tag: str
    name: str
    area: str
    reference_at: datetime
    metrics: list[MetricReading]
    severity: Severity

    @property
    def observed_at(self) -> datetime:
        return max((m.collected_at for m in self.metrics), default=self.reference_at)

    @property
    def completeness_ratio(self) -> float:
        if not self.metrics:
            return 0.0
        collected = sum(1 for m in self.metrics if m.value is not None)
        return collected / len(self.metrics)

    @property
    def freshness_seconds(self) -> float:
        if not self.metrics:
            return 0.0
        oldest = min(m.collected_at for m in self.metrics)
        return (self.reference_at - oldest).total_seconds()

    def age_of(self, metric: MetricReading) -> float:
        return (self.reference_at - metric.collected_at).total_seconds()
