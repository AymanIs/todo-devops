import pytest

from app import create_app
from store import MemoryStore


@pytest.fixture
def client():
    application = create_app(store=MemoryStore())
    application.config["TESTING"] = True
    return application.test_client()


def test_page_accueil_repond(client):
    reponse = client.get("/")
    assert reponse.status_code == 200
    assert "Aujourd'hui" in reponse.get_data(as_text=True)


def test_health_expose_le_statut(client):
    reponse = client.get("/health")
    assert reponse.status_code == 200
    assert reponse.get_json()["status"] == "up"


def test_ajout_dune_tache(client):
    client.post("/tasks", data={"title": "Preparer la soutenance"})
    taches = client.get("/api/tasks").get_json()
    assert len(taches) == 1
    assert taches[0]["title"] == "Preparer la soutenance"
    assert taches[0]["done"] is False


def test_titre_vide_ignore(client):
    client.post("/tasks", data={"title": "   "})
    assert client.get("/api/tasks").get_json() == []


def test_basculer_letat_dune_tache(client):
    client.post("/tasks", data={"title": "Ecrire le README"})
    identifiant = client.get("/api/tasks").get_json()[0]["id"]

    client.post("/tasks/%d/toggle" % identifiant)
    assert client.get("/api/tasks").get_json()[0]["done"] is True

    client.post("/tasks/%d/toggle" % identifiant)
    assert client.get("/api/tasks").get_json()[0]["done"] is False


def test_suppression_dune_tache(client):
    client.post("/tasks", data={"title": "Nettoyer les images Docker"})
    identifiant = client.get("/api/tasks").get_json()[0]["id"]

    client.post("/tasks/%d/delete" % identifiant)
    assert client.get("/api/tasks").get_json() == []


def test_redirection_apres_ajout(client):
    reponse = client.post("/tasks", data={"title": "Relire le pipeline"})
    assert reponse.status_code == 302
    assert reponse.headers["Location"].endswith("/")


def test_avancement_affiche_dans_la_page(client):
    client.post("/tasks", data={"title": "Configurer Jenkins"})
    client.post("/tasks", data={"title": "Ecrire les manifests"})
    identifiant = client.get("/api/tasks").get_json()[0]["id"]
    client.post("/tasks/%d/toggle" % identifiant)

    page = client.get("/").get_data(as_text=True)
    assert "width: 50%" in page
    assert "1 terminees sur 2" in page
