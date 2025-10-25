# 🚀 Guide de Démarrage Rapide - Agent Knowledge Interne

## ⚡ Démarrage en 5 minutes

### 1. Prérequis
- Docker et Docker Compose installés
- 8GB RAM minimum
- Ports 8501 et 11434 libres

### 2. Installation Express

```bash
# Cloner le projet
git clone <votre-repo>
cd agentia

# Démarrer avec Docker Compose
docker-compose up --build
```

### 3. Accès à l'Application

1. **Ouvrir le navigateur** : http://localhost:8501
2. **Se connecter** avec les identifiants :
   - **admin** / admin123 (Administrateur)
   - **user** / user123 (Utilisateur standard)
   - **demo** / demo123 (Utilisateur démo)

### 4. Première Utilisation

1. **Indexer les documents d'exemple** :
   - Dans la sidebar, cliquez sur "Indexer tous les documents du dossier"
   - Attendez la fin du traitement

2. **Tester avec une question** :
   - Tapez : "Quelle est la politique de télétravail ?"
   - L'agent répondra en utilisant les documents indexés

## 🔧 Configuration Rapide

### Variables Importantes (config.env)

```env
# Modèle LLM
OLLAMA_MODEL=llama3:8b

# Limites
MAX_DOCUMENT_SIZE_MB=50
MAX_CHUNK_SIZE=1000
```

### Ajouter Vos Documents

1. Placez vos fichiers dans le dossier `data/`
2. Formats supportés : PDF, Word (.docx), Markdown (.md), Texte (.txt)
3. Re-indexez via l'interface web

## 🐛 Résolution de Problèmes Courants

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
- Réduire `MAX_CHUNK_SIZE` à 500
- Utiliser un modèle plus petit (llama3:7b)

### Documents non indexés
- Vérifier les formats (PDF, DOCX, MD, TXT uniquement)
- Contrôler la taille (< 50MB)
- Consulter les logs : `logs/agent.log`

## 📊 Tests Rapides

```bash
# Tester l'installation
python test_agent.py

# Tests unitaires
python -m pytest tests/
```

## 🎯 Cas d'Usage Types

### Questions RH
- "Quelle est la politique de télétravail ?"
- "Comment déclarer un congé maternité ?"
- "Quels sont les avantages sociaux ?"

### Questions IT
- "Comment réinitialiser le serveur de staging ?"
- "Quelle est la procédure de déploiement ?"
- "Comment créer un compte utilisateur ?"

### Questions Support Client
- "Quelle est la procédure de remboursement ?"
- "Comment répondre à une demande client ?"
- "Quels sont les SLA définis ?"

## 🔒 Sécurité

- **Données locales** : Aucune donnée envoyée à l'extérieur
- **Modèle local** : Ollama fonctionne entièrement en local
- **Authentification** : Système de connexion intégré
- **Chiffrement** : ChromaDB stocke les données localement

## 📈 Monitoring

### Vérifier le Statut
- **Interface web** : http://localhost:8501
- **Logs** : `docker-compose logs -f`
- **Statistiques** : Affichées dans la sidebar

### Métriques Importantes
- Nombre de documents indexés
- Temps de réponse moyen
- Score de confiance des réponses

## 🚀 Déploiement Production

```bash
# Utiliser la configuration production
docker-compose -f docker-compose.prod.yml up -d

# Avec reverse proxy Nginx
./deploy.sh
```

## 📞 Support Rapide

- **Problème technique** : Consulter les logs Docker
- **Question fonctionnelle** : Tester avec les documents d'exemple
- **Performance** : Vérifier les ressources système

---

**🎉 Félicitations ! Votre Agent Knowledge Interne est prêt à l'emploi !**
