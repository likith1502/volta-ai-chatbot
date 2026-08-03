# ADR 003: URI Path API Versioning Strategy

## Status
Accepted

## Date
2026-08-03

## Context
As API contracts evolve across client versions (`testing-ui`, mobile applications, third-party partner integrations), breaking changes must be managed without disrupting existing active clients.

## Decision
We adopted explicit **URI Path Versioning** under `/api/v1/`. All versioned endpoints are grouped in `app/api/v1/` and exposed through `api_v1_router`.

## Alternatives Considered
1. **Header-Based Versioning (`Accept-Version: v1`)**: Clean URLs, but harder to test in standard web browsers and cache proxies.
2. **Query Parameter Versioning (`?version=1`)**: Prone to missing parameters and caching collisions on edge CDN networks.
3. **No Versioning**: Causes breaking changes to immediately crash older active clients.

## Consequences
- **Positive**: Explicit, human-readable route versioning, clear deprecation path for future versions (`/api/v2/`), seamless proxy routing.
- **Negative**: Requires maintaining parallel version routers during major version migrations.

## Future Review
Review upon design of `/api/v2/` endpoints during major feature additions.
