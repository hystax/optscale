""""removed_azure_tax_percent"

Revision ID: a34d9c7b1d96
Revises: e9ed3e231f20
Create Date: 2020-10-08 05:18:50.566167

"""
import json
import os

from alembic import op
import sqlalchemy as sa

from sqlalchemy import and_, bindparam
from sqlalchemy.orm import Session
from config_client.client import Client as EtcdClient
from pymongo import MongoClient, UpdateMany

# revision identifiers, used by Alembic.
revision = 'a34d9c7b1d96'
down_revision = 'e9ed3e231f20'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
AZURE_TYPE = 'AZURE_CNR'


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_expenses_collection():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.expenses


cloud_table = sa.table('cloudcredentials',
                       sa.Column('id', sa.String(36)),
                       sa.Column('type', sa.String(36)),
                       sa.Column('deleted_at', sa.Integer()),
                       sa.Column('cloud_credentials', sa.Text()))


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        stmt = sa.select([cloud_table]).where(and_(
            cloud_table.c.type == AZURE_TYPE,
            cloud_table.c.deleted_at == 0))
        creds_updates = []
        id_tax_map = {}
        for id, type_, _, creds in session.execute(stmt):
            new_creds = json.loads(creds)
            tax_percent = new_creds.pop('tax_percent', 0)
            if tax_percent > 0:
                id_tax_map[id] = tax_percent
            new_creds = json.dumps(new_creds)
            creds_updates.append({'_id': id, 'cloud_credentials': new_creds})

        mongo_clean = _get_expenses_collection()
        requests = []
        for cred_id, tax in id_tax_map.items():
            multiplier = 100 / (100 + tax)
            request = UpdateMany(
                filter={'cloud_credentials_id': cred_id},
                update={'$mul': {'cost': multiplier}}
            )
            requests.append(request)
        if len(requests) > 0:
            mongo_clean.bulk_write(requests)

        if len(creds_updates) > 0:
            update_query = sa.update(cloud_table).where(
                cloud_table.c.id == bindparam('_id')
            ).values(cloud_credentials=bindparam('cloud_credentials'))
            session.execute(update_query, creds_updates)
            session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        stmt = sa.select([cloud_table]).where(and_(
            cloud_table.c.type == AZURE_TYPE,
            cloud_table.c.deleted_at == 0))
        creds_updates = []
        for id, type_, deleted_at, creds in session.execute(stmt):
            new_creds = json.loads(creds)
            new_creds['tax_percent'] = 0
            new_creds = json.dumps(new_creds)
            creds_updates.append({'_id': id, 'cloud_credentials': new_creds})

        if len(creds_updates) > 0:
            update_query = sa.update(cloud_table).where(
                cloud_table.c.id == bindparam('_id')
            ).values(cloud_credentials=bindparam('cloud_credentials'))
            session.execute(update_query, creds_updates)
            session.commit()
    finally:
        session.close()
