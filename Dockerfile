# base image avec Python
FROM python:3.11-slim

# définir le dossier de travail
WORKDIR /app

# copier les fichiers
COPY . .

# installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# exposer le port utilisé par Streamlit
EXPOSE 8501

# commande pour démarrer l'application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
