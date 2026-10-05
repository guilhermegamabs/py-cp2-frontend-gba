import uuid

import streamlit as st

_SESSION_KEY = "observability_session_id"


def current_session_id() -> str:
    if _SESSION_KEY not in st.session_state:
        st.session_state[_SESSION_KEY] = f"ui-{uuid.uuid4().hex[:12]}"
    return st.session_state[_SESSION_KEY]


def reset_session_id() -> str:
    st.session_state.pop(_SESSION_KEY, None)
    return current_session_id()
