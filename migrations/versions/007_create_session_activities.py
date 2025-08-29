"""Create session activities table

Revision ID: 007_session_activities
Revises: 006_session_tables
Create Date: 2025-08-29 09:06:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = "007_session_activities"
down_revision: Union[str, Sequence[str], None] = "006_session_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create session_activities table
    op.create_table(
        "session_activities",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("session_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "activity_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False
        ),
        sa.Column(
            "endpoint", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.Column("method", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=True),
        sa.Column(
            "client_ip", sqlmodel.sql.sqltypes.AutoString(length=45), nullable=False
        ),
        sa.Column(
            "user_agent", sqlmodel.sql.sqltypes.AutoString(length=512), nullable=True
        ),
        sa.Column(
            "request_id", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True
        ),
        sa.Column("response_status", sa.Integer(), nullable=True),
        sa.Column("extra_data", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["user_sessions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_session_activities_activity_type"),
        "session_activities",
        ["activity_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_session_activities_id"), "session_activities", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_session_activities_session_id"),
        "session_activities",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_session_activities_user_id"),
        "session_activities",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop session_activities table and indexes
    op.drop_index(
        op.f("ix_session_activities_user_id"), table_name="session_activities"
    )
    op.drop_index(
        op.f("ix_session_activities_session_id"), table_name="session_activities"
    )
    op.drop_index(op.f("ix_session_activities_id"), table_name="session_activities")
    op.drop_index(
        op.f("ix_session_activities_activity_type"), table_name="session_activities"
    )
    op.drop_table("session_activities")
