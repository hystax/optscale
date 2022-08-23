""""added_resource_name_index"

Revision ID: 6684759fb02e
Revises: 789c5407caad
Create Date: 2021-10-27 17:57:07.903631

"""
import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy import and_, false
from sqlalchemy.orm import Session
from pymongo import MongoClient, UpdateOne, UpdateMany
from config_client.client import Client as EtcdClient

# revision identifiers, used by Alembic.
revision = '6684759fb02e'
down_revision = '789c5407caad'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
UPDATE_CHUNK_SIZE = 1000
UPDATE_MANY_CHUNK_SIZE = 100
ORG_INDEX_NAME = 'OrganizationID'


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_webhook_observer_collection():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.webhook_observer


def _get_webhook_logs_collection():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.webhook_logs


def upgrade():
    webhook_observer_collection = _get_webhook_observer_collection()
    webhook_observer_collection.create_index([('organization_id', 1)],
                                             name=ORG_INDEX_NAME)
    webhook_logs_collection = _get_webhook_logs_collection()
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        org_table = sa.table('organization',
                             sa.Column('deleted_at', sa.Integer()),
                             sa.Column('id', sa.String(36)),
                             sa.Column('is_demo', sa.Boolean()))
        stmt = sa.select([org_table]).where(
            and_(
                org_table.c.deleted_at == 0,
                org_table.c.is_demo == false(),
            )
        )
        active_organizations = session.execute(stmt)
        org_ids = [org['id'] for org in active_organizations]
        pipeline = [
            {
                '$match': {
                    'organization_id': {'$in': org_ids}
                }
            },
            {
                '$group': {
                    '_id': '$organization_id',
                    'observe_time': {"$max": "$observe_time"},
                }
            }
        ]
        webhook_logs = webhook_logs_collection.aggregate(pipeline)
        org_id_observe_map = {wl['_id']: wl['observe_time'] for wl in
                              webhook_logs}
        observer_infos = []
        webhook_logs_infos = []
        for org_id, observe_time in org_id_observe_map.items():
            update_data = {
                'organization_id': org_id,
                'observe_time': observe_time
            }
            observer_infos.append(UpdateOne(
                filter={'organization_id': org_id},
                update={
                    '$set': {k: v for k, v in update_data.items()}
                },
                upsert=True
            ))
            webhook_logs_infos.append(UpdateMany(
                filter={
                    'organization_id': org_id
                },
                update={
                    '$unset': {'observe_time': 1}
                }
            ))
        for i in range(0, len(observer_infos), UPDATE_CHUNK_SIZE):
            chunk_observer_infos = observer_infos[i:i + UPDATE_CHUNK_SIZE]
            webhook_observer_collection.bulk_write(chunk_observer_infos)
        for i in range(0, len(webhook_logs_infos), UPDATE_MANY_CHUNK_SIZE):
            chunk_webhook_logs_infos = webhook_logs_infos[
                                       i:i + UPDATE_MANY_CHUNK_SIZE]
            webhook_logs_collection.bulk_write(chunk_webhook_logs_infos)
    except Exception:
        webhook_observer_collection.drop()
        raise
    finally:
        session.commit()


def downgrade():
    webhook_observer_collection = _get_webhook_observer_collection()
    webhook_observer_collection.drop()
