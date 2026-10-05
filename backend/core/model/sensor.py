from dataclasses import dataclass, field


@dataclass(frozen=True)
class Sensor:
    tag: str
    name: str
    area: str
    nominal_voltage: float
    nominal_current: float
    nominal_rotation: float
    status: str
    thresholds: dict = field(default_factory=dict)
