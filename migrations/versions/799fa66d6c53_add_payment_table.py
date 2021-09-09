"""add payment table

Revision ID: 799fa66d6c53
Revises: 62b689736774
Create Date: 2021-02-01 22:02:33.262697

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '799fa66d6c53'
down_revision = '62b689736774'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.add_column('order', sa.Column('payment_method_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'order', 'payment', ['payment_method_id'], ['id'])
    op.drop_column('order', 'payment_method')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('payment_method', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_column('order', 'payment_method_id')
    op.drop_table('payment')
    # ### end Alembic commands ###
