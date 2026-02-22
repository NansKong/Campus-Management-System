"""drop password hash from users

Revision ID: e1a2c3d4f5a6
Revises: c4d7e9f8a1b2
Create Date: 2026-02-21 01:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1a2c3d4f5a6"
down_revision: Union[str, Sequence[str], None] = "c4d7e9f8a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "password_hash")


def downgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))
