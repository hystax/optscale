""""“removed_parent_partner”"

Revision ID: 14c9909cb961
Revises: 7093cd6a30e6
Create Date: 2017-08-10 09:53:38.022757

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '14c9909cb961'
down_revision = '7093cd6a30e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('partner_ibfk_1', 'partner', type_='foreignkey')
    op.drop_column('partner', 'parent_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('partner', sa.Column('parent_id', sa.String(length=36), nullable=True))
    op.create_foreign_key('partner_ibfk_1', 'partner', 'partner', ['parent_id'], ['id'])
    # ### end Alembic commands ###
