"""create_shareable_book_table

Revision ID: 91979a9bd827
Revises: a7724a716593
Create Date: 2021-08-12 15:25:25.344073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91979a9bd827'
down_revision = 'a7724a716593'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'shareable_booking',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.String(36), nullable=False),
        sa.Column('acquired_by_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('acquired_since', sa.Integer(), nullable=False),
        sa.Column('released_at', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['acquired_by_id'], ['employee.id']),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('shareable_booking')
