# Organisation Git du projet

## Branches

| Branche | Role |
|---|---|
| `main` | Code stable, seule branche deployee en production par Jenkins |
| `dev` | Branche d'integration, reçoit les fonctionnalites terminees |
| `feature/*` | Une branche par fonctionnalite, partant toujours de `dev` |
| `fix/*` | Correction de bug |

`main` n'est jamais modifiee directement : tout passe par une pull request depuis `dev`.

## Mise en place du depot

```bash
git init
git branch -M main
git add .
git commit -m "chore(init): structure du projet"
git remote add origin git@github.com:<votre-compte>/todo-devops.git
git push -u origin main

git checkout -b dev
git push -u origin dev

bash githooks/install-hooks.sh
```

## Cycle de travail habituel

```bash
git checkout dev
git pull
git checkout -b feature/filtre-taches

# ... modifications ...
git add app/
git commit -m "feat(app): filtre des taches terminees"
git push -u origin feature/filtre-taches
```

Ensuite, ouverture d'une pull request `feature/filtre-taches` vers `dev` sur GitHub,
relecture, puis fusion. Quand `dev` est stable, une seconde pull request `dev` vers
`main` declenche le deploiement.

## Convention de messages

Le hook `commit-msg` impose le format `type(portee): description`.

```
feat(app): ajout de la route de suppression
fix(k8s): correction du chemin PGDATA du volume
docs(readme): procedure d'installation de Jenkins
ci(jenkins): ajout de l'etape de lint
test(store): couverture du store memoire
chore(git): ajout du .gitignore
refactor(app): extraction de la couche store
```

## Protection de branche a activer sur GitHub

Dans `Settings > Branches > Add rule` pour `main` :

- Require a pull request before merging (au moins 1 approbation)
- Require status checks to pass before merging
- Do not allow bypassing the above settings

## Etiquettes de version

```bash
git tag -a v1.0.0 -m "Version presentee en soutenance"
git push origin v1.0.0
```
