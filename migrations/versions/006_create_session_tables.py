"""Create session management tables

Revision ID: 006_session_tables
Revises: 005_auth_tables
Create Date: 2025-08-29 09:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = "006_session_tables"
down_revision: Union[str, Sequence[str], None] = "005_auth_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create user_sessions table
    op.create_table(
        "user_sessions",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "session_token_hash",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "client_ip", sqlmodel.sql.sqltypes.AutoString(length=45), nullable=False
        ),
        sa.Column(
            "user_agent", sqlmodel.sql.sqltypes.AutoString(length=512), nullable=True
        ),
        sa.Column(
            "device_fingerprint",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.Column(
            "location", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_activity", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column(
            "revocation_reason",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=True,
        ),
        sa.Column(
            "login_method", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True
        ),
        sa.Column("request_count", sa.Integer(), nullable=False),
        sa.Column("suspicious_activity", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_sessions_expires_at"),
        "user_sessions",
        ["expires_at"],
        unique=False,
    )
    op.create_index(op.f("ix_user_sessions_id"), "user_sessions", ["id"], unique=False)
    op.create_index(
        op.f("ix_user_sessions_is_active"), "user_sessions", ["is_active"], unique=False
    )
    op.create_index(
        op.f("ix_user_sessions_last_activity"),
        "user_sessions",
        ["last_activity"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_sessions_session_token_hash"),
        "user_sessions",
        ["session_token_hash"],
        unique=True,
    )
    op.create_index(
        op.f("ix_user_sessions_user_id"), "user_sessions", ["user_id"], unique=False
    )
    
    # Create sessionanalytics table
    op.create_table(
        "sessionanalytics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("device_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("browser", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("os", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("ip_address", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("country", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("city", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("login_time", sa.DateTime(), nullable=False),
        sa.Column("last_activity", sa.DateTime(), nullable=False),
        sa.Column("logout_time", sa.DateTime(), nullable=True),
        sa.Column("session_duration", sa.Integer(), nullable=True),
        sa.Column("page_views", sa.Integer(), nullable=False),
        sa.Column("api_calls", sa.Integer(), nullable=False),
        sa.Column("last_page", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("last_endpoint", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("is_suspicious", sa.Boolean(), nullable=False),
        sa.Column("security_score", sa.Integer(), nullable=False),
        sa.Column("failed_actions", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sessionanalytics_session_id"),
        "sessionanalytics",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sessionanalytics_user_id"),
        "sessionanalytics",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop sessionanalytics table and indexes
    op.drop_index(op.f("ix_sessionanalytics_user_id"), table_name="sessionanalytics")
    op.drop_index(op.f("ix_sessionanalytics_session_id"), table_name="sessionanalytics")
    op.drop_table("sessionanalytics")
    
    # Drop user_sessions table and indexes
    op.drop_index(op.f("ix_user_sessions_user_id"), table_name="user_sessions")
    op.drop_index(
        op.f("ix_user_sessions_session_token_hash"), table_name="user_sessions"
    )
    op.drop_index(op.f("ix_user_sessions_last_activity"), table_name="user_sessions")
    op.drop_index(op.f("ix_user_sessions_is_active"), table_name="user_sessions")
    op.drop_index(op.f("ix_user_sessions_id"), table_name="user_sessions")
    op.drop_index(op.f("ix_user_sessions_expires_at"), table_name="user_sessions")
    op.drop_table("user_sessions")
