"""
Script d'installation et de test pour l'Agent Knowledge Interne
"""
import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Installer les dependances Python"""
    print("Installation des dependances Python...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependances installees avec succes")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'installation: {e}")
        return False

def test_imports():
    """Tester les imports des modules"""
    print("\nTest des imports...")
    
    try:
        # Ajouter le repertoire src au path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from config import Config
        print("Config importe")
        
        from document_processor import DocumentProcessor
        print("DocumentProcessor importe")
        
        from vector_store import VectorStore
        print("VectorStore importe")
        
        from llm_client import OllamaClient
        print("OllamaClient importe")
        
        from auth import SimpleAuth
        print("SimpleAuth importe")
        
        return True
        
    except ImportError as e:
        print(f"Erreur d'import: {e}")
        return False

def test_config():
    """Tester la configuration"""
    print("\nTest de la configuration...")
    
    try:
        from config import Config
        
        # Tester l'initialisation
        Config.setup_directories()
        print("Repertoires crees")
        
        # Verifier les repertoires
        assert Config.DATA_DIR.exists(), "Repertoire data manquant"
        assert Config.CHROMA_DB_DIR.exists(), "Repertoire chroma_db manquant"
        assert Config.LOGS_DIR.exists(), "Repertoire logs manquant"
        print("Repertoires verifies")
        
        return True
        
    except Exception as e:
        print(f"Erreur de configuration: {e}")
        return False

def test_document_processing():
    """Tester le traitement des documents"""
    print("\nTest du traitement des documents...")
    
    try:
        from document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Verifier les extensions supportees
        expected_extensions = {'.pdf', '.docx', '.doc', '.md', '.txt'}
        assert processor.supported_extensions == expected_extensions
        print("Extensions supportees verifiees")
        
        # Tester la creation de chunks
        test_text = "Ceci est un test. Voici une deuxieme phrase."
        metadata = {'source': 'test.txt', 'filename': 'test.txt'}
        
        chunks = processor.create_chunks(test_text, metadata)
        assert len(chunks) > 0, "Aucun chunk cree"
        print("Creation de chunks testee")
        
        return True
        
    except Exception as e:
        print(f"Erreur de traitement: {e}")
        return False

def test_data_files():
    """Tester les fichiers de donnees"""
    print("\nTest des fichiers de donnees...")
    
    data_dir = Path('data')
    if not data_dir.exists():
        print("Repertoire data non trouve")
        return False
    
    files = list(data_dir.glob('*.md'))
    if not files:
        print("Aucun fichier de donnees trouve")
        return False
    
    print(f"{len(files)} fichiers de donnees trouves")
    
    for file_path in files:
        content = file_path.read_text(encoding='utf-8')
        if len(content) > 0:
            print(f"{file_path.name} lu avec succes")
        else:
            print(f"{file_path.name} est vide")
    
    return True

def main():
    """Fonction principale"""
    print("Installation et Test de l'Agent Knowledge Interne")
    print("=" * 60)
    
    # Installation des dependances
    if not install_requirements():
        print("Echec de l'installation des dependances")
        return
    
    # Tests
    tests = [
        ("Imports des modules", test_imports),
        ("Configuration", test_config),
        ("Traitement des documents", test_document_processing),
        ("Fichiers de donnees", test_data_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Resume
    print("\n" + "=" * 60)
    print("Resume des tests:")
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResultat: {passed}/{len(results)} tests reussis")
    
    if passed == len(results):
        print("\nInstallation reussie !")
        print("\nProchaines etapes:")
        print("   1. Demarrer Ollama: docker run -d -p 11434:11434 ollama/ollama:latest")
        print("   2. Telecharger le modele: docker exec <container> ollama pull llama3:8b")
        print("   3. Demarrer l'application: python start.py")
        print("   4. Ouvrir http://localhost:8501")
    else:
        print("\nCertains tests ont echoue. Verifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    main()