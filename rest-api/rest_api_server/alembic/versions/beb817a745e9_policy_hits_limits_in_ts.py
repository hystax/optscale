""""policy_hits_limits_in_ts"

Revision ID: beb817a745e9
Revises: 6a227d6ad5ce
Create Date: 2021-03-25 17:40:35.993117

"""
import os
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy import select, update, and_
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from config_client.client import Client
from pymongo import MongoClient


# revision identifiers, used by Alembic.
revision = 'beb817a745e9'
down_revision = '6a227d6ad5ce'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80
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


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        now = int(datetime.utcnow().timestamp())
        resource_limit_hits_map = {}
        stmt = select([LH_TABLE]).where(and_(
            LH_TABLE.c.type == 'TTL', LH_TABLE.c.constraint_limit <= 720))
        for entry in session.execute(stmt):
            obj = resource_limit_hits_map.get(entry.resource_id)
            if not obj:
                obj = {}
            if not obj.get(entry.id):
                obj[entry.id] = {}
            obj[entry.id] = entry.constraint_limit
            resource_limit_hits_map[entry.resource_id] = obj
        res_ids = list(resource_limit_hits_map.keys())
        resource_first_seen_map = get_resource_first_seen(res_ids)

        for res_id, objs in resource_limit_hits_map.items():
            first_seen = resource_first_seen_map.get(res_id, now)
            for obj_id, constraint_limit in objs.items():
                stmt = update(LH_TABLE).values(
                    constraint_limit=first_seen + constraint_limit * 3600).where(
                    LH_TABLE.c.id == obj_id)
                print(stmt)
                session.execute(stmt)
            session.flush()
        session.commit()
    except DatabaseError:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade():
    pass
