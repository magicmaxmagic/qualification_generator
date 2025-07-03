# Étape 1 : base image avec Python
FROM python:3.11-slim

# Étape 2 : définir le dossier de travail
WORKDIR /app

# Étape 3 : copier les fichiers
COPY . .

# Étape 4 : installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : exposer le port utilisé par Streamlit
EXPOSE 8501

# Étape 6 : commande pour démarrer l'application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]