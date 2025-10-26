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
                    
                    # Générer la réponse
                    response = llm_client.generate_response(chat_query, context)
                    
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

uploaded_file = st.file_uploader(
    "Choisissez un document",
    type=['pdf', 'docx', 'txt', 'md'],
    help="Formats supportés: PDF, Word, TXT, Markdown"
)

if uploaded_file is not None:
    with st.spinner("Extraction du texte en cours..."):
        from src.document_reader import DocumentReader
        
        # Créer le dossier data s'il n'existe pas
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Sauvegarder temporairement
        temp_path = data_dir / uploaded_file.name
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
            - Chaque chunk = un "embedding" dans ChromaDB
            """)
            
            # Afficher les chunks
            with st.expander(f"📑 Chunks ({len(result['chunks'])} morceaux)"):
                for i, chunk in enumerate(result['chunks'], 1):
                    st.markdown(f"### Chunk {i}")
                    st.text(chunk)
                    st.markdown("---")
            
            # Générer et afficher les embeddings
            st.subheader("🔢 Génération des Embeddings (Vecteurs 384D)")
            
            with st.spinner("Conversion des chunks en vecteurs..."):
                try:
                    from sentence_transformers import SentenceTransformer
                    model = SentenceTransformer('all-MiniLM-L6-v2')
                    
                    chunks = result['chunks']
                    embeddings = model.encode(chunks, convert_to_tensor=False)
                    
                    st.success(f"✅ {len(embeddings)} embeddings générés!")
                    
                    # Afficher les détails
                    with st.expander(f"📊 Détails des vecteurs ({len(embeddings)} embeddings)", expanded=True):
                        for i, (chunk, emb) in enumerate(zip(chunks, embeddings), 1):
                            st.markdown(f"#### Vecteur {i} (Chunk {i})")
                            
                            # Informations générales
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Dimensions", len(emb))
                            with col2:
                                st.metric("Taille", f"{len(emb) * 4} bytes")
                            with col3:
                                st.metric("Type", "float32")
                            
                            # Afficher le vecteur complet formaté
                            st.markdown("**Le vecteur complet (384 nombres):**")
                            st.markdown("```")
                            st.code(f"[{', '.join(map(lambda x: f'{x:.4f}', emb[:50]))}, ... (334 autres)]")
                            st.markdown("```")
                            
                            # Premiers 50 nombres visuellement
                            st.markdown("**Premiers 50 nombres (pour voir les détails):**")
                            cols = st.columns(10)
                            for j in range(min(50, len(emb))):
                                cols[j % 10].markdown(f"`{emb[j]:.3f}`")
                            
                            # Statistiques
                            st.markdown("**Statistiques du vecteur:**")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Min", f"{emb.min():.3f}")
                            with col2:
                                st.metric("Max", f"{emb.max():.3f}")
                            with col3:
                                st.metric("Moyenne", f"{emb.mean():.3f}")
                            with col4:
                                st.metric("Écart-type", f"{emb.std():.3f}")
                            
                            # Exemple de ce que représente le vecteur
                            st.info(f"""
                            **Ce que représente ce vecteur :**
                            - Chaque nombre capture une information sémantique
                            - Les 384 nombres ensemble = représentation du texte
                            - Texte source: "{chunk[:150]}..."
                            """)
                            
                            st.markdown("---")
                    
                    # Explication pédagogique
                    with st.expander("📚 Explication"):
                        st.markdown("""
                        **Pourquoi 384 dimensions exactement?**
                        
                        - **Modèle utilisé:** all-MiniLM-L6-v2
                        - **Architecture:** Transformer 6 couches
                        - **Sortie du pooler:** 384 nombres (décision du design)
                        
                        **Pourquoi pas 768 comme GPT?**
                        - ✅ Plus petit = plus rapide
                        - ✅ Moins de mémoire (1536 bytes vs 3072 bytes)
                        - ✅ Suffisant pour la recherche sémantique
                        - ✅ Qualité excellente pour la taille
                        
                        **Chaque dimension capture quoi?**
                        - Dimensions apprises automatiquement par le modèle
                        - Ne correspondent pas à des concepts simples
                        - Combinaison complexe de sémantique
                        - Résultat: des représentations riches en sens
                        
                        **Comparaison des tailles:**
                        - 384D (all-MiniLM): Plus rapide, assez précis ✅
                        - 768D (BERT-base): Plus lent, plus précis
                        - 1536D (GPT-3 embeddings): Très lent, très précis
                        
                        **Pourquoi des vecteurs?**
                        - Permet la recherche par sens (pas juste mots)
                        - Textes similaires = vecteurs proches
                        - Ultra rapide avec ChromaDB (<1ms)
                        """)
                    
                    # Section: Résumé pour ChromaDB
                    st.markdown("---")
                    st.subheader("💾 Ce qui sera transféré vers ChromaDB")
                    
                    with st.expander("📦 Données à stocker (cliquez pour voir tout)", expanded=True):
                        st.markdown("### 1. Embeddings (Vecteurs)")
                        for i, emb in enumerate(embeddings, 1):
                            st.code(f"Embedding {i}: {len(emb)} dimensions, {len(emb)*4} bytes", language=None)
                        
                        st.markdown("### 2. Chunks (Textes originaux)")
                        for i, chunk in enumerate(chunks, 1):
                            st.text_area(f"Chunk {i}", chunk[:200] + "..." if len(chunk) > 200 else chunk, 
                                       height=80, key=f"chunk_{i}", disabled=True)
                        
                        st.markdown("### 3. Métadonnées (JSON)")
                        st.json(metadata)
                        
                        st.markdown("### 4. Identifiants uniques")
                        for i in range(len(chunks)):
                            doc_id = f"{uploaded_file.name}_{i}"
                            st.code(f"ID {i+1}: {doc_id}", language=None)
                        
                        total_size = sum(len(emb) * 4 for emb in embeddings)
                        st.info(f"📊 Taille totale: ~{total_size/1024:.2f} KB pour les embeddings + métadonnées")
                    
                    st.success(f"✅ {len(embeddings)} éléments prêts pour ChromaDB!")
                    
                    # Bouton pour stocker dans ChromaDB
                    st.markdown("---")
                    st.subheader("💾 Stockage dans ChromaDB")
                    
                    if st.button("💾 Stocker dans ChromaDB", type="primary"):
                        with st.spinner("Stockage en cours..."):
                            try:
                                from src.vector_store import VectorStore
                                import numpy as np
                                
                                # Initialiser la base vectorielle
                                vector_store = VectorStore()
                                vector_store.create_collection()
                                
                                # Préparer les données pour ChromaDB
                                doc_ids = [f"{uploaded_file.name}_{i}" for i in range(len(chunks))]
                                metadatas = []
                                for i, chunk in enumerate(chunks):
                                    metadatas.append({
                                        "source": uploaded_file.name,
                                        "chunk_index": i,
                                        "total_chunks": len(chunks),
                                        "file_type": metadata["file_type"]
                                    })
                                
                                # Convertir en listes (ChromaDB n'aime pas numpy arrays)
                                embeddings_list = [emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in embeddings]
                                
                                # Stocker dans ChromaDB
                                vector_store.add_documents(
                                    embeddings=embeddings_list,
                                    documents=chunks,
                                    metadatas=metadatas,
                                    ids=doc_ids
                                )
                                
                                st.success(f"✅ {len(chunks)} chunks stockés dans ChromaDB!")
                                
                                # Afficher les infos de la collection
                                info = vector_store.get_collection_info()
                                st.info(f"📊 Total dans la base: {info['count']} documents")
                                
                            except Exception as e:
                                st.error(f"❌ Erreur lors du stockage: {e}")
                                st.exception(e)
                    
                except ImportError:
                    st.warning("⚠️ sentence-transformers non installé. Les embeddings réels seront générés plus tard.")
                    st.markdown("""
                    **Pour le moment, voici à quoi ressemblerait un vecteur:**
                    
                    - **Dimensions:** 384
                    - **Exemple:** [0.0234, -0.1567, 0.2845, ..., -0.0794]
                    - **Taille:** 1536 bytes par chunk
                    - **Type:** float32 (nombres à virgule flottante)
                    
                    Chaque nombre capture une caractéristique sémantique du texte!
                    """)
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
        else:
            st.error("❌ Erreur lors du traitement du document")
        
        # Nettoyer
        temp_path.unlink()
