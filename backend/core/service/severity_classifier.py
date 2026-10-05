from core.enums.metric import Metric
from core.enums.severity import SEVERITY_RANK, Severity
from core.model.sensor import Sensor
from core.model.threshold import SEVERITY_THRESHOLDS


class SeverityClassifier:
    def classify(self, sensor: Sensor, metric: Metric, value: float | None) -> Severity:
        if sensor.status == "off":
            # Motor parado com 0 A não é `ok`: seria mostrado como operando.
            return Severity.OFF
        if value is None:
            return Severity.UNKNOWN

        threshold = SEVERITY_THRESHOLDS.get(metric)
        if threshold is None:
            return Severity.OK

        if threshold.mode == "absolute":
            observed = value
            warn, crit = threshold.warn, threshold.crit
        else:
            nominal = self._nominal(sensor, metric)
            if not nominal:
                return Severity.UNKNOWN
            observed = abs(value - nominal) / nominal
            warn, crit = threshold.warn, threshold.crit

        if observed >= crit:
            return Severity.CRIT
        if observed >= warn:
            return Severity.WARN
        return Severity.OK

    @staticmethod
    def worst(severities: list[Severity]) -> Severity:
        if not severities:
            return Severity.UNKNOWN
        return max(severities, key=lambda s: SEVERITY_RANK[s])

    @staticmethod
    def _nominal(sensor: Sensor, metric: Metric) -> float | None:
        return {
            Metric.VOLTAGE: sensor.nominal_voltage,
            Metric.CURRENT: sensor.nominal_current,
            Metric.ROTATION: sensor.nominal_rotation,
        }.get(metric)
