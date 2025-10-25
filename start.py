"""
Script de démarrage pour l'Agent Knowledge Interne
"""
import subprocess
import sys
import time
import requests
from pathlib import Path

def check_ollama_status():
    """Vérifier si Ollama est disponible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """Démarrer Ollama avec Docker"""
    print("🐳 Démarrage d'Ollama...")
    
    try:
        # Vérifier si Ollama est déjà en cours d'exécution
        if check_ollama_status():
            print("✅ Ollama est déjà en cours d'exécution")
            return True
        
        # Démarrer Ollama
        result = subprocess.run([
            "docker", "run", "-d", 
            "--name", "ollama-agentia",
            "-p", "11434:11434",
            "-v", "ollama_data:/root/.ollama",
            "ollama/ollama:latest"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Ollama démarré avec succès")
            
            # Attendre que le service soit prêt
            print("⏳ Attente du démarrage d'Ollama...")
            for i in range(30):  # Attendre maximum 30 secondes
                if check_ollama_status():
                    print("✅ Ollama est prêt")
                    return True
                time.sleep(1)
            
            print("⚠️ Ollama prend plus de temps que prévu à démarrer")
            return False
        else:
            print(f"❌ Erreur lors du démarrage d'Ollama: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Docker n'est pas installé ou n'est pas dans le PATH")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du démarrage d'Ollama: {e}")
        return False

def pull_llama_model():
    """Télécharger le modèle Llama"""
    print("📥 Téléchargement du modèle Llama...")
    
    try:
        result = subprocess.run([
            "docker", "exec", "ollama-agentia",
            "ollama", "pull", "llama3:8b"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Modèle Llama téléchargé")
            return True
        else:
            print(f"❌ Erreur lors du téléchargement: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement du modèle: {e}")
        return False

def setup_environment():
    """Configurer l'environnement"""
    print("🔧 Configuration de l'environnement...")
    
    # Créer les répertoires nécessaires
    directories = ['data', 'chroma_db', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Répertoire {directory} créé")
    
    # Copier le fichier de configuration
    config_file = Path('config.env')
    if not config_file.exists():
        print("⚠️ Fichier config.env non trouvé")
        print("   Créez le fichier config.env à partir de config.env.example")
        return False
    
    print("✅ Configuration terminée")
    return True

def start_streamlit():
    """Démarrer l'application Streamlit"""
    print("🚀 Démarrage de l'application Streamlit...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Arrêt de l'application")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de Streamlit: {e}")

def main():
    """Fonction principale"""
    print("🤖 Agent Knowledge Interne - Script de Démarrage")
    print("=" * 50)
    
    # Configuration de l'environnement
    if not setup_environment():
        print("❌ Échec de la configuration")
        return
    
    # Démarrer Ollama
    if not start_ollama():
        print("❌ Impossible de démarrer Ollama")
        print("   Vous pouvez démarrer l'application sans Ollama pour tester l'interface")
        response = input("Continuer sans Ollama ? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Télécharger le modèle Llama
    if check_ollama_status():
        if not pull_llama_model():
            print("⚠️ Modèle Llama non téléchargé")
            print("   Vous pouvez le télécharger manuellement plus tard")
    
    # Démarrer l'application
    print("\n🌐 Démarrage de l'application web...")
    print("   L'application sera accessible sur: http://localhost:8501")
    print("   Appuyez sur Ctrl+C pour arrêter")
    
    start_streamlit()

if __name__ == "__main__":
    main()
