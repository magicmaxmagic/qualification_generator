#!/bin/bash

# Script de réparation pour le chatbot IVÉO BI
# Ce script corrige les conflits de versions OpenAI/httpx

echo "🔧 Réparation de l'environnement IVÉO BI..."
echo "=========================================="

# Se placer dans le bon répertoire
cd "$(dirname "$0")"

echo "📍 Répertoire courant : $(pwd)"

# Méthode 1 : Réparation avec Python système
echo ""
echo "🔄 Tentative de réparation avec Python système..."

# Désinstaller les versions conflictuelles
echo "🗑️  Désinstallation des packages conflictuels..."
python3 -m pip uninstall openai httpx -y &>/dev/null

# Installer les versions compatibles
echo "📦 Installation des versions compatibles..."
python3 -m pip install httpx==0.24.1
python3 -m pip install openai==1.3.0

# Vérification
echo ""
echo "✅ Vérification de l'installation..."
if python3 -c "import openai; print('✅ OpenAI:', openai.__version__)" 2>/dev/null; then
    if python3 -c "import httpx; print('✅ httpx:', httpx.__version__)" 2>/dev/null; then
        echo "🎉 Réparation réussie !"
        echo ""
        echo "📋 Prochaines étapes :"
        echo "1. Redémarrez l'application Streamlit"
        echo "2. Allez sur la page '🤖 Assistant IA'"
        echo "3. Entrez votre clé API OpenAI"
        echo "4. Profitez du chatbot !"
        echo ""
        exit 0
    fi
fi

echo ""
echo "⚠️  Réparation partielle. Essayons une autre méthode..."

# Méthode 2 : Recréer l'environnement virtuel
echo ""
echo "🔄 Méthode 2: Recréation de l'environnement virtuel..."

# Sauvegarder l'ancien environnement
if [ -d "venv" ]; then
    echo "💾 Sauvegarde de l'ancien environnement..."
    mv venv venv_backup_$(date +%Y%m%d_%H%M%S)
fi

# Créer un nouvel environnement
echo "🆕 Création d'un nouvel environnement virtuel..."
python3 -m venv venv

# Activer le nouvel environnement
echo "⚡ Activation du nouvel environnement..."
source venv/bin/activate

# Installer toutes les dépendances
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install streamlit pandas openpyxl plotly geopy streamlit-cookies-manager streamlit-aggrid
pip install httpx==0.24.1 openai==1.3.0

# Vérification finale
echo ""
echo "🔍 Vérification finale..."
if python -c "import openai; print('✅ OpenAI:', openai.__version__)" 2>/dev/null; then
    if python -c "import httpx; print('✅ httpx:', httpx.__version__)" 2>/dev/null; then
        echo "🎉 Environnement virtuel réparé avec succès !"
        echo ""
        echo "📋 Pour utiliser le nouvel environnement :"
        echo "1. source venv/bin/activate"
        echo "2. streamlit run main.py"
        echo ""
        exit 0
    fi
fi

echo ""
echo "❌ Échec de la réparation automatique."
echo "📞 Contactez le support technique avec ces informations :"
echo "   - OS: $(uname -s)"
echo "   - Python: $(python3 --version)"
echo "   - Répertoire: $(pwd)"
echo ""
echo "🔗 Solution manuelle dans INSTALLATION_CHATBOT.md"
