"""non nullable fields

Revision ID: e0688a829fc9
Revises: 31d8f37a2e74
Create Date: 2021-01-13 19:00:18.594311

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e0688a829fc9'
down_revision = '31d8f37a2e74'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('item', 'name',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)
    op.alter_column('item', 'price',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    op.alter_column('item', 'store_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('item', 'store_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('item', 'price',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.alter_column('item', 'name',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)
    # ### end Alembic commands ###
