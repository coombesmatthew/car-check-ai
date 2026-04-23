"""Initial schema — users, vehicle_checks, payments.

Revision ID: 000
Revises: None
Create Date: 2026-04-23

Pre-existed in code as SQLAlchemy models at app/models/check.py but the
production DB was never migrated. This bootstraps the schema so 001
(add product column) and 002 (add api_calls table) apply cleanly to an
empty database. Schema mirrors app/models/check.py exactly, minus the
`product` column (which 001 adds).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


revision = "000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
    )

    op.create_table(
        "vehicle_checks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("registration", sa.String(20), nullable=False),
        sa.Column("listing_url", sa.Text()),
        sa.Column("listing_price", sa.Integer()),
        sa.Column("make", sa.String(100)),
        sa.Column("model", sa.String(100)),
        sa.Column("year", sa.Integer()),
        sa.Column("mot_data", JSONB()),
        sa.Column("market_data", JSONB()),
        sa.Column("analysis_result", JSONB()),
        # product column is added by migration 001 — intentionally omitted here
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("tier", sa.String(20)),
        sa.Column("price_paid", sa.Integer()),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
    )
    op.create_index(
        "idx_vehicle_checks_registration", "vehicle_checks", ["registration"]
    )
    op.create_index(
        "idx_vehicle_checks_status", "vehicle_checks", ["status"]
    )

    op.create_table(
        "payments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "check_id",
            UUID(as_uuid=True),
            sa.ForeignKey("vehicle_checks.id", ondelete="CASCADE"),
        ),
        sa.Column(
            "stripe_payment_intent_id",
            sa.String(255),
            unique=True,
        ),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(3), server_default="gbp"),
        sa.Column("status", sa.String(50)),
        sa.Column("created_at", sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_index("idx_vehicle_checks_status", table_name="vehicle_checks")
    op.drop_index("idx_vehicle_checks_registration", table_name="vehicle_checks")
    op.drop_table("vehicle_checks")
    op.drop_table("users")
