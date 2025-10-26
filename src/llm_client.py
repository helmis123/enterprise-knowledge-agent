"""
Client pour interagir avec Ollama (LLM local)
"""
import requests
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client pour Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialise le client Ollama"""
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
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Génère une réponse avec le LLM"""
        # Construire le prompt complet
        full_prompt = self._build_prompt(prompt, context)
        
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
    
    def _build_prompt(self, question: str, context: Optional[str]) -> str:
        """Construire le prompt avec le contexte"""
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

RÉPONSE:"""
        else:
            return f"""Tu es un assistant IA interne d'entreprise. Réponds en français.

QUESTION: {question}

RÉPONSE:"""


class KnowledgeAgent:
    """Agent principal qui combine recherche vectorielle et génération LLM"""
    
    def __init__(self, vector_store, ollama_client):
        self.vector_store = vector_store
        self.ollama_client = ollama_client
        self.conversation_history = []
    
    def ask_question(self, question: str, include_sources: bool = True) -> Dict[str, Any]:
        """Poser une question à l'agent"""
        logger.info(f"Question reçue: {question}")
        
        # Rechercher des documents pertinents (limiter à 2 pour réduire le contexte)
        relevant_docs = self.vector_store.search_similar(question, n_results=2)
        
        if not relevant_docs:
            return {
                'answer': "Je ne trouve pas d'informations pertinentes dans les documents internes pour répondre à votre question.",
                'sources': [],
                'confidence': 0.0
            }
        
        # Construire le contexte à partir des documents trouvés
        context_parts = []
        sources = []
        
        for doc in relevant_docs:
            # Limiter la taille du contenu pour éviter les timeouts
            content = doc['content'][:800] + "..." if len(doc['content']) > 800 else doc['content']
            context_parts.append(f"Source: {doc['metadata'].get('filename', 'Document')}\n{content}")
            sources.append({
                'filename': doc['metadata'].get('filename', 'Document'),
                'source': doc['metadata'].get('source', ''),
                'similarity_score': doc['similarity_score'],
                'content_preview': doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
            })
        
        context = "\n\n".join(context_parts)
        
        # Générer la réponse avec Ollama
        answer = self.ollama_client.generate_response(question, context)
        
        # Calculer un score de confiance basé sur la similarité
        avg_similarity = sum(doc['similarity_score'] for doc in relevant_docs) / len(relevant_docs)
        confidence = min(avg_similarity * 1.2, 1.0)  # Amplifier légèrement le score
        
        # Ajouter à l'historique
        self.conversation_history.append({
            'question': question,
            'answer': answer,
            'sources': sources if include_sources else [],
            'confidence': confidence
        })
        
        result = {
            'answer': answer,
            'confidence': confidence
        }
        
        if include_sources:
            result['sources'] = sources
        
        return result
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Obtenir l'historique de conversation"""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Effacer l'historique de conversation"""
        self.conversation_history.clear()
        logger.info("Historique de conversation effacé")

