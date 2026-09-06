"""Petite application de gestion de taches (projet DevOps)."""

import os

from flask import Flask, jsonify, redirect, render_template, request, url_for

from store import MemoryStore, PostgresStore


def build_store():
    """Retourne le store adapte a l'environnement courant."""
    if os.getenv("TODO_BACKEND", "postgres") == "memory":
        return MemoryStore()
    return PostgresStore()


def create_app(store=None):
    app = Flask(__name__)
    app.config["STORE"] = store or build_store()

    if os.getenv("INIT_SCHEMA", "1") == "1":
        app.config["STORE"].init_schema()

    @app.get("/")
    def index():
        tasks = app.config["STORE"].all()
        restantes = sum(1 for t in tasks if not t["done"])
        faites = len(tasks) - restantes
        avancement = round(100 * faites / len(tasks)) if tasks else 0
        return render_template(
            "index.html", tasks=tasks, restantes=restantes, avancement=avancement
        )

    @app.post("/tasks")
    def create_task():
        titre = (request.form.get("title") or "").strip()
        if titre:
            app.config["STORE"].add(titre[:200])
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/toggle")
    def toggle_task(task_id):
        app.config["STORE"].toggle(task_id)
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id):
        app.config["STORE"].delete(task_id)
        return redirect(url_for("index"))

    @app.get("/api/tasks")
    def api_tasks():
        return jsonify(app.config["STORE"].all())

    @app.get("/health")
    def health():
        try:
            app.config["STORE"].ping()
        except Exception as exc:  # la sonde Kubernetes doit voir l'echec
            return jsonify(status="down", detail=str(exc)), 503
        return jsonify(status="up")

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
