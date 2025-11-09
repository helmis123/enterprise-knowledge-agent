"""
Agent principal qui combine recherche vectorielle et génération LLM
"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


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

