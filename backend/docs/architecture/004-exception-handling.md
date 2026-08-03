# ADR 004: Centralized Application Exception Handling

## Status
Accepted

## Date
2026-08-03

## Context
Unhandled exceptions or inconsistent error payloads across different endpoints create security vulnerabilities (leaking stack traces) and complicate client-side error handling.

## Decision
We established a **Centralized Global Exception Interceptor** mechanism using FastAPI exception handlers. All domain errors, validation failures, HTTP errors, and unhandled internal exceptions are transformed into a uniform JSON response envelope:
`{"success": false, "message": "...", "data": null, "errors": ...}`.

## Alternatives Considered
1. **Ad-Hoc Try-Except in Route Handlers**: Leads to code duplication, inconsistent error responses, and risk of missing unhandled exceptions.
2. **Standard FastAPI Default Exception Handlers**: Works out of the box but returns varying payload formats for HTTP versus validation errors.

## Consequences
- **Positive**: Consistent client error experience, internal stack trace logging without exposing raw errors to API consumers, clean domain exception triggering via `AppException`.
- **Negative**: Requires all custom application exceptions to inherit from `AppException`.

---

## Planned Future Exception Hierarchy
As business modules are added in future milestones, `app/core/exceptions.py` will be extended with the following structured exception tree:

```
AppException (Base Application Exception)
├── DomainException
│   ├── NotFoundException (HTTP 404)
│   ├── ValidationException (HTTP 422)
│   ├── UnauthorizedException (HTTP 401)
│   ├── ForbiddenException (HTTP 403)
│   └── ConflictException (HTTP 409)
└── InfrastructureException
    ├── DatabaseException (HTTP 500)
    ├── CacheException (HTTP 500)
    └── ExternalServiceException (HTTP 502 / 503)
```

## Future Review
Review error code taxonomy when adding localized multi-language error message payloads.
