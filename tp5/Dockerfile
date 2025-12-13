FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY app.py .

# Installer Flask
RUN pip install --no-cache-dir flask

# Exposer le port
EXPOSE 5000

# Lancer l'application
CMD ["python", "app.py"]
