# VOLTA AI Platform — Modern Production Admin Console

Enterprise-grade, production-ready administration console for the VOLTA AI Platform built with **React 18, TypeScript, Vite, Tailwind CSS, React Router v7, and TanStack Query v5**.

---

## 🚀 Key Features

1. **Executive Administration Dashboard**: Real-time status cards, system health overview, subsystem operational statuses, and active integration provider counts.
2. **Dedicated Studio Pages**:
   - **Prompt Studio**: Inspect templates, profiles, render parameters, and variable payloads.
   - **Memory Explorer**: Search memory records, inspect short-term/long-term/session state repositories.
   - **Tool Explorer**: Inspect registered tool definitions, capabilities, and execute tool pipelines.
   - **Graph Studio**: Graph State Runtime workflow runner, state transitions, and node metrics.
   - **Agent Studio**: Multi-Agent Runtime agents, team roles, supervisor orchestration, and telemetry.
   - **Knowledge Studio**: RAG knowledge sources, document chunking, semantic retrieval, and reranking.
   - **Integration Studio**: 28 registered production integration adapters across 8 categories with category filters, capability matrix, and audit log.
   - **Operations Studio**: Deployment operations, scaling status, environment configuration, and release health.
   - **Request History**: Audit execution requests, duration, model parameters, and runtime execution logs.
   - **Error Viewer**: System errors, liveness failures, and exception metadata.
3. **No Fake Data Policy**: Every displayed metric and status is strictly driven by live backend REST API responses. If an endpoint metric is unavailable, it renders an explicit `"Unavailable"` status badge rather than fabricated data.
4. **Recursive Secret Redaction Engine**: Automatic masking (`sk-***`) for sensitive fields (`password`, `secret`, `api_key`, `token`, `connection_string`, etc.) inside tables and the `JsonInspector` component.
5. **API Failure Isolation**: Subsystems fail independently using React `ErrorBoundary` and TanStack Query error state without breaking the rest of the application.
6. **Theme Switcher**: Dark mode, light mode, and system preference persistence.
7. **Legacy Migration Safety**: The legacy developer testing console `testing-ui/` remains active and mounted at `/console`.

---

## 🛠️ Development & Production Scripts

From the `frontend/` directory:

```bash
# Start Vite development server with proxy to backend (http://127.0.0.1:8000)
npm run dev

# Run Vitest unit & integration tests
npm run test

# Run TypeScript compilation lint check
npm run lint

# Build production bundle with code splitting and lazy loading
npm run build

# Preview production build locally
npm run preview
```

---

## 📁 Architecture Overview

```text
frontend/
├── dist/                     # Optimized production bundle
├── public/
├── src/
│   ├── api/                  # Typed REST API modules (Axios client)
│   ├── components/
│   │   ├── common/           # Badge, Card, Skeleton, Button, Modal
│   │   ├── feedback/        # EmptyState, ErrorBoundary
│   │   ├── inspector/        # JsonInspector with secret redaction & search
│   │   └── layout/           # Sidebar, Header, Breadcrumbs
│   ├── hooks/                # useTheme, usePermission, usePolling
│   ├── pages/                # Lazy-loaded Studio pages
│   ├── types/                # TypeScript interface definitions
│   ├── utils/                # Secret redaction, formatters
│   ├── App.tsx               # Lazy router & QueryClientProvider
│   └── main.tsx
├── vitest.config.ts
├── vite.config.ts
└── package.json
```
