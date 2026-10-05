import random
from datetime import datetime, timedelta, timezone

from core.enums.metric import Metric
from core.model.sensor import Sensor
from core.model.sensor_reading import RawSample
from core.repository.sensor_seed import SENSOR_SEED

# Grandezas publicadas por ativo, na ordem em que aparecem na interface.
_METRICS = [Metric.VOLTAGE, Metric.CURRENT, Metric.TEMPERATURE, Metric.ROTATION, Metric.VIBRATION]

# Sem ruído a série sai constante e nenhum indicador de tendência mostra nada.
_NOISE = {Metric.VOLTAGE: 3.0, Metric.CURRENT: 0.8, Metric.TEMPERATURE: 4.0,
          Metric.ROTATION: 10.0, Metric.VIBRATION: 0.4}

# Com 0.0 nos dois, completude e freshness mediriam 100% para sempre.
_MISSING_RATE = 0.06
_STALE_RATE = 0.08


class SensorRepository:
    def __init__(self) -> None:
        self._sensors = {
            item["tag"]: Sensor(
                tag=item["tag"],
                name=item["name"],
                area=item["area"],
                nominal_voltage=item["nominal_voltage"],
                nominal_current=item["nominal_current"],
                nominal_rotation=item["nominal_rotation"],
                status=item["status"],
            )
            for item in SENSOR_SEED
        }
        self._baselines = {item["tag"]: item["baseline"] for item in SENSOR_SEED}

    def find_all(self) -> list[Sensor]:
        return list(self._sensors.values())

    def find_by_tag(self, tag: str) -> Sensor | None:
        # Tag é case-insensitive: `m-101` na URL é o mesmo ativo que `M-101`.
        return self._sensors.get(tag.upper())

    def read_current(
        self, tag: str, reference: datetime | None = None
    ) -> tuple[datetime, list[RawSample]]:
        reference = reference or datetime.now(timezone.utc)
        # Bucket de 30 s: sem ele, cada F5 inventaria uma leitura nova.
        bucket = int(reference.timestamp() // 30)
        return reference, self._sample(tag, reference, bucket)

    def read_history(
        self, tag: str, hours: int, interval_minutes: int, reference: datetime | None = None
    ) -> list[tuple[datetime, list[RawSample]]]:
        reference = reference or datetime.now(timezone.utc)
        points = max(1, int((hours * 60) / interval_minutes))
        history = []
        for step in range(points, 0, -1):
            moment = reference - timedelta(minutes=interval_minutes * step)
            # Semente pelo instante do ponto: a série passada não muda entre consultas.
            bucket = int(moment.timestamp() // (interval_minutes * 60))
            history.append((moment, self._sample(tag, moment, bucket)))
        return history

    def _sample(self, tag: str, moment: datetime, bucket: int) -> list[RawSample]:
        baseline = self._baselines[tag.upper()]
        samples = []
        for metric in _METRICS:
            rng = random.Random(f"{tag.upper()}|{bucket}|{metric.value}")
            value = baseline[metric.value]
            if value != 0.0:
                value = round(value + (rng.random() - 0.5) * _NOISE[metric], 2)

            missing = rng.random() < _MISSING_RATE
            lag = 180.0 + rng.random() * 600.0 if rng.random() < _STALE_RATE else rng.random() * 20.0
            samples.append(
                RawSample(
                    metric=metric.value,
                    value=None if missing else value,
                    collected_at=moment - timedelta(seconds=lag),
                )
            )
        return samples
