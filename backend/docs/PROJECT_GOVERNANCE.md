# VOLTA AI Chatbot - Project Governance & Decision Framework

## Overview
This document establishes the official governance rules, decision-making framework, code review philosophy, and repository standards for the VOLTA AI Chatbot engineering organization.

---

## 1. Project Philosophy
- **Production-Grade Quality**: Every component must be built for production deployment from day one. No temporary hacks, pseudocode, or unmaintained prototypes.
- **Incremental Architecture**: Features proceed through explicit, documented milestones. We build strong foundations (Infrastructure -> Database -> Repositories -> Models -> AI Core) rather than rushing into business logic.

---

## 2. Architecture Philosophy
- **Clean Layered Architecture**: Strict separation of concerns between HTTP Routers (`app/api/`), Domain Services (`app/services/`), Repositories (`app/repositories/`), and Infrastructure (`app/database/`, `app/cache/`).
- **Composition Over Inheritance**: Utilize composable mixins (`app/database/mixins.py`) to share cross-cutting database capabilities rather than building rigid monolithic parent classes.

---

## 3. Documentation Philosophy
- **Documentation-Driven Development**: Architecture Decision Records (ADRs) capture major design choices, alternatives, and trade-offs before implementation.
- **Living Documentation**: Architectural blueprints under `docs/` are updated alongside code modifications to maintain a single source of truth.

---

## 4. Engineering Standards
- **Python Standard**: Python 3.11+ with explicit type annotations on all function signatures.
- **Code Style**: PEP 8 compliance enforced by Black formatting (88-character line limit).
- **Asynchronous Execution**: 100% async I/O for network, database (`asyncpg`), and caching (`redis-py`) operations.

---

## 5. ADR Process (Architecture Decision Records)
1. **Identify Decision**: When a major technical choice or architectural trade-off arises, create a new ADR.
2. **Use ADR Template**: Copy `docs/architecture/ADR_TEMPLATE.md` to `docs/architecture/XXX-short-title.md`.
3. **Evaluate Options**: Detail at least two viable technical alternatives with advantages and disadvantages.
4. **Peer Review**: Submit the ADR for team review and alignment before beginning implementation.
5. **Index in README**: Add the accepted ADR to the central index in `docs/README.md`.

---

## 6. Code Review Philosophy
- **Small Focused PRs**: Pull requests should focus on a single responsibility or milestone chapter.
- **Zero Breaking Changes**: Infrastructure changes must remain backward-compatible unless authorized by an ADR.
- **Automated Test Gate**: All automated pytest test cases must pass 100% before merging.

---

## 7. Definition of Done (DoD)
A task or milestone chapter is complete **only when**:
1. Code compiles and runs locally without errors.
2. Automated unit and integration tests pass cleanly.
3. Code quality standards (formatting, typing) are verified.
4. Architectural documentation and README files are updated.
5. Production readiness review is verified.

---

## 8. Versioning & Chapter Strategy
To prevent confusion between learning/engineering progression and semantic software releases:
- **Chapters (Chapter 1.1, 2.1, 2.2, etc.)**: Track internal step-by-step engineering progression.
- **Semantic Releases (`v1.0`, `v1.1`, `v2.0`, etc.)**: Track major system milestone releases.

---

## 9. Git Tag & GitHub Release Strategy
- **GitHub Releases**: Major version releases are published using official **GitHub Releases** featuring formatted release notes detailing verified components (e.g. `v1.0 Infrastructure Foundation`).
- **Release Tags**: Git tags (e.g. `v1.0-infrastructure`) anchor official milestone commits in Git history.

---

## 10. Branch Strategy
- **`main`**: Production-ready code only. Tagged with semantic milestone releases.
- **`develop`**: Integration branch for active development.
- **`feature/*`**: Feature branches off `develop` (e.g., `feature/domain-models`).
- **`bugfix/*`**: Bug fix branches off `develop`.
- **`release/*`**: Release candidate staging branches before merging to `main`.
