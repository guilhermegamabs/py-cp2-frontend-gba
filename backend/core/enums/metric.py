from enum import Enum


class Metric(str, Enum):
    VOLTAGE = "v"
    CURRENT = "i"
    TEMPERATURE = "t"
    ROTATION = "rpm"
    VIBRATION = "vib"

    @property
    def label(self) -> str:
        return _META[self][0]

    @property
    def unit(self) -> str:
        return _META[self][1]


_META = {
    Metric.VOLTAGE: ("Tensão", "V"),
    Metric.CURRENT: ("Corrente", "A"),
    Metric.TEMPERATURE: ("Temperatura", "°C"),
    Metric.ROTATION: ("Rotação", "rpm"),
    Metric.VIBRATION: ("Vibração", "mm/s"),
}
