#!/bin/bash

# Script de déploiement pour l'Agent Knowledge Interne

set -e

echo "🚀 Déploiement de l'Agent Knowledge Interne"
echo "=========================================="

# Vérifier les prérequis
echo "🔍 Vérification des prérequis..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé"
    exit 1
fi

echo "✅ Prérequis vérifiés"

# Créer les répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p data chroma_db logs ssl
echo "✅ Répertoires créés"

# Copier la configuration
if [ ! -f .env ]; then
    echo "📝 Copie de la configuration..."
    cp env.production .env
    echo "⚠️  N'oubliez pas de modifier le SECRET_KEY dans .env"
fi

# Construire et démarrer les services
echo "🐳 Construction et démarrage des services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 30

# Vérifier le statut des services
echo "🔍 Vérification du statut des services..."
docker-compose -f docker-compose.prod.yml ps

# Télécharger le modèle Llama
echo "📥 Téléchargement du modèle Llama..."
docker-compose -f docker-compose.prod.yml exec ollama ollama pull llama3:8b

echo ""
echo "🎉 Déploiement terminé !"
echo ""
echo "📋 Informations importantes:"
echo "   - Application: http://localhost"
echo "   - Logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   - Arrêt: docker-compose -f docker-compose.prod.yml down"
echo ""
echo "🔧 Prochaines étapes:"
echo "   1. Ajoutez vos documents dans le dossier 'data/'"
echo "   2. Accédez à l'interface web"
echo "   3. Indexez vos documents"
echo "   4. Commencez à poser des questions !"
echo ""
