""""report_imports"

Revision ID: d4e6b2040357
Revises: 7ea7a125a3f4
Create Date: 2020-03-31 11:58:47.433730

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e6b2040357'
down_revision = '7ea7a125a3f4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'reportimport',
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('cloud_credentials_id', sa.String(36), nullable=False),
        sa.Column('import_file', sa.String(256), nullable=True),
        sa.Column('state', sa.Enum('SCHEDULED', 'IN_PROGRESS', 'COMPLETED',
                                   'FAILED'), nullable=False),
        sa.Column('state_reason', sa.TEXT(), nullable=True),
        sa.ForeignKeyConstraint(
            ['cloud_credentials_id'], ['cloudcredentials.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('reportimport')
