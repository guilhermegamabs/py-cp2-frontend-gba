import pandas as pd
import streamlit as st

from core.api import sensor_api
from core.service import formatter
from core.service.session_service import current_session_id
from core.types.api import ApiError
from core.view import components


def render() -> None:
    st.header("Leitura atual")
    st.caption(
        "Consome `GET /v1/sensores/{tag}/leitura-atual`. Cada consulta gera uma linha em "
        "`sensor_tb_request_processing`, com os headers de contexto desta sessão."
    )

    session_id = current_session_id()
    try:
        sensors = sensor_api.list_sensors(session_id)
    except ApiError as error:
        components.show_api_error(error)
        return

    tag = components.sensor_selectbox(sensors, key="leitura_tag")
    if st.button("Consultar leitura", type="primary"):
        # Sem isto o botão não teria efeito visível quando o bucket não mudou.
        st.session_state["leitura_consultada"] = tag

    if st.session_state.get("leitura_consultada") != tag:
        st.info("Selecione o ativo e consulte a leitura.")
        return

    try:
        reading = sensor_api.get_current_reading(session_id, tag)
    except ApiError as error:
        components.show_api_error(error)
        return

    _render_header(reading)
    _render_metrics(reading)


def _render_header(reading: dict) -> None:
    st.markdown(f"### {reading['tag']} — {reading['nome']}")
    st.caption(reading["area"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Severidade**")
        st.markdown(components.severity_badge(reading["severidade"]), unsafe_allow_html=True)
    col2.metric("Completude do snapshot", formatter.percent(reading["taxa_completude"]))
    col3.metric("Freshness", formatter.duration_seconds(reading["freshness_segundos"]))
    st.caption(f"Observado em {formatter.instant(reading['observado_em'])}")


def _render_metrics(reading: dict) -> None:
    st.markdown("#### Grandezas")
    rows = [
        {
            "Grandeza": metric["rotulo"],
            "Valor": formatter.number(metric["valor"], f" {metric['unidade']}"),
            "Severidade": formatter.severity_label(metric["severidade"]),
            "Coletado em": formatter.instant(metric["coletado_em"]),
            "Idade": formatter.duration_seconds(metric["idade_segundos"]),
        }
        for metric in reading["metricas"]
    ]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    missing = [m["rotulo"] for m in reading["metricas"] if m["valor"] is None]
    if missing:
        # Ausência vira aviso, não zero: é o que puxa a completude para baixo.
        st.warning(f"Sem leitura nesta coleta: {', '.join(missing)}.")
