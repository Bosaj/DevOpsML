# TP Docker - Application Flask

Application Flask simple containerisée avec Docker.

## Prérequis
- Docker installé

## Instructions

### Construire l'image
docker build -t hello-tp .

text

### Lancer le conteneur
docker run -d -p 5000:5000 --name hello hello-tp

text

### Accéder à l'application
Ouvrez votre navigateur sur http://localhost:5000

### Arrêter et supprimer
docker stop hello
docker rm hello
docker rmi hello-tp
