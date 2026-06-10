"""
Home page for the Adaptive RAG Streamlit app.
"""

import uuid

import streamlit as st

from utils.api_client import check_backend_health

st.set_page_config(
    page_title="Adaptive RAG - Login",
    page_icon="🔐",
    layout="centered",
)

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔐 Adaptive RAG Assistant")
st.caption("Upload documents and chat with an adaptive retrieval agent.")

if not check_backend_health():
    st.error(
        "FastAPI backend is not running. Start it first:\n\n"
        "`python -m uvicorn src.main:app --reload --port 8000`"
    )
    st.stop()

st.success("Backend connected.")

with st.form("start_form"):
    username = st.text_input(
        "Display name",
        placeholder="e.g. umang",
        help="Used to label your session. No password required.",
    )
    submit = st.form_submit_button("Start Chat", use_container_width=True)

if submit:
    if not username.strip():
        st.error("Please enter a display name.")
    else:
        st.session_state["username"] = username.strip()
        st.session_state["session_id"] = f"{username.strip()}_{uuid.uuid4().hex[:8]}"
        st.switch_page("pages/chat.py")
