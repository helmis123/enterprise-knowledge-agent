"""
Application principale avec authentification
"""
import streamlit as st
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
st.header("🎯 Bienvenue !")
st.markdown("""
Vous êtes connecté à l'Agent IA.

**Prochaines étapes :**
1. ✅ Authentification - FAIT
2. ⏳ Extraction de texte (PDF, Word)
3. ⏳ Génération d'embeddings
4. ⏳ Base vectorielle (ChromaDB)
5. ⏳ Recherche sémantique
6. ⏳ Interface de chat
7. ⏳ Intégration LLM (Ollama)
""")

