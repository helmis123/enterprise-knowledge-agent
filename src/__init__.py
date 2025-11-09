"""
Package src - Modules de l'application

Structure organisée en sous-packages :
- clients/ : Clients pour services externes (Ollama, etc.)
- agents/ : Agents intelligents (KnowledgeAgent, etc.)
- storage/ : Gestion du stockage (VectorStore, etc.)
- documents/ : Lecture et analyse de documents
- core/ : Modules de base (auth, config)
"""
# Exports principaux pour faciliter les imports
from src.clients import OllamaClient
from src.agents import KnowledgeAgent
from src.storage import VectorStore
from src.documents import DocumentReader
from src.core import SimpleAuth

__all__ = [
    'OllamaClient',
    'KnowledgeAgent',
    'VectorStore',
    'DocumentReader',
    'SimpleAuth',
]
