"""
Package core - Modules de base (auth, config)
"""
from src.core.auth import SimpleAuth
from src.core.config import (
    BASE_DIR,
    DATA_DIR,
    CHROMA_DB_DIR,
    LOGS_DIR,
    STREAMLIT_PORT,
    STREAMLIT_HOST,
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)

__all__ = [
    'SimpleAuth',
    'BASE_DIR',
    'DATA_DIR',
    'CHROMA_DB_DIR',
    'LOGS_DIR',
    'STREAMLIT_PORT',
    'STREAMLIT_HOST',
    'CHROMA_COLLECTION_NAME',
    'CHROMA_PERSIST_DIRECTORY',
    'EMBEDDING_MODEL',
    'OLLAMA_BASE_URL',
    'OLLAMA_MODEL',
]

