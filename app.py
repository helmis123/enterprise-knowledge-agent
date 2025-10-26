"""
Application principale avec authentification
"""
import streamlit as st
from pathlib import Path
from src.auth import SimpleAuth

# Configuration de la page
st.set_page_config(
    page_title="Agent IA - Connexion",
    page_icon="🤖",
    layout="centered"
)

# Initialiser l'authentification
auth = SimpleAuth()

# Vérifier l'authentification
if not auth.require_auth():
    st.stop()

# Si authentifié, afficher l'application
st.title("🤖 Agent IA")
st.markdown("---")

# Informations utilisateur
user_info = st.session_state.get("user_info", {})
st.info(f"👤 Connecté en tant que : **{user_info.get('name', 'Utilisateur')}**")
st.caption(f"Rôle : {user_info.get('role', 'user')}")

# Sidebar avec menu
with st.sidebar:
    st.header("📋 Menu")
    
    if st.button("🚪 Déconnexion"):
        auth.logout()
    
    st.markdown("---")
    st.markdown("**État :** ✅ Authentifié")

# Contenu principal
st.header("🎯 Agent IA")

# Upload et extraction de documents
st.subheader("📄 Upload de Documents")

uploaded_file = st.file_uploader(
    "Choisissez un document",
    type=['pdf', 'docx', 'txt', 'md'],
    help="Formats supportés: PDF, Word, TXT, Markdown"
)

if uploaded_file is not None:
    with st.spinner("Extraction du texte en cours..."):
        from src.document_reader import DocumentReader
        
        # Sauvegarder temporairement
        temp_path = Path("data") / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Extraire le texte
        reader = DocumentReader()
        result = reader.process_document(temp_path)
        
        if result["success"]:
            st.success(f"✅ Document traité: {uploaded_file.name}")
            
            # Afficher les métadonnées
            with st.expander("📊 Métadonnées"):
                metadata = result["metadata"]
                st.write(f"**Fichier:** {metadata['filename']}")
                st.write(f"**Type:** {metadata['file_type']}")
                st.write(f"**Chunks:** {metadata['num_chunks']}")
                st.write(f"**Mots:** {metadata['total_words']}")
                st.write(f"**Caractères:** {metadata['total_characters']}")
            
            # Afficher un aperçu
            with st.expander("👁️ Aperçu du texte"):
                st.text(result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"])
            
            st.info(f"💡 {len(result['chunks'])} chunks créés (prêts pour les embeddings)")
            
            # Explication des chunks
            st.markdown("""
            **📚 À quoi servent les chunks ?**
            - Chaque chunk sera converti en vecteur 384D (embedding)
            - Les embeddings permettent la recherche sémantique
            - Plus petits = plus précis, mais contexte plus limité
            - Chaque chunk = un "documents'embedding" dans ChromaDB
            """)
            
            # Afficher les chunks
            with st.expander(f"📑 Chunks ({len(result['chunks'])} morceaux)"):
                for i, chunk in enumerate(result['chunks'], 1):
                    st.markdown(f"### Chunk {i}")
                    st.text(chunk)
                    st.markdown("---")
        else:
            st.error("❌ Erreur lors du traitement du document")
        
        # Nettoyer
        temp_path.unlink()

