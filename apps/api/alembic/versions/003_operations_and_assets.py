"""Operations and assets

Revision ID: 003
Revises: 002
Create Date: 2035-03-16

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("world_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("asset_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("supports_recon", sa.Boolean(), nullable=False),
        sa.Column("supports_strike", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["world_id"], ["worlds.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assets_world_id", "assets", ["world_id"])

    op.create_table(
        "operations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("world_id", sa.Integer(), nullable=False),
        sa.Column("operation_type", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("intel_report_id", sa.String(length=36), nullable=False),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("region_name", sa.String(length=128), nullable=False),
        sa.Column("target_latitude", sa.Float(), nullable=False),
        sa.Column("target_longitude", sa.Float(), nullable=False),
        sa.Column("intel_confidence", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.Integer(), nullable=False),
        sa.Column("completes_at", sa.Integer(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["intel_report_id"], ["intelligence_reports.id"]),
        sa.ForeignKeyConstraint(["world_id"], ["worlds.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_operations_world_id", "operations", ["world_id"])
    op.create_index("ix_operations_completes_at", "operations", ["completes_at"])

    op.create_table(
        "operation_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("operation_id", sa.String(length=36), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("outcome_summary", sa.Text(), nullable=False),
        sa.Column("confidence_at_planning", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["operation_id"], ["operations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("operation_id"),
    )


def downgrade() -> None:
    op.drop_table("operation_results")
    op.drop_table("operations")
    op.drop_table("assets")
