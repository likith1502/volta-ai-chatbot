# VOLTA AI Platform — Frontend API Limitations & Discovery Mapping

This document documents existing backend REST capabilities, schema mapping, and limitations discovered during Phase 1 API audit. To adhere to the **No Fake UI Data** and **Backend Freeze** rules, any UI feature that is not supported by an active backend endpoint is rendered as `"Unavailable"` rather than using simulated or mock metrics.

---

## Endpoint Availability & Feature Mapping

| Page / Feature | Endpoint Consumed | Data Exposed | Limitations / Unsupported UI Elements |
| :--- | :--- | :--- | :--- |
| **Dashboard Health** | `GET /api/v1/health` | Overall status, subsystem health, version, environment | None |
| **Dashboard Metrics** | `GET /api/v1/runtime/metrics` | System runtime metrics | Detailed GPU memory usage is `"Unavailable"` |
| **Prompt Studio** | `GET /api/v1/prompt/templates`, `GET /api/v1/prompt/profiles` | Template IDs, profiles, variables, render | Live LLM fine-tuning is `"Unavailable"` |
| **Memory Explorer** | `GET /api/v1/memory/records`, `POST /api/v1/memory/search` | Stored records, metadata, search queries | Vector embeddings visualization is `"Unavailable"` |
| **Tool Explorer** | `GET /api/v1/tools/registered`, `POST /api/v1/tools/execute` | Registered tools, parameters, execution | Tool source code modification is `"Unavailable"` |
| **Graph Studio** | `GET /api/v1/graph_runtime/graphs`, `POST /api/v1/graph_runtime/execute` | Graph definition, node state, execution | Drag-and-drop graph editing is `"Unavailable"` |
| **Agent Studio** | `GET /api/v1/agents`, `GET /api/v1/agents/health` | Registered agents, capabilities, status | Real-time agent websocket stream is `"Unavailable"` |
| **Knowledge Studio** | `GET /api/v1/rag/sources`, `POST /api/v1/rag/query` | RAG sources, query results, retrieval stats | Document file uploading UI is `"Unavailable"` |
| **Integration Studio**| `GET /api/v1/integrations/providers`, `GET /api/v1/integrations/matrix` | 28 registered providers, health, capabilities | Dynamic credential rotation via UI is `"Unavailable"` |
| **Operations Studio** | `GET /api/v1/deployment/environment`, `GET /api/v1/deployment/health` | Environment settings, scaling status, deployment health | Cloud infrastructure auto-scaling controls are `"Unavailable"` |
| **Request History** | `GET /api/v1/runtime/executions` | Execution history, duration, model, status | Raw HTTP payload packet capture is `"Unavailable"` |
| **Error Viewer** | `GET /api/v1/health/liveness` | Platform liveness, error state | System core dump file download is `"Unavailable"` |
