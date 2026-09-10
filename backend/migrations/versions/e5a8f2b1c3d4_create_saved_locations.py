"""create saved locations table

Revision ID: e5a8f2b1c3d4
Revises: None
Create Date: 2026-09-10 09:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5a8f2b1c3d4"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "saved_locations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column(
            "is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_saved_locations_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_saved_locations"),
    )
    op.create_index("ix_saved_locations_id", "saved_locations", ["id"], unique=False)
    op.create_index(
        "ix_saved_locations_user_id", "saved_locations", ["user_id"], unique=False
    )
    op.create_index(
        "ix_saved_locations_label", "saved_locations", ["label"], unique=False
    )
    op.create_index(
        "ix_saved_locations_is_deleted", "saved_locations", ["is_deleted"], unique=False
    )
    op.create_index(
        "ix_saved_locations_user_label_active",
        "saved_locations",
        ["user_id", sa.text("lower(label)")],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
        sqlite_where=sa.text("is_deleted = 0"),
    )


def downgrade() -> None:
    op.drop_index("ix_saved_locations_user_label_active", table_name="saved_locations")
    op.drop_index("ix_saved_locations_is_deleted", table_name="saved_locations")
    op.drop_index("ix_saved_locations_label", table_name="saved_locations")
    op.drop_index("ix_saved_locations_user_id", table_name="saved_locations")
    op.drop_index("ix_saved_locations_id", table_name="saved_locations")
    op.drop_table("saved_locations")
