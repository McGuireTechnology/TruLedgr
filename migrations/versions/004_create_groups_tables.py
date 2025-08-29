"""Create groups table and user groups junction

Revision ID: 004_groups_tables
Revises: 003_users_table
Create Date: 2025-08-29 09:03:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = "004_groups_tables"
down_revision: Union[str, Sequence[str], None] = "003_users_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create groups table
    op.create_table(
        "groups",
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("slug", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column(
            "description", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True
        ),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("is_open", sa.Boolean(), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("member_count", sa.Integer(), nullable=False),
        sa.Column("max_members", sa.Integer(), nullable=True),
        sa.Column(
            "group_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False
        ),
        sa.Column("tags", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("owner_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_by", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "settings", sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_groups_id"), "groups", ["id"], unique=False)
    op.create_index(op.f("ix_groups_is_active"), "groups", ["is_active"], unique=False)
    op.create_index(op.f("ix_groups_is_public"), "groups", ["is_public"], unique=False)
    op.create_index(
        op.f("ix_groups_member_count"), "groups", ["member_count"], unique=False
    )
    op.create_index(op.f("ix_groups_name"), "groups", ["name"], unique=True)
    op.create_index(op.f("ix_groups_slug"), "groups", ["slug"], unique=True)
    
    # Create user_groups junction table
    op.create_table(
        "user_groups",
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("group_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
        sa.Column("joined_by", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "role_in_group", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("user_id", "group_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop user_groups junction table
    op.drop_table("user_groups")
    
    # Drop groups table and indexes
    op.drop_index(op.f("ix_groups_slug"), table_name="groups")
    op.drop_index(op.f("ix_groups_name"), table_name="groups")
    op.drop_index(op.f("ix_groups_member_count"), table_name="groups")
    op.drop_index(op.f("ix_groups_is_public"), table_name="groups")
    op.drop_index(op.f("ix_groups_is_active"), table_name="groups")
    op.drop_index(op.f("ix_groups_id"), table_name="groups")
    op.drop_table("groups")
