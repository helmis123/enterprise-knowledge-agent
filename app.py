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

# Section de recherche sémantique
st.subheader("🔍 Recherche Sémantique")
st.markdown("Posez une question et trouvez les documents pertinents dans la base vectorielle.")

search_query = st.text_input("Votre question :", placeholder="Ex: Quels sont les avantages du télétravail ?")

if search_query:
    with st.spinner("Recherche en cours..."):
        try:
            from src.vector_store import VectorStore
            from sentence_transformers import SentenceTransformer
            
            # Initialiser le modèle d'embeddings
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialiser la base vectorielle
            vector_store = VectorStore()
            vector_store.create_collection()
            
            # Convertir la requête en embedding
            query_embedding = model.encode([search_query], convert_to_tensor=False)[0].tolist()
            
            # Rechercher dans ChromaDB
            results = vector_store.search(query_embedding, n_results=5)
            
            # Afficher les résultats
            if results['documents'] and len(results['documents'][0]) > 0:
                st.success(f"✅ {len(results['documents'][0])} résultats trouvés")
                
                for i, (doc, metadata) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0] if results['metadatas'] else [{}] * len(results['documents'][0])
                ), 1):
                    with st.expander(f"📄 Résultat {i}", expanded=True):
                        st.markdown(f"**Document:**\n{doc}")
                        if metadata:
                            st.markdown(f"**Source:** {metadata.get('source', 'N/A')}")
                            st.markdown(f"**Chunk:** {metadata.get('chunk_index', 'N/A')}/{metadata.get('total_chunks', 'N/A')}")
                            st.markdown(f"**Type:** {metadata.get('file_type', 'N/A')}")
            else:
                st.warning("Aucun résultat trouvé. Essayez de stocker des documents d'abord.")
                
        except Exception as e:
            st.error(f"❌ Erreur lors de la recherche: {e}")
            st.exception(e)

st.markdown("---")

# Section chatbot RAG
st.subheader("💬 Chatbot avec vos documents")
st.markdown("Posez une question et obtenez une réponse basée sur vos documents stockés dans ChromaDB.")

chat_query = st.text_input("Votre question :", placeholder="Ex: Expliquez le télétravail", key="chat_input")

if chat_query:
    with st.spinner("Recherche et génération de réponse..."):
        try:
            from src.llm_client import OllamaClient
            from src.vector_store import VectorStore
            from sentence_transformers import SentenceTransformer
            
            # Vérifier Ollama
            llm_client = OllamaClient()
            if not llm_client.check_connection():
                st.error("⚠️ Ollama n'est pas accessible sur http://localhost:11434")
            else:
                # Rechercher dans ChromaDB
                model = SentenceTransformer('all-MiniLM-L6-v2')
                query_emb = model.encode([chat_query], convert_to_tensor=False)[0].tolist()
                
                vector_store = VectorStore()
                vector_store.create_collection()
                results = vector_store.search(query_emb, n_results=3)
                
                if results['documents'] and len(results['documents'][0]) > 0:
                    # Construire le contexte (limiter à 2 documents et 1500 chars max)
                    context_parts = []
                    total_length = 0
                    max_length = 1500
                    
                    for doc in results['documents'][0][:2]:  # Max 2 documents
                        if total_length + len(doc) > max_length:
                            remaining = max_length - total_length
                            context_parts.append(doc[:remaining])
                            break
                        context_parts.append(doc)
                        total_length += len(doc)
                    
                    context = "\n\n".join(context_parts)
                    
                    # Récupérer le nom d'utilisateur
                    user_name = user_info.get('name', 'Utilisateur')
                    
                    # Générer la réponse
                    response = llm_client.generate_response(chat_query, context, user_name)
                    
                    st.success("✅ Réponse générée :")
                    st.markdown(response)
                    
                    # Sources
                    with st.expander("📚 Documents utilisés (3 sources)"):
                        for i, doc in enumerate(results['documents'][0], 1):
                            st.markdown(f"**Source {i}:**")
                            st.text(doc[:300] + "..." if len(doc) > 300 else doc)
                else:
                    st.warning("Aucun document trouvé dans ChromaDB. Upload et stockez des documents d'abord.")
                    
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
            st.exception(e)

st.markdown("---")

# Upload et extraction de documents
st.subheader("📄 Upload de Documents")

uploaded_files = st.file_uploader(
    "Choisissez un ou plusieurs documents",
    type=['pdf', 'docx', 'txt', 'md'],
    help="Formats supportés: PDF, Word, TXT, Markdown",
    accept_multiple_files=True
)

if uploaded_files is not None and len(uploaded_files) > 0:
    from src.document_reader import DocumentReader
    
    # Créer le dossier data s'il n'existe pas
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Traiter chaque fichier
    all_results = []
    total_chunks = []
    all_metadata = []
    
    for uploaded_file in uploaded_files:
        with st.spinner(f"Extraction du texte en cours: {uploaded_file.name}..."):
            # Sauvegarder temporairement
            temp_path = data_dir / uploaded_file.name
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Extraire le texte
            reader = DocumentReader()
            result = reader.process_document(temp_path)
            
            if result["success"]:
                all_results.append({
                    "file": uploaded_file.name,
                    "result": result
                })
                st.success(f"✅ Document traité: {uploaded_file.name}")
                
                # Collecter les chunks pour l'upload en batch
                for i, chunk in enumerate(result["chunks"]):
                    total_chunks.append(chunk)
                    all_metadata.append({
                        "source": uploaded_file.name,
                        "chunk_index": i,
                        "total_chunks": len(result["chunks"]),
                        "file_type": result["metadata"]["file_type"]
                    })
                
                # Nettoyer le fichier temporaire
                temp_path.unlink()
            else:
                st.error(f"❌ Erreur lors du traitement de {uploaded_file.name}")
    
    # Si des fichiers ont été traités avec succès
    if all_results:
        st.markdown("---")
        st.success(f"✅ {len(all_results)} fichier(s) traité(s) avec succès")
        
        # Afficher le résumé global
        total_chunks_count = sum(len(r["result"]["chunks"]) for r in all_results)
        st.info(f"📊 Total: {total_chunks_count} chunks créés à partir de {len(all_results)} fichier(s)")
        
        # Afficher les détails par fichier
        for idx, file_data in enumerate(all_results):
            result = file_data["result"]
            with st.expander(f"📄 {file_data['file']}", expanded=False):
                metadata = result["metadata"]
                st.write(f"**Type:** {metadata['file_type']}")
                st.write(f"**Chunks:** {metadata['num_chunks']}")
                st.write(f"**Mots:** {metadata['total_words']}")
                st.write(f"**Caractères:** {metadata['total_characters']}")
        
        # Génération des embeddings pour tous les fichiers en batch
        st.markdown("---")
        st.subheader("🔢 Génération des Embeddings pour tous les fichiers")
        
        with st.spinner(f"Génération des embeddings pour {total_chunks_count} chunks..."):
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L6-v2')
                
                # Générer tous les embeddings en une fois
                embeddings = model.encode(total_chunks, convert_to_tensor=False)
                
                st.success(f"✅ {len(embeddings)} embeddings générés pour tous les fichiers!")
                
                # Préparer les IDs
                doc_ids = []
                for file_data in all_results:
                    filename = file_data["file"]
                    num_chunks = len(file_data["result"]["chunks"])
                    for i in range(num_chunks):
                        doc_ids.append(f"{filename}_{i}")
                
                # Stockage dans ChromaDB
                st.markdown("---")
                st.subheader("💾 Stockage dans ChromaDB")
                
                # Afficher le résumé avant le stockage
                with st.expander("📊 Résumé avant stockage", expanded=True):
                    st.markdown(f"**Nombre de fichiers:** {len(all_results)}")
                    st.markdown(f"**Nombre total de chunks:** {total_chunks_count}")
                    st.markdown(f"**Nombre total d'embeddings:** {len(embeddings)}")
                    
                    # Taille approximative
                    total_size = total_chunks_count * 384 * 4  # 384 dimensions * 4 bytes
                    st.info(f"📊 Taille approximative: ~{total_size/1024:.2f} KB")
                
                if st.button("💾 Stocker tous les fichiers dans ChromaDB", type="primary"):
                    with st.spinner("Stockage en cours..."):
                        try:
                            from src.vector_store import VectorStore
                            
                            # Initialiser la base vectorielle
                            vector_store = VectorStore()
                            vector_store.create_collection()
                            
                            # Convertir en listes (ChromaDB n'aime pas numpy arrays)
                            embeddings_list = [emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in embeddings]
                            
                            # Stocker dans ChromaDB
                            vector_store.add_documents(
                                embeddings=embeddings_list,
                                documents=total_chunks,
                                metadatas=all_metadata,
                                ids=doc_ids
                            )
                            
                            st.success(f"✅ {total_chunks_count} chunks stockés dans ChromaDB depuis {len(all_results)} fichier(s)!")
                            
                            # Afficher les infos de la collection
                            info = vector_store.get_collection_info()
                            st.info(f"📊 Total dans la base: {info['count']} documents")
                            
                        except Exception as e:
                            st.error(f"❌ Erreur lors du stockage: {e}")
                            st.exception(e)
                
            except ImportError:
                st.warning("⚠️ sentence-transformers non installé.")
                st.markdown("""
                **Pour installer les dépendances:**
                
                ```bash
                pip install -r requirements.txt
                ```
                """)
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
                st.exception(e)


