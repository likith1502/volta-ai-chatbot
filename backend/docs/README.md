# VOLTA AI Chatbot - Backend Technical Documentation Hub

Welcome to the central technical documentation hub for the VOLTA AI Chatbot backend platform. This directory serves as the engineering knowledge base, containing architectural decision records (ADRs), system design blueprints, project milestones, governance rules, database constitutions, and coding standards.

---

## Core Governance & Status Documents

- 📘 [Project Governance Framework](PROJECT_GOVERNANCE.md): Decision-making rules, ADR processes, code review philosophy, and git strategies.
- 🎯 [Project Milestones & Roadmap](PROJECT_MILESTONES.md): Official status, completion dates, and roadmap versions across all development phases.
- 🔒 [Foundation Lock Status Record](FOUNDATION_STATUS.md): Official lock records for Infrastructure Foundation v1.0 and Database Base Mixins v1.1.

---

## Architecture Documents & ADR Index

- [ADR Template](architecture/ADR_TEMPLATE.md): Standard template for writing new Architecture Decision Records.
- [001 - FastAPI Framework Adoption](architecture/001-fastapi-framework.md)
- [002 - Modular Project Structure & Layered Architecture](architecture/002-project-structure.md)
- [003 - URI Path API Versioning Strategy](architecture/003-api-versioning.md)
- [004 - Centralized Application Exception Handling](architecture/004-exception-handling.md)
- [005 - Code Quality & Static Analysis Roadmap](architecture/005-code-quality-roadmap.md)
- [006 - API Response Envelope Standard](architecture/006-api-response-standard.md)
- [007 - Milestone 2 Infrastructure Implementation Plan](architecture/007-milestone-2-plan.md)
- [008 - Architectural Plan: Future Database Mixins](architecture/008-future-database-mixins.md)
- [009 - Database Request Flow Architecture](architecture/009-database-request-flow.md)
- [010 - Alembic Database Migration Strategy](architecture/010-alembic-migration-strategy.md)
- [011 - Infrastructure Foundation Lock Record](architecture/011-infrastructure-lock.md)
- [012 - Domain Modeling Guidelines](architecture/012-domain-modeling-guidelines.md)
- [013 - Model Inheritance Strategy & Composable Mixins](architecture/013-model-inheritance-strategy.md)
- [014 - ORM Relationship & Cascade Strategy](architecture/014-relationship-strategy.md)
- [015 - Database Enum Strategy & Migration Governance](architecture/015-enum-strategy.md)

---

## Architecture Decision Records (ADR Index)
ADRs capture significant architectural choices, context, alternatives evaluated, and long-term consequences:

| ADR ID | Title | Status | Date |
| :--- | :--- | :--- | :--- |
| **ADR 001** | Adoption of FastAPI Web Framework | Accepted | 2026-08-03 |
| **ADR 002** | Modular Project Structure & Layered Architecture | Accepted | 2026-08-03 |
| **ADR 003** | URI Path API Versioning Strategy | Accepted | 2026-08-03 |
| **ADR 004** | Centralized Application Exception Handling | Accepted | 2026-08-03 |
| **ADR 013** | Model Inheritance Strategy & Composable Mixins | Accepted | 2026-08-03 |
| **ADR 014** | ORM Relationship & Cascade Strategy | Accepted | 2026-08-03 |
| **ADR 015** | Database Enum Strategy & Migration Governance | Accepted | 2026-08-03 |

---

## Technical Constitutions & Sub-Directories

### 🗄️ [Database Documentation](database/README.md)
- [Domain Models Specification](database/database-models.md)
- [Entity Relationship (ER) Blueprint](database/entity-relationship.md)
- [Relationship & Loading Guidelines](database/relationship-guidelines.md)
- [Database Base Mixins Architecture](database/database-mixins.md)
- [Database Design Principles](database/database-design-principles.md)
- [Database Request & Migration Architecture](database/database-architecture.md)

### 🛠️ [Engineering Documentation](engineering/README.md)
- [Engineering Principles & Constitution](engineering/engineering-principles.md)
- [Official Project Standards](engineering/project-standards.md)

### 🌐 [API Documentation](api/README.md)
- OpenAPI specs, versioning contracts (`/api/v1/`), and payload standards.

### 🚀 [Deployment Documentation](deployment/README.md)
- Deployment runbooks, container specs, and release guidelines.
