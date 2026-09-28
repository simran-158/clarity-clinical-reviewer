"""Safe public smoke check without AI usage. Uses only a fictional note."""

import sys

import httpx

origin = sys.argv[1].rstrip("/")
with httpx.Client(base_url=origin, timeout=30) as client:
    page = client.get("/")
    assert page.status_code == 200 and "Clarity" in page.text
    health = client.get("/api/health")
    assert health.status_code == 200 and health.json()["status"] == "ok"
    session = client.get("/api/session")
    assert session.status_code == 200
    if origin.startswith("https://"):
        attributes = session.headers.get("set-cookie", "").lower()
        assert "secure" in attributes and "httponly" in attributes
    history = client.get("/api/analyses")
    assert history.status_code == 200 and isinstance(history.json()["items"], list)
    assert client.get("/api/unknown").status_code == 404
    if not health.json()["ai_configured"]:
        response = client.post(
            "/api/analyses",
            headers={"Origin": origin},
            json={
                "text": "SYNTHETIC NOTE. Fictional patient reports a cough.",
                "synthetic_confirmed": True,
            },
        )
        assert (
            response.status_code == 503
            and response.json()["error"]["code"] == "ai_not_configured"
        )
    print(
        "PASS: public UI, health, secure session, history, API 404, and unconfigured-AI response."
    )
    print("AI configured:", health.json()["ai_configured"])
