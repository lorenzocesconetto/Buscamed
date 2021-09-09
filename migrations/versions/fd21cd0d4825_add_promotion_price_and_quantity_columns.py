"""Add promotion price and quantity columns

Revision ID: fd21cd0d4825
Revises: 9c334bdf5ea8
Create Date: 2020-12-21 20:59:27.930781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd21cd0d4825'
down_revision = '9c334bdf5ea8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item', sa.Column('promotion_price', sa.Float(), nullable=True))
    op.add_column('item', sa.Column('promotion_qty', sa.Integer(), nullable=True))
    op.drop_constraint('_sku_store_uc', 'item', type_='unique')
    op.create_unique_constraint(None, 'store', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'store', type_='unique')
    op.create_unique_constraint('_sku_store_uc', 'item', ['sku', 'store_id'])
    op.drop_column('item', 'promotion_qty')
    op.drop_column('item', 'promotion_price')
    # ### end Alembic commands ###