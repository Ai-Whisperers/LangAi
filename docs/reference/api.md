# API Reference

The Company Researcher API provides REST endpoints and WebSocket support for company research operations.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Include your API key in requests:

```
X-API-Key: your-api-key-here
```

## Endpoints

### Research

#### Start Research
```http
POST /research
```

**Request Body:**
```json
{
  "company_name": "Tesla",
  "depth": "standard",
  "include_financial": true,
  "include_market": true,
  "include_competitive": true,
  "include_news": true
}
```

**Response:**
```json
{
  "task_id": "task_1234567890",
  "company_name": "Tesla",
  "status": "pending",
  "depth": "standard",
  "created_at": "2024-01-15T10:30:00Z",
  "estimated_duration_seconds": 120
}
```

#### Get Research Status
```http
GET /research/{task_id}
```

#### Get Research Results
```http
GET /research/{task_id}/result
```

#### Cancel Research
```http
DELETE /research/{task_id}
```

### Batch Operations

#### Start Batch Research
```http
POST /research/batch
```

**Request Body:**
```json
{
  "companies": ["Tesla", "Apple", "Microsoft"],
  "depth": "standard",
  "priority": 2
}
```

#### Get Batch Status
```http
GET /research/batch/{batch_id}
```

### Health & Status

#### Health Check
```http
GET /health
```

#### Statistics
```http
GET /stats
```

## WebSocket

Connect to real-time updates:

```
ws://localhost:8000/ws
```

### Messages

**Subscribe to task:**
```json
{
  "type": "subscribe",
  "task_id": "task_1234567890"
}
```

**Progress update (received):**
```json
{
  "type": "progress",
  "task_id": "task_1234567890",
  "timestamp": "2024-01-15T10:30:05Z",
  "data": {
    "progress": 45,
    "stage": "financial_analysis"
  }
}
```

## Rate Limits

- **Per minute:** 60 requests
- **Per hour:** 1000 requests

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 55
```

## Error Responses

```json
{
  "error": "Rate limit exceeded",
  "retry_after": 30,
  "code": "RATE_LIMIT_EXCEEDED"
}
```

## Python Client Example

```python
import httpx

client = httpx.Client(
    base_url="http://localhost:8000/api/v1",
    headers={"X-API-Key": "your-key"}
)

# Start research
response = client.post("/research", json={
    "company_name": "Tesla",
    "depth": "comprehensive"
})
task = response.json()

# Check status
status = client.get(f"/research/{task['task_id']}").json()
print(f"Status: {status['status']}")
```
