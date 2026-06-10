"""
Chat page for the Adaptive RAG Streamlit application.
"""

import streamlit as st

from utils.api_client import check_backend_health, document_upload_rag, query_backend

st.set_page_config(
    page_title="Adaptive RAG - Chat",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "session_id" not in st.session_state:
    st.warning("Please start a session from the home page.")
    if st.button("Go to Home"):
        st.switch_page("home.py")
    st.stop()

if not check_backend_health():
    st.error("FastAPI backend is not running. Start it and refresh this page.")
    st.stop()

username = st.session_state.get("username", "User")
session_id = st.session_state["session_id"]

if "show_logout_confirm" not in st.session_state:
    st.session_state.show_logout_confirm = False

col1, col2 = st.columns([10, 2])
with col1:
    st.title("💬 Adaptive RAG Chat")
    st.caption(f"Signed in as **{username}**")
with col2:
    st.write("")
    if st.button("🔒 Logout", use_container_width=True):
        st.session_state.show_logout_confirm = True

if st.session_state.show_logout_confirm:
    st.warning("End this session and return to the home page?")
    col_confirm, col_cancel = st.columns(2)
    with col_confirm:
        if st.button("✅ Yes, logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("home.py")
    with col_cancel:
        if st.button("❌ Cancel"):
            st.session_state.show_logout_confirm = False

with st.sidebar:
    st.header("📂 Upload Documents")
    st.caption("Upload a PDF or TXT file, then ask questions about it.")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])

    if uploaded_file:
        file_description = st.text_input(
            "Describe your document (required)",
            max_chars=300,
            placeholder="E.g. My resume with work history and skills",
        )

        if "uploaded_files" not in st.session_state:
            st.session_state.uploaded_files = {}

        file_key = f"{uploaded_file.name}_{file_description}"

        if file_description:
            if file_key not in st.session_state.uploaded_files:
                with st.spinner("Uploading and indexing document..."):
                    success = document_upload_rag(uploaded_file, file_description)
                if success:
                    st.success(f"Indexed: {uploaded_file.name}")
                    st.session_state.uploaded_files[file_key] = True
                else:
                    st.error(f"Upload failed: {uploaded_file.name}")
            else:
                st.info(f"Already indexed: {uploaded_file.name}")
        else:
            st.warning("Add a short description before uploading.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Ask a question...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("Thinking..."):
        response = query_backend(user_input, session_id)
    st.session_state.chat_history.append(("assistant", response))
    st.rerun()

for role, text in st.session_state.chat_history:
    st.chat_message(role).write(text)
