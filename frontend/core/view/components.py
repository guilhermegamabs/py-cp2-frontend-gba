import streamlit as st

from core.service import formatter
from core.types.api import ApiError

# Componentes compartilhados entre as telas. Cada tela usa; nenhuma reimplementa.


def show_api_error(error: ApiError) -> None:
    if error.status == 0:
        st.error(f"**API inacessível** — {error.message}")
        return
    st.error(f"**{error.status}** — {error.message}")
    for item in error.field_errors:
        st.caption(f"`{item.campo}`: {item.mensagem}")


def severity_badge(severity: str | None) -> str:
    color = formatter.severity_color(severity)
    return (
        f"<span style='background:{color}22;color:{color};padding:3px 10px;"
        f"border-radius:999px;font-size:12px;font-weight:600'>"
        f"{formatter.severity_label(severity)}</span>"
    )


def compliance_badge(compliant: bool | None) -> str:
    if compliant is None:
        return "⚪ sem dado"
    return "🟢 conforme" if compliant else "🔴 estourado"


def sensor_selectbox(sensors: list[dict], key: str) -> str:
    options = {f"{s['tag']} — {s['nome']}": s["tag"] for s in sensors}
    chosen = st.selectbox("Ativo monitorado", list(options.keys()), key=key)
    return options[chosen]
