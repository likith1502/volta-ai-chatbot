"""add unique constraint to bookings recommendation_id

Revision ID: f1a7b8c9d0e2
Revises: e5a8f2b1c3d4
Create Date: 2026-09-28 14:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import context, op

# revision identifiers, used by Alembic.
revision: str = "f1a7b8c9d0e2"
down_revision: Union[str, None] = "e5a8f2b1c3d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Pre-check: In online mode, ensure no duplicate non-null recommendation_id exists in bookings table
    if not context.is_offline_mode():
        conn = op.get_bind()
        inspector = sa.inspect(conn)
        if "bookings" in inspector.get_table_names():
            duplicates = conn.execute(
                sa.text(
                    """
                    SELECT recommendation_id, count(*) as count
                    FROM bookings
                    WHERE recommendation_id IS NOT NULL
                    GROUP BY recommendation_id
                    HAVING count(*) > 1
                    """
                )
            ).fetchall()

            if duplicates:
                dup_details = ", ".join(f"{row[0]} ({row[1]} occurrences)" for row in duplicates)
                raise RuntimeError(
                    f"Cannot apply unique constraint 'uq_bookings_recommendation_id': "
                    f"found duplicate recommendation_id entries in bookings table: {dup_details}"
                )

    # 2. Create unique constraint on recommendation_id
    with op.batch_alter_table("bookings", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            "uq_bookings_recommendation_id",
            ["recommendation_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("bookings", schema=None) as batch_op:
        batch_op.drop_constraint("uq_bookings_recommendation_id", type_="unique")
