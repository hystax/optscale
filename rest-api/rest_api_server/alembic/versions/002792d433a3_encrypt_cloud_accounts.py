""""encrypted_cloud_configs"

Revision ID: 002792d433a3
Revises: 9459cfa84bec
Create Date: 2022-08-09 05:38:09.515991

"""
import os
import json
import logging
import sqlalchemy as sa
import cryptocode
import uuid
from alembic import op
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column

revision = '002792d433a3'
down_revision = '9459cfa84bec'

branch_labels = None
depends_on = None


LOG = logging.getLogger(__name__)
KEY = "/encryption_salt"




def _get_encryption_salt():

    return str(uuid.uuid4())


def _encrypt_config(session, cloud_acc_table, ca):
    config = ca['config']
    try:
        json.loads(config)
    except (json.JSONDecodeError, TypeError):
        # assuming config already encrypted, skipping
        return
    upd_stmt = update(cloud_acc_table).values(
        config=cryptocode.encrypt(config, _get_encryption_salt())
    ).where(cloud_acc_table.c.id == ca['id'])
    session.execute(upd_stmt)


def _decrypt_config(session, cloud_acc_table, ca):
    config = ca['config']
    try:
        json.loads(config)
        # successful json.loads() assuming config already decrypted
        return
    except (json.JSONDecodeError, TypeError):
        pass
    upd_stmt = update(cloud_acc_table).values(
        config=cryptocode.decrypt(config, _get_encryption_salt())
    ).where(cloud_acc_table.c.id == ca['id'])
    session.execute(upd_stmt)


def process_cloud_accounts(session, func):
    cloud_acc_table = table(
        'cloudaccount',
        column('id', sa.String(36)),
        column('config', sa.Text())
    )
    all_cloud_accounts = session.execute(select([cloud_acc_table.c.id, cloud_acc_table.c.config]))
    total_cnt = all_cloud_accounts.rowcount
    cnt, last = 0, 0
    for ca in all_cloud_accounts:
        func(session, cloud_acc_table, ca)
        cnt += 1
        percents = int(cnt / total_cnt * 100)
        if percents != last:
            last = percents
            LOG.info('Processing cloud accounts: %s' % percents)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        process_cloud_accounts(session, _encrypt_config)
        LOG.info('Committing changes...')
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        process_cloud_accounts(session, _decrypt_config)
        LOG.info('Committing changes...')
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
