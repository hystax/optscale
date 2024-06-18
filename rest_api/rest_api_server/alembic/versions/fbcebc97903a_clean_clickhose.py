""""clean_clickhose"

Revision ID: fbcebc97903a
Revises: 368673a367ac
Create Date: 2024-06-14 09:17:07.515427

"""
import os
import logging
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session
from clickhouse_driver import Client as ClickHouseClient
from optscale_client.config_client.client import Client as EtcdClient

# revision identifiers, used by Alembic.
revision = 'fbcebc97903a'
down_revision = '368673a367ac'
branch_labels = None
depends_on = None


DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
LOG = logging.getLogger(__name__)


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_clickhouse_client():
    config_cl = _get_etcd_config_client()
    user, password, host, db_name = config_cl.clickhouse_params()
    return ClickHouseClient(
        host=host, password=password, database=db_name, user=user)


def get_cloud_accounts():
    bind = op.get_bind()
    session = Session(bind=bind)
    cloud_accs_t = sa.table(
        'cloudaccount',
        sa.Column('id', sa.String()),
        sa.Column('deleted_at', sa.Integer()),
    )
    try:
        cloud_accs_q = sa.select([cloud_accs_t.c.id]).where(
            cloud_accs_t.c.deleted_at != 0)
        cloud_accounts = [x[0] for x in session.execute(cloud_accs_q)]
    finally:
        session.close()
    return cloud_accounts


def upgrade():
    ch = _get_clickhouse_client()
    for cloud_account_id in get_cloud_accounts():
        LOG.info('Processing cloud account: %s', cloud_account_id)
        ch.execute(
            """ALTER TABLE traffic_expenses DELETE
               WHERE cloud_account_id=%(cloud_account_id)s""",
            params={'cloud_account_id': cloud_account_id}
        )
        ch.execute(
            """ALTER TABLE average_metrics DELETE
               WHERE cloud_account_id=%(cloud_account_id)s""",
            params={'cloud_account_id': cloud_account_id}
        )
        ch.execute(
            """ALTER TABLE k8s_metrics DELETE
               WHERE cloud_account_id=%(cloud_account_id)s""",
            params={'cloud_account_id': cloud_account_id}
        )
        ch.execute(
            """ALTER TABLE risp.ri_sp_usage DELETE
               WHERE cloud_account_id=%(cloud_account_id)s""",
            params={'cloud_account_id': cloud_account_id}
        )
        ch.execute(
            """ALTER TABLE risp.uncovered_usage DELETE
               WHERE cloud_account_id=%(cloud_account_id)s""",
            params={'cloud_account_id': cloud_account_id}
        )
    for table in ['traffic_expenses', 'average_metrics', 'k8s_metrics',
                  'risp.ri_sp_usage', 'risp.uncovered_usage']:
        ch.execute(f"""OPTIMIZE TABLE {table} FINAL""")


def downgrade():
    pass
