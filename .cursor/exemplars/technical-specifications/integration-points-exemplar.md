---
id: exemplar.technical-specifications.integration-points.v1
kind: exemplar
version: 1.0.0
description: Example of a well-structured Integration Points specification
illustrates: technical-specifications.integration-points
use: critic-only
notes: Pattern extraction only. NEVER copy content to production outputs.
provenance:
  owner: team-technical-specs
  last_review: 2025-12-06
---

# Integration Points: Unit Conversion API

**Domain**: Units Management  
**Status**: API Specification Complete  
**Created**: 2025-11-29  
**Last Updated**: 2025-11-29  
**Source**: `eBase/Services/UnitConversionService.h`, external API documentation

## Overview

The Unit Conversion API provides external systems with programmatic access to unit conversion services, enabling consistent unit handling across the energy management ecosystem. This API exposes core conversion functionality while maintaining type safety, validation, and business rule enforcement.

**Integration Purpose**: External systems (market portals, billing systems, reporting tools, data warehouses) require standardized unit conversion capabilities to:
- Convert imported market data to internal units
- Present data in user-preferred units for reports
- Validate unit compatibility before data exchange
- Ensure consistent unit handling across system boundaries

**Key Integration Insight**: The API serves as the authoritative conversion service for the entire eBase ecosystem, ensuring all unit conversions follow identical business rules regardless of calling system.

### Related Specifications
- **Domain Object**: [MeasurementUnit Domain Object](../domain/domain-objects/measurement-unit-domain-object.md) for data model
- **Business Rules**: [Unit Conversion Business Rules](../business-rules/unit-conversion-business-rules.md) for validation logic
- **Database Schema**: [Units Database Schema](../database/units-database-schema.md) for unit definitions

## Integration Architecture

### System Context

```
┌────────────────────────────────────────────────────────────────────┐
│                     External Systems Ecosystem                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────┐          │
│  │ Market      │   │  Billing     │   │  Reporting     │          │
│  │ Portal      │   │  System      │   │  Tools         │          │
│  └──────┬──────┘   └──────┬───────┘   └────────┬───────┘          │
│         │                  │                    │                  │
│         └──────────────────┼────────────────────┘                  │
│                            │                                        │
│                   ┌────────▼────────┐                              │
│                   │  API Gateway    │                              │
│                   │  (Auth/Routing) │                              │
│                   └────────┬────────┘                              │
└────────────────────────────┼────────────────────────────────────────┘
                             │
         ┌───────────────────▼───────────────────┐
         │    Unit Conversion API (REST)         │
         │  ┌─────────────────────────────────┐  │
         │  │ GET  /api/units                 │  │
         │  │ GET  /api/units/{id}            │  │
         │  │ POST /api/units/convert         │  │
         │  │ POST /api/units/convert/batch   │  │
         │  │ POST /api/units/validate        │  │
         │  └─────────────────────────────────┘  │
         └───────────────────┬───────────────────┘
                             │
         ┌───────────────────▼───────────────────┐
         │   Unit Conversion Service (Domain)    │
         │  ┌─────────────────────────────────┐  │
         │  │ • ValidateTypeCompatibility()   │  │
         │  │ • Convert()                     │  │
         │  │ • BatchConvert()                │  │
         │  │ • ConvertTimeSeries()           │  │
         │  └─────────────────────────────────┘  │
         └───────────────────┬───────────────────┘
                             │
         ┌───────────────────▼───────────────────┐
         │   MeasurementUnit Repository          │
         │   (Data Access Layer)                 │
         └───────────────────┬───────────────────┘
                             │
         ┌───────────────────▼───────────────────┐
         │   D_MEASUREMENTUNIT Table             │
         │   (Database)                          │
         └───────────────────────────────────────┘
```

### Integration Patterns

**Pattern 1: Synchronous REST API** (Primary)
- **Use Case**: Real-time unit conversions for interactive applications
- **Protocol**: HTTPS REST with JSON payloads
- **Authentication**: OAuth 2.0 Bearer tokens
- **Response Time**: < 200ms for single conversions, < 500ms for batches

**Pattern 2: Batch Processing** (Secondary)
- **Use Case**: Large-scale data migration and ETL processes
- **Protocol**: Same REST API with batch endpoints
- **Optimization**: Single factor calculation per batch, vectorized operations
- **Throughput**: 10,000+ conversions/second

**Pattern 3: Async Message Queue** (Future)
- **Use Case**: Asynchronous conversion requests for non-interactive scenarios
- **Protocol**: RabbitMQ or Azure Service Bus
- **Pattern**: Request-response with correlation IDs
- **Benefits**: Decoupling, load leveling, resilience

## API Endpoints

### GET /api/units

**Purpose**: Retrieve list of available measurement units

**Authentication**: Required (API key or OAuth 2.0)

**Request**:
```http
GET /api/units?unitType=Energy&pageSize=50&pageNumber=1 HTTP/1.1
Host: api.ebase.example.com
Authorization: Bearer {access_token}
Accept: application/json
```

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| unitType | string | No | Filter by unit type (Energy, Volume, Power, etc.) |
| searchTerm | string | No | Search units by symbol or name |
| pageSize | int | No | Results per page (default: 50, max: 500) |
| pageNumber | int | No | Page number (1-based, default: 1) |

**Response** (200 OK):
```json
{
  "units": [
    {
      "id": 1234,
      "symbol": "kWh",
      "unitType": "Energy",
      "factor": 1000.0,
      "description": "Kilowatt-hour",
      "orderNr": 10.0
    },
    {
      "id": 1235,
      "symbol": "MWh",
      "unitType": "Energy",
      "factor": 0.001,
      "description": "Megawatt-hour",
      "orderNr": 20.0
    }
  ],
  "pagination": {
    "totalCount": 127,
    "pageSize": 50,
    "pageNumber": 1,
    "totalPages": 3
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication
- `400 Bad Request`: Invalid query parameters
- `500 Internal Server Error`: Server-side error

---

### GET /api/units/{id}

**Purpose**: Retrieve specific measurement unit by ID

**Authentication**: Required

**Request**:
```http
GET /api/units/1234 HTTP/1.1
Host: api.ebase.example.com
Authorization: Bearer {access_token}
Accept: application/json
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | long | Unit identifier (NR field) |

**Response** (200 OK):
```json
{
  "id": 1234,
  "symbol": "kWh",
  "unitType": "Energy",
  "factor": 1000.0,
  "description": "Kilowatt-hour",
  "orderNr": 10.0,
  "switchInterval": 15,
  "counterUnit": {
    "id": 1235,
    "symbol": "MWh"
  },
  "metadata": {
    "created": "2023-01-15T10:30:00Z",
    "lastModified": "2024-03-20T14:45:00Z"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Unit ID does not exist
- `500 Internal Server Error`: Server-side error

---

### POST /api/units/convert

**Purpose**: Convert a single value between two units

**Authentication**: Required

**Request**:
```http
POST /api/units/convert HTTP/1.1
Host: api.ebase.example.com
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json

{
  "value": 1500.0,
  "sourceUnit": "kWh",
  "targetUnit": "MWh",
  "precision": 6
}
```

**Request Body Schema**:
```json
{
  "value": "number (required) - Value to convert",
  "sourceUnit": "string (required) - Source unit symbol or ID",
  "targetUnit": "string (required) - Target unit symbol or ID",
  "precision": "integer (optional) - Decimal places in result (default: 6, max: 15)"
}
```

**Alternate Request Format** (using IDs):
```json
{
  "value": 1500.0,
  "sourceUnitId": 1234,
  "targetUnitId": 1235,
  "precision": 6
}
```

**Response** (200 OK):
```json
{
  "convertedValue": 1.5,
  "sourceValue": 1500.0,
  "sourceUnit": {
    "id": 1234,
    "symbol": "kWh",
    "unitType": "Energy"
  },
  "targetUnit": {
    "id": 1235,
    "symbol": "MWh",
    "unitType": "Energy"
  },
  "factor": 0.001,
  "precision": 6,
  "timestamp": "2025-11-29T12:34:56.789Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request (missing fields, invalid unit references)
  ```json
  {
    "error": "BadRequest",
    "message": "Source unit 'kWX' not found",
    "timestamp": "2025-11-29T12:34:56Z"
  }
  ```

- `422 Unprocessable Entity`: Type mismatch (incompatible unit types)
  ```json
  {
    "error": "UnitTypeMismatch",
    "message": "Cannot convert between incompatible types: Energy → Volume",
    "sourceUnit": "kWh",
    "sourceType": "Energy",
    "targetUnit": "m³",
    "targetType": "Volume",
    "timestamp": "2025-11-29T12:34:56Z"
  }
  ```

- `401 Unauthorized`: Missing or invalid authentication
- `500 Internal Server Error`: Server-side error

---

### POST /api/units/convert/batch

**Purpose**: Convert multiple values between same unit pair (optimized)

**Authentication**: Required

**Request**:
```http
POST /api/units/convert/batch HTTP/1.1
Host: api.ebase.example.com
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json

{
  "values": [100.0, 200.0, 300.0, 400.0],
  "sourceUnit": "kWh",
  "targetUnit": "MWh",
  "precision": 3
}
```

**Request Body Schema**:
```json
{
  "values": "array of numbers (required) - Values to convert (max 10000 items)",
  "sourceUnit": "string (required) - Source unit symbol or ID",
  "targetUnit": "string (required) - Target unit symbol or ID",
  "precision": "integer (optional) - Decimal places (default: 6)"
}
```

**Response** (200 OK):
```json
{
  "convertedValues": [0.1, 0.2, 0.3, 0.4],
  "sourceUnit": {
    "id": 1234,
    "symbol": "kWh"
  },
  "targetUnit": {
    "id": 1235,
    "symbol": "MWh"
  },
  "factor": 0.001,
  "itemCount": 4,
  "precision": 3,
  "processingTimeMs": 12,
  "timestamp": "2025-11-29T12:34:56Z"
}
```

**Performance Characteristics**:
- **Optimization**: Factor calculated once, applied to all values
- **Throughput**: 10,000-50,000 conversions/second
- **Max Batch Size**: 10,000 items per request
- **Recommended**: Use batch endpoint for > 100 conversions

**Error Responses**:
- `400 Bad Request`: Invalid request, empty values array, exceeds max batch size
- `422 Unprocessable Entity`: Type mismatch between units
- `401 Unauthorized`: Missing or invalid authentication
- `500 Internal Server Error`: Server-side error

---

### POST /api/units/validate

**Purpose**: Validate conversion compatibility without performing conversion

**Authentication**: Required

**Request**:
```http
POST /api/units/validate HTTP/1.1
Host: api.ebase.example.com
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "sourceUnit": "kWh",
  "targetUnit": "MWh"
}
```

**Response** (200 OK):
```json
{
  "compatible": true,
  "sourceUnit": {
    "id": 1234,
    "symbol": "kWh",
    "unitType": "Energy"
  },
  "targetUnit": {
    "id": 1235,
    "symbol": "MWh",
    "unitType": "Energy"
  },
  "factor": 0.001,
  "validationRules": {
    "typeCompatible": true,
    "factorValid": true,
    "symmetryValid": true
  },
  "timestamp": "2025-11-29T12:34:56Z"
}
```

**Response** (incompatible units):
```json
{
  "compatible": false,
  "sourceUnit": {
    "id": 1234,
    "symbol": "kWh",
    "unitType": "Energy"
  },
  "targetUnit": {
    "id": 2000,
    "symbol": "m³",
    "unitType": "Volume"
  },
  "validationRules": {
    "typeCompatible": false,
    "reason": "Cannot convert between Energy and Volume unit types"
  },
  "timestamp": "2025-11-29T12:34:56Z"
}
```

## Authentication & Authorization

### OAuth 2.0 Bearer Token

**Token Endpoint**: `https://auth.ebase.example.com/oauth/token`

**Request**:
```http
POST /oauth/token HTTP/1.1
Host: auth.ebase.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id={client_id}
&client_secret={client_secret}
&scope=units:read units:convert
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "units:read units:convert"
}
```

**Usage**:
```http
GET /api/units HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Required Scopes

| Endpoint | Required Scope | Description |
|----------|---------------|-------------|
| `GET /api/units` | `units:read` | Read unit definitions |
| `GET /api/units/{id}` | `units:read` | Read specific unit |
| `POST /api/units/convert` | `units:convert` | Perform conversions |
| `POST /api/units/convert/batch` | `units:convert` | Batch conversions |
| `POST /api/units/validate` | `units:read` | Validate compatibility |

## Data Formats

### Request/Response Content Types

**Supported Formats**:
- `application/json` (default, recommended)
- `application/xml` (legacy support)

**Content Negotiation**:
```http
Accept: application/json        # JSON response
Accept: application/xml         # XML response
Accept: */*                     # Server chooses (defaults to JSON)
```

### Date/Time Format

**Standard**: ISO 8601 with UTC timezone  
**Format**: `YYYY-MM-DDTHH:mm:ss.fffZ`  
**Example**: `2025-11-29T12:34:56.789Z`

### Number Precision

**Default Precision**: 6 decimal places  
**Max Precision**: 15 decimal places  
**Rounding**: Banker's rounding (round to even)

## Error Handling

### Standard Error Response Format

```json
{
  "error": "ErrorCode",
  "message": "Human-readable error description",
  "details": {
    "field": "sourceUnit",
    "value": "invalid_unit",
    "reason": "Unit symbol not found"
  },
  "timestamp": "2025-11-29T12:34:56Z",
  "requestId": "abc123-def456-ghi789"
}
```

### Error Codes

| HTTP Status | Error Code | Description | Retry |
|-------------|------------|-------------|-------|
| 400 | `BadRequest` | Invalid request format or parameters | No |
| 401 | `Unauthorized` | Missing or invalid authentication | No |
| 403 | `Forbidden` | Insufficient permissions for operation | No |
| 404 | `NotFound` | Requested resource does not exist | No |
| 422 | `UnitTypeMismatch` | Incompatible unit types for conversion | No |
| 429 | `RateLimitExceeded` | Too many requests from client | Yes (after delay) |
| 500 | `InternalServerError` | Server-side error | Yes (with backoff) |
| 503 | `ServiceUnavailable` | Service temporarily unavailable | Yes (with backoff) |

### Rate Limiting

**Limits**:
- **Standard Tier**: 1000 requests/hour per client
- **Premium Tier**: 10000 requests/hour per client
- **Burst**: Up to 100 requests/minute

**Response Headers**:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1638360000
Retry-After: 3600
```

**Error Response** (429 Too Many Requests):
```json
{
  "error": "RateLimitExceeded",
  "message": "Rate limit of 1000 requests/hour exceeded",
  "retryAfter": 3600,
  "timestamp": "2025-11-29T12:34:56Z"
}
```

## Performance Characteristics

### Response Time SLAs

| Operation | Target | Maximum | Percentile |
|-----------|--------|---------|------------|
| GET /api/units | 50ms | 200ms | p95 |
| GET /api/units/{id} | 30ms | 150ms | p95 |
| POST /api/units/convert | 100ms | 300ms | p95 |
| POST /api/units/convert/batch (100 items) | 150ms | 500ms | p95 |
| POST /api/units/validate | 50ms | 200ms | p95 |

### Throughput Capacity

| Endpoint | Requests/Second | Concurrent Clients |
|----------|-----------------|-------------------|
| GET /api/units | 5000 | 500 |
| POST /api/units/convert | 2000 | 200 |
| POST /api/units/convert/batch | 500 (50K conversions/sec) | 50 |

### Caching Strategy

**Client-Side Caching**:
```http
Cache-Control: public, max-age=3600
ETag: "abc123def456"
Last-Modified: Wed, 29 Nov 2025 12:00:00 GMT
```

**Cache Invalidation**: Units rarely change - 1 hour cache TTL recommended

## Integration Examples

### Example 1: Convert Energy Values (C#)

```csharp
using System.Net.Http;
using System.Net.Http.Json;

public class UnitConversionClient
{
    private readonly HttpClient _httpClient;
    
    public UnitConversionClient(string baseUrl, string accessToken)
    {
        _httpClient = new HttpClient { BaseAddress = new Uri(baseUrl) };
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}");
    }
    
    public async Task<decimal> ConvertAsync(decimal value, string sourceUnit, string targetUnit)
    {
        var request = new
        {
            value,
            sourceUnit,
            targetUnit
        };
        
        var response = await _httpClient.PostAsJsonAsync("/api/units/convert", request);
        response.EnsureSuccessStatusCode();
        
        var result = await response.Content.ReadFromJsonAsync<ConversionResponse>();
        return result.ConvertedValue;
    }
}

// Usage
var client = new UnitConversionClient("https://api.ebase.example.com", accessToken);
var mwhValue = await client.ConvertAsync(1500.0M, "kWh", "MWh");
// Result: 1.5 MWh
```

### Example 2: Batch Conversion (Python)

```python
import requests
import json

class UnitConversionClient:
    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def convert_batch(self, values, source_unit, target_unit):
        url = f"{self.base_url}/api/units/convert/batch"
        payload = {
            "values": values,
            "sourceUnit": source_unit,
            "targetUnit": target_unit
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()["convertedValues"]

# Usage
client = UnitConversionClient("https://api.ebase.example.com", access_token)
kwh_values = [100, 200, 300, 400]
mwh_values = client.convert_batch(kwh_values, "kWh", "MWh")
# Result: [0.1, 0.2, 0.3, 0.4]
```

### Example 3: Validation Before Conversion (JavaScript)

```javascript
async function convertWithValidation(value, sourceUnit, targetUnit) {
    const baseUrl = "https://api.ebase.example.com";
    const headers = {
        "Authorization": `Bearer ${accessToken}`,
        "Content-Type": "application/json"
    };
    
    // Step 1: Validate compatibility
    const validateResponse = await fetch(`${baseUrl}/api/units/validate`, {
        method: "POST",
        headers,
        body: JSON.stringify({ sourceUnit, targetUnit })
    });
    
    const validation = await validateResponse.json();
    
    if (!validation.compatible) {
        throw new Error(`Incompatible units: ${validation.validationRules.reason}`);
    }
    
    // Step 2: Perform conversion
    const convertResponse = await fetch(`${baseUrl}/api/units/convert`, {
        method: "POST",
        headers,
        body: JSON.stringify({ value, sourceUnit, targetUnit })
    });
    
    const result = await convertResponse.json();
    return result.convertedValue;
}

// Usage
try {
    const result = await convertWithValidation(1500, "kWh", "MWh");
    console.log(`Converted: ${result} MWh`);
} catch (error) {
    console.error(`Conversion failed: ${error.message}`);
}
```

## Migration Considerations

### C++ API Compatibility

**Legacy Endpoint Support**: C# API must support existing C++ API contracts

**Mapping Table**:
| C++ Endpoint | C# Endpoint | Status |
|--------------|-------------|--------|
| `/ConvertUnit` | `/api/units/convert` | Supported (legacy alias) |
| `/GetUnitList` | `/api/units` | Supported (legacy alias) |
| `/ValidateConversion` | `/api/units/validate` | Supported (legacy alias) |

**Transition Strategy**:
1. Deploy C# API alongside C++ API
2. Configure API gateway to route requests based on version header
3. Migrate clients incrementally to new endpoints
4. Deprecate legacy endpoints after 12-month transition period

### Behavioral Preservation

**Critical Requirements**:
- Conversion results must match C++ API exactly (same precision)
- Error message formats must match for client compatibility
- Response times must meet or exceed C++ performance
- Rate limiting behavior must be equivalent

**Validation Tests**:
```csharp
[Test]
public async Task ConversionResults_MustMatchCppApi()
{
    // Test against known C++ API results
    var cppResult = 1.5M; // kWh → MWh conversion result from C++ API
    var csharpResult = await _client.ConvertAsync(1500.0M, "kWh", "MWh");
    
    Assert.AreEqual(cppResult, csharpResult, 0.000000001M,
        "C# API conversion result must match C++ API result");
}
```

## Related Documentation

- **Business Rules**: [Unit Conversion Business Rules](../business-rules/unit-conversion-business-rules.md) for conversion logic
- **Domain Model**: [MeasurementUnit Domain Object](../domain/domain-objects/measurement-unit-domain-object.md) for data structures
- **Database Schema**: [Units Database Schema](../database/units-database-schema.md) for persistence
- **Authentication**: [OAuth 2.0 Integration Guide](../../authentication/oauth-integration.md) for authentication setup
- **API Reference**: [Complete API Specification (OpenAPI)](../api/unit-conversion-openapi.yaml) for machine-readable format

---

**Migration Phase**: 2 - Specification Creation  
**Generated by**: rule.migration.spec-create.v1  
**Source System**: eBase C++ Services API  
**Analyzed Source**: eBase/Services/UnitConversionService.h, external API documentation  
**Created**: 2025-11-29  
**Last Updated**: 2025-11-29  
**Status**: Integration Review Complete  
**Quality Gate**: Passed
