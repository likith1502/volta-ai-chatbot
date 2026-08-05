# 033: Streaming & Real-Time Engineering Guidelines

## 1. Message Immutability & Naming Rules

1. **Strict Immutability**: `StreamMessage` models are frozen (`frozen=True`). Once created, a stream message MUST NOT be mutated.
2. **Stream Priority**: Enforce explicit `StreamPriority` enum values (`CRITICAL`, `HIGH`, `NORMAL`, `LOW`, `BACKGROUND`).
3. **Stream Types**: Categorize messages using `StreamType` (`EVENT`, `STATE`, `EXECUTION`, `CHECKPOINT`, `METRICS`, `LOG`, `SYSTEM`, `HEARTBEAT`, `CUSTOM`).

---

## 2. Transport Independence & Adapter Rules

1. **Zero Third-Party Coupling**: The core `app.streaming` module MUST NOT import FastAPI, Starlette, WebSockets, Redis, Kafka, or RabbitMQ.
2. **Adapter Contracts**: Implement custom transport adapters by inheriting from `StreamAdapter` and declaring supported capabilities via `AdapterCapabilities`.
3. **Serialization Isolation**: Payload serialization MUST implement the `StreamSerializer` abstract interface (`JSONStreamSerializer`, `MessagePackStreamSerializer`, `ProtobufStreamSerializer`).

---

## 3. Failure Isolation & Dispatching

1. **Subscriber Protection**: `StreamDispatcher` MUST wrap subscriber callbacks in try/except blocks. An exception in one subscriber callback MUST be captured in `StreamResult.errors` and MUST NOT disrupt other subscribers.
2. **Priority Ordering**: Dispatching MUST process subscribers in descending priority order (`CRITICAL` -> `HIGH` -> `NORMAL` -> `LOW` -> `BACKGROUND`).
