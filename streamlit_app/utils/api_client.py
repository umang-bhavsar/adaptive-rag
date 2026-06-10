"""
API client for communicating with the FastAPI RAG backend.
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

PYTHON_BASE_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:8000")


def check_backend_health() -> bool:
    """Return True if the FastAPI backend is reachable."""
    try:
        response = requests.get(f"{PYTHON_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def query_backend(query: str, session_id: str) -> str:
    """
    Send a query to the RAG backend.

    Args:
        query: The user's query text.
        session_id: Session identifier for tracking conversation.

    Returns:
        Response text from the backend or error message.
    """
    url = f"{PYTHON_BASE_URL}/rag/query"
    logger.info("Calling %s for session %s", url, session_id)

    try:
        response = requests.post(
            url,
            json={"query": query, "session_id": session_id},
            timeout=120,
        )
    except requests.RequestException as exc:
        return f"Error: Could not reach backend at {PYTHON_BASE_URL}. Is it running? ({exc})"

    if response.status_code == 200:
        return response.json()["result"]["content"]

    return f"Error: {response.status_code} - {response.text}"


def document_upload_rag(file, description: str) -> bool:
    """
    Upload a document to the RAG system.

    Args:
        file: File object to upload.
        description: Description of the document.

    Returns:
        True if upload succeeds, False otherwise.
    """
    headers = {"X-Description": description}
    url = f"{PYTHON_BASE_URL}/rag/documents/upload"

    if not file:
        return False

    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(url, files=files, headers=headers, timeout=120)
    except requests.RequestException as exc:
        logger.exception("Document upload failed: %s", exc)
        return False

    return response.status_code == 200
