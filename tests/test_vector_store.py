"""
Tests pour le module vector_store.py
"""
import unittest
import numpy as np
from pathlib import Path
import tempfile
import shutil

from src.vector_store import VectorStore


class TestVectorStore(unittest.TestCase):
    """Tests pour la classe VectorStore"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        # Créer un dossier temporaire pour chaque test
        self.temp_dir = tempfile.mkdtemp()
        self.vector_store = VectorStore(persist_directory=self.temp_dir)
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        # Supprimer le dossier temporaire
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_collection(self):
        """Test de création d'une collection"""
        self.vector_store.create_collection("test_collection")
        self.assertIsNotNone(self.vector_store.collection)
        self.assertEqual(self.vector_store.collection.name, "test_collection")
    
    def test_add_documents(self):
        """Test d'ajout de documents"""
        # Créer la collection
        self.vector_store.create_collection("test_collection")
        
        # Préparer des données de test
        embeddings = [[0.1, 0.2, 0.3, 0.4] * 96]  # 384 dimensions
        documents = ["Ceci est un test"]
        metadatas = [{"source": "test.txt", "chunk_index": 0}]
        ids = ["test_0"]
        
        # Ajouter les documents
        self.vector_store.add_documents(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # Vérifier que les documents ont été ajoutés
        info = self.vector_store.get_collection_info()
        self.assertEqual(info['count'], 1)
    
    def test_search(self):
        """Test de recherche"""
        # Créer la collection
        self.vector_store.create_collection("test_collection")
        
        # Ajouter des documents
        embeddings = [
            [0.1, 0.2, 0.3, 0.4] * 96,  # Document 1
            [0.5, 0.6, 0.7, 0.8] * 96   # Document 2
        ]
        documents = ["Document test 1", "Document test 2"]
        metadatas = [{"source": "test.txt"}, {"source": "test2.txt"}]
        ids = ["test_0", "test_1"]
        
        self.vector_store.add_documents(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # Rechercher
        results = self.vector_store.search(
            query_embedding=[0.1, 0.2, 0.3, 0.4] * 96,
            n_results=2
        )
        
        # Vérifier les résultats
        self.assertIn('documents', results)
        self.assertGreaterEqual(len(results['documents'][0]), 1)
    
    def test_get_collection_info(self):
        """Test de récupération des infos de collection"""
        # Collection vide
        self.vector_store.create_collection("empty_collection")
        info = self.vector_store.get_collection_info()
        self.assertEqual(info['count'], 0)
        
        # Ajouter des documents
        embeddings = [[0.1, 0.2, 0.3, 0.4] * 96]
        documents = ["Test"]
        metadatas = [{"source": "test.txt"}]
        ids = ["test_0"]
        
        self.vector_store.add_documents(embeddings, documents, metadatas, ids)
        
        # Vérifier le count
        info = self.vector_store.get_collection_info()
        self.assertEqual(info['count'], 1)
    
    def test_multiple_documents(self):
        """Test avec plusieurs documents"""
        self.vector_store.create_collection("multi_test")
        
        # Générer 5 documents avec embeddings 384D
        embeddings = [[i * 0.01 for _ in range(384)] for i in range(5)]
        documents = [f"Document {i+1}" for i in range(5)]
        metadatas = [{"source": f"file_{i}.txt", "chunk_index": i} for i in range(5)]
        ids = [f"doc_{i}" for i in range(5)]
        
        self.vector_store.add_documents(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # Vérifier
        info = self.vector_store.get_collection_info()
        self.assertEqual(info['count'], 5)


if __name__ == '__main__':
    unittest.main()

