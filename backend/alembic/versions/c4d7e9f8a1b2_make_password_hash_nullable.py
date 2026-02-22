"""make password hash nullable for firebase auth only

Revision ID: c4d7e9f8a1b2
Revises: b7f3c3d2c1e1
Create Date: 2026-02-21 01:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4d7e9f8a1b2"
down_revision: Union[str, Sequence[str], None] = "b7f3c3d2c1e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "password_hash", existing_type=sa.String(length=255), nullable=True)


def downgrade() -> None:
    op.alter_column("users", "password_hash", existing_type=sa.String(length=255), nullable=False)
