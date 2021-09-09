"""Make ean not nullable

Revision ID: da2a936aea65
Revises: 59ac87e00a58
Create Date: 2020-12-18 21:58:23.528846

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da2a936aea65'
down_revision = '59ac87e00a58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('item', 'ean',
               existing_type=sa.BIGINT(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('item', 'ean',
               existing_type=sa.BIGINT(),
               nullable=True)
    # ### end Alembic commands ###
