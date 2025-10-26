"""
Module pour gérer le stockage vectoriel avec ChromaDB
"""
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Gestion de la base vectorielle ChromaDB
    Stocke les embeddings et permet la recherche sémantique
    """
    
    def __init__(self, persist_directory: str = "chroma_db"):
        """
        Initialise la connexion à ChromaDB
        
        Args:
            persist_directory: Répertoire où stocker la base de données
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Configuration ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Collection pour stocker les documents
        self.collection = None
        
    def create_collection(self, name: str = "documents"):
        """
        Crée ou récupère une collection
        
        Args:
            name: Nom de la collection
        """
        try:
            self.collection = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}  # Distance cosinus pour similarité
            )
            logger.info(f"Collection '{name}' créée/récupérée")
        except Exception as e:
            logger.error(f"Erreur lors de la création de la collection: {e}")
            raise
    
    def add_documents(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """
        Ajoute des documents avec leurs embeddings à la base
        
        Args:
            embeddings: Liste des vecteurs (embeddings)
            documents: Liste des textes originaux
            metadatas: Liste des métadonnées pour chaque document
            ids: Liste des identifiants uniques
        """
        if self.collection is None:
            self.create_collection()
        
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Ajouté {len(documents)} documents à la base")
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des documents: {e}")
            raise
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Recherche les documents les plus similaires
        
        Args:
            query_embedding: Embedding de la requête
            n_results: Nombre de résultats à retourner
            
        Returns:
            Dictionnaire avec les documents trouvés
        """
        if self.collection is None:
            self.create_collection()
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Retourne des informations sur la collection
        
        Returns:
            Dictionnaire avec les infos de la collection
        """
        if self.collection is None:
            return {"count": 0, "name": None}
        
        try:
            count = self.collection.count()
            return {
                "count": count,
                "name": self.collection.name,
                "metadata": self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos: {e}")
            return {"count": 0, "name": None}

