""""added_detected_at_to_optimizations_data"

Revision ID: 802b9d3424c5
Revises: 69b78adf3fdc
Create Date: 2022-04-08 14:11:00.931661

"""
import logging
import os
from collections import defaultdict

import sqlalchemy as sa

from alembic import op
from sqlalchemy import false, and_
from sqlalchemy.orm import Session

from config_client.client import Client as EtcdClient
from pymongo import MongoClient, UpdateOne

# revision identifiers, used by Alembic.
revision = '802b9d3424c5'
down_revision = '69b78adf3fdc'
branch_labels = None
depends_on = None

DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80

LOG = logging.getLogger(__name__)

MODULE_UNIQUE_KEYS_MAP = {
    'inactive_users': ('cloud_account_id', 'user_id'),
    'inactive_console_users': ('cloud_account_id', 'user_id'),
    'insecure_security_groups': ('cloud_account_id', 'cloud_resource_id', 'security_group_id')
}
DEFAULT_UNIQUE_KEY = ('cloud_account_id', 'cloud_resource_id')

ORGANIZATION_TABLE = sa.table(
    'organization',
    sa.Column('id', sa.String()),
    sa.Column('deleted_at', sa.Integer()),
    sa.Column('is_demo', sa.Boolean())
)


def get_organization_ids(session):
    orgs_q = sa.select([
        ORGANIZATION_TABLE.c.id
    ]).where(and_(
        ORGANIZATION_TABLE.c.deleted_at == 0,
        ORGANIZATION_TABLE.c.is_demo == false(),
    ))
    return [x[0] for x in session.execute(orgs_q)]


def get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def get_checklists_collection():
    config_cl = get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.checklists


def get_pipeline(organization_id):
    return [
        {'$match': {'$and': [
            {'organization_id': organization_id},
            {'data': {'$type': "array"}}
        ]}},
        {'$unwind': "$data"},
        {'$group': {
            '_id': {
                'module': '$module',
                'cloud_account_id': '$data.cloud_account_id',
                'cloud_resource_id': '$data.cloud_resource_id',
                'user_id': '$data.user_id',
                'security_group_id': '$data.security_group_id'
            },
            'first_seen': {'$min': '$created_at'},
            'last_seen': {'$max': '$created_at'},
        }},
    ]


def collect_changes(checklists_collection, organization_id):
    pipeline = get_pipeline(organization_id)
    data = checklists_collection.aggregate(pipeline, allowDiskUse=True)

    module_last_run_map = defaultdict(int)
    module_objects_map = defaultdict(dict)
    for val in data:
        module = val['_id'].pop('module')
        if module_last_run_map[module] < val['last_seen']:
            module_objects_map[module].clear()
            module_last_run_map[module] = val['last_seen']
        elif module_last_run_map[module] > val['last_seen']:
            continue
        unique_keys = MODULE_UNIQUE_KEYS_MAP.get(module, DEFAULT_UNIQUE_KEY)
        unique_values = tuple(val['_id'][x] for x in unique_keys)
        module_objects_map[module][unique_values] = val['first_seen']

    last_run_modules_map = defaultdict(list)
    for module, last_run in module_last_run_map.items():
        last_run_modules_map[last_run].append(module)

    updates = []
    for last_run, modules in last_run_modules_map.items():
        optimizations = checklists_collection.find({'$and': [
            {'organization_id': organization_id},
            {'created_at': last_run},
            {'module': {'$in': modules}},
        ]})
        for optimization in optimizations:
            if not isinstance(optimization.get('data'), list):
                LOG.error(
                    "Unexpected optimization %s (organization_id %s, module %s) data format",
                    optimization['created_at'], optimization['organization_id'],
                    optimization['module'])
                continue

            module = optimization.get('module')
            unique_keys = MODULE_UNIQUE_KEYS_MAP.get(module, DEFAULT_UNIQUE_KEY)
            for data_obj in optimization['data']:
                search_key = tuple(data_obj.get(k) for k in unique_keys)
                search_val = module_objects_map.get(module, {}).get(search_key)
                if not search_val:
                    LOG.warning(
                        "Failed to find target value by %s in "
                        "optimization %s (organization_id %s, module %s). Using default",
                        search_val, optimization['created_at'],
                        optimization['organization_id'], optimization['module'])
                    search_val = optimization['created_at']
                data_obj['detected_at'] = search_val
            updates.append(UpdateOne(
                filter={
                    '_id': optimization['_id'],
                },
                update={'$set': {'data': optimization['data']}}
            ))
    return updates


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    checklists_collection = get_checklists_collection()
    try:
        organization_ids = get_organization_ids(session)
        for organization_id in organization_ids:
            LOG.info('Processing organization %s', organization_id)
            updates = collect_changes(checklists_collection, organization_id)
            LOG.info('Detected %s module updates for organization %s',
                     len(updates), organization_id)
            if updates:
                checklists_collection.bulk_write(updates)
    finally:
        session.close()


def downgrade():
    # migration is idempotent and there is no need to unset props
    pass
