"""add processing started timestamp

Revision ID: c59407ad7a79
Revises: 1531a6bfcff4
Create Date: 2026-09-01 12:21:13.449637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c59407ad7a79'
down_revision: Union[str, Sequence[str], None] = '1531a6bfcff4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        "media",
        sa.Column("processing_started_at", sa.DateTime(), nullable=True),
    )

def downgrade() -> None:
    op.drop_column("media", "processing_started_at")
