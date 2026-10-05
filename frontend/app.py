import streamlit as st

st.set_page_config(page_title="Sensor Monitoring — Forzy", page_icon="📡", layout="wide")

from core.config.settings import API_BASE_URL  # noqa: E402  (depende do set_page_config)
from core.service.session_service import current_session_id, reset_session_id
from core.view import historico_view, leitura_atual_view, observabilidade_view

PAGES = {
    "Leitura atual": leitura_atual_view.render,
    "Histórico": historico_view.render,
    "Observabilidade": observabilidade_view.render,
}

with st.sidebar:
    st.markdown("### Sensor Monitoring")
    st.caption("Digital Twin Forzy · provider de Sensores")
    choice = st.radio("Telas", list(PAGES.keys()), label_visibility="collapsed")

    st.divider()
    st.caption(f"API: `{API_BASE_URL}`")
    st.caption(f"Sessão: `{current_session_id()}`")
    if st.button("Nova sessão", help="Gera outro X-Session-Id para isolar uma coleta"):
        reset_session_id()
        st.rerun()

PAGES[choice]()
