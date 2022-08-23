""""move_resource_fields_under_meta"

Revision ID: 6ce6170a7898
Revises: 802b9d3424c5
Create Date: 2022-04-04 17:20:29.240778

"""
import os
import logging
import sqlalchemy as sa
from alembic import op
from config_client.client import Client as EtcdClient
from pymongo import MongoClient, UpdateOne
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = '6ce6170a7898'
down_revision = '802b9d3424c5'
branch_labels = None
depends_on = None


LOG = logging.getLogger(__name__)
CHUNK_SIZE = 500
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
COMMON_META_FIELDS = ['cloud_console_link']
R_TYPE_META_NEW_MAP = {
    'Instance': ['stopped_allocated', 'last_seen_not_stopped', 'spotted',
                 'cpu_count', 'os', 'security_groups', 'image_id',
                 'preinstalled', 'flavor'],
    'RDS Instance': ['zone_id', 'category', 'engine', 'engine_version',
                     'storage_type', 'cpu_count', 'flavor'],
    'Volume': ['attached', 'last_attached', 'size', 'volume_type',
               'snapshot_id'],
    'Snapshot': ['size', 'description', 'state', 'volume_id', 'last_used'],
    'Snapshot Chain': ['size', 'volume_id', 'snapshots', 'last_used'],
    'Bucket': ['is_public_policy', 'is_public_acls'],
    'Image': ['block_device_mappings'],
    'IP Address': ['available', 'last_used', 'instance_id'],
    'K8s Pod': ['pod_ip', 'instance_address', 'host_ip']
}
R_TYPE_META_OLD_MAP = {
    'Instance': ['stopped_allocated', 'last_seen_not_stopped', 'spotted'],
    'RDS Instance': [],
    'Volume': ['attached', 'last_attached'],
    'Snapshot': [],
    'Snapshot Chain': [],
    'Bucket': ['is_public_policy', 'is_public_acls'],
    'Image': [],
    'IP Address': ['available', 'last_used', 'instance_id'],
    'K8s Pod': []
}


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def get_mongo_resources():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.resources


def get_cloud_accounts_ids(session):
    organization_t = sa.table("organization",
                              sa.Column('id', sa.String()),
                              sa.Column('is_demo', sa.Boolean()),
                              sa.Column('deleted_at', sa.Integer()))
    cloud_account_t = sa.table("cloudaccount",
                               sa.Column('id', sa.String()),
                               sa.Column('organization_id', sa.String()),
                               sa.Column('type', sa.String()),
                               sa.Column('deleted_at', sa.Integer()))
    organizations = session.execute(
        sa.select([organization_t.c.id]).where(sa.and_(
            organization_t.c.deleted_at == 0,
            organization_t.c.is_demo.is_(False))))
    cloud_accounts = session.execute(sa.select([cloud_account_t.c.id]).where(
        sa.and_(
            cloud_account_t.c.organization_id.in_([x[0] for x in organizations]),
            cloud_account_t.c.deleted_at == 0)))
    return [x[0] for x in cloud_accounts]


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        cloud_accounts = get_cloud_accounts_ids(session)
    finally:
        session.close()
    mongo_resources = get_mongo_resources()
    for ca in cloud_accounts:
        updates = []
        resources = mongo_resources.find({
            'cloud_account_id': ca,
            'resource_type': {'$in': list(R_TYPE_META_NEW_MAP.keys())},
            'deleted_at': 0
        })
        for res in resources:
            meta_fields = R_TYPE_META_NEW_MAP[
                              res['resource_type']] + COMMON_META_FIELDS
            update = {'$set': {'meta': {f: res.get(f)
                                        for f in meta_fields
                                        if res.get(f) is not None}},
                      '$unset': {f: 1 for f in meta_fields}}
            updates.append(UpdateOne(
                filter={'_id': res['_id']}, update=update))
            if len(updates) >= CHUNK_SIZE:
                mongo_resources.bulk_write(updates)
                updates = []
        if updates:
            mongo_resources.bulk_write(updates)
        LOG.info('Finished updating resources for cloud account %s' % ca)


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        cloud_accounts = get_cloud_accounts_ids(session)
    finally:
        session.close()
    mongo_resources = get_mongo_resources()
    for ca in cloud_accounts:
        updates = []
        resources = mongo_resources.find({
            'cloud_account_id': ca,
            'resource_type': {'$in': list(R_TYPE_META_NEW_MAP.keys())},
            'deleted_at': 0
        })
        for r in resources:
            meta = r.get('meta')
            if meta:
                exp_meta_fields = R_TYPE_META_OLD_MAP[r['resource_type']]
                update = {'$set': {}}
                result_meta = {}
                for k, v in meta.items():
                    update['$set'][k] = v
                    if k in exp_meta_fields:
                        result_meta[k] = v
                update['$set']['meta'] = result_meta
                updates.append(UpdateOne(
                    filter={'_id': r['_id']}, update=update))
            if len(updates) >= CHUNK_SIZE:
                mongo_resources.bulk_write(updates)
                updates = []
        if updates:
            mongo_resources.bulk_write(updates)
        LOG.info('Finished updating resources for cloud account %s' % ca)
