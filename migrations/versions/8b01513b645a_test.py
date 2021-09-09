"""test

Revision ID: 8b01513b645a
Revises: be1f7fd578be
Create Date: 2021-03-02 23:45:03.102001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b01513b645a'
down_revision = 'be1f7fd578be'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product_detail_click',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ean', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_detail_click_user_id'), 'product_detail_click', ['user_id'], unique=False)
    op.create_table('searches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('search', sa.String(length=128), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_searches_user_id'), 'searches', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_searches_user_id'), table_name='searches')
    op.drop_table('searches')
    op.drop_index(op.f('ix_product_detail_click_user_id'), table_name='product_detail_click')
    op.drop_table('product_detail_click')
    # ### end Alembic commands ###