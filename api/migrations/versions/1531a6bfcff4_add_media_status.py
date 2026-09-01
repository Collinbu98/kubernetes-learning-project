"""add media status

Revision ID: 1531a6bfcff4
Revises: 
Create Date: 2026-09-01 09:15:46.557511

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1531a6bfcff4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE media
        ADD COLUMN status TEXT NOT NULL DEFAULT 'ready'
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE media
        DROP COLUMN status
    """)
