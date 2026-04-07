"""Початкова схема: users (з phone) та posts.

Revision ID: 20260406_01
Revises:
Create Date: 2026-04-06

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260406_01"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("telegram_id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("username", sa.String(length=32), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="user",
        ),
        sa.Column(
            "is_banned",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "is_scammer",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "balance",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "rating",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("telegram_id"),
    )
    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=5000), nullable=False),
        sa.Column("budget", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column(
            "post_type",
            sa.String(length=20),
            nullable=False,
            server_default="public",
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("author_id", sa.BigInteger(), nullable=False),
        sa.Column("executor_id", sa.BigInteger(), nullable=True),
        sa.Column("channel_message_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ("
            "'draft', 'moderation', 'published', 'working', "
            "'completed', 'archived', 'dispute', 'cancelled'"
            ")",
            name="check_post_status",
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.telegram_id"],
        ),
        sa.ForeignKeyConstraint(
            ["executor_id"],
            ["users.telegram_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("posts")
    op.drop_table("users")
