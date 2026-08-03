# ADR 002: Modular Project Structure & Layered Architecture

## Status
Accepted

## Date
2026-08-03

## Context
As an enterprise AI Chatbot backend with multiple domain components (Conversation, Intent, Entity, Context, Memory, Booking, Recommendation), a flat or monolithic structure leads to tight coupling, poor testability, and circular imports.

## Decision
We adopted a **Modular Layered Architecture** under `backend/app/` where every domain feature resides in its own isolated module package containing clear responsibilities. Top-level operational directories (`tests/`, `migrations/`, `scripts/`, `logs/`, `docs/`) remain cleanly separated outside `app/`.

## Alternatives Considered
1. **Flat File Structure**: All models, schemas, and routes in single top-level files (`models.py`, `routes.py`). Unusable for large team collaboration.
2. **Framework-Centric Directory Layout**: Grouping strictly by layer (`controllers/`, `views/`, `models/`). Forces developers to touch multiple unrelated folders for a single domain feature.

## Consequences
- **Positive**: Clean separation of concerns, high modularity, simplified unit testing, strict scoping of business logic, prevention of circular dependency loops.
- **Negative**: Requires maintaining multiple `__init__.py` files and strict import paths.

## Future Review
Review modular boundaries when expanding to multi-repo microservices if domain modules require independent deployment.
