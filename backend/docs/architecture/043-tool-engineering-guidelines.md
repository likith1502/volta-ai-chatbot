# ADR 043: Tool Engineering Guidelines & Extension Standards

## Status
Accepted

## Date
2026-08-07

## Context
As Phase 7 advances into Graph Runtime Integration, Multi-Agent Runtime, and RAG Engine, clear tool engineering standards are required for tool creation, JSON schema specifications, security permissions, execution policies, and pipeline integration.

## Guidelines & Rules

### 1. Tool Creation & Subclassing
- All concrete tools MUST inherit from `BaseTool` in `app/tools/tool.py`.
- Every tool MUST specify a valid `ToolType` (`SYSTEM`, `UTILITY`, `MATH`, `TIME`, `TEXT`, `FILE`, `NETWORK`, `SEARCH`, `CUSTOM`).

### 2. Schema Specification Rules
- Every tool MUST define a valid `input_schema` dict complying with standard JSON Schema.
- Tool input arguments MUST be validated by `ToolValidator` before execution.

### 3. Security & Policy Enforcement
- Tools requiring elevated privileges MUST specify `required_permission` in `ToolManifest`.
- Execution timeouts, retries, and rate limits MUST be configured via `ToolPolicy`.

### 4. Integration Standards
- Concrete external API integrations (Google, Slack, GitHub, Database connectors) MUST be placed inside `backend/app/tools/adapters/`.
- Inter-layer communications MUST use public contracts (`ToolRequest`, `ToolResult`, `ToolManifest`).
