# 🤖 Agent Knowledge Interne

Un assistant IA interne capable de lire les documents d'entreprise et de répondre aux questions des employés en langage naturel.

## 🎯 Fonctionnalités

- **📚 Indexation automatique** des documents (PDF, Word, Markdown, TXT)
- **🔍 Recherche sémantique** avec ChromaDB
- **💬 Interface de chat** intuitive avec Streamlit
- **🤖 Réponses contextuelles** avec Ollama (modèle local)
- **📊 Sources citées** pour chaque réponse
- **🔒 Sécurité** : tout fonctionne en local
- **🐳 Déploiement Docker** simple

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.11+
- Docker et Docker Compose
- 8GB RAM minimum (pour le modèle Llama)

### Installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd agentia
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer l'environnement**
```bash
cp config.env.example config.env
# Éditer config.env selon vos besoins
```

4. **Démarrer avec Docker Compose**
```bash
docker-compose up --build
```

5. **Ou démarrer manuellement**
```bash
# Terminal 1: Démarrer Ollama
docker run -d -p 11434:11434 ollama/ollama:latest

# Terminal 2: Télécharger le modèle
docker exec <container-id> ollama pull llama3:8b

# Terminal 3: Démarrer l'application
python start.py
```

6. **Accéder à l'application**
Ouvrez votre navigateur sur : http://localhost:8501

## 📁 Structure du Projet

```
agentia/
├── src/                    # Code source principal
│   ├── config.py          # Configuration
│   ├── document_processor.py # Traitement des documents
│   ├── vector_store.py    # Base vectorielle ChromaDB
│   └── llm_client.py      # Client Ollama
├── data/                  # Documents à indexer
├── chroma_db/            # Base de données vectorielle
├── logs/                 # Fichiers de logs
├── app.py                # Interface Streamlit
├── start.py              # Script de démarrage
├── test_agent.py         # Tests
├── docker-compose.yml    # Configuration Docker
├── Dockerfile           # Image Docker
└── requirements.txt     # Dépendances Python
```

## 🔧 Configuration

### Variables d'environnement (config.env)

```env
# Modèle LLM
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3:8b

# Base vectorielle
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=enterprise_documents

# Modèle d'embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Limites
MAX_DOCUMENT_SIZE_MB=50
MAX_CHUNK_SIZE=1000
MAX_CHUNKS_PER_DOCUMENT=100
```

## 📚 Utilisation

### 1. Ajouter des Documents

Placez vos documents dans le dossier `data/` :
- **PDF** : `.pdf`
- **Word** : `.docx`, `.doc`
- **Markdown** : `.md`
- **Texte** : `.txt`

### 2. Indexer les Documents

Dans l'interface web :
1. Allez dans la sidebar
2. Cliquez sur "Indexer tous les documents du dossier"
3. Attendez la fin du traitement

### 3. Poser des Questions

Exemples de questions :
- "Quelle est la politique de télétravail ?"
- "Comment réinitialiser le serveur de staging ?"
- "Quelle est la procédure de remboursement ?"

## 🧪 Tests

Exécuter les tests :
```bash
python test_agent.py
```

Les tests vérifient :
- ✅ Traitement des documents
- ✅ Base vectorielle ChromaDB
- ✅ Connexion Ollama
- ✅ Agent complet

## 🔒 Sécurité

- **Données locales** : Aucune donnée n'est envoyée à l'extérieur
- **Modèle local** : Ollama fonctionne entièrement en local
- **Chiffrement** : ChromaDB stocke les données localement
- **Authentification** : Prêt pour intégration OAuth (à implémenter)

## 🚀 Déploiement Production

### Avec Docker Compose

```bash
# Production
docker-compose -f docker-compose.prod.yml up -d
```

### Serveur Dédié

1. **Serveur Ubuntu 20.04+**
2. **Installation Docker**
3. **Configuration reverse proxy** (Nginx)
4. **SSL/TLS** avec Let's Encrypt
5. **Monitoring** avec Prometheus/Grafana

## 📊 Monitoring

### Métriques Disponibles

- Nombre de documents indexés
- Temps de réponse moyen
- Score de confiance des réponses
- Utilisation des ressources

### Logs

Les logs sont disponibles dans :
- `logs/agent.log` : Logs de l'application
- Docker logs : `docker-compose logs -f`

## 🔧 Développement

### Structure du Code

- **`config.py`** : Configuration centralisée
- **`document_processor.py`** : Extraction et traitement des documents
- **`vector_store.py`** : Gestion ChromaDB et embeddings
- **`llm_client.py`** : Interface Ollama et agent principal
- **`app.py`** : Interface utilisateur Streamlit

### Ajouter de Nouveaux Formats

1. Étendre `DocumentProcessor` dans `document_processor.py`
2. Ajouter la méthode d'extraction correspondante
3. Mettre à jour `supported_extensions`

### Intégrations Futures

- **Google Drive API** : Synchronisation automatique
- **Notion API** : Import des pages internes
- **Slack Bot** : Interface dans Slack
- **SharePoint** : Connexion aux documents SharePoint

## 🐛 Dépannage

### Ollama ne démarre pas

```bash
# Vérifier Docker
docker ps

# Redémarrer Ollama
docker restart ollama-agentia

# Vérifier les logs
docker logs ollama-agentia
```

### Erreur de mémoire

- Réduire `MAX_CHUNK_SIZE` dans `config.env`
- Utiliser un modèle plus petit (llama3:7b au lieu de 8b)
- Augmenter la RAM du serveur

### Documents non indexés

- Vérifier les formats supportés
- Contrôler la taille des fichiers (< 50MB)
- Consulter les logs dans `logs/agent.log`

## 📈 Roadmap

### Version 1.1
- [ ] Authentification OAuth
- [ ] Interface d'administration
- [ ] API REST
- [ ] Intégration Slack

### Version 1.2
- [ ] Support multimédia (images, diagrammes)
- [ ] Workflow automatisé
- [ ] Analytics avancées
- [ ] Mode hors ligne

### Version 2.0
- [ ] Agents multiples (CrewAI)
- [ ] Génération automatique de FAQ
- [ ] Intégration CRM
- [ ] Mobile app

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

- **Issues** : Utilisez GitHub Issues
- **Email** : support@techcorp.com
- **Documentation** : [Wiki du projet](https://github.com/your-repo/wiki)

---

**Développé avec ❤️ pour améliorer l'efficacité des équipes internes**
