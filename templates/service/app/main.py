import os, time
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

SERVICE = os.getenv("SERVICE_NAME", "__SERVICE_NAME__")
VERSION = os.getenv("SERVICE_VERSION", "__VERSION__")
ENVIRONMENT = os.getenv("SERVICE_ENVIRONMENT", "__ENVIRONMENT__")
START = time.time(); REQUESTS = {"total": 0}

app = FastAPI(title="__SERVICE_TITLE__", version=VERSION, description="__SERVICE_DESCRIPTION__")

@app.middleware("http")
async def count_requests(request, call_next):
    REQUESTS["total"] += 1
    return await call_next(request)

@app.get("/healthz")
def healthz(): return {"status": "ok", "service": SERVICE}

@app.get("/readyz")
def readyz(): return {"status": "ready", "service": SERVICE, "version": VERSION}

@app.get("/api/info")
def info():
    return {"service": SERVICE, "version": VERSION, "environment": ENVIRONMENT,
            "description": "__SERVICE_DESCRIPTION__", "owner": "__OWNER__", "uptime_seconds": round(time.time() - START, 3)}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return (f"# HELP http_requests_total Requests served\n# TYPE http_requests_total counter\n"
            f"http_requests_total{{service=\"{SERVICE}\"}} {REQUESTS['total']}\n"
            f"# HELP service_up Service is up\n# TYPE service_up gauge\nservice_up{{service=\"{SERVICE}\"}} 1\n")
