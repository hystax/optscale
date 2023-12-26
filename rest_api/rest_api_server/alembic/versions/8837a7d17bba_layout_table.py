""""layout_table"

Revision ID: 8837a7d17bba
Revises: 53c710842488
Create Date: 2023-12-01 05:10:49.108262

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from rest_api.rest_api_server.models.types import NullableBool

# revision identifiers, used by Alembic.
revision = '8837a7d17bba'
down_revision = '53c710842488'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('layout',
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('name', mysql.VARCHAR(length=256),
                              nullable=False),
                    sa.Column('type', sa.String(length=256),
                              nullable=False),
                    sa.Column('data', mysql.MEDIUMTEXT(), nullable=False),
                    sa.Column('shared', NullableBool(), nullable=False),
                    sa.Column('owner_id', sa.String(length=36),
                              nullable=False),
                    sa.Column('entity_id', sa.String(length=36),
                              nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['owner_id'],
                                            ['employee.id'], ))


def downgrade():
    op.drop_table('layout')
