"""
Configuration de l'application
"""
import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"
LOGS_DIR = BASE_DIR / "logs"

# Configuration Streamlit
STREAMLIT_PORT = 8501
STREAMLIT_HOST = "0.0.0.0"

# ChromaDB
CHROMA_COLLECTION_NAME = "documents"
CHROMA_PERSIST_DIRECTORY = "./chroma_db"

# Modèle d'embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3:8b"

# Créer les répertoires
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DB_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

