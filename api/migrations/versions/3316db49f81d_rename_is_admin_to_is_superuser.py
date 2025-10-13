"""Rename is_admin to is_superuser

Revision ID: 3316db49f81d
Revises: 8be61d0cc541
Create Date: 2025-10-13 13:05:42.926302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3316db49f81d'
down_revision: Union[str, Sequence[str], None] = '8be61d0cc541'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename column is_admin to is_superuser in users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'is_admin',
            new_column_name='is_superuser',
            existing_type=sa.Boolean(),
            nullable=False
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Rename column is_superuser back to is_admin in users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'is_superuser',
            new_column_name='is_admin',
            existing_type=sa.Boolean(),
            nullable=False
        )
