"""add analytics

Revision ID: be1f7fd578be
Revises: e7e4519094c2
Create Date: 2021-03-02 23:01:27.675403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be1f7fd578be'
down_revision = 'e7e4519094c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('order', 'cash_value',
               existing_type=sa.NUMERIC(precision=6, scale=2),
               type_=sa.Numeric(precision=8, scale=2),
               existing_nullable=True)
    op.alter_column('order', 'delivery_fee',
               existing_type=sa.NUMERIC(precision=6, scale=2),
               type_=sa.Numeric(precision=8, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'frontend_total',
               existing_type=sa.NUMERIC(precision=6, scale=2),
               type_=sa.Numeric(precision=8, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'total',
               existing_type=sa.NUMERIC(precision=6, scale=2),
               type_=sa.Numeric(precision=8, scale=2),
               existing_nullable=False)
    op.alter_column('order_items', 'unit_price',
               existing_type=sa.NUMERIC(precision=6, scale=2),
               type_=sa.Numeric(precision=8, scale=2),
               existing_nullable=False)
    op.drop_table('product_detail_click')
    op.drop_table('searches')
    # op.add_column('product_detail_click', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    # op.add_column('product_detail_click', sa.Column('timestamp', sa.DateTime(), nullable=False))
    # op.add_column('product_detail_click', sa.Column('user_id', sa.Integer(), nullable=True))
    # op.create_index(op.f('ix_product_detail_click_user_id'), 'product_detail_click', ['user_id'], unique=False)
    # op.create_foreign_key(None, 'product_detail_click', 'user', ['user_id'], ['id'])
    # op.drop_column('product_detail_click', 'clicks')
    # op.add_column('searches', sa.Column('user_id', sa.Integer(), nullable=True))
    # op.create_index(op.f('ix_searches_user_id'), 'searches', ['user_id'], unique=False)
    # op.create_foreign_key(None, 'searches', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_constraint(None, 'searches', type_='foreignkey')
    # op.drop_index(op.f('ix_searches_user_id'), table_name='searches')
    # op.drop_column('searches', 'user_id')
    # op.add_column('product_detail_click', sa.Column('clicks', sa.INTEGER(), autoincrement=False, nullable=False))
    # op.drop_constraint(None, 'product_detail_click', type_='foreignkey')
    # op.drop_index(op.f('ix_product_detail_click_user_id'), table_name='product_detail_click')
    # op.drop_column('product_detail_click', 'user_id')
    # op.drop_column('product_detail_click', 'timestamp')
    # op.drop_column('product_detail_click', 'id')
    op.alter_column('order_items', 'unit_price',
               existing_type=sa.Numeric(precision=8, scale=2),
               type_=sa.NUMERIC(precision=6, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'total',
               existing_type=sa.Numeric(precision=8, scale=2),
               type_=sa.NUMERIC(precision=6, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'frontend_total',
               existing_type=sa.Numeric(precision=8, scale=2),
               type_=sa.NUMERIC(precision=6, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'delivery_fee',
               existing_type=sa.Numeric(precision=8, scale=2),
               type_=sa.NUMERIC(precision=6, scale=2),
               existing_nullable=False)
    op.alter_column('order', 'cash_value',
               existing_type=sa.Numeric(precision=8, scale=2),
               type_=sa.NUMERIC(precision=6, scale=2),
               existing_nullable=True)
    # ### end Alembic commands ###
