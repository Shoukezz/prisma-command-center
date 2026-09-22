"""Analysts and assessments

Revision ID: 004
Revises: 003
Create Date: 2035-03-17

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "analysts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("world_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("specialty", sa.String(length=64), nullable=False),
        sa.Column("reliability", sa.Float(), nullable=False),
        sa.Column("bias", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["world_id"], ["worlds.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysts_world_id", "analysts", ["world_id"])

    op.create_table(
        "analyst_assessments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("intel_report_id", sa.String(length=36), nullable=False),
        sa.Column("analyst_id", sa.String(length=36), nullable=False),
        sa.Column("assessment", sa.Text(), nullable=False),
        sa.Column("assessed_confidence", sa.Integer(), nullable=False),
        sa.Column("game_minutes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["analyst_id"], ["analysts.id"]),
        sa.ForeignKeyConstraint(["intel_report_id"], ["intelligence_reports.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analyst_assessments_intel_report_id", "analyst_assessments", ["intel_report_id"])
    op.create_index("ix_analyst_assessments_analyst_id", "analyst_assessments", ["analyst_id"])


def downgrade() -> None:
    op.drop_table("analyst_assessments")
    op.drop_table("analysts")
