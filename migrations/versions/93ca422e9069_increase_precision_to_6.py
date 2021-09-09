"""increase precision to 6

Revision ID: 93ca422e9069
Revises: 7e509160c070
Create Date: 2021-01-31 21:04:15.909722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93ca422e9069'
down_revision = '7e509160c070'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('order', 'cash_value',
               existing_type=sa.NUMERIC(precision=5, scale=2),
               type_=sa.Numeric(precision=6, scale=2),
               existing_nullable=True)
    op.alter_column('order', 'delivery_fee',
               existing_type=sa.NUMERIC(precision=5, scale=2),
               type_=sa.Numeric(precision=6, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'frontend_total',
               existing_type=sa.NUMERIC(precision=5, scale=2),
               type_=sa.Numeric(precision=6, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'total',
               existing_type=sa.NUMERIC(precision=5, scale=2),
               type_=sa.Numeric(precision=6, scale=2),
               existing_nullable=False)
    op.alter_column('order_items', 'unit_price',
               existing_type=sa.NUMERIC(precision=5, scale=2),
               type_=sa.Numeric(precision=6, scale=2),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('order_items', 'unit_price',
               existing_type=sa.Numeric(precision=6, scale=2),
               type_=sa.NUMERIC(precision=5, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'total',
               existing_type=sa.Numeric(precision=6, scale=2),
               type_=sa.NUMERIC(precision=5, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'frontend_total',
               existing_type=sa.Numeric(precision=6, scale=2),
               type_=sa.NUMERIC(precision=5, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'delivery_fee',
               existing_type=sa.Numeric(precision=6, scale=2),
               type_=sa.NUMERIC(precision=5, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'cash_value',
               existing_type=sa.Numeric(precision=6, scale=2),
               type_=sa.NUMERIC(precision=5, scale=2),
               existing_nullable=True)
    # ### end Alembic commands ###