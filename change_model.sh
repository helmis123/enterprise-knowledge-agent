#!/bin/bash

# Script pour changer de modèle Ollama

echo "🔄 Changement de modèle Ollama"
echo "=============================="

# Vérifier si Ollama est en cours d'exécution
if ! docker ps | grep -q ollama; then
    echo "❌ Ollama n'est pas démarré"
    echo "Démarrez Ollama avec : docker run -d -p 11434:11434 ollama/ollama:latest"
    exit 1
fi

# Lister les modèles disponibles
echo "📋 Modèles disponibles :"
echo "1. llama3:7b  (4GB)   - Très rapide, ressources minimales"
echo "2. llama3:8b  (4.7GB) - Rapide, bon compromis (recommandé)"
echo "3. llama3:13b (7.5GB) - Modéré, très bonne qualité"
echo "4. llama3:70b (40GB)  - Lent, qualité maximale (nécessite 64GB+ RAM)"

read -p "Choisissez un modèle (1-4): " choice

case $choice in
    1)
        MODEL="llama3:7b"
        echo "📥 Téléchargement de llama3:7b..."
        ;;
    2)
        MODEL="llama3:8b"
        echo "📥 Téléchargement de llama3:8b..."
        ;;
    3)
        MODEL="llama3:13b"
        echo "📥 Téléchargement de llama3:13b..."
        ;;
    4)
        MODEL="llama3:70b"
        echo "⚠️  Attention : llama3:70b nécessite au moins 64GB de RAM"
        read -p "Continuer ? (y/N): " confirm
        if [[ $confirm != "y" ]]; then
            echo "❌ Annulé"
            exit 1
        fi
        echo "📥 Téléchargement de llama3:70b (cela peut prendre du temps)..."
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac

# Télécharger le modèle
docker exec ollama-agentia ollama pull $MODEL

if [ $? -eq 0 ]; then
    echo "✅ Modèle $MODEL téléchargé avec succès"
    
    # Mettre à jour la configuration
    echo "🔧 Mise à jour de la configuration..."
    sed -i "s/OLLAMA_MODEL=.*/OLLAMA_MODEL=$MODEL/" config.env
    
    echo "✅ Configuration mise à jour"
    echo ""
    echo "📋 Prochaines étapes :"
    echo "1. Redémarrez l'application : docker-compose restart app"
    echo "2. Ou relancez : python start.py"
    echo ""
    echo "🎯 Modèle actuel : $MODEL"
else
    echo "❌ Erreur lors du téléchargement du modèle"
    exit 1
fi
