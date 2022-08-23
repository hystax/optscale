""""traffic_processing_task_table"

Revision ID: a3cb068fe60f
Revises: c8777666e641
Create Date: 2022-04-20 13:22:01.685497

"""
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy import insert, select, String, Integer
from sqlalchemy.sql import table, column
from sqlalchemy.orm import Session
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'a3cb068fe60f'
down_revision = 'c8777666e641'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'traffic_processing_task',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('cloud_account_id', sa.String(length=36), nullable=False),
        sa.Column('start_date', sa.Integer(), nullable=False),
        sa.Column('end_date', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['cloud_account_id'], ['cloudaccount.id'], name='cloud_account_fk'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cloud_account_id', 'start_date', 'end_date', 'deleted_at', name='uc_acc_id_start_end_deleted_at')
    )
    bind = op.get_bind()
    session = Session(bind=bind)
    ca_table = table('cloudaccount',
                     column('id', sa.String(36)),
                     column('type', sa.String(36)),
                     column('deleted_at', Integer()),
                     column('last_import_at', Integer()),
                     column('organization_id', sa.String(36))
                     )
    traffic_task_table = table('traffic_processing_task',
                               column('id', sa.String(36)),
                               column('cloud_account_id', sa.String(36)),
                               column('start_date', sa.Integer()),
                               column('end_date', sa.Integer()),
                               column('deleted_at', sa.Integer()),
                               column('created_at', sa.Integer()),
                               )
    organization_table = table(
        'organization', column('id', String()),
        column('deleted_at', Integer()),
        column('is_demo', Integer()),
    )

    try:
        organization_stmt = select([organization_table]).where(
            sa.and_(
                organization_table.c.deleted_at == 0,
                organization_table.c.is_demo.is_(sa.false())
            )
        )
        org_ids = [p['id'] for p in session.execute(organization_stmt)]
        active_cloud_accounts_stmt = select([ca_table.c.id]).where(
            sa.and_(
                ca_table.c.type.in_(['ALIBABA_CNR', 'AWS_CNR', 'AZURE_CNR']),
                ca_table.c.deleted_at == 0,
                ca_table.c.last_import_at != 0,
                ca_table.c.organization_id.in_(org_ids)
            )
        )

        active_cloud_account_ids = [
            cloud_info['id'] for cloud_info in
            session.execute(active_cloud_accounts_stmt)]
        dt = int(datetime.utcnow().timestamp())
        for ca in active_cloud_account_ids:
            ins_stmt = insert(traffic_task_table).values(
                id=str(uuid.uuid4()),
                created_at=dt,
                deleted_at=0,
                cloud_account_id=ca,
                start_date=0,
                end_date=dt
            )
            session.execute(ins_stmt)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade():
    op.drop_table('traffic_processing_task')
