from dataclasses import dataclass

from core.enums.metric import Metric


@dataclass(frozen=True)
class Threshold:
    mode: str
    warn: float
    crit: float
    source: str


# A Governança é dona destes números; `source` registra a origem de cada um.
SEVERITY_THRESHOLDS: dict[Metric, Threshold] = {
    Metric.TEMPERATURE: Threshold("absolute", 75.0, 90.0, "Classe de isolamento F (WEG W22)"),
    Metric.VIBRATION: Threshold("absolute", 2.8, 4.5, "ISO 10816-3, zonas B/C e C/D"),
    Metric.CURRENT: Threshold("deviation", 0.10, 0.15, "Fator de serviço 1.15 sobre a corrente de placa"),
    Metric.VOLTAGE: Threshold("deviation", 0.05, 0.10, "NBR 5410 — faixa adequada de tensão"),
    Metric.ROTATION: Threshold("deviation", 0.01, 0.02, "Escorregamento nominal do motor de indução"),
}
