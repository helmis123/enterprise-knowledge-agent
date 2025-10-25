"""
Interface utilisateur Streamlit pour l'Agent Knowledge Interne
"""
import streamlit as st
import logging
from pathlib import Path
from typing import Dict, Any, List
import sys
import os

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from document_processor import DocumentProcessor
from vector_store import VectorStore
from llm_client import OllamaClient, KnowledgeAgent
from auth import SimpleAuth, auth_sidebar

# Configuration de la page
st.set_page_config(
    page_title="Agent Knowledge Interne",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .source-card {
        background-color: #f5f5f5;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
        border-left: 3px solid #4caf50;
    }
    .confidence-badge {
        background-color: #4caf50;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des composants
@st.cache_resource
def initialize_components():
    """Initialiser les composants de l'application"""
    try:
        # Initialiser les composants
        doc_processor = DocumentProcessor()
        vector_store = VectorStore()
        ollama_client = OllamaClient()
        knowledge_agent = KnowledgeAgent(vector_store, ollama_client)
        
        return doc_processor, vector_store, ollama_client, knowledge_agent
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation: {e}")
        return None, None, None, None

def display_chat_message(message: str, is_user: bool = False):
    """Afficher un message dans le chat"""
    css_class = "user-message" if is_user else "assistant-message"
    st.markdown(f'<div class="chat-message {css_class}">{message}</div>', unsafe_allow_html=True)

def display_sources(sources: List[Dict[str, Any]]):
    """Afficher les sources d'une réponse"""
    if not sources:
        return
    
    st.markdown("**📚 Sources utilisées:**")
    for source in sources:
        with st.expander(f"📄 {source['filename']} (Score: {source['similarity_score']:.2f})"):
            st.text(f"Fichier: {source['source']}")
            st.text(f"Contenu: {source['content_preview']}")

def main():
    """Fonction principale de l'application"""
    
    # Initialiser l'authentification
    auth = SimpleAuth()
    
    # Vérifier l'authentification
    if not auth.require_auth():
        return
    
    # En-tête
    st.markdown('<h1 class="main-header">🤖 Agent Knowledge Interne</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialiser les composants
    doc_processor, vector_store, ollama_client, knowledge_agent = initialize_components()
    
    if not all([doc_processor, vector_store, ollama_client, knowledge_agent]):
        st.error("❌ Erreur lors de l'initialisation des composants")
        return
    
    # Sidebar pour la gestion des documents
    with st.sidebar:
        # Afficher les informations d'authentification
        auth_sidebar()
        
        st.header("📁 Gestion des Documents")
        
        # Vérifier le statut d'Ollama
        if ollama_client.is_available():
            st.success("✅ Ollama disponible")
            available_models = ollama_client.get_available_models()
            if available_models:
                st.info(f"Modèles disponibles: {', '.join(available_models)}")
        else:
            st.error("❌ Ollama non disponible")
            st.info("Assurez-vous qu'Ollama est démarré et accessible")
        
        # Statistiques de la base vectorielle
        stats = vector_store.get_collection_stats()
        if stats:
            st.metric("Documents indexés", stats.get('total_documents', 0))
        
        st.markdown("---")
        
        # Upload de nouveaux documents
        st.subheader("📤 Ajouter des Documents")
        uploaded_files = st.file_uploader(
            "Choisissez des fichiers",
            type=['pdf', 'docx', 'doc', 'md', 'txt'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("Indexer les Documents"):
                with st.spinner("Indexation en cours..."):
                    for uploaded_file in uploaded_files:
                        # Sauvegarder le fichier temporairement
                        temp_path = Config.DATA_DIR / uploaded_file.name
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Traiter le document
                        chunks = doc_processor.process_document(temp_path)
                        if chunks:
                            success = vector_store.add_documents(chunks)
                            if success:
                                st.success(f"✅ {uploaded_file.name} indexé")
                            else:
                                st.error(f"❌ Erreur lors de l'indexation de {uploaded_file.name}")
                        
                        # Supprimer le fichier temporaire
                        temp_path.unlink()
                
                st.rerun()
        
        # Bouton pour traiter tous les documents du dossier data
        if st.button("🔄 Indexer tous les documents du dossier"):
            with st.spinner("Traitement en cours..."):
                chunks = doc_processor.process_directory(Config.DATA_DIR)
                if chunks:
                    success = vector_store.add_documents(chunks)
                    if success:
                        st.success(f"✅ {len(chunks)} chunks indexés")
                    else:
                        st.error("❌ Erreur lors de l'indexation")
                else:
                    st.warning("⚠️ Aucun document trouvé")
            
            st.rerun()
        
        # Bouton pour vider la base
        if st.button("🗑️ Vider la Base de Connaissances"):
            if st.checkbox("Confirmer la suppression"):
                vector_store.clear_collection()
                st.success("✅ Base vidée")
                st.rerun()
    
    # Zone principale de chat
    st.header("💬 Chat avec l'Agent")
    
    # Initialiser l'historique de session
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Afficher l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                display_sources(message["sources"])
    
    # Zone de saisie
    if prompt := st.chat_input("Posez votre question..."):
        # Ajouter le message utilisateur à l'historique
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Afficher le message utilisateur
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Générer la réponse
        with st.chat_message("assistant"):
            with st.spinner("Recherche et génération de la réponse..."):
                try:
                    result = knowledge_agent.ask_question(prompt)
                    
                    # Afficher la réponse
                    st.markdown(result['answer'])
                    
                    # Afficher le score de confiance
                    confidence_color = "green" if result['confidence'] > 0.7 else "orange" if result['confidence'] > 0.4 else "red"
                    st.markdown(f"**Confiance:** :{confidence_color}[{result['confidence']:.2f}]")
                    
                    # Afficher les sources
                    if "sources" in result and result["sources"]:
                        display_sources(result["sources"])
                    
                    # Ajouter la réponse à l'historique
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result['answer'],
                        "sources": result.get("sources", [])
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Erreur lors de la génération de la réponse: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Bouton pour effacer l'historique
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.messages = []
        knowledge_agent.clear_history()
        st.rerun()

if __name__ == "__main__":
    main()
