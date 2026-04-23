"""Add api_calls audit table.

Revision ID: 002
Revises: 001
Create Date: 2026-04-23

One row per outbound API call (One Auto, Anthropic, Resend, ...). Used for
diagnostics (status codes + response snippets) and cost rollups.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_calls",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("service", sa.String(32), nullable=False),
        sa.Column("endpoint", sa.String(256), nullable=False),
        sa.Column("status_code", sa.Integer()),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("cost_gbp", sa.Numeric(10, 4), server_default="0"),
        sa.Column("registration", sa.String(16)),
        sa.Column("tier", sa.String(16)),
        sa.Column("session_id", sa.String(128)),
        sa.Column("error", sa.String(512)),
        sa.Column("response_body", sa.Text()),
        sa.Column("tokens_in", sa.Integer()),
        sa.Column("tokens_out", sa.Integer()),
    )
    op.create_index("ix_api_calls_created_at", "api_calls", ["created_at"])
    op.create_index("ix_api_calls_service", "api_calls", ["service"])
    op.create_index("ix_api_calls_registration", "api_calls", ["registration"])
    op.create_index(
        "ix_api_calls_service_created_at",
        "api_calls",
        ["service", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_api_calls_service_created_at", table_name="api_calls")
    op.drop_index("ix_api_calls_registration", table_name="api_calls")
    op.drop_index("ix_api_calls_service", table_name="api_calls")
    op.drop_index("ix_api_calls_created_at", table_name="api_calls")
    op.drop_table("api_calls")
