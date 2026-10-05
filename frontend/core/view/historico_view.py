import altair as alt
import pandas as pd
import streamlit as st

from core.api import sensor_api
from core.service import formatter
from core.service.session_service import current_session_id
from core.types.api import ApiError
from core.view import components


def render() -> None:
    st.header("Histórico")
    st.caption(
        "Consome `GET /v1/sensores/{tag}/historico`. A janela e o intervalo vão como query "
        "params e a série volta do ponto mais antigo para o mais recente."
    )

    session_id = current_session_id()
    try:
        sensors = sensor_api.list_sensors(session_id)
    except ApiError as error:
        components.show_api_error(error)
        return

    tag = components.sensor_selectbox(sensors, key="historico_tag")
    col1, col2 = st.columns(2)
    hours = col1.slider("Janela (horas)", min_value=1, max_value=168, value=24)
    interval = col2.select_slider(
        "Intervalo entre pontos (minutos)", options=[15, 30, 60, 120, 240], value=60
    )

    if not st.button("Consultar histórico", type="primary"):
        st.info("Ajuste a janela e consulte o histórico.")
        return

    try:
        history = sensor_api.get_history(session_id, tag, hours, interval)
    except ApiError as error:
        components.show_api_error(error)
        return

    st.markdown(f"### {history['tag']} — {history['nome']}")
    st.caption(
        f"{history['total_pontos']} pontos · janela de {history['janela_horas']} h · "
        f"intervalo de {history['intervalo_minutos']} min"
    )

    frame = _to_frame(history)
    if frame.empty:
        st.warning("A janela pedida não devolveu nenhum ponto.")
        return

    _render_series(frame)
    _render_table(history)


def _to_frame(history: dict) -> pd.DataFrame:
    rows = []
    for point in history["pontos"]:
        row = {"instante": pd.to_datetime(point["observado_em"])}
        for metric in point["metricas"]:
            # NaN, não 0: o gráfico abre um vão, a leitura honesta de "não houve coleta".
            row[f"{metric['rotulo']} ({metric['unidade']})"] = metric["valor"]
        rows.append(row)
    return pd.DataFrame(rows).set_index("instante") if rows else pd.DataFrame()


def _render_series(frame: pd.DataFrame) -> None:
    st.markdown("#### Evolução das grandezas")
    # Uma grandeza por gráfico: tensão e vibração na mesma escala achatam a segunda.
    for column in frame.columns:
        st.caption(column)
        st.altair_chart(_line_chart(frame, column), use_container_width=True)


def _line_chart(frame: pd.DataFrame, column: str) -> alt.Chart:
    data = frame.reset_index().rename(columns={column: "valor"})
    return (
        alt.Chart(data)
        .mark_line(point=True)
        .encode(
            x=alt.X("instante:T", title=None),
            y=alt.Y("valor:Q", title=None, scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip("instante:T", title="Instante"),
                     alt.Tooltip("valor:Q", title=column)],
        )
        .properties(height=180)
    )


def _render_table(history: dict) -> None:
    with st.expander("Pontos da série, com severidade e qualidade do dado"):
        rows = [
            {
                "Instante": formatter.instant(point["observado_em"]),
                "Severidade": formatter.severity_label(point["severidade"]),
                "Completude": formatter.percent(point["taxa_completude"]),
                "Freshness": formatter.duration_seconds(point["freshness_segundos"]),
                **{
                    metric["rotulo"]: formatter.number(metric["valor"])
                    for metric in point["metricas"]
                },
            }
            for point in reversed(history["pontos"])
        ]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
