from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
def test_healthz(): r=c.get("/healthz"); assert r.status_code==200 and r.json()["status"]=="ok"
def test_readyz(): assert c.get("/readyz").json()["status"]=="ready"
def test_info():
    j=c.get("/api/info").json()
    assert j["service"]=="__SERVICE_NAME__" and j["version"]=="__VERSION__" and j["environment"]=="__ENVIRONMENT__"
def test_metrics(): r=c.get("/metrics"); assert r.status_code==200 and "http_requests_total" in r.text
def test_not_found(): assert c.get("/nope").status_code==404
