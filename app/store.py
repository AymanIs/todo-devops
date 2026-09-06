"""Acces aux donnees.

Deux implementations partagent la meme interface :
- PostgresStore : utilisee en production (conteneur / Kubernetes)
- MemoryStore   : utilisee par les tests unitaires, aucune base requise
"""

import os
import time
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    done       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def dsn_from_env():
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    return (
        "host={host} port={port} dbname={db} user={user} password={pwd}".format(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            db=os.getenv("DB_NAME", "todo"),
            user=os.getenv("DB_USER", "todo"),
            pwd=os.getenv("DB_PASSWORD", "todo"),
        )
    )


class PostgresStore:
    def __init__(self, dsn=None):
        self.dsn = dsn or dsn_from_env()

    @contextmanager
    def _cursor(self, commit=False):
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = psycopg2.connect(self.dsn)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                yield cur
            if commit:
                conn.commit()
        finally:
            conn.close()

    def init_schema(self, tentatives=10, pause=3):
        """Cree la table. La base peut demarrer apres l'application."""
        derniere = None
        for essai in range(1, tentatives + 1):
            try:
                with self._cursor(commit=True) as cur:
                    cur.execute(SCHEMA)
                print("Schema pret (tentative %d)" % essai, flush=True)
                return
            except Exception as exc:
                derniere = exc
                print("Base indisponible, nouvel essai dans %ds" % pause, flush=True)
                time.sleep(pause)
        raise RuntimeError("Connexion a PostgreSQL impossible: %s" % derniere)

    def ping(self):
        with self._cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()

    def all(self):
        with self._cursor() as cur:
            cur.execute(
                "SELECT id, title, done FROM tasks ORDER BY done, created_at DESC"
            )
            return [dict(ligne) for ligne in cur.fetchall()]

    def add(self, title):
        with self._cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO tasks (title) VALUES (%s) RETURNING id", (title,)
            )
            return cur.fetchone()["id"]

    def toggle(self, task_id):
        with self._cursor(commit=True) as cur:
            cur.execute("UPDATE tasks SET done = NOT done WHERE id = %s", (task_id,))

    def delete(self, task_id):
        with self._cursor(commit=True) as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))


class MemoryStore:
    def __init__(self):
        self._taches = []
        self._sequence = 0

    def init_schema(self):
        return None

    def ping(self):
        return None

    def all(self):
        return [dict(t) for t in sorted(self._taches, key=lambda t: t["done"])]

    def add(self, title):
        self._sequence += 1
        self._taches.insert(0, {"id": self._sequence, "title": title, "done": False})
        return self._sequence

    def toggle(self, task_id):
        for tache in self._taches:
            if tache["id"] == task_id:
                tache["done"] = not tache["done"]

    def delete(self, task_id):
        self._taches = [t for t in self._taches if t["id"] != task_id]
