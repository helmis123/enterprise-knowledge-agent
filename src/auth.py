"""
Module d'authentification basique pour l'Agent Knowledge Interne
"""
import streamlit as st
import hashlib
import logging
from typing import Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class SimpleAuth:
    """Système d'authentification simple"""
    
    def __init__(self):
        # Utilisateurs par défaut (en production, utiliser une vraie base de données)
        self.users = {
            "admin": {
                "password": self._hash_password("admin123"),
                "role": "admin",
                "name": "Administrateur"
            },
            "user": {
                "password": self._hash_password("user123"),
                "role": "user", 
                "name": "Utilisateur Standard"
            },
            "demo": {
                "password": self._hash_password("demo123"),
                "role": "user",
                "name": "Utilisateur Démo"
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hasher un mot de passe"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authentifier un utilisateur"""
        if username in self.users:
            hashed_password = self._hash_password(password)
            if self.users[username]["password"] == hashed_password:
                return {
                    "username": username,
                    "role": self.users[username]["role"],
                    "name": self.users[username]["name"]
                }
        return None
    
    def is_authenticated(self) -> bool:
        """Vérifier si l'utilisateur est authentifié"""
        return "authenticated" in st.session_state and st.session_state["authenticated"]
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Obtenir les informations de l'utilisateur actuel"""
        if self.is_authenticated():
            return st.session_state.get("user_info")
        return None
    
    def login_page(self) -> bool:
        """Afficher la page de connexion et retourner True si authentifié"""
        st.markdown("""
        <style>
            .login-container {
                max-width: 400px;
                margin: 0 auto;
                padding: 2rem;
                border: 1px solid #ddd;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.title("🔐 Connexion")
        st.markdown("Connectez-vous pour accéder à l'Agent Knowledge Interne")
        
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit_button = st.form_submit_button("Se connecter")
            
            if submit_button:
                user_info = self.authenticate(username, password)
                if user_info:
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = user_info
                    st.success(f"✅ Bienvenue, {user_info['name']} !")
                    st.rerun()
                else:
                    st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Informations de connexion pour la démo
        with st.expander("ℹ️ Comptes de démonstration"):
            st.markdown("""
            **Comptes disponibles :**
            - **admin** / admin123 (Administrateur)
            - **user** / user123 (Utilisateur standard)
            - **demo** / demo123 (Utilisateur démo)
            
            ⚠️ **Important** : Changez ces mots de passe en production !
            """)
        
        return False
    
    def logout(self):
        """Déconnecter l'utilisateur"""
        if "authenticated" in st.session_state:
            del st.session_state["authenticated"]
        if "user_info" in st.session_state:
            del st.session_state["user_info"]
        st.rerun()
    
    def require_auth(self, required_role: str = "user") -> bool:
        """Décorateur pour exiger l'authentification"""
        if not self.is_authenticated():
            return self.login_page()
        
        user_info = self.get_current_user()
        if not user_info:
            return self.login_page()
        
        # Vérifier les rôles
        if required_role == "admin" and user_info["role"] != "admin":
            st.error("❌ Accès refusé : droits administrateur requis")
            return False
        
        return True

def auth_sidebar():
    """Afficher les informations d'authentification dans la sidebar"""
    auth = SimpleAuth()
    
    if auth.is_authenticated():
        user_info = auth.get_current_user()
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **Connecté en tant que :** {user_info['name']}")
        st.sidebar.markdown(f"🔑 **Rôle :** {user_info['role']}")
        
        if st.sidebar.button("🚪 Déconnexion"):
            auth.logout()
    else:
        st.sidebar.markdown("---")
        st.sidebar.markdown("🔐 **Non connecté**")
        st.sidebar.markdown("Connectez-vous pour accéder à toutes les fonctionnalités")
