"""adress

Revision ID: 62b689736774
Revises: 93ca422e9069
Create Date: 2021-02-01 21:48:26.176690

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '62b689736774'
down_revision = '93ca422e9069'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('complemento', sa.String(length=64), nullable=True))
    op.alter_column('user', 'cep',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               type_=sa.Integer(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'cep',
               existing_type=sa.Integer(),
               type_=postgresql.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    op.drop_column('user', 'complemento')
    # ### end Alembic commands ###
