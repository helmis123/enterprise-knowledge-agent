"""
Configuration et utilitaires pour l'Agent Knowledge Interne
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('config.env')

class Config:
    """Configuration centralisée de l'application"""
    
    # Modèle LLM
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3:8b')
    
    # Base de données vectorielle
    CHROMA_PERSIST_DIRECTORY = os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db')
    CHROMA_COLLECTION_NAME = os.getenv('CHROMA_COLLECTION_NAME', 'enterprise_documents')
    
    # Modèle d'embeddings
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    
    # Configuration Streamlit
    STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))
    STREAMLIT_SERVER_ADDRESS = os.getenv('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')
    
    # Sécurité
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    # Logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/agent.log')
    
    # Limites
    MAX_DOCUMENT_SIZE_MB = int(os.getenv('MAX_DOCUMENT_SIZE_MB', '50'))
    MAX_CHUNK_SIZE = int(os.getenv('MAX_CHUNK_SIZE', '1000'))
    MAX_CHUNKS_PER_DOCUMENT = int(os.getenv('MAX_CHUNKS_PER_DOCUMENT', '100'))
    
    # Chemins
    DATA_DIR = Path('data')
    CHROMA_DB_DIR = Path(CHROMA_PERSIST_DIRECTORY)
    LOGS_DIR = Path('logs')
    
    @classmethod
    def setup_directories(cls):
        """Créer les répertoires nécessaires"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.CHROMA_DB_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def setup_logging(cls):
        """Configurer le système de logging"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

# Initialiser la configuration
Config.setup_directories()
logger = Config.setup_logging()
