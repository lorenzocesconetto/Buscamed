"""Make address optional

Revision ID: 9aa8b8cbaad0
Revises: 20163b617cce
Create Date: 2021-01-21 12:08:50.047816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9aa8b8cbaad0'
down_revision = '20163b617cce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'address',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'address',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    # ### end Alembic commands ###
