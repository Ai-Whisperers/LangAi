# Deployment

This project supports running as:

- A **local CLI** (`python run_research.py ...`)
- A **FastAPI service** (Docker/Kubernetes-friendly)

---

## Health checks

- **Liveness/readiness**: `GET /health`
- **API health**: `GET /api/v1/health`

---

## Run the API locally (no Docker)

```bash
pip install -r requirements.txt
python -m company_researcher.api.app --host 0.0.0.0 --port 8000
```

Docs:

- OpenAPI UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Docker (single container)

```bash
docker build -f deploy/Dockerfile -t company-researcher:local .
docker run --rm -p 8000:8000 --env-file .env company-researcher:local
```

---

## Docker Compose (API + Redis + ChromaDB + Celery)

From repo root:

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up --build
```

Services:

- **app**: API server on `http://localhost:${APP_PORT:-8000}`
- **redis**: `localhost:${REDIS_PORT:-6379}`
- **chromadb**: `localhost:${CHROMADB_PORT:-8001}`
- **worker**/**scheduler**: Celery worker/beat (requires `REDIS_URL`)
- **flower**: optional monitoring profile

To enable Flower:

```bash
docker compose -f deploy/docker-compose.yml --env-file .env --profile monitoring up --build
```

---

## Kubernetes

Reference manifests are in:

- `deploy/kubernetes/deployment.yaml`

Notes:

- The deployment expects container port **8000** and probes **`/health`**
- Secrets/config are injected via `company-researcher-secrets` / `company-researcher-config`


