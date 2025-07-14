# Installation du Chatbot IA - Correction des Conflits

## 🚨 Problème actuel : Conflit de versions

**Erreur rencontrée** : `cannot import name 'BaseTransport' from 'httpx'`

**Cause** : Incompatibilité entre les versions d'OpenAI et httpx.

## ✅ Solution rapide (Recommandée)

```bash
# Étape 1 : Désinstaller les versions conflictuelles
pip uninstall openai httpx -y

# Étape 2 : Installer les versions compatibles
pip install httpx==0.24.1
pip install openai==1.3.0

# Étape 3 : Redémarrer l'application Streamlit
```

## 🔄 Solution alternative

```bash
# Installation avec contraintes de compatibilité
pip install "openai[datalib]==1.3.0"
pip install "httpx>=0.23.0,<0.25.0"
```

## 🛠️ En cas de problème persistant

1. **Créer un nouvel environnement virtuel** :
```bash
python3 -m venv venv_chatbot
source venv_chatbot/bin/activate  # macOS/Linux
# ou
venv_chatbot\Scripts\activate     # Windows

pip install streamlit pandas openpyxl plotly geopy streamlit-cookies-manager streamlit-aggrid
pip install httpx==0.24.1 openai==1.3.0
```

2. **Utiliser conda** (plus stable) :
```bash
conda create -n iveo_env python=3.11
conda activate iveo_env
conda install streamlit pandas openpyxl plotly
pip install httpx==0.24.1 openai==1.3.0 streamlit-aggrid streamlit-cookies-manager geopy
```

## 📋 Configuration après installation

1. Obtenez une clé API OpenAI sur https://platform.openai.com/api-keys
2. Dans l'application, allez sur la page "🤖 Assistant IA"
3. Entrez votre clé API dans la sidebar
4. Commencez à chatter !

## 🎯 Fonctionnalités disponibles

- 💬 Chat interactif avec GPT
- 🎛️ Paramètres ajustables (modèle, créativité, longueur)
- 📊 Analyse contextuelle de vos données
- ⚡ Questions rapides dans la sidebar
- 🎯 Actions prédéfinies pour l'analyse

## 🔍 Vérification de l'installation

```bash
python -c "import openai; print('OpenAI version:', openai.__version__)"
python -c "import httpx; print('httpx version:', httpx.__version__)"
```

Les versions doivent être :
- **OpenAI** : 1.3.0
- **httpx** : 0.24.1

## ⚠️ Interface temporaire

En attendant la correction, une interface temporaire est disponible avec :
- Aperçu des données
- Suggestions d'analyse
- Enregistrement des demandes
- Documentation des besoins
