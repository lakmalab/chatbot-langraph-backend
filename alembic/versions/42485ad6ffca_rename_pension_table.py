"""rename pension table

Revision ID: 42485ad6ffca
Revises: e4a54d696fb9
Create Date: 2025-10-11 16:08:47.579531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42485ad6ffca'
down_revision: Union[str, None] = 'e4a54d696fb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
