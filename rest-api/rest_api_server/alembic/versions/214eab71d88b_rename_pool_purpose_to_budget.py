"""Rename pool purpose to budget

Revision ID: 214eab71d88b
Revises: 93c81a1434d7
Create Date: 2021-06-09 16:44:56.053050

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = '214eab71d88b'
down_revision = '93c81a1434d7'
branch_labels = None
depends_on = None
new_budget_purposes = sa.Enum('BUDGET', 'BUSINESS_UNIT', 'TEAM', 'PROJECT', 'CICD',
                              'MLAI', 'ASSET_POOL')
temp_budget_purposes = sa.Enum('BUDGET', 'BUSINESS_UNIT', 'TEAM', 'PROJECT', 'CICD',
                               'MLAI', 'ASSET_POOL', 'POOL')
old_budget_purposes = sa.Enum('BUSINESS_UNIT', 'TEAM', 'PROJECT', 'CICD',
                              'MLAI', 'ASSET_POOL', 'POOL')


def _update_pool_table(session, source_purpose, target_purpose):
    pool_table = sa.table('pool',
                            sa.Column('id', sa.String(36)),
                            sa.Column('purpose', temp_budget_purposes))
    session.execute(sa.update(pool_table).values(purpose=target_purpose).where(
        pool_table.c.purpose == source_purpose))


def upgrade():
    op.alter_column('pool', 'purpose', existing_type=old_budget_purposes,
                    type_=temp_budget_purposes, existing_nullable=False)
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        _update_pool_table(session, 'POOL', 'BUDGET')
        session.commit()
    finally:
        session.close()
    op.alter_column('pool', 'purpose', existing_type=temp_budget_purposes,
                    type_=new_budget_purposes, existing_nullable=False)


def downgrade():
    op.alter_column('pool', 'purpose', existing_type=new_budget_purposes,
                    type_=temp_budget_purposes, existing_nullable=False)
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        _update_pool_table(session, 'BUDGET', 'POOL')
        session.commit()
    finally:
        session.close()
    op.alter_column('pool', 'purpose', existing_type=temp_budget_purposes,
                    type_=old_budget_purposes, existing_nullable=False)
