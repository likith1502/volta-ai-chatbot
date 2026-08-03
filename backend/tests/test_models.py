import uuid
from sqlalchemy import UUID, Enum
from app.database.base import Base
from app.models import (
    AuditLog,
    Booking,
    BookingStatus,
    Conversation,
    ConversationSource,
    ConversationStatus,
    Entity,
    Intent,
    Memory,
    MemoryType,
    Message,
    MessageRole,
    Notification,
    NotificationType,
    Recommendation,
    RecommendationStatus,
    User,
)


def test_models_metadata_registration():
    """Verify all 10 domain models are registered in Base.metadata."""
    tables = Base.metadata.tables.keys()
    expected_tables = [
        "users",
        "conversations",
        "messages",
        "memories",
        "intents",
        "entities",
        "recommendations",
        "bookings",
        "notifications",
        "audit_logs",
    ]
    for table_name in expected_tables:
        assert table_name in tables


def test_user_model_structure_and_indexes():
    """Verify User model columns, mixins, indexes, and constraints."""
    table = Base.metadata.tables["users"]
    cols = table.columns

    assert isinstance(cols["id"].type, UUID)
    assert cols["id"].primary_key is True
    assert cols["email"].unique is True
    assert cols["phone_number"].index is True
    assert "created_at" in cols
    assert "is_deleted" in cols
    assert "created_by" in cols


def test_audit_log_event_metadata_renaming():
    """Verify AuditLog defines event_metadata and NOT reserved metadata attribute."""
    table = Base.metadata.tables["audit_logs"]
    cols = table.columns

    assert "id" in cols
    assert "created_at" in cols
    assert "is_deleted" not in cols
    assert "event_type" in cols
    assert "event_metadata" in cols
    assert hasattr(AuditLog, "event_metadata")
    assert AuditLog.metadata == Base.metadata


def test_foreign_key_constraints_and_cascades():
    """Verify explicit Foreign Keys and cascade delete directives."""
    conversations = Base.metadata.tables["conversations"]
    user_fk = list(conversations.foreign_keys)[0]
    assert user_fk.column.table.name == "users"
    assert user_fk.ondelete == "CASCADE"

    messages = Base.metadata.tables["messages"]
    conv_fk = list(messages.foreign_keys)[0]
    assert conv_fk.column.table.name == "conversations"
    assert conv_fk.ondelete == "CASCADE"

    bookings = Base.metadata.tables["bookings"]
    rec_fk = list(bookings.foreign_keys)[0]
    assert rec_fk.column.table.name == "recommendations"
    assert rec_fk.ondelete == "SET NULL"
    assert bookings.columns["recommendation_id"].nullable is True


def test_enum_mappings_and_defaults():
    """Verify Enum column types, defaults, and Python enum values."""
    conv_table = Base.metadata.tables["conversations"]
    status_col = conv_table.columns["status"]
    source_col = conv_table.columns["source"]

    assert isinstance(status_col.type, Enum)
    assert status_col.default.arg == ConversationStatus.ACTIVE
    assert isinstance(source_col.type, Enum)
    assert source_col.default.arg == ConversationSource.WEB

    conv = Conversation(
        user_id=uuid.uuid4(),
        session_id="sess_12345",
        status=ConversationStatus.ACTIVE,
        source=ConversationSource.WEB,
    )
    assert conv.source == ConversationSource.WEB

    mem = Memory(
        conversation_id=uuid.uuid4(),
        memory_key="user_name",
        memory_value="John",
        memory_type=MemoryType.EPISODIC,
    )
    assert mem.memory_type == MemoryType.EPISODIC


def test_ai_readiness_fields_and_relationships():
    """Verify AI readiness attributes and relationship bindings across models."""
    user_id = uuid.uuid4()
    user = User(id=user_id, full_name="Jane Doe", email="jane@example.com")
    conv = Conversation(user_id=user_id, session_id="sess_abc", user=user)

    msg = Message(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="Book a ride to airport",
        sequence_number=1,
        processing_time_ms=150,
        model_used="gemini-1.5-pro",
        conversation=conv,
    )

    intent = Intent(
        conversation_id=conv.id,
        intent_name="book_ride",
        confidence_score=0.98,
        model_version="v1.2",
        conversation=conv,
    )

    entity = Entity(
        intent_id=intent.id,
        entity_type="destination",
        entity_value="Airport",
        confidence_score=0.99,
        intent=intent,
    )

    rec = Recommendation(
        conversation_id=conv.id,
        recommendation_type="ride",
        recommendation_data={"pickup": "Home", "dropoff": "Airport"},
        status=RecommendationStatus.PENDING,
        conversation=conv,
    )

    booking = Booking(
        recommendation_id=rec.id,
        booking_reference="BK-98765",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
        recommendation=rec,
    )

    assert msg.sequence_number == 1
    assert msg.model_used == "gemini-1.5-pro"
    assert intent.intent_name == "book_ride"
    assert entity.entity_type == "destination"
    assert entity.intent == intent
    assert booking.recommendation == rec
    assert booking.booking_reference == "BK-98765"
