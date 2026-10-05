import pandas as pd
import streamlit as st

from core.api import observability_api
from core.service import formatter
from core.service.session_service import current_session_id
from core.types.api import ApiError
from core.view import components

# Formatadores por unidade do indicador: fração vira porcentagem, segundo vira duração.
_UNIT_FORMATTERS = {
    "fração": formatter.percent,
    "s": formatter.duration_seconds,
    "ms": lambda value: formatter.number(value, " ms"),
    "chamadas": lambda value: formatter.number(value, "", 0),
}


def render() -> None:
    st.header("Observabilidade")
    st.caption(
        "Consome `GET /v1/observabilidade`. É o relatório que a disciplina de Governança em IA "
        "usa como evidência: cada linha é uma chamada registrada pelo back-end."
    )

    session_id = current_session_id()
    col1, col2, col3 = st.columns([2, 2, 3])
    limit = col1.number_input("Registros exibidos", min_value=10, max_value=1000, value=100, step=10)
    feature = col2.selectbox(
        "Funcionalidade", ["todas", "leitura-atual", "historico", "observabilidade", "desconhecida"]
    )
    only_session = col3.checkbox(
        "Somente esta sessão", value=False,
        help=f"Filtra por X-Session-Id = {session_id}",
    )

    try:
        report = observability_api.get_report(
            session_id,
            limit=int(limit),
            feature=None if feature == "todas" else feature,
            only_this_session=only_session,
        )
    except ApiError as error:
        components.show_api_error(error)
        return

    st.caption(
        f"Relatório gerado em {formatter.instant(report['gerado_em'])} · "
        f"{report['total_chamadas']} chamadas na janela · "
        f"{report['registros_retornados']} exibidas · sessão desta aba: `{session_id}`"
    )

    _render_indicators(report["indicadores"])
    _render_distributions(report)
    _render_latency_series(report["registros"])
    _render_records(report["registros"])
    _render_contract(report["indicadores"])


def _render_indicators(indicators: list[dict]) -> None:
    st.markdown("#### Indicadores")
    # Três por linha: mais que isso e o rótulo do indicador quebra em duas linhas.
    for start in range(0, len(indicators), 3):
        for column, indicator in zip(st.columns(3), indicators[start:start + 3]):
            with column:
                shown = _UNIT_FORMATTERS.get(
                    indicator["unidade"], lambda value: formatter.number(value)
                )(indicator["valor"])
                column.metric(indicator["rotulo"], shown)
                limiar = _UNIT_FORMATTERS.get(
                    indicator["unidade"], lambda value: formatter.number(value)
                )(indicator["limiar"])
                st.caption(
                    f"{components.compliance_badge(indicator['conforme'])} · "
                    f"limiar {indicator['operador']} {limiar}"
                )


def _render_distributions(report: dict) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Chamadas por funcionalidade")
        data = report["chamadas_por_funcionalidade"]
        if data:
            st.bar_chart(pd.Series(data, name="chamadas"), height=220)
    with col2:
        st.markdown("#### Chamadas por sessão")
        data = report["chamadas_por_sessao"]
        if data:
            st.bar_chart(pd.Series(data, name="chamadas"), height=220)


def _render_latency_series(records: list[dict]) -> None:
    closed = [r for r in records if r["latencia_ms"] is not None]
    if not closed:
        return
    st.markdown("#### Latência por chamada")
    frame = pd.DataFrame(
        {
            "instante": [pd.to_datetime(r["iniciado_em"]) for r in closed],
            "latência (ms)": [r["latencia_ms"] for r in closed],
        }
    ).set_index("instante").sort_index()
    st.line_chart(frame, height=220)


def _render_records(records: list[dict]) -> None:
    st.markdown("#### Registros de processamento")
    if not records:
        st.info("Nenhuma chamada registrada ainda. Use as outras telas e volte aqui.")
        return

    rows = [
        {
            "Início": formatter.instant(record["iniciado_em"]),
            "Fim": formatter.instant(record["finalizado_em"]),
            "Sessão": record["sessao"],
            "Funcionalidade": record["funcionalidade"],
            "Rota": record["rota"],
            "Tag": record["tag"] or "—",
            "Processamento": record["status_processamento"],
            "HTTP": record["status_http"] or "—",
            "Latência": formatter.number(record["latencia_ms"], " ms"),
            "Severidade": formatter.severity_label(record["severidade"]),
            "Freshness": formatter.duration_seconds(record["freshness_segundos"]),
            "Completude": formatter.percent(record["taxa_completude"]),
            "Erro": record["erro"] or "—",
        }
        for record in records
    ]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    in_progress = [r for r in records if r["status_processamento"] == "EM_PROCESSAMENTO"]
    if in_progress:
        st.caption(
            f"{len(in_progress)} chamada(s) em `EM_PROCESSAMENTO`. A própria consulta deste "
            "relatório aparece assim, porque a linha dela só fecha depois que a resposta sai. "
            "Linha antiga nesse estado é requisição que morreu no meio do processamento."
        )


def _render_contract(indicators: list[dict]) -> None:
    with st.expander("Contrato de observabilidade — limiar, gráfico sugerido e ação de estouro"):
        st.caption(
            "Vem de `GET /v1/observabilidade/contrato`, a mesma fonte que a API aplica. "
            "É o insumo direto do documento da disciplina de Governança em IA."
        )
        for indicator in indicators:
            st.markdown(
                f"**{indicator['rotulo']}** (`{indicator['codigo']}`) — limiar "
                f"`{indicator['operador']} {indicator['limiar']}` {indicator['unidade']}"
            )
            st.markdown(f"- Camada gráfica: {indicator['grafico_sugerido']}")
            st.markdown(f"- Ao estourar: {indicator['acao_ao_estourar']}")
