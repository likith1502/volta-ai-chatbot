# API Response Envelope Standard & Migration Strategy

## Overview
This document specifies the response payload standard for all public HTTP APIs in the VOLTA AI Chatbot backend. Establishing a unified response envelope simplifies client integration (such as `testing-ui` and future mobile clients) and ensures deterministic error handling across all endpoints.

---

## 1. Current Response Format

### Success Response Envelope
```json
{
  "success": true,
  "message": "V1 Health check successful",
  "data": {
    "status": "healthy",
    "application": "VOLTA AI Chatbot",
    "version": "0.1.0",
    "environment": "development"
  },
  "errors": null
}
```

### Error Response Envelope
```json
{
  "success": false,
  "message": "Validation Error",
  "data": null,
  "errors": [
    {
      "loc": ["query", "page"],
      "msg": "Input should be a valid integer",
      "type": "int_type"
    }
  ]
}
```

---

## 2. Future Strongly-Typed Response Models

In future phases, response payloads will be backed by generic Pydantic models defined under `app/schemas/`:

```python
# Conceptual representation (to be implemented in future schema phases)
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class ResponseEnvelope(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    errors: Optional[Any] = None
```

---

## 3. Key Advantages
- **Automatic OpenAPI Documentation**: Strongly typed models generate exact TypeScript interfaces in OpenAPI client generators.
- **Type Safety**: FastAPI routes benefit from full static type checking when returning complex response bodies.
- **Client Predictability**: Consuming applications can depend on a consistent top-level JSON structure regardless of the underlying domain module.

---

## 4. Migration Strategy
1. **Phase 1 (Completed)**: Foundation response helper functions (`success_response`, `error_response`) operating with dynamic dict payloads.
2. **Phase 2 (Upcoming - Schemas Module)**: Formalize `ResponseEnvelope[T]` in `app/schemas/base_response.py`.
3. **Phase 3 (Domain Integration)**: Wrap domain specific response schemas (e.g. `BookingResponse`, `IntentResult`) inside `ResponseEnvelope[T]`.
