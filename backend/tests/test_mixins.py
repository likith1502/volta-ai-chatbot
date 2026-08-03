import uuid
from datetime import datetime
from sqlalchemy import UUID, DateTime
from app.db.base import Base
from app.db.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin


class DummyModel(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "dummy_test_table"


def test_uuid_column_and_python_type():
    """Verify UUID column is native PostgreSQL UUID type and Python returns uuid.UUID."""
    table = Base.metadata.tables["dummy_test_table"]
    id_col = table.columns["id"]

    assert isinstance(id_col.type, UUID)
    assert id_col.type.as_uuid is True
    assert id_col.primary_key is True

    instance = DummyModel()
    generated_uuid = uuid.uuid4()
    instance.id = generated_uuid
    assert isinstance(instance.id, uuid.UUID)
    assert instance.id == generated_uuid


def test_timestamp_column_timezone_awareness():
    """Verify created_at and updated_at are configured with DateTime(timezone=True)."""
    table = Base.metadata.tables["dummy_test_table"]
    created_col = table.columns["created_at"]
    updated_col = table.columns["updated_at"]

    assert isinstance(created_col.type, DateTime)
    assert created_col.type.timezone is True
    assert isinstance(updated_col.type, DateTime)
    assert updated_col.type.timezone is True
    assert updated_col.onupdate is not None


def test_soft_delete_idempotence():
    """Verify soft_delete() and restore() are idempotent across repeated invocations."""
    instance = DummyModel()
    assert instance.is_deleted is False or instance.is_deleted is None
    assert instance.deleted_at is None

    # First soft_delete call
    instance.soft_delete()
    assert instance.is_deleted is True
    first_deleted_at = instance.deleted_at
    assert isinstance(first_deleted_at, datetime)

    # Second soft_delete call must be idempotent and preserve initial timestamp
    instance.soft_delete()
    assert instance.is_deleted is True
    assert instance.deleted_at == first_deleted_at

    # First restore call
    instance.restore()
    assert instance.is_deleted is False
    assert instance.deleted_at is None

    # Second restore call must be idempotent
    instance.restore()
    assert instance.is_deleted is False
    assert instance.deleted_at is None


def test_audit_fields_defaults_and_assignment():
    """Verify AuditMixin fields default to None and accept UUID values."""
    instance = DummyModel()
    assert instance.created_by is None
    assert instance.updated_by is None

    creator_id = uuid.uuid4()
    modifier_id = uuid.uuid4()
    instance.created_by = creator_id
    instance.updated_by = modifier_id

    assert isinstance(instance.created_by, uuid.UUID)
    assert isinstance(instance.updated_by, uuid.UUID)
    assert instance.created_by == creator_id
    assert instance.updated_by == modifier_id


def test_mixin_composition_metadata():
    """Verify all composed mixin columns register correctly on Base.metadata."""
    table = Base.metadata.tables["dummy_test_table"]
    columns = table.columns.keys()

    expected_columns = [
        "id",
        "created_at",
        "updated_at",
        "is_deleted",
        "deleted_at",
        "created_by",
        "updated_by",
    ]
    for col in expected_columns:
        assert col in columns
