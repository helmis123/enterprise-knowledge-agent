"""
Tests unitaires simples pour l'Agent Knowledge Interne
"""
import unittest
import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from document_processor import DocumentProcessor

class TestConfig(unittest.TestCase):
    """Tests pour la configuration"""
    
    def test_config_initialization(self):
        """Tester l'initialisation de la configuration"""
        self.assertIsNotNone(Config.OLLAMA_BASE_URL)
        self.assertIsNotNone(Config.CHROMA_PERSIST_DIRECTORY)
        self.assertIsNotNone(Config.EMBEDDING_MODEL)
    
    def test_directories_creation(self):
        """Tester la création des répertoires"""
        Config.setup_directories()
        self.assertTrue(Config.DATA_DIR.exists())
        self.assertTrue(Config.CHROMA_DB_DIR.exists())
        self.assertTrue(Config.LOGS_DIR.exists())

class TestDocumentProcessor(unittest.TestCase):
    """Tests pour le processeur de documents"""
    
    def setUp(self):
        """Configuration des tests"""
        self.processor = DocumentProcessor()
    
    def test_supported_extensions(self):
        """Tester les extensions supportées"""
        expected_extensions = {'.pdf', '.docx', '.doc', '.md', '.txt'}
        self.assertEqual(self.processor.supported_extensions, expected_extensions)
    
    def test_chunk_creation(self):
        """Tester la création de chunks"""
        test_text = "Ceci est un test. Voici une deuxième phrase. Et une troisième phrase pour tester le découpage."
        metadata = {'source': 'test.txt', 'filename': 'test.txt'}
        
        chunks = self.processor.create_chunks(test_text, metadata)
        
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        
        for chunk in chunks:
            self.assertIn('content', chunk)
            self.assertIn('metadata', chunk)
            self.assertLessEqual(len(chunk['content']), self.processor.max_chunk_size)

class TestDataFiles(unittest.TestCase):
    """Tests pour les fichiers de données"""
    
    def test_data_files_exist(self):
        """Tester l'existence des fichiers de données d'exemple"""
        data_dir = Path('data')
        if data_dir.exists():
            files = list(data_dir.glob('*.md'))
            self.assertGreater(len(files), 0, "Aucun fichier de données d'exemple trouvé")
            
            # Vérifier le contenu des fichiers
            for file_path in files:
                content = file_path.read_text(encoding='utf-8')
                self.assertGreater(len(content), 0, f"Le fichier {file_path} est vide")

if __name__ == '__main__':
    # Créer une suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajouter les tests
    test_suite.addTest(unittest.makeSuite(TestConfig))
    test_suite.addTest(unittest.makeSuite(TestDocumentProcessor))
    test_suite.addTest(unittest.makeSuite(TestDataFiles))
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Afficher le résumé
    print(f"\n{'='*50}")
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    
    if result.failures:
        print("\nÉchecs:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErreurs:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 Tous les tests sont passés !")
    else:
        print("\n❌ Certains tests ont échoué.")
