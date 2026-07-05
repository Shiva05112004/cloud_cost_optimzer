"""create metric_features table

Revision ID: 0001_metric_features
Revises: 
Create Date: 2026-05-22
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_metric_features"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "metric_features",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cpu", sa.Float, nullable=False),
        sa.Column("memory", sa.Float, nullable=False),
        sa.Column("connections", sa.Float, nullable=False),
        sa.Column("cpu_velocity", sa.Float, nullable=True),
        sa.Column("memory_velocity", sa.Float, nullable=True),
        sa.Column("connections_velocity", sa.Float, nullable=True),
        sa.Column("rolling_cpu", sa.Float, nullable=True),
        sa.Column("rolling_memory", sa.Float, nullable=True),
        sa.Column("rolling_connections", sa.Float, nullable=True),
        sa.Column("is_failure_imminent", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_metric_features_ts", "metric_features", ["ts"])


def downgrade() -> None:
    op.drop_index("ix_metric_features_ts", table_name="metric_features")
    op.drop_table("metric_features")
