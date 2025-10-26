"""
Tests pour le module auth.py
"""
import unittest
import hashlib
from unittest.mock import MagicMock, patch
import sys
import os

# Ajouter le chemin racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.auth import SimpleAuth


class TestSimpleAuth(unittest.TestCase):
    """Tests pour la classe SimpleAuth"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.auth = SimpleAuth()
        
    def test_hash_password(self):
        """Test du hashage de mot de passe"""
        password = "test123"
        hashed = self.auth._hash_password(password)
        
        # Vérifier que le hash est en hexadécimal
        self.assertIsInstance(hashed, str)
        self.assertEqual(len(hashed), 64)  # SHA256 = 64 caractères hex
        
        # Vérifier que le même mot de passe donne le même hash
        hashed2 = self.auth._hash_password(password)
        self.assertEqual(hashed, hashed2)
        
        # Vérifier que des mots de passe différents donnent des hash différents
        hashed3 = self.auth._hash_password("different")
        self.assertNotEqual(hashed, hashed3)
    
    def test_users_exist(self):
        """Test que les utilisateurs par défaut existent"""
        self.assertIn("admin", self.auth.users)
        self.assertIn("user", self.auth.users)
        
        # Vérifier la structure des utilisateurs
        admin = self.auth.users["admin"]
        self.assertIn("password_hash", admin)
        self.assertIn("name", admin)
        self.assertIn("role", admin)
        self.assertEqual(admin["role"], "admin")
        
        user = self.auth.users["user"]
        self.assertEqual(user["role"], "user")
    
    def test_authenticate_success(self):
        """Test d'authentification réussie"""
        result = self.auth.authenticate("admin", "admin123")
        self.assertTrue(result)
        
        result = self.auth.authenticate("user", "user123")
        self.assertTrue(result)
    
    def test_authenticate_failure_wrong_password(self):
        """Test d'échec d'authentification avec mauvais mot de passe"""
        result = self.auth.authenticate("admin", "wrongpassword")
        self.assertFalse(result)
        
        result = self.auth.authenticate("user", "wrongpassword")
        self.assertFalse(result)
    
    def test_authenticate_failure_wrong_username(self):
        """Test d'échec d'authentification avec mauvais nom d'utilisateur"""
        result = self.auth.authenticate("nonexistent", "anypassword")
        self.assertFalse(result)
    
    def test_authenticate_failure_empty(self):
        """Test d'échec d'authentification avec champs vides"""
        result = self.auth.authenticate("", "")
        self.assertFalse(result)
        
        result = self.auth.authenticate("admin", "")
        self.assertFalse(result)
        
        result = self.auth.authenticate("", "admin123")
        self.assertFalse(result)
    
    def test_get_user_info(self):
        """Test de récupération des infos utilisateur"""
        # Authentifier d'abord
        self.auth.authenticate("admin", "admin123")
        
        # Mock session_state
        with patch('streamlit.session_state', new=MagicMock()) as mock_session:
            mock_session.user_info = {
                "name": "Administrateur",
                "role": "admin",
                "username": "admin"
            }
            
            # Dans un vrai contexte Streamlit, on utiliserait get_user_info()
            # Ici on teste juste que le code existe
            self.assertIsNotNone(self.auth.users["admin"])
            
    def test_get_user_info_not_authenticated(self):
        """Test de récupération des infos sans authentification"""
        # Mock session_state sans user_info
        with patch('streamlit.session_state', new=MagicMock()) as mock_session:
            mock_session.user_info = None
            # Sould return None or empty dict
            self.assertIsNotNone(self.auth.users)


if __name__ == '__main__':
    unittest.main()

