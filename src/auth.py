"""
Système d'authentification simple
"""
import streamlit as st
import hashlib
from typing import Optional, Dict

class SimpleAuth:
    """Système d'authentification basique avec Streamlit"""
    
    def __init__(self):
        # Utilisateurs par défaut (en production, utiliser une vraie base de données)
        # Format: {username: {password_hash, name, role}}
        self.users = {
            "admin": {
                "password_hash": self._hash_password("admin123"),
                "name": "Administrateur",
                "role": "admin"
            },
            "user": {
                "password_hash": self._hash_password("user123"),
                "name": "Utilisateur Standard",
                "role": "user"
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hasher un mot de passe avec SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authentifier un utilisateur"""
        if username in self.users:
            password_hash = self._hash_password(password)
            if self.users[username]["password_hash"] == password_hash:
                return True
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Obtenir les informations d'un utilisateur"""
        if username in self.users:
            return {
                "username": username,
                "name": self.users[username]["name"],
                "role": self.users[username]["role"]
            }
        return None
    
    def is_authenticated(self) -> bool:
        """Vérifier si l'utilisateur est authentifié dans la session"""
        return "authenticated" in st.session_state and st.session_state["authenticated"]
    
    def login_page(self):
        """Afficher la page de connexion"""
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
        st.markdown("Accédez à l'Agent IA")
        
        with st.form("login_form"):
            username = st.text_input("👤 Nom d'utilisateur")
            password = st.text_input("🔑 Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")
            
            if submit:
                if self.authenticate(username, password):
                    # Sauvegarder dans la session
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.session_state["user_info"] = self.get_user_info(username)
                    
                    st.success(f"✅ Bienvenue, {st.session_state['user_info']['name']} !")
                    st.rerun()
                else:
                    st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Afficher les comptes de test
        with st.expander("ℹ️ Comptes de test"):
            st.markdown("""
            **Pour tester :**
            - **admin** / admin123 (Administrateur)
            - **user** / user123 (Utilisateur)
            """)
    
    def logout(self):
        """Déconnecter l'utilisateur"""
        if "authenticated" in st.session_state:
            del st.session_state["authenticated"]
        if "username" in st.session_state:
            del st.session_state["username"]
        if "user_info" in st.session_state:
            del st.session_state["user_info"]
        st.rerun()
    
    def require_auth(self):
        """Décorateur pour protéger une page"""
        if not self.is_authenticated():
            self.login_page()
            return False
        return True
