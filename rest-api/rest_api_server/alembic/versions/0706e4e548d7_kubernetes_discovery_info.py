"""kubernetes_discovery_info

Revision ID: 0706e4e548d7
Revises: 1c776bf61113
Create Date: 2021-05-17 15:51:23.552663

"""
from alembic import op
import sqlalchemy as sa
import datetime
import uuid
from sqlalchemy import insert, select, String, Integer
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '0706e4e548d7'
down_revision = '1c776bf61113'
branch_labels = None
depends_on = None

old_discovery_info_types = sa.Enum('instance', 'volume', 'snapshot', 'bucket')

new_discovery_info_types = sa.Enum('instance', 'volume', 'snapshot', 'bucket', 'k8s_pod')


def upgrade():
    op.alter_column('discovery_info', 'resource_type', existing_type=old_discovery_info_types,
                    type_=new_discovery_info_types, nullable=False)
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        cloud_acc_table = table('cloudaccount',
                                column('id', sa.String(36)),
                                column('deleted_at', Integer()))
        active_cloud_accounts_stmt = select([cloud_acc_table.c.id]).where(cloud_acc_table.c.deleted_at == 0)
        active_cloud_account_ids = [cloud_info['id'] for cloud_info in session.execute(active_cloud_accounts_stmt)]
        d_info_table = table('discovery_info',
                             column('id', String(36)),
                             column('cloud_account_id', String(36)),
                             column('resource_type', String(36)),
                             column('created_at', Integer()),
                             column('deleted_at', Integer()),
                             column('last_discovery_at', sa.Integer()),
                             )
        for active_cloud_account_id in active_cloud_account_ids:
            dt = datetime.datetime.utcnow().timestamp()
            ins_stmt = insert(d_info_table).values(
                id=str(uuid.uuid4()),
                cloud_account_id=active_cloud_account_id,
                resource_type='k8s_pod',
                created_at=dt,
                deleted_at=0,
                last_discovery_at=0,
            )
            session.execute(ins_stmt)
    finally:
        session.commit()


def downgrade():
    ct = sa.sql.table('discovery_info', sa.sql.column('resource_type', new_discovery_info_types))
    op.execute(ct.delete().where(ct.c.resource_type.in_(['k8s_pod'])))
    op.alter_column('discovery_info', 'resource_type', existing_type=new_discovery_info_types,
                    type_=old_discovery_info_types, nullable=False)
