# Image Jenkins outillee pour ce projet.
#
# L'image officielle ne fournit que git ; le Jenkinsfile a besoin en plus de
# python3-venv (etape de tests), du client Docker (etape de build et de push)
# et de kubectl (etape de deploiement). On les ajoute ici plutot que de les
# installer a la main dans un conteneur : l'environnement de build reste
# reproductible et se relit dans le depot.
FROM jenkins/jenkins:lts

USER root

# GID du groupe docker de la machine hote : le socket /var/run/docker.sock y est
# monte en lecture-ecriture, l'utilisateur jenkins doit appartenir au meme groupe
# pour pouvoir dialoguer avec le demon.
ARG DOCKER_GID=126
ARG KUBECTL_MINOR=v1.37

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates curl gnupg python3 python3-venv python3-pip \
    && install -m 0755 -d /etc/apt/keyrings \
    # depot officiel Docker, pour le client uniquement (pas de demon dans l'image)
    && curl -fsSL https://download.docker.com/linux/debian/gpg \
        -o /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
        > /etc/apt/sources.list.d/docker.list \
    # depot officiel Kubernetes, aligne sur la version du cluster
    && curl -fsSL "https://pkgs.k8s.io/core:/stable:/${KUBECTL_MINOR}/deb/Release.key" \
        | gpg --dearmor -o /etc/apt/keyrings/kubernetes.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/kubernetes.gpg] \
https://pkgs.k8s.io/core:/stable:/${KUBECTL_MINOR}/deb/ /" \
        > /etc/apt/sources.list.d/kubernetes.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli kubectl \
    && rm -rf /var/lib/apt/lists/*

# On rattache jenkins au groupe proprietaire du socket. Si le GID existe deja
# sous un autre nom, on reutilise ce groupe au lieu d'echouer.
RUN if getent group ${DOCKER_GID} >/dev/null; then \
        usermod -aG "$(getent group ${DOCKER_GID} | cut -d: -f1)" jenkins; \
    else \
        groupadd -g ${DOCKER_GID} docker && usermod -aG docker jenkins; \
    fi

USER jenkins
