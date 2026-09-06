# Pull request simulee : `dev` vers `main`

Ce document reprend le contenu de la pull request ouverte sur le depot, avec la
relecture et la validation. A accompagner d'une capture d'ecran de la PR fusionnee.

---

**PR #4 — Deploiement automatise de la TODO list**
`dev` → `main` · 11 commits · 24 fichiers modifies

## Ce que contient cette PR

Premiere version complete de la chaine : application, conteneurisation, pipeline
Jenkins et manifests Kubernetes.

- Application Flask avec liste, ajout, changement d'etat et suppression de taches
- Couche `store` separee, ce qui permet de tester sans base de donnees
- Image Docker basee sur `python:3.11-slim`, execution avec un utilisateur non root
- Pipeline Jenkins : lint, tests, build, push DockerHub, deploiement, verification
- Manifests Kubernetes : Namespace, Secret, ConfigMap, PV/PVC, Deployment, Service NodePort
- Provisionnement Terraform des deux VM et configuration Ansible

## Comment tester

```bash
docker compose up --build
curl http://localhost:5000/health
cd app && TODO_BACKEND=memory INIT_SCHEMA=0 pytest
```

## Points de vigilance

Le secret `01-secret.yaml` contient des valeurs en clair pour faciliter la
correction. En conditions reelles il serait genere hors du depot.

---

## Relecture

**Relecteur : @binome** · Demande de modifications

> `k8s/04-postgres.yaml` : le montage sur `/var/lib/postgresql/data` fait echouer
> initdb parce que le repertoire n'est pas vide au premier demarrage.

Corrige dans `a3f1c9d` : ajout de `PGDATA=/var/lib/postgresql/data/pgdata`.

> `Jenkinsfile` : le mot de passe DockerHub apparait dans le log si on utilise
> `docker login -p`.

Corrige dans `7b20e4f` : passage par `--password-stdin` et `withCredentials`.

> L'etape de tests n'a pas besoin d'une base, mais rien ne le garantit.

Corrige dans `c81d55a` : `TODO_BACKEND=memory` explicite dans le pipeline et dans
le hook `pre-commit`.

**Relecteur : @binome** · Approuve

> Les trois points sont regles, le build #12 est vert et l'application repond sur
> le NodePort. Bon pour la fusion.

## Validation

- Build Jenkins #12 : succes (13 tests, 0 echec)
- Image publiee : `moncompte/todo-app:12`
- `kubectl -n todo get pods` : 2/2 pods `todo-app` et 1/1 `postgres` en `Running`

Fusion en `Squash and merge`, branche `feature` supprimee apres fusion.
