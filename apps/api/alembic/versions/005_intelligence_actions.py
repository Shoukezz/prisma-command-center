"""Add player intelligence actions and action provenance.

Revision ID: 005
Revises: 004
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intelligence_actions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("world_id", sa.Integer(), nullable=False),
        sa.Column("intel_report_id", sa.String(length=36), nullable=False),
        sa.Column("action_type", sa.String(length=24), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("taken_at", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["world_id"], ["worlds.id"]),
        sa.ForeignKeyConstraint(["intel_report_id"], ["intelligence_reports.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_intelligence_actions_world_id", "intelligence_actions", ["world_id"])
    op.create_index(
        "ix_intelligence_actions_intel_report_id",
        "intelligence_actions",
        ["intel_report_id"],
    )

    with op.batch_alter_table("intelligence_reports") as batch_op:
        batch_op.add_column(sa.Column("requested_by_action_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            "fk_intelligence_reports_requested_by_action",
            "intelligence_actions",
            ["requested_by_action_id"],
            ["id"],
        )

    with op.batch_alter_table("operations") as batch_op:
        batch_op.add_column(sa.Column("triggering_action_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            "fk_operations_triggering_action",
            "intelligence_actions",
            ["triggering_action_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("operations") as batch_op:
        batch_op.drop_constraint("fk_operations_triggering_action", type_="foreignkey")
        batch_op.drop_column("triggering_action_id")

    with op.batch_alter_table("intelligence_reports") as batch_op:
        batch_op.drop_constraint("fk_intelligence_reports_requested_by_action", type_="foreignkey")
        batch_op.drop_column("requested_by_action_id")

    op.drop_index("ix_intelligence_actions_intel_report_id", table_name="intelligence_actions")
    op.drop_index("ix_intelligence_actions_world_id", table_name="intelligence_actions")
    op.drop_table("intelligence_actions")
