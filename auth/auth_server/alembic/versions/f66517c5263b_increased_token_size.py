""""increased_token_size"

Revision ID: f66517c5263b
Revises: 8fda986dfc7d
Create Date: 2017-05-12 14:45:07.241447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f66517c5263b'
down_revision = '8fda986dfc7d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('token')
    op.create_table('token',
    sa.Column('token', sa.String(length=350), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('valid_until', sa.TIMESTAMP(), nullable=False),
    sa.Column('ip', sa.String(length=39), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('token'), mysql_row_format='DYNAMIC'
    )
    op.create_index(op.f('ix_token_valid_until'), 'token', ['valid_until'],
                    unique=False)


def downgrade():
    pass
