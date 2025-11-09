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
                metadata={"hnsw:space": "cosine"},  # Distance cosinus pour similarité
                embedding_function=None  # Pas d'embedding function car on fournit déjà les embeddings
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
    
    def search_similar(
        self,
        query_text: str,
        n_results: int = 5,
        embedding_model=None
    ) -> List[Dict[str, Any]]:
        """
        Recherche des documents similaires à partir d'un texte (nécessite un modèle d'embedding)
        
        Args:
            query_text: Texte de la requête
            n_results: Nombre de résultats à retourner
            embedding_model: Modèle pour générer les embeddings (SentenceTransformer)
            
        Returns:
            Liste de dictionnaires avec 'content', 'metadata', 'similarity_score'
        """
        if embedding_model is None:
            raise ValueError("embedding_model est requis pour search_similar")
        
        if self.collection is None:
            self.create_collection()
        
        try:
            # Générer l'embedding de la requête
            query_embedding = embedding_model.encode([query_text], convert_to_tensor=False)[0].tolist()
            
            # Rechercher dans la base
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Formater les résultats comme attendu par knowledge_agent
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    # Calculer le score de similarité (1 - distance pour cosine)
                    distance = results['distances'][0][i] if results.get('distances') and results['distances'][0] else 1.0
                    similarity_score = 1.0 - distance  # Pour cosine distance, plus proche de 0 = plus similaire
                    
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results.get('metadatas') and results['metadatas'][0] else {},
                        'similarity_score': max(0.0, min(1.0, similarity_score))  # S'assurer que c'est entre 0 et 1
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Erreur lors de la recherche similaire: {e}")
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
    
    def clear_collection(self):
        """
        Vide complètement la collection (supprime tous les documents)
        """
        if self.collection is None:
            self.create_collection()
        
        try:
            # Récupérer tous les IDs
            all_ids = self.collection.get()["ids"]
            if all_ids:
                # Supprimer tous les documents
                self.collection.delete(ids=all_ids)
                logger.info(f"Collection vidée : {len(all_ids)} documents supprimés")
                return len(all_ids)
            else:
                logger.info("Collection déjà vide")
                return 0
        except Exception as e:
            logger.error(f"Erreur lors du vidage de la collection: {e}")
            raise
    
    def delete_collection(self):
        """
        Supprime complètement la collection
        """
        if self.collection is None:
            return
        
        try:
            collection_name = self.collection.name
            self.client.delete_collection(name=collection_name)
            self.collection = None
            logger.info(f"Collection '{collection_name}' supprimée")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la collection: {e}")
            raise

