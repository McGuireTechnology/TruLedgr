"""Create role permissions junction table

Revision ID: 002_role_permissions
Revises: 001_base_tables
Create Date: 2025-08-29 09:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = "002_role_permissions"
down_revision: Union[str, Sequence[str], None] = "001_base_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create role_permissions junction table
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("permission_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(), nullable=False),
        sa.Column("assigned_by", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("role_permissions")
