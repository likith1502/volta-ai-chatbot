import sys
import uuid
import pytest
from app.events import (
    DuplicateEventError,
    DuplicateListenerError,
    EventDispatchError,
    EventEnvelope,
    EventListenerNotFoundError,
    EventPriority,
    EventSerializationError,
    EventSubscription,
    JSONEventSerializer,
    MessagePackEventSerializer,
    ProtobufEventSerializer,
    WorkflowEvent,
    WorkflowEventBus,
    WorkflowEventCategory,
    WorkflowEventDispatcher,
    WorkflowEventError,
    WorkflowEventFilter,
    WorkflowEventListener,
    WorkflowEventMetadata,
    WorkflowEventMetrics,
    WorkflowEventRegistry,
    WorkflowEventResult,
    WorkflowEventStatus,
    WorkflowEventType,
)


class MockTestListener(WorkflowEventListener):
    """Mock listener for testing event dispatching."""

    received_events: list[WorkflowEvent] = []

    async def on_event(self, event: WorkflowEvent) -> None:
        self.received_events.append(event)


class FailingTestListener(WorkflowEventListener):
    """Mock listener that raises an error during on_event."""

    error_called: bool = False

    async def on_event(self, event: WorkflowEvent) -> None:
        raise ValueError("Listener failure")

    async def on_error(self, event: WorkflowEvent, error: Exception) -> None:
        self.error_called = True


def test_event_creation_and_immutability() -> None:
    """Verify WorkflowEvent instantiation, UUID generation, categories, and immutability."""
    meta = WorkflowEventMetadata(priority=EventPriority.HIGH, tags=["test"])
    evt = WorkflowEvent(
        event_type=WorkflowEventType.NODE_STARTED,
        category=WorkflowEventCategory.NODE,
        workflow_id="wf_123",
        node_id="node_1",
        metadata=meta,
    )

    assert isinstance(evt.event_id, uuid.UUID)
    assert evt.event_type == WorkflowEventType.NODE_STARTED
    assert evt.category == WorkflowEventCategory.NODE
    assert evt.metadata.priority == EventPriority.HIGH

    # Immutability check
    with pytest.raises(Exception):
        evt.workflow_id = "wf_456"  # type: ignore


def test_event_envelope_and_subscription() -> None:
    """Verify EventEnvelope transport wrapper and EventSubscription metadata."""
    evt = WorkflowEvent(event_type=WorkflowEventType.EXECUTION_STARTED)
    envelope = EventEnvelope(event=evt, headers={"Content-Type": "application/json"})

    assert envelope.event == evt
    assert envelope.headers["Content-Type"] == "application/json"
    assert envelope.serialization_format == "json"

    listener = MockTestListener(listener_id="l_1")
    sub = EventSubscription(listener=listener, priority=EventPriority.CRITICAL)
    assert sub.listener == listener
    assert sub.priority == EventPriority.CRITICAL
    assert sub.enabled is True


@pytest.mark.asyncio
async def test_event_bus_and_dispatcher_flow() -> None:
    """Verify WorkflowEventBus publish, subscription, and listener notification flow."""
    bus = WorkflowEventBus()
    listener = MockTestListener(listener_id="l_bus", received_events=[])

    bus.subscribe(listener)
    assert bus.exists("l_bus") is True

    evt = WorkflowEvent(
        event_type=WorkflowEventType.EXECUTION_COMPLETED,
        category=WorkflowEventCategory.EXECUTION,
    )

    res = await bus.publish(evt)
    assert res.success is True
    assert res.processed == 1
    assert len(listener.received_events) == 1
    assert listener.received_events[0] == evt

    bus.clear()
    assert len(bus.list_subscribers()) == 0


@pytest.mark.asyncio
async def test_listener_priority_ordering() -> None:
    """Verify subscribers are ordered by priority (CRITICAL -> HIGH -> NORMAL -> LOW)."""
    registry = WorkflowEventRegistry()

    l_low = MockTestListener(listener_id="low", priority=EventPriority.LOW)
    l_crit = MockTestListener(listener_id="crit", priority=EventPriority.CRITICAL)
    l_norm = MockTestListener(listener_id="norm", priority=EventPriority.NORMAL)

    registry.register(l_low)
    registry.register(l_crit)
    registry.register(l_norm)

    subs = registry.list_subscribers()
    assert [s.listener.listener_id for s in subs] == ["crit", "norm", "low"]


@pytest.mark.asyncio
async def test_listener_error_isolation() -> None:
    """Verify error in one listener does not prevent other listeners from receiving event."""
    dispatcher = WorkflowEventDispatcher()

    l_ok = MockTestListener(listener_id="ok", received_events=[])
    l_fail = FailingTestListener(listener_id="fail")

    sub_ok = EventSubscription(listener=l_ok)
    sub_fail = EventSubscription(listener=l_fail)

    evt = WorkflowEvent(event_type=WorkflowEventType.NODE_FAILED)
    res = await dispatcher.dispatch(evt, [sub_fail, sub_ok])

    assert res.processed == 1
    assert len(res.errors) == 1
    assert res.errors[0]["listener_id"] == "fail"
    assert l_fail.error_called is True
    assert len(l_ok.received_events) == 1


def test_event_filter_matching() -> None:
    """Verify WorkflowEventFilter predicate matching by category, event_type, and priority."""
    filter_node = WorkflowEventFilter(
        categories=[WorkflowEventCategory.NODE],
        event_types=[WorkflowEventType.NODE_STARTED],
        min_priority=EventPriority.NORMAL,
    )

    evt_match = WorkflowEvent(
        event_type=WorkflowEventType.NODE_STARTED,
        category=WorkflowEventCategory.NODE,
        metadata=WorkflowEventMetadata(priority=EventPriority.HIGH),
    )

    evt_mismatch_type = WorkflowEvent(
        event_type=WorkflowEventType.NODE_COMPLETED,
        category=WorkflowEventCategory.NODE,
    )

    evt_mismatch_priority = WorkflowEvent(
        event_type=WorkflowEventType.NODE_STARTED,
        category=WorkflowEventCategory.NODE,
        metadata=WorkflowEventMetadata(priority=EventPriority.LOW),
    )

    assert filter_node.matches(evt_match) is True
    assert filter_node.matches(evt_mismatch_type) is False
    assert filter_node.matches(evt_mismatch_priority) is False


def test_json_and_contract_serializers() -> None:
    """Verify JSONEventSerializer serialization and deserialization."""
    serializer = JSONEventSerializer()
    evt = WorkflowEvent(
        event_type=WorkflowEventType.STATE_UPDATED,
        category=WorkflowEventCategory.STATE,
        payload={"key": "val"},
    )

    serialized = serializer.serialize(evt)
    assert isinstance(serialized, str)
    assert "state_updated" in serialized

    deserialized = serializer.deserialize(serialized)
    assert deserialized.event_id == evt.event_id
    assert deserialized.event_type == evt.event_type
    assert deserialized.payload == {"key": "val"}

    # Placeholders
    msgpack_ser = MessagePackEventSerializer()
    proto_ser = ProtobufEventSerializer()
    assert msgpack_ser.serialize(evt) is not None
    assert proto_ser.serialize(evt) is not None


def test_registry_crud_and_factory() -> None:
    """Verify registry register, register_factory, unregister, duplicate exception, and lookup."""
    registry = WorkflowEventRegistry()

    def factory() -> WorkflowEventListener:
        return MockTestListener(listener_id="lazy_l")

    registry.register_factory("lazy_l", factory)
    assert registry.exists("lazy_l") is True

    sub = registry.lookup("lazy_l")
    assert sub.listener.listener_id == "lazy_l"

    with pytest.raises(DuplicateListenerError):
        registry.register_factory("lazy_l", factory)

    registry.unregister("lazy_l")
    assert registry.exists("lazy_l") is False

    with pytest.raises(EventListenerNotFoundError):
        registry.lookup("lazy_l")


def test_exception_hierarchy() -> None:
    """Verify exception hierarchy inheritance."""
    assert issubclass(DuplicateEventError, WorkflowEventError)
    assert issubclass(DuplicateListenerError, WorkflowEventError)
    assert issubclass(EventListenerNotFoundError, WorkflowEventError)
    assert issubclass(EventDispatchError, WorkflowEventError)
    assert issubclass(EventSerializationError, WorkflowEventError)


def test_import_isolation_and_no_framework_leakage() -> None:
    """Verify app.events modules do not import forbidden framework dependencies or messaging brokers."""
    forbidden_modules = [
        "sqlalchemy",
        "redis",
        "kafka",
        "rabbitmq",
        "opentelemetry",
        "prometheus",
        "grafana",
        "websockets",
        "langgraph",
        "openai",
        "app.db",
        "app.repositories",
        "app.services",
        "app.api",
    ]

    import app.events as ev_mod

    for mod_name in sys.modules:
        if mod_name.startswith("app.events"):
            mod = sys.modules[mod_name]
            mod_file = getattr(mod, "__file__", "")
            if mod_file:
                with open(mod_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    for forbidden in forbidden_modules:
                        assert forbidden not in content, f"Forbidden dependency '{forbidden}' found in {mod_name}!"
