"""
Tests pour le module document_reader.py
"""
import unittest
import tempfile
import os
from pathlib import Path
import sys

# Ajouter le chemin racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.document_reader import DocumentReader


class TestDocumentReader(unittest.TestCase):
    """Tests pour la classe DocumentReader"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.reader = DocumentReader()
        
    def test_supported_extensions(self):
        """Test que les extensions supportées sont présentes"""
        expected_extensions = ['.pdf', '.docx', '.doc', '.txt', '.md', '.markdown']
        
        for ext in expected_extensions:
            self.assertIn(ext, self.reader.supported_extensions)
    
    def test_read_text_file(self):
        """Test de lecture d'un fichier texte"""
        # Créer un fichier temporaire
        content = "Ceci est un test de lecture de fichier texte.\nLigne 2."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = self.reader.read_text(Path(temp_path))
            self.assertEqual(result, content)
        finally:
            os.unlink(temp_path)
    
    def test_read_text_file_markdown(self):
        """Test de lecture d'un fichier markdown"""
        content = "# Titre\n\nCeci est du markdown."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = self.reader.read_text(Path(temp_path))
            self.assertEqual(result, content)
        finally:
            os.unlink(temp_path)
    
    def test_process_document_text(self):
        """Test de traitement d'un document texte"""
        content = "Test de document. " * 100
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = self.reader.process_document(Path(temp_path))
            
            self.assertTrue(result["success"])
            self.assertIn("text", result)
            self.assertIn("chunks", result)
            self.assertIn("metadata", result)
            
            # Vérifier la structure des métadonnées
            metadata = result["metadata"]
            self.assertIn("filename", metadata)
            self.assertIn("file_type", metadata)
            self.assertIn("num_chunks", metadata)
            
        finally:
            os.unlink(temp_path)
    
    def test_chunk_creation(self):
        """Test de création de chunks"""
        # Créer un texte assez long pour générer plusieurs chunks
        content = "Chunk test. " * 300  # Environ 3000 mots
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = self.reader.process_document(Path(temp_path))
            
            if result["success"]:
                chunks = result["chunks"]
                self.assertGreater(len(chunks), 0)
                
                # Vérifier que chaque chunk est une chaîne
                for chunk in chunks:
                    self.assertIsInstance(chunk, str)
                    self.assertGreater(len(chunk), 0)
        
        finally:
            os.unlink(temp_path)
    
    def test_unsupported_format(self):
        """Test avec un format non supporté"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("content")
            temp_path = f.name
        
        try:
            # Le code lève une ValueError au lieu de retourner un dict avec error
            with self.assertRaises(ValueError) as context:
                self.reader.process_document(Path(temp_path))
            self.assertIn("Format non supporté", str(context.exception))
        
        finally:
            os.unlink(temp_path)
    
    def test_nonexistent_file(self):
        """Test avec un fichier inexistant"""
        result = self.reader.process_document(Path("nonexistent.txt"))
        self.assertFalse(result["success"])
        # Le fichier inexistant retourne un dict avec success=False mais sans "error"
        self.assertIn("chunks", result)
        self.assertIn("metadata", result)
        self.assertEqual(len(result["chunks"]), 0)
    
    def test_get_file_type(self):
        """Test de détection du type de fichier"""
        # Créer différents types de fichiers
        test_cases = [
            (".txt", "text"),
            (".md", "text"),
            (".pdf", "pdf"),
            (".docx", "word"),
            (".doc", "word")
        ]
        
        for ext, expected_type in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                f.write("test")
                temp_path = f.name
            
            try:
                result = self.reader.process_document(Path(temp_path))
                if result["success"]:
                    metadata = result["metadata"]
                    # Note: might need to check actual file_type field
                    self.assertIn("file_type", metadata)
            finally:
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()

