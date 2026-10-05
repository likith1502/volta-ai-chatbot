# ADR 039: Prompt Engineering Guidelines & Extension Standards

## Status
Accepted

## Date
2026-08-07

## Context
As Phase 7 expands into memory runtimes, tool runtimes, multi-agent frameworks, and RAG engines, clear prompt engineering guidelines are required to ensure consistent variable interpolation, template inheritance, security sanitization, and linting.

## Guidelines & Rules

### 1. Template Authoring Rules
- Every template MUST extend `BasePromptTemplate` (`app/prompt/templates/base_template.py`).
- Placeholder syntax MUST use curly braces `{variable_name}`.
- Required variables MUST be declared in the template's `variables` list.
- Templates SHOULD specify a `parent_template_id` if inheriting common system instructions.

### 2. PromptProfile Separation
- Do NOT hardcode generation parameters (temperature, max tokens, model) inside prompt templates.
- Use `PromptProfile` objects to encapsulate generation behavior.

### 3. Prompt Linter & Security Standards
- System instructions SHOULD NOT exceed 2000 characters.
- Variables containing potential prompt injection patterns (e.g. "ignore previous instructions") MUST be flagged by `PromptSecurityPolicy` and `SecurityMiddleware`.

### 4. Extension Hooks
- Custom pre/post processing MUST be attached via extension hooks (`PreRenderHook`, `PostRenderHook`, `PreExecutionHook`, `PostExecutionHook`) in `app/prompt/hooks.py`.
