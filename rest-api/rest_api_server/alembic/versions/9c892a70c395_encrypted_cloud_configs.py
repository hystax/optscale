""""encrypted_cloud_configs"

Revision ID: 9c892a70c395
Revises: 444e8c1c0455
Create Date: 2022-08-09 05:38:09.515991

"""
import os
import logging
import sqlalchemy as sa
import cryptocode
from alembic import op
from config_client.client import Client as EtcdClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '9c892a70c395'
down_revision = '444e8c1c0455'
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


def _get_encryption_salt():
    config_cl = _get_etcd_config_client()
    return config_cl.encryption_salt()


def encode_config(json_string, salt):
    return cryptocode.encrypt(json_string, salt)


def decode_config(encoded_str, salt):
    return cryptocode.decrypt(encoded_str, salt)


def recode_configs(func):
    bind = op.get_bind()
    session = Session(bind=bind)
    encryption_salt = _get_encryption_salt()
    try:
        cloud_acc_table = table(
            'cloudaccount',
            column('id', sa.String(36)),
            column('config', sa.Text())
        )
        all_cloud_accounts = session.execute(select([cloud_acc_table.c.id, cloud_acc_table.c.config]))
        total_cnt = all_cloud_accounts.rowcount
        cnt, last = 0, 0
        for ca in all_cloud_accounts:
            upd_stmt = update(cloud_acc_table).values(
                config=func(ca['config'], encryption_salt)
            ).where(cloud_acc_table.c.id == ca['id'])
            session.execute(upd_stmt)
            cnt += 1
            percents = int(cnt / total_cnt * 100)
            if percents != last:
                last = percents
                LOG.info('Processing cloud accounts: %s' % percents)
        LOG.info('Commit changes...')
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def upgrade():
    recode_configs(encode_config)


def downgrade():
    recode_configs(decode_config)
