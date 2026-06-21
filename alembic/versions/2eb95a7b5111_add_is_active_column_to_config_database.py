"""add is_active column to config database

Revision ID: 2eb95a7b5111
Revises: 1c21ae0a1a70
Create Date: 2026-06-19 19:17:35.095394

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2eb95a7b5111"
down_revision: Union[str, None] = "1c21ae0a1a70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "config",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column("config", "is_active")
