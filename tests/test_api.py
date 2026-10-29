import os
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

# Keep tests away from the developer's database.
_tmp = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_tmp.name) / "test.db")
from backend.main import app, sync_projects
from backend.importer import parse_markdown

def test_import_deduplicates():
    row = "| Agent | Education | Helps learners | [Code](https://github.com/example/agent) |"
    assert len(parse_markdown(row + "\n" + row)) == 1

def test_search_and_repeat_import():
    with TestClient(app) as c:
        first = c.get("/api/projects").json()
        assert first["total"] > 10
        sync_projects()
        assert c.get("/api/projects").json()["total"] == first["total"]
        item = first["items"][0]
        data = c.get("/api/projects", params={"q": item["name"], "industry": item["industry"]}).json()
        assert item["id"] in [p["id"] for p in data["items"]]
        assert c.get("/api/projects", params={"q":"unlikely-no-match-12345"}).json()["total"] == 0
        assert c.get("/api/projects", params={"q":"%"}).json()["total"] == 0
        assert c.get("/api/projects?page=0").status_code == 422
        assert c.get("/api/projects?page_size=10000").status_code == 422
        assert c.get("/api/projects?sort=invalid").status_code == 422
        second = c.get("/api/projects?page=2").json()
        assert not ({p["id"] for p in first["items"]} & {p["id"] for p in second["items"]})
        assert c.get("/api/facets").json()["industry"]
