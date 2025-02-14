"""add discogs_links column

Revision ID: 1c21ae0a1a70
Revises: 819b5cfaf9d0
Create Date: 2025-02-11 17:44:38.541249

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c21ae0a1a70'
down_revision: Union[str, None] = '819b5cfaf9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tracks', sa.Column('discogs_link', sa.String(255), nullable=False))


def downgrade() -> None:
    op.drop_column('tracks', 'discogs_link')