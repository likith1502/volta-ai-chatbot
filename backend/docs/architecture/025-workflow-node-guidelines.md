# 025: Workflow Node Engineering Guidelines

## 1. Naming Conventions

- **Node Class Names**: Must use PascalCase ending with `Node` (e.g., `StartNode`, `LLMNode`, `CustomProcessingNode`).
- **File Names**: Must use snake_case matching class name without redundant prefixes (e.g., `start_node.py`, `llm_node.py`).
- **Node Category**: Must be selected from `WorkflowNodeType` enum (`START`, `END`, `LLM`, `TOOL`, `MEMORY`, `INTENT`, `ENTITY`, `DECISION`, `RESPONSE`, `CUSTOM`).
- **Node ID**: Standard format is `node_<category>_<name>` or lower-snake class name (e.g., `start_node`, `llm_node_v1`).

---

## 2. Folder Conventions

All workflow nodes reside in:
`backend/app/workflow/`
- `base.py`: Base abstract class definitions.
- `metadata.py`: Schemas for metadata, config, capabilities, execution context.
- `node_types.py`: Category enums.
- `exceptions.py`: Node-specific exception hierarchy.
- `registry.py`: Registry implementation.
- `nodes/`: Directory containing all concrete node implementations.

---

## 3. Inheritance Rules

1. Every node MUST inherit from `BaseWorkflowNode`.
2. Do NOT inherit directly from `BaseNode` or `IGraphNode` for workflow nodes (let `BaseWorkflowNode` handle graph compatibility).
3. Do NOT create deep inheritance trees. Prefer flat inheritance under `BaseWorkflowNode` and compose logic via services/helpers.

---

## 4. Lifecycle Hook Usage

- `before_execute(state, context)`: Use for pre-condition checks and input schema validation.
- `execute(state, context)`: Primary node transformation. Must be async. Must return `ConversationState`.
- `after_execute(state, context)`: Use for post-condition checks and output schema validation.
- `on_error(state, error, context)`: Error handler hook. Use for fallback state transformation during failures.

---

## 5. When to Create a New Node

Create a new node when:
- Defining a distinct architectural contract (e.g., a new domain capability like intent routing or memory retrieval).
- The operation requires distinct input/output contracts or distinct capability flags.
- The unit of execution is intended to be independently placed, wired, or visualized in workflow graphs.

---

## 6. When NOT to Create a New Node

Do NOT create a new node when:
- The change is merely a minor parameter variation of an existing node (use `WorkflowNodeConfig` or node arguments instead).
- The operation represents internal business logic belonging in a Service or Domain Repository.
- The operation performs direct database access, payment handling, or external API communication (delegate to dedicated services or tool execution handlers).
- Creating temporary or workflow-specific execution state (runtime state belongs in `ConversationState`).
