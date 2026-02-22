"""Add product column to vehicle_checks.

Revision ID: 001
Revises: None
Create Date: 2026-02-18
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add product column (defaults existing rows to 'car')
    op.add_column(
        "vehicle_checks",
        sa.Column("product", sa.String(20), server_default="car", nullable=False),
    )
    op.create_index("idx_vehicle_checks_product", "vehicle_checks", ["product"])


def downgrade() -> None:
    op.drop_index("idx_vehicle_checks_product", table_name="vehicle_checks")
    op.drop_column("vehicle_checks", "product")
