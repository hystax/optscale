""""rename_webhook_body_fields"

Revision ID: 789c5407caad
Revises: 66ec977d8b6f
Create Date: 2021-10-26 14:14:52.718008

"""
import json
import os
from config_client.client import Client as ConfigClient
from pymongo import MongoClient, UpdateOne

# revision identifiers, used by Alembic.
revision = '789c5407caad'
down_revision = '66ec977d8b6f'
branch_labels = None
depends_on = None

DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80
CHUNK_SIZE = 1000
DESCRIPTION_VALUES = [('owner', 'booking_owner'),
                      ('booking', 'booking_details')]


def get_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = ConfigClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def get_webhook_logs_collections():
    config_cl = get_config_client()
    conn_string = "mongodb://%s:%s@%s:%s" % config_cl.mongo_params()[:-1]
    mongo_cl = MongoClient(conn_string)
    return mongo_cl.restapi.webhook_logs


def upgrade():
    # mongo changes
    webhook_logs = get_webhook_logs_collections()
    # need to get all webhooks, in all of them we have owner and booking
    # fields, also body value is a string where we have these params
    find_cond = {}
    updates = []
    for id_body_map in webhook_logs.find(find_cond, ['_id', 'body']):
        item_id, item_body = id_body_map['_id'], id_body_map['body']
        body_value = json.loads(item_body)
        description = body_value.get('description')
        if not description:
            continue
        for old, new in DESCRIPTION_VALUES:
            description[new] = description.pop(old)
        updates.append(
            UpdateOne(
                filter={
                    '_id': item_id
                },
                update={'$set': {
                    'body': json.dumps(body_value)
                }}
            )
        )
    if updates:
        for i in range(0, len(updates), CHUNK_SIZE):
            ids_chunk = updates[i:i + CHUNK_SIZE]
            webhook_logs.bulk_write(ids_chunk)


def downgrade():
    # mongo changes
    webhook_logs = get_webhook_logs_collections()
    find_cond = {}
    updates = []
    for id_body_map in webhook_logs.find(find_cond, ['_id', 'body']):
        item_id, item_body = id_body_map['_id'], id_body_map['body']
        body_value = json.loads(item_body)
        description = body_value.get('description')
        if not description:
            continue
        for old, new in DESCRIPTION_VALUES:
            description[old] = description.pop(new)
        updates.append(
            UpdateOne(
                filter={
                    '_id': item_id
                },
                update={'$set': {
                    'body': json.dumps(body_value)
                }}
            )
        )
    if updates:
        for i in range(0, len(updates), CHUNK_SIZE):
            ids_chunk = updates[i:i + CHUNK_SIZE]
            webhook_logs.bulk_write(ids_chunk)
