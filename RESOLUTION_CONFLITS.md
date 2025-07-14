# Solution aux conflits de dépendances IVÉO BI

## 🚨 Diagnostic du problème

Vous avez plusieurs packages en conflit :
- **ollama** : exige httpx<0.29,>=0.27
- **llama-index** (multiple) : exige openai>=1.14.0
- **langchain-openai** : exige openai<2.0.0,>=1.58.1
- **langsmith** : exige httpx<1,>=0.23.0

## ✅ Solution recommandée : Environnement dédié

### Option 1 : Nouvel environnement pour IVÉO seulement

```bash
# Créer un environnement spécifique pour IVÉO
python3 -m venv iveo_env
source iveo_env/bin/activate

# Installer seulement les dépendances IVÉO
pip install streamlit pandas openpyxl plotly geopy streamlit-cookies-manager streamlit-aggrid

# Installer OpenAI compatible (version récente)
pip install "openai>=1.58.1,<2.0.0"
pip install "httpx>=0.27.0,<0.29.0"
```

### Option 2 : Versions compatibles avec tous vos packages

```bash
# Dans votre environnement actuel, installer des versions compatibles
pip install "openai>=1.58.1,<2.0.0"
pip install "httpx>=0.27.0,<0.29.0"
```

### Option 3 : Isolation avec conda (recommandé pour éviter les conflits)

```bash
# Créer un environnement conda isolé
conda create -n iveo python=3.11
conda activate iveo

# Installer les packages via conda quand possible
conda install pandas openpyxl plotly
pip install streamlit geopy streamlit-cookies-manager streamlit-aggrid
pip install "openai>=1.58.1,<2.0.0" "httpx>=0.27.0,<0.29.0"
```

## 🔧 Mise à jour du code pour la nouvelle version OpenAI

La nouvelle version d'OpenAI a une API légèrement différente. Voici les ajustements :

### Client OpenAI moderne
```python
from openai import OpenAI

# Initialisation
client = OpenAI(api_key="your-api-key")

# Appel API
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## 🎯 Instructions spécifiques pour IVÉO

1. **Testez d'abord l'option 2** (plus simple) :
```bash
pip install --upgrade "openai>=1.58.1,<2.0.0" "httpx>=0.27.0,<0.29.0"
```

2. **Si ça ne fonctionne pas**, utilisez l'option 1 (environnement dédié)

3. **Redémarrez Streamlit** après l'installation

## 📋 Vérification

```bash
python -c "import openai; print('OpenAI:', openai.__version__)"
python -c "import httpx; print('httpx:', httpx.__version__)"
```

Versions attendues :
- **OpenAI** : 1.58.1 ou plus récent
- **httpx** : 0.27.0 à 0.28.x

## 🔄 Si le problème persiste

Contactez-moi avec la sortie de :
```bash
pip list | grep -E "(openai|httpx|llama|langchain)"
```
