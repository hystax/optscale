""""ttl_constraints_and_hits_limits_in_ts"

Revision ID: 6a227d6ad5ce
Revises: 0b0598948237
Create Date: 2021-03-20 15:59:22.765903

"""
import os
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy import select, update
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from config_client.client import Client
from pymongo import MongoClient


# revision identifiers, used by Alembic.
revision = '6a227d6ad5ce'
down_revision = '0b0598948237'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80

RC_TABLE = sa.table(
    'resource_constraint',
    sa.Column('id', sa.String(36)),
    sa.Column('resource_id', sa.String(36)),
    sa.Column('limit', sa.Integer()),
    sa.Column('type', sa.String(36)))
LH_TABLE = sa.table(
    'constraint_limit_hit',
    sa.Column('id', sa.String(36)),
    sa.Column('resource_id', sa.String(36)),
    sa.Column('constraint_limit', sa.Integer()),
    sa.Column('hit_value', sa.Integer()),
    sa.Column('type', sa.String(36)))


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = Client(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_resources_collection():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.resources


def get_resource_first_seen(resource_ids):
    rss = _get_resources_collection().find(
        {'_id': {'$in': resource_ids}})
    return {r['_id']: r.get('first_seen', r.get('created_at')) for r in rss}


def process(transform_func):
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        now = int(datetime.utcnow().timestamp())
        resource_constraints_map = {}
        resource_limit_hits_map = {}
        processing_list = [(RC_TABLE, ['limit'], resource_constraints_map),
                           (LH_TABLE, ['constraint_limit', 'hit_value'],
                            resource_limit_hits_map)]

        for table, column_names, dest_dict in processing_list:
            stmt = select([table]).where(table.c.type == 'TTL')
            for entry in session.execute(stmt):
                obj = dest_dict.get(entry.resource_id)
                if not obj:
                    obj = {}
                if not obj.get(entry.id):
                    obj[entry.id] = {}
                for column_name in column_names:
                    obj[entry.id][column_name] = getattr(entry, column_name)
                dest_dict[entry.resource_id] = obj
        res_ids = list(set(
            resource_constraints_map.keys() | resource_limit_hits_map.keys()))
        resource_first_seen_map = get_resource_first_seen(res_ids)

        for table, _, src_dict in processing_list:
            for res_id, objs in src_dict.items():
                first_seen = resource_first_seen_map.get(res_id, now)
                for obj_id, obj_limits in objs.items():
                    updates = {k: transform_func(v, first_seen)
                               for k, v in obj_limits.items()}
                    stmt = update(table).values(**updates).where(
                        table.c.id == obj_id)
                    session.execute(stmt)
            session.flush()
        session.commit()
    except DatabaseError:
        session.rollback()
        raise
    finally:
        session.close()


def upgrade():
    def to_ts_limit(limit, first_seen):
        return first_seen + limit * 3600

    process(to_ts_limit)


def downgrade():
    def to_limit(ts_limit, first_seen):
        limit = (ts_limit - first_seen) // 3600
        if limit <= 0:
            limit = 1
        return limit

    process(to_limit)
