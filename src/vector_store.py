"""
Module de gestion de la base de données vectorielle ChromaDB
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from config import Config

logger = logging.getLogger(__name__)

class VectorStore:
    """Gestionnaire de la base de données vectorielle ChromaDB"""
    
    def __init__(self):
        self.persist_directory = Config.CHROMA_PERSIST_DIRECTORY
        self.collection_name = Config.CHROMA_COLLECTION_NAME
        self.embedding_model_name = Config.EMBEDDING_MODEL
        
        # Initialiser ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Charger le modèle d'embeddings
        logger.info(f"Chargement du modèle d'embeddings: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Obtenir ou créer la collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Collection '{self.collection_name}' chargée")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Documents internes de l'entreprise"}
            )
            logger.info(f"Collection '{self.collection_name}' créée")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Générer les embeddings pour une liste de textes"""
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embeddings: {e}")
            return []
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """Ajouter des documents à la base vectorielle"""
        if not chunks:
            logger.warning("Aucun chunk à ajouter")
            return False
        
        try:
            # Extraire les contenus et métadonnées
            contents = [chunk['content'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            # Générer les IDs uniques
            ids = [f"doc_{i}_{hash(content)}" for i, content in enumerate(contents)]
            
            # Générer les embeddings
            logger.info(f"Génération des embeddings pour {len(contents)} chunks...")
            embeddings = self.generate_embeddings(contents)
            
            if not embeddings:
                logger.error("Échec de la génération des embeddings")
                return False
            
            # Ajouter à ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Ajouté {len(chunks)} chunks à la base vectorielle")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des documents: {e}")
            return False
    
    def search_similar(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Rechercher des documents similaires à la requête"""
        try:
            # Générer l'embedding de la requête
            query_embedding = self.generate_embeddings([query])
            if not query_embedding:
                return []
            
            # Rechercher dans ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Formater les résultats
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    formatted_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity_score': 1 - distance,  # Convertir distance en score de similarité
                        'rank': i + 1
                    })
            
            logger.info(f"Trouvé {len(formatted_results)} résultats pour la requête")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques de la collection"""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model_name,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {}
    
    def clear_collection(self) -> bool:
        """Vider la collection"""
        try:
            # Supprimer la collection existante
            self.client.delete_collection(name=self.collection_name)
            
            # Recréer la collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Documents internes de l'entreprise"}
            )
            
            logger.info("Collection vidée et recréée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du vidage de la collection: {e}")
            return False
    
    def delete_documents_by_source(self, source_path: str) -> bool:
        """Supprimer tous les documents d'une source spécifique"""
        try:
            # Rechercher les documents avec cette source
            results = self.collection.get(
                where={"source": source_path},
                include=['metadatas']
            )
            
            if results['ids']:
                # Supprimer les documents trouvés
                self.collection.delete(ids=results['ids'])
                logger.info(f"Supprimé {len(results['ids'])} documents de la source: {source_path}")
                return True
            else:
                logger.info(f"Aucun document trouvé pour la source: {source_path}")
                return True
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression par source: {e}")
            return False
