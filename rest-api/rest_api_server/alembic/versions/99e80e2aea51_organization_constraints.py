""""organization_constraints"

Revision ID: 99e80e2aea51
Revises: a6056e705872
Create Date: 2022-02-09 14:17:55.530864

"""
import json
import uuid
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import insert

# revision identifiers, used by Alembic.
revision = '99e80e2aea51'
down_revision = 'a6056e705872'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('organization_constraint',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('type', sa.Enum('RESOURCE_COUNT_ANOMALY', 'EXPENSE_ANOMALY'),
                  nullable=False),
        sa.Column('definition', sa.TEXT(), nullable=False, server_default='{}'),
        sa.Column('filters', sa.TEXT(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('last_run', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.PrimaryKeyConstraint('id')
    )
    bind = op.get_bind()
    session = Session(bind=bind)
    org_table = sa.table(
        'organization', sa.column('id', sa.String(36)),
        sa.column('deleted_at', sa.Integer()))
    org_constraint_table = sa.table(
        'organization_constraint',
        sa.column('id', sa.String(36)),
        sa.column('organization_id', sa.String(36)),
        sa.column('name', sa.String(256)),
        sa.column('type', sa.Enum(
            'RESOURCE_COUNT_ANOMALY', 'EXPENSE_ANOMALY')),
        sa.column('definition', sa.TEXT()),
        sa.column('deleted_at', sa.Integer()),
        sa.column('created_at', sa.Integer()),
        sa.column('last_run', sa.Integer())
    )
    try:
        for org in session.execute(
                sa.select([org_table]).where(org_table.c.deleted_at == 0)):
            for _type in ['RESOURCE_COUNT_ANOMALY', 'EXPENSE_ANOMALY']:
                _id = str(uuid.uuid4())
                dt = datetime.utcnow().timestamp()
                ins_stmt = insert(org_constraint_table).values(
                    id=_id,
                    name='Default - %s' % _type.replace('_', ' ').lower(),
                    type=_type,
                    organization_id=org.id,
                    definition=json.dumps(
                        {'threshold_days': 7, 'threshold': 30}),
                    deleted_at=0,
                    last_run=0,
                    created_at=dt
                )
                session.execute(ins_stmt)
        session.commit()
    except Exception:
        session.rollback()
        op.drop_table('organization_constraint')
        raise
    finally:
        session.close()


def downgrade():
    op.drop_table('organization_constraint')
