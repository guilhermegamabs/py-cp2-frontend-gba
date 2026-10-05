from datetime import datetime

from core.config.settings import SEVERITY_COLORS

_SEVERITY_LABELS = {
    "ok": "Operando",
    "warn": "Atenção",
    "crit": "Crítico",
    "off": "Desligado",
    "desconhecida": "Sem dado",
}


def severity_color(severity: str | None) -> str:
    return SEVERITY_COLORS.get(severity or "", "#737373")


def severity_label(severity: str | None) -> str:
    return _SEVERITY_LABELS.get(severity or "", "—")


def instant(value: str | None) -> str:
    if not value:
        return "—"
    moment = datetime.fromisoformat(value).astimezone()
    return moment.strftime("%d/%m/%Y %H:%M:%S")


def number(value: float | None, suffix: str = "", decimals: int = 2) -> str:
    if value is None:
        return "—"
    return f"{value:,.{decimals}f}".replace(",", "@").replace(".", ",").replace("@", ".") + suffix


def percent(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f}%".replace(".", ",")


def duration_seconds(value: float | None) -> str:
    if value is None:
        return "—"
    if value < 60:
        return f"{value:.0f} s"
    if value < 3600:
        return f"{value / 60:.1f} min".replace(".", ",")
    return f"{value / 3600:.1f} h".replace(".", ",")
