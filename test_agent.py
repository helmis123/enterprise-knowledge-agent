"""
Script de test pour l'Agent Knowledge Interne
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from document_processor import DocumentProcessor
from vector_store import VectorStore
from llm_client import OllamaClient, KnowledgeAgent

def test_document_processing():
    """Tester le traitement des documents"""
    print("🧪 Test du traitement des documents...")
    
    processor = DocumentProcessor()
    
    # Tester avec les fichiers d'exemple
    data_dir = Config.DATA_DIR
    if not data_dir.exists():
        print(f"❌ Répertoire data non trouvé: {data_dir}")
        return False
    
    # Lister les fichiers supportés
    supported_files = processor.get_supported_files(data_dir)
    print(f"📁 Fichiers trouvés: {len(supported_files)}")
    
    for file_path in supported_files:
        print(f"  - {file_path.name}")
    
    if not supported_files:
        print("⚠️ Aucun fichier supporté trouvé")
        return False
    
    # Traiter le premier fichier
    test_file = supported_files[0]
    chunks = processor.process_document(test_file)
    
    if chunks:
        print(f"✅ Traitement réussi: {len(chunks)} chunks créés")
        print(f"   Premier chunk: {chunks[0]['content'][:100]}...")
        return True
    else:
        print("❌ Échec du traitement")
        return False

def test_vector_store():
    """Tester la base vectorielle"""
    print("\n🧪 Test de la base vectorielle...")
    
    try:
        vector_store = VectorStore()
        
        # Obtenir les statistiques
        stats = vector_store.get_collection_stats()
        print(f"📊 Statistiques: {stats}")
        
        # Test de recherche
        results = vector_store.search_similar("télétravail", n_results=2)
        print(f"🔍 Recherche 'télétravail': {len(results)} résultats")
        
        if results:
            for i, result in enumerate(results):
                print(f"   {i+1}. Score: {result['similarity_score']:.3f}")
                print(f"      Source: {result['metadata'].get('filename', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur base vectorielle: {e}")
        return False

def test_ollama_connection():
    """Tester la connexion Ollama"""
    print("\n🧪 Test de la connexion Ollama...")
    
    ollama_client = OllamaClient()
    
    if ollama_client.is_available():
        print("✅ Ollama disponible")
        
        # Lister les modèles
        models = ollama_client.get_available_models()
        if models:
            print(f"🤖 Modèles disponibles: {', '.join(models)}")
        else:
            print("⚠️ Aucun modèle trouvé")
        
        return True
    else:
        print("❌ Ollama non disponible")
        print("   Assurez-vous qu'Ollama est démarré:")
        print("   docker run -d -p 11434:11434 ollama/ollama")
        return False

def test_knowledge_agent():
    """Tester l'agent complet"""
    print("\n🧪 Test de l'agent complet...")
    
    try:
        # Initialiser les composants
        vector_store = VectorStore()
        ollama_client = OllamaClient()
        
        if not ollama_client.is_available():
            print("⚠️ Ollama non disponible, test limité")
            return False
        
        knowledge_agent = KnowledgeAgent(vector_store, ollama_client)
        
        # Tester une question simple
        test_question = "Quelle est la politique de télétravail ?"
        print(f"❓ Question test: {test_question}")
        
        result = knowledge_agent.ask_question(test_question)
        
        print(f"✅ Réponse générée:")
        print(f"   Confiance: {result['confidence']:.3f}")
        print(f"   Réponse: {result['answer'][:200]}...")
        
        if 'sources' in result and result['sources']:
            print(f"   Sources: {len(result['sources'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur agent: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests de l'Agent Knowledge Interne")
    print("=" * 60)
    
    # Initialiser la configuration
    Config.setup_directories()
    
    tests = [
        ("Traitement des documents", test_document_processing),
        ("Base vectorielle", test_vector_store),
        ("Connexion Ollama", test_ollama_connection),
        ("Agent complet", test_knowledge_agent)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé des résultats
    print("\n" + "=" * 60)
    print("📋 Résumé des tests:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Résultat: {passed}/{len(results)} tests réussis")
    
    if passed == len(results):
        print("🎉 Tous les tests sont passés ! L'agent est prêt.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main()
