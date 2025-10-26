"""
Tests pour le module llm_client
"""
import pytest
from unittest.mock import Mock, patch
from src.llm_client import OllamaClient


class TestOllamaClient:
    """Tests pour OllamaClient"""
    
    def test_init_default(self):
        """Test de l'initialisation par défaut"""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.model == "llama3:8b"
    
    def test_init_custom(self):
        """Test de l'initialisation avec URL personnalisée"""
        client = OllamaClient(base_url="http://custom:11434")
        assert client.base_url == "http://custom:11434"
        assert client.model == "llama3:8b"
    
    def test_check_connection_success(self):
        """Test de la vérification de connexion réussie"""
        client = OllamaClient()
        
        with patch('src.llm_client.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            assert client.check_connection() is True
            mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)
    
    def test_check_connection_failure(self):
        """Test de la vérification de connexion échouée"""
        client = OllamaClient()
        
        with patch('src.llm_client.requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection error")
            
            assert client.check_connection() is False
    
    def test_generate_response_with_context(self):
        """Test de la génération de réponse avec contexte"""
        client = OllamaClient()
        
        with patch('src.llm_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"response": "Test réponse"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            result = client.generate_response("Question test", context="Contexte test")
            
            assert result == "Test réponse"
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            
            assert call_args[1]['json']['model'] == "llama3:8b"
            assert "stream" in call_args[1]['json']
            assert call_args[1]['json']['stream'] is False
    
    def test_generate_response_without_context(self):
        """Test de la génération de réponse sans contexte"""
        client = OllamaClient()
        
        with patch('src.llm_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"response": "Réponse directe"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            result = client.generate_response("Question")
            
            assert result == "Réponse directe"
    
    def test_generate_response_error(self):
        """Test de la gestion des erreurs lors de la génération"""
        client = OllamaClient()
        
        with patch('src.llm_client.requests.post') as mock_post:
            mock_post.side_effect = Exception("Erreur réseau")
            
            result = client.generate_response("Question")
            
            assert "Erreur" in result
            assert "Erreur réseau" in result

