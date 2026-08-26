import sys
import uuid
import pytest
from app.streaming import (
    AdapterCapabilities,
    BackpressurePolicy,
    DeliveryGuarantee,
    JSONStreamSerializer,
    MessagePackStreamSerializer,
    OverflowStrategy,
    ProtobufStreamSerializer,
    StreamAdapter,
    StreamAdapterError,
    StreamChannel,
    StreamChannelError,
    StreamContext,
    StreamDispatcher,
    StreamEnvelope,
    StreamError,
    StreamFilter,
    StreamHeartbeat,
    StreamHistory,
    StreamManager,
    StreamMessage,
    StreamMetadata,
    StreamMetrics,
    StreamMode,
    StreamPriority,
    StreamRegistry,
    StreamResult,
    StreamSerializationError,
    StreamStatus,
    StreamSubscription,
    StreamType,
    StreamValidationResult,
)


def test_stream_models_and_immutability() -> None:
    """Verify StreamMessage instantiation, UUID generation, priority, and immutability."""
    meta = StreamMetadata(priority=StreamPriority.HIGH, tags=["test"])
    msg = StreamMessage(
        stream_type=StreamType.EVENT,
        workflow_id="wf_stream",
        graph_id="g_stream",
        payload={"data": 123},
        metadata=meta,
    )

    assert isinstance(msg.message_id, uuid.UUID)
    assert msg.stream_type == StreamType.EVENT
    assert msg.metadata.priority == StreamPriority.HIGH
    assert msg.payload == {"data": 123}

    # Verify immutability
    with pytest.raises(Exception):
        msg.workflow_id = "wf_mutated"  # type: ignore


def test_stream_enums_validation_and_history() -> None:
    """Verify StreamPriority, StreamMode, DeliveryGuarantee, OverflowStrategy, StreamValidationResult, and StreamHistory."""
    val_res = StreamValidationResult(is_valid=True, schema_version="1.0")
    assert val_res.is_valid is True

    ctx = StreamContext(replay_mode=StreamMode.LIVE)
    assert ctx.replay_mode == StreamMode.LIVE

    policy = BackpressurePolicy(overflow_strategy=OverflowStrategy.DROP_OLDEST)
    assert policy.overflow_strategy == OverflowStrategy.DROP_OLDEST

    history = StreamHistory()
    rec = history.record_delivery(
        message_id=uuid.uuid4(),
        channel="ch_1",
        adapter="test_adapter",
        delivery_result="success",
    )
    assert rec.channel == "ch_1"
    assert len(history.records) == 1


@pytest.mark.asyncio
async def test_stream_manager_publication_and_subscription() -> None:
    """Verify StreamManager channel lifecycle, subscription, publication, and priority dispatching."""
    mgr = StreamManager()
    mgr.open_stream("ch_live", "Live Channel")

    received_messages = []

    def subscriber_cb(msg: StreamMessage) -> None:
        received_messages.append(msg)

    sub = mgr.subscribe(
        channel_id="ch_live",
        subscriber_id="sub_1",
        callback=subscriber_cb,
        priority=StreamPriority.CRITICAL,
    )

    assert isinstance(sub, StreamSubscription)
    assert sub.subscriber_id == "sub_1"

    msg = StreamMessage(stream_type=StreamType.STATE, payload={"state": "active"})
    pub_res = await mgr.publish("ch_live", msg)

    assert isinstance(pub_res, StreamResult)
    assert pub_res.success is True
    assert pub_res.delivered == 1
    assert len(received_messages) == 1
    assert received_messages[0].payload == {"state": "active"}

    # Pause channel & test dropped publish
    mgr.pause("ch_live")
    paused_res = await mgr.publish("ch_live", msg)
    assert paused_res.success is False
    assert paused_res.skipped == 1

    # Resume channel & test batch publish
    mgr.resume("ch_live")
    batch_res = await mgr.publish_batch("ch_live", [msg, msg])
    assert batch_res.success is True
    assert batch_res.delivered == 2


@pytest.mark.asyncio
async def test_stream_dispatcher_priority_and_error_isolation() -> None:
    """Verify StreamDispatcher executes priority ordering and isolates subscriber callback errors."""
    dispatcher = StreamDispatcher()
    ch = StreamChannel(channel_id="ch_disp", name="Dispatch Channel")

    execution_order = []

    def low_cb(msg: StreamMessage) -> None:
        execution_order.append("low")

    def failing_cb(msg: StreamMessage) -> None:
        execution_order.append("failing")
        raise RuntimeError("Subscriber error!")

    def critical_cb(msg: StreamMessage) -> None:
        execution_order.append("critical")

    sub_low = StreamSubscription(subscriber_id="low", priority=StreamPriority.LOW)
    sub_fail = StreamSubscription(subscriber_id="fail", priority=StreamPriority.HIGH)
    sub_crit = StreamSubscription(subscriber_id="crit", priority=StreamPriority.CRITICAL)

    dispatcher.register_subscriber("ch_disp", sub_low, low_cb)
    dispatcher.register_subscriber("ch_disp", sub_fail, failing_cb)
    dispatcher.register_subscriber("ch_disp", sub_crit, critical_cb)

    msg = StreamMessage(stream_type=StreamType.EVENT)
    res = await dispatcher.dispatch(ch, msg)

    # Critical executed first, then failing (high), then low
    assert execution_order == ["critical", "failing", "low"]
    assert res.delivered == 2
    assert len(res.errors) == 1
    assert res.errors[0]["subscriber_id"] == "fail"


def test_stream_filter_matching() -> None:
    """Verify StreamFilter predicate matching rules."""
    msg = StreamMessage(
        stream_type=StreamType.METRICS,
        workflow_id="wf_filter",
        metadata=StreamMetadata(priority=StreamPriority.HIGH, tags=["telemetry"]),
    )

    flt_pass = StreamFilter(stream_types=[StreamType.METRICS], workflow_id="wf_filter", min_priority=StreamPriority.NORMAL)
    assert flt_pass.matches(msg) is True

    flt_fail_type = StreamFilter(stream_types=[StreamType.CHECKPOINT])
    assert flt_fail_type.matches(msg) is False

    flt_fail_priority = StreamFilter(min_priority=StreamPriority.CRITICAL)
    assert flt_fail_priority.matches(msg) is False


def test_stream_serializers() -> None:
    """Verify JSONStreamSerializer roundtrip and MessagePack/Protobuf contracts."""
    msg = StreamMessage(stream_type=StreamType.LOG, payload={"log": "test"})

    json_serializer = JSONStreamSerializer()
    data = json_serializer.serialize(msg)
    assert isinstance(data, bytes)

    deserialized = json_serializer.deserialize(data)
    assert deserialized.message_id == msg.message_id
    assert deserialized.payload == {"log": "test"}

    # Placeholder contracts
    msgpack_serializer = MessagePackStreamSerializer()
    assert isinstance(msgpack_serializer.serialize(msg), bytes)

    proto_serializer = ProtobufStreamSerializer()
    assert isinstance(proto_serializer.serialize(msg), bytes)


def test_stream_registry() -> None:
    """Verify StreamRegistry register, lookup, unregister, and factory support."""
    registry = StreamRegistry()

    class DummyAdapter(StreamAdapter):
        async def connect(self) -> None: pass
        async def disconnect(self) -> None: pass
        async def send(self, message: StreamMessage) -> bool: return True
        async def flush(self) -> None: pass
        async def heartbeat(self) -> StreamHeartbeat: return StreamHeartbeat()

    registry.register_adapter(DummyAdapter, adapter_id="dummy")
    assert registry.exists("dummy") is True

    adapter = registry.lookup("dummy")
    assert isinstance(adapter, DummyAdapter)
    assert isinstance(adapter.capabilities, AdapterCapabilities)

    registry.unregister("dummy")
    assert registry.exists("dummy") is False


def test_exception_hierarchy() -> None:
    """Verify streaming exception hierarchy inheritance."""
    assert issubclass(StreamChannelError, StreamError)
    assert issubclass(StreamAdapterError, StreamError)
    assert issubclass(StreamSerializationError, StreamError)


def test_import_isolation_and_no_framework_leakage() -> None:
    """Verify app.streaming modules do not import forbidden framework dependencies, DB layers, or Redis."""
    forbidden_modules = [
        "fastapi",
        "starlette",
        "websockets",
        "socketio",
        "redis",
        "kafka",
        "rabbitmq",
        "grpc",
        "opentelemetry",
        "prometheus",
        "sqlalchemy",
        "app.db",
        "app.repositories",
        "app.services",
        "app.api",
    ]

    import app.streaming as str_mod

    for mod_name in sys.modules:
        if mod_name.startswith("app.streaming"):
            mod = sys.modules[mod_name]
            mod_file = getattr(mod, "__file__", "")
            if mod_file:
                with open(mod_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    for forbidden in forbidden_modules:
                        assert forbidden not in content, f"Forbidden dependency '{forbidden}' found in {mod_name}!"
