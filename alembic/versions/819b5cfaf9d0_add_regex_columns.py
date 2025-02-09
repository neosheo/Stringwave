"""add regex columns

Revision ID: 819b5cfaf9d0
Revises: 
Create Date: 2025-02-08 18:30:11.021055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '819b5cfaf9d0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('subs', sa.Column('video_title_regex', sa.String(255), nullable=True))
    op.add_column('subs', sa.Column('regex_type', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('subs', 'video_title_regex')
    op.drop_column('subs', 'regex_type')
