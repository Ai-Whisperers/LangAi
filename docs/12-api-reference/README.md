# API Reference

This project exposes a FastAPI service with:

- REST endpoints under `/api/v1`
- WebSocket endpoint at `/ws`

---

## Run the API server

```bash
pip install -r requirements.txt
python -m company_researcher.api.app --host 0.0.0.0 --port 8000
```

Interactive docs:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

---

## Health

- `GET /health`: container/cluster health checks
- `GET /api/v1/health`: API-level health (includes storage backend info)

---

## REST endpoints (v1)

Base path: `/api/v1`

- `POST /research`: start a research task (returns `task_id`)
- `GET /research/{task_id}`: task status and (eventually) results
- `GET /research/{task_id}/result`: final result payload (only when completed)
- `DELETE /research/{task_id}`: cancel a task
- `POST /research/batch`: start batch research (returns `batch_id` + task IDs)
- `GET /research/batch/{batch_id}`: batch status
- `GET /research`: list tasks (filters: `status`, `company`, pagination)
- `GET /stats`: basic API stats

See `src/company_researcher/api/routes.py` for the authoritative list.

---

## WebSocket

- `GET /ws` (WebSocket): real-time updates / message handling

See `src/company_researcher/api/websocket.py`.
