from store import MemoryStore, dsn_from_env


def test_les_taches_faites_passent_en_bas():
    store = MemoryStore()
    a = store.add("Provisionner les VM")
    store.add("Configurer Jenkins")
    store.toggle(a)

    titres = [t["title"] for t in store.all()]
    assert titres[-1] == "Provisionner les VM"


def test_dsn_construite_depuis_les_variables(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_HOST", "postgres")
    monkeypatch.setenv("DB_NAME", "todo")
    monkeypatch.setenv("DB_USER", "todo")
    monkeypatch.setenv("DB_PASSWORD", "secret")

    dsn = dsn_from_env()
    assert "host=postgres" in dsn
    assert "user=todo" in dsn


def test_database_url_prioritaire(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://a:b@c:5432/d")
    assert dsn_from_env() == "postgresql://a:b@c:5432/d"
