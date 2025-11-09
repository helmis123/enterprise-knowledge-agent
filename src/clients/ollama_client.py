"""
Client pour interagir avec Ollama (LLM local)
"""
import requests
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client pour Ollama API"""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialise le client Ollama"""
        # Utiliser la variable d'environnement ou le paramètre, sinon valeur par défaut
        # Dans Docker, utiliser le nom du service 'ollama'
        if base_url is None:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.base_url = base_url
        self.model = "llama3:8b"
        self.timeout = 180  # Augmenter le timeout à 3 minutes
    
    def check_connection(self) -> bool:
        """Vérifie que Ollama est accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Impossible de se connecter à Ollama: {e}")
            return False
    
    def generate_response(self, prompt: str, context: Optional[str] = None, user_name: Optional[str] = None) -> str:
        """Génère une réponse avec le LLM"""
        # Construire le prompt complet
        full_prompt = self._build_prompt(prompt, context, user_name)
        
        # Préparer la requête avec des paramètres optimisés
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Réduire pour des réponses plus cohérentes
                "top_p": 0.8,        # Réduire pour plus de précision
                "num_predict": 1000,  # Augmenter la limite de réponse
                "repeat_penalty": 1.1
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "Erreur lors de la génération").strip()
        except requests.exceptions.Timeout:
            logger.error("Timeout lors de la génération de la réponse")
            return "Délai d'attente dépassé. Veuillez réessayer."
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return f"Erreur: {str(e)}"
    
    def _build_prompt(self, question: str, context: Optional[str], user_name: Optional[str] = None) -> str:
        """Construire le prompt avec le contexte"""
        
        # Ajouter le nom d'utilisateur à l'instruction
        user_context = ""
        if user_name:
            user_context = f"\n- L'utilisateur qui pose la question est: {user_name}. Ne confonds PAS ce nom avec les noms mentionnés dans les documents."
        
        if context:
            return f"""Tu es un assistant IA interne d'entreprise. Réponds en français en utilisant uniquement les informations des documents fournis.

DOCUMENTS INTERNES:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Réponds uniquement en français
- Utilise uniquement les informations des documents ci-dessus
- Donne une réponse complète et détaillée
- Si l'information n'est pas dans les documents, réponds: "Je ne trouve pas cette information dans les documents internes disponibles."
- Sois précis et cite les sources quand c'est possible
- Réponds de manière professionnelle et utile
- Ne mentionne JAMAIS les noms des personnes trouvés dans les documents dans ta réponse{user_context}

RÉPONSE:"""
        else:
            user_context = ""
            if user_name:
                user_context = f"\n\nL'utilisateur qui pose la question est: {user_name}."
            
            return f"""Tu es un assistant IA interne d'entreprise. Réponds en français.{user_context}

QUESTION: {question}

RÉPONSE:"""

