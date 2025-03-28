"""add picture_url to user model

Revision ID: baa2d68771cb
Revises: d64cd479e135
Create Date: 2025-03-28 19:17:12.971244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'baa2d68771cb'
down_revision: Union[str, None] = 'd64cd479e135'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('picture_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'picture_url')
    # ### end Alembic commands ###
