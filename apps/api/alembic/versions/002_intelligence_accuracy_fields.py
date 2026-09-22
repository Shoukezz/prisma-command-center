"""Intelligence accuracy metadata (server-only)

Revision ID: 002
Revises: 001
Create Date: 2035-03-15

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("intelligence_reports") as batch_op:
        batch_op.add_column(
            sa.Column("content_accuracy", sa.Float(), nullable=False, server_default="0.5")
        )
        batch_op.add_column(
            sa.Column("location_accuracy", sa.Float(), nullable=False, server_default="0.5")
        )


def downgrade() -> None:
    with op.batch_alter_table("intelligence_reports") as batch_op:
        batch_op.drop_column("location_accuracy")
        batch_op.drop_column("content_accuracy")
