import time

import pytest
from app.config import Settings
from app.db import Database
from app.main import create_app
from app.models import Analysis
from app.schemas import Evidence, EvidencePage, Report
from fastapi.testclient import TestClient
from test_storage import empty_report


class Provider:
    configured = True

    def extract(self, document):
        return Evidence(
            pages=[
                EvidencePage(
                    page=p.page, text=p.text or "Synthetic cough.", warnings=[]
                )
                for p in document.pages
            ],
            is_clinical=True,
            warnings=[],
        )

    def review(self, evidence, repair=False):
        return Report(**empty_report())


@pytest.fixture
def settings(tmp_path):
    return Settings(
        database_url=f"sqlite:///{tmp_path}/test.db",
        upload_dir=tmp_path / "uploads",
        session_secret="test-secret-123456789012345678901234",
        _env_file=None,
    )


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings, Provider())) as client:
        client.get("/api/session")
        yield client


def submit(client):
    return client.post(
        "/api/analyses",
        json={"text": "Synthetic patient with cough.", "synthetic_confirmed": True},
    )


def await_result(client, identifier):
    for _ in range(100):
        result = client.get("/api/analyses/" + identifier).json()
        if result["status"] != "processing":
            return result
        time.sleep(0.02)
    pytest.fail("Job did not finish")


def test_submit_poll_history(client):
    response = submit(client)
    assert response.status_code == 202
    result = await_result(client, response.json()["id"])
    assert result["status"] == "completed"
    assert result["report"]["missing_information"] == ["Allergies"]
    assert client.get("/api/analyses").json()["items"][0]["id"] == result["id"]


def test_cross_session_access_is_404(client):
    identifier = submit(client).json()["id"]
    client.cookies.clear()
    client.get("/api/session")
    assert client.get("/api/analyses/" + identifier).status_code == 404
    assert client.get("/api/analyses").json()["items"] == []


@pytest.mark.parametrize(
    "body",
    [
        {"text": "", "synthetic_confirmed": True},
        {"text": "a" * 20001, "synthetic_confirmed": True},
        {"text": "Cough", "synthetic_confirmed": False},
    ],
)
def test_invalid_input(client, body):
    assert client.post("/api/analyses", json=body).status_code == 422


def test_origin_rejected(client):
    assert (
        client.post(
            "/api/analyses",
            json={"text": "Cough", "synthetic_confirmed": True},
            headers={"Origin": "https://evil.example"},
        ).status_code
        == 403
    )


def test_unconfigured_provider_is_clear(settings):
    with TestClient(create_app(settings)) as client:
        client.get("/api/session")
        assert client.get("/api/health").json()["ai_configured"] is False
        assert submit(client).status_code == 503


def test_invalid_upload(client):
    response = client.post(
        "/api/analyses",
        data={"synthetic_confirmed": "true"},
        files={"file": ("note.pdf", b"broken", "application/pdf")},
    )
    assert response.status_code == 422


def test_global_rate_limit(client, settings):
    settings.global_submissions_per_hour = 1
    assert submit(client).status_code == 202
    client.cookies.clear()
    client.get("/api/session")
    assert submit(client).status_code == 429


def test_failed_job_cleans_input(settings):
    class BrokenProvider(Provider):
        def extract(self, document):
            raise RuntimeError("secret must not leak")

    with TestClient(create_app(settings, BrokenProvider())) as client:
        client.get("/api/session")
        result = await_result(client, submit(client).json()["id"])
        assert result["status"] == "failed"
        assert "secret" not in result["error"]
        assert list(settings.upload_dir.iterdir()) == []


def test_restart_marks_interrupted_job_failed(settings):
    db = Database(settings.database_url)
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.attributes["database_url"] = settings.database_url
    command.upgrade(config, "head")
    settings.upload_dir.mkdir()
    path = settings.upload_dir / "old.json"
    path.write_text("{}")
    with db.session() as session:
        session.add(
            Analysis(
                owner_hash="owner",
                title="Interrupted",
                input_type="text",
                status="processing",
                input_path=str(path),
            )
        )
        session.commit()
    with TestClient(create_app(settings, Provider())):
        with db.session() as session:
            item = session.query(Analysis).one()
            assert item.status == "failed"
            assert "interrupted" in item.error.lower()
        assert not path.exists()


def test_body_size_limit(client):
    response = client.post(
        "/api/analyses",
        content=b"x" * (11 * 1024 * 1024 + 1),
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 413


def test_real_file_routes_with_fixture_provider(client):
    from pathlib import Path

    samples = Path(__file__).resolve().parents[2] / "samples"
    for name in [
        "typed-note.pdf",
        "scanned-note.pdf",
        "mixed-note.pdf",
        "typed-note.png",
    ]:
        response = client.post(
            "/api/analyses",
            data={"synthetic_confirmed": "true"},
            files={"file": (name, (samples / name).read_bytes())},
        )
        assert response.status_code == 202, response.text
        assert await_result(client, response.json()["id"])["status"] == "completed"


def test_pending_capacity_blocks_submission(client, settings):
    settings.max_pending_jobs = 0
    assert submit(client).status_code == 429


def test_unknown_api_never_returns_frontend(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")


def test_malformed_json_has_safe_error(client):
    response = client.post(
        "/api/analyses", content=b"{", headers={"content-type": "application/json"}
    )
    assert response.status_code == 422
    assert "malformed" in response.json()["error"]["message"]
