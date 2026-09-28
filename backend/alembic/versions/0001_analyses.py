"""Persist session-owned analyses."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "analyses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_hash", sa.String(64), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("input_type", sa.String(10), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary", sa.Text),
        sa.Column("report", sa.JSON),
        sa.Column("evidence", sa.JSON),
        sa.Column("error", sa.Text),
        sa.Column("input_path", sa.Text),
    )
    op.create_index("ix_analyses_owner_hash", "analyses", ["owner_hash"])
    op.create_index("ix_analyses_status", "analyses", ["status"])


def downgrade():
    op.drop_table("analyses")
