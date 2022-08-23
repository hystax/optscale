""""rename_budget_on_pool"

Revision ID: a46a37cfef14
Revises: da0145def701
Create Date: 2021-04-20 15:00:05.969698

"""
import os
import logging

import pymongo
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session
from config_client.client import Client as EtcdClient
from pymongo import MongoClient

revision = 'a46a37cfef14'
down_revision = 'b9ea270310d3'
branch_labels = None
depends_on = None
LOG = logging.getLogger(__name__)
old_budget_purposes = sa.Enum('BUDGET', 'BUSINESS_UNIT', 'TEAM', 'PROJECT', 'CICD',
                              'MLAI', 'ASSET_POOL')
temp_budget_purposes = sa.Enum('BUDGET', 'BUSINESS_UNIT', 'TEAM', 'PROJECT', 'CICD',
                               'MLAI', 'ASSET_POOL', 'POOL')
new_budget_purposes = sa.Enum('BUSINESS_UNIT', 'TEAM', 'PROJECT', 'CICD',
                              'MLAI', 'ASSET_POOL', 'POOL')
old_invite_assignment_scope_types = sa.Enum('ORGANIZATION', 'BUDGET')
temp_invite_assignment_scope_types = sa.Enum('ORGANIZATION', 'BUDGET', 'POOL')
new_invite_assignment_scope_types = sa.Enum('ORGANIZATION', 'POOL')
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
EVENT_CLASSES = [('BUDGET_DELETED', 'POOL_DELETED'), ('BUDGET_CREATED', 'POOL_CREATED'),
                 ('BUDGET_UPDATED', 'POOL_UPDATED'), ('BUDGET_POLICY_UPDATED', 'POLICY_UPDATED')]
UPDATE_CHUNK_SIZE = 50000
UPDATE_RULE_CHUNK_SIZE = 20000
REPORT_EVERY = 1000000


def _update_budget_table(session, source_purpose, target_purpose):
    budget_table = sa.table('budget',
                            sa.Column('id', sa.String(36)),
                            sa.Column('purpose', temp_budget_purposes))
    session.execute(sa.update(budget_table).values(purpose=target_purpose).where(
        budget_table.c.purpose == source_purpose))


def _update_invite_assignment_table(session, source_scope_type, target_scope_type):
    invite_assignment_table = sa.table('invite_assignment',
                                       sa.Column('id', sa.String(36)),
                                       sa.Column('scope_type', temp_invite_assignment_scope_types))
    session.execute(sa.update(invite_assignment_table).values(scope_type=target_scope_type).where(
        invite_assignment_table.c.scope_type == source_scope_type))


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_mongo_client():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    return MongoClient(mongo_conn_string)


def _update_event_field(field, old_value, new_value):
    mongo = _get_mongo_client()
    LOG.info('Event collection update started, field %s' % field)
    _update_by_many(mongo.keeper.event, UPDATE_CHUNK_SIZE,
                    {field: {'$eq': old_value}}, {'$set': {field: new_value}})


def _update_by_many(collection, chunk_size, find_cond, update_cond):
    found = collection.find(find_cond).count()
    updated = 0
    reported = REPORT_EVERY - 1
    for i in range(0, found, chunk_size):
        list_ids = [x['_id'] for x in collection.find(find_cond, ['_id']).limit(chunk_size)]
        result = collection.update_many({'_id': {'$in': list_ids}}, update_cond)
        updated += result.modified_count
        if updated > reported:
            LOG.info('Updated %s of %s' % (updated, found))
            reported += REPORT_EVERY
    if found != updated:
        LOG.warning('Something wrong: updated %s from %s', updated, found)


def _update_applied_rules(chunk_size, old_field, new_field):
    mongo = _get_mongo_client()
    collection = mongo.restapi.resources
    updated = 0
    reported = REPORT_EVERY - 1
    find_cond = {'applied_rules': {'$elemMatch': {old_field: {'$exists': True}}}}
    found = collection.find(find_cond).count()
    pipeline = [
        {
            '$addFields': {
                'applied_rules': {
                    '$map': {
                        'input': '$applied_rules',
                        'as': 'row',
                        'in': {
                            'id': '$$row.id',
                            'name': '$$row.name',
                            new_field: '$$row.' + old_field
                        }
                    }
                }
            }
        }
    ]
    for i in range(0, found, chunk_size):
        list_ids = [x['_id'] for x in collection.find(find_cond, ['_id']).limit(chunk_size)]
        count_update = len(list_ids)
        cond = {
            '$match': {
                '_id': {
                    '$in': list_ids
                }
            }
        }
        pipeline.insert(0, cond)
        resources = list(collection.aggregate(pipeline))
        pipeline.pop(0)
        collection.delete_many({'_id': {'$in': list_ids}})
        collection.insert_many(resources)
        updated += count_update
        if updated > reported:
            LOG.info('Updated %s of %s' % (updated, found))
            reported += REPORT_EVERY
    if found != updated:
        LOG.warning('Something wrong: updated %s from %s', updated, found)


def upgrade():
    # mongo changes
    mongo_restapi = _get_mongo_client().restapi
    update_expr = {
        "$rename": {
                "budget_id": "pool_id"
        }}
    mongo_collections = ['expenses', 'expenses_group_month_resource', 'resources']
    for col_name in mongo_collections:
        collection = getattr(mongo_restapi, col_name, None)
        if collection:
            LOG.info('%s collection update started' % col_name)
            _update_by_many(collection, UPDATE_CHUNK_SIZE,
                            {'budget_id': {'$exists': True}}, update_expr)
        else:
            LOG.warning('%s collection not found!' % col_name)
    _update_applied_rules(UPDATE_RULE_CHUNK_SIZE, 'budget_id', 'pool_id')
    _update_event_field('object_type', 'budget', 'pool')
    for old, new in EVENT_CLASSES:
        _update_event_field('evt_class', old, new)

    # maria changes
    # rename fields
    op.alter_column('budget', 'purpose', existing_type=old_budget_purposes,
                    type_=temp_budget_purposes, existing_nullable=False)
    op.alter_column('invite_assignment', 'scope_type', existing_type=old_invite_assignment_scope_types,
                    type_=temp_invite_assignment_scope_types, existing_nullable=False)
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        _update_budget_table(session, 'BUDGET', 'POOL')
        _update_invite_assignment_table(session, 'BUDGET', 'POOL')
        session.commit()
    finally:
        session.close()
    op.alter_column('budget', 'purpose', existing_type=temp_budget_purposes,
                    type_=new_budget_purposes, existing_nullable=False)
    op.alter_column('invite_assignment', 'scope_type', existing_type=temp_invite_assignment_scope_types,
                    type_=new_invite_assignment_scope_types, existing_nullable=False)
    # rename columns
    op.alter_column('alert_contact', 'budget_alert_id',
                    existing_type=sa.String(36), nullable=False,
                    new_column_name='pool_alert_id')
    op.alter_column('assignment_request', 'source_budget_id',
                    existing_type=sa.String(36), nullable=False,
                    new_column_name='source_pool_id')
    op.alter_column('budget', 'budget',
                    existing_type=sa.BigInteger, nullable=False,
                    new_column_name='limit')
    op.alter_column('budget_alert', 'budget_id',
                    existing_type=sa.String(36), nullable=False,
                    new_column_name='pool_id')
    op.alter_column('budget_policy', 'budget_id',
                    existing_type=sa.String(36), nullable=False,
                    new_column_name='pool_id')
    op.alter_column('constraint_limit_hit', 'budget_id',
                    existing_type=sa.String(36), nullable=True,
                    new_column_name='pool_id')
    op.alter_column('employee', 'default_budget_id',
                    existing_type=sa.String(36), nullable=True,
                    new_column_name='default_pool_id')
    op.alter_column('organization', 'budget_id',
                    existing_type=sa.String(36), nullable=True,
                    new_column_name='pool_id')
    op.alter_column('rule', 'budget_id',
                    existing_type=sa.String(36), nullable=False,
                    new_column_name='pool_id')
    # rename tables
    op.rename_table('budget', 'pool')
    op.rename_table('budget_alert', 'pool_alert')
    op.rename_table('budget_policy', 'pool_policy')


def downgrade():
    # mongo changes
    mongo_restapi = _get_mongo_client().restapi
    update_expr = {
        "$rename": {
                "pool_id": "budget_id"
        }}
    mongo_collections = ['expenses', 'expenses_group_month_resource', 'resources']
    for col_name in mongo_collections:
        collection = getattr(mongo_restapi, col_name, None)
        if collection:
            LOG.info('%s collection update started' % col_name)
            _update_by_many(collection, UPDATE_CHUNK_SIZE,
                            {'pool_id': {'$exists': True}}, update_expr)
        else:
            LOG.warning('%s collection not found!' % col_name)
    _update_event_field('object_type', 'pool', 'budget')
    _update_applied_rules(UPDATE_RULE_CHUNK_SIZE, 'pool_id', 'budget_id')
    for new, old in EVENT_CLASSES:
        _update_event_field('evt_class', old, new)

    # maria changes
    # return old table names
    op.rename_table('pool', 'budget')
    op.rename_table('pool_alert', 'budget_alert')
    op.rename_table('pool_policy', 'budget_policy')

    # return old table column names
    op.alter_column('alert_contact', 'pool_alert_id',
                    existing_type=sa.String(36), nullable=False,
                    new_column_name='budget_alert_id')
    op.alter_column('assignment_request', 'source_pool_id',
                    existing_type=sa.String(36), nullable=False,
                    new_column_name='source_budget_id')
    op.alter_column('budget', 'limit',
                    existing_type=sa.BigInteger, nullable=False,
                    new_column_name='budget')
    op.alter_column('budget_alert', 'pool_id',
                    existing_type=sa.String(36), nullable=False,
                    new_column_name='budget_id')
    op.alter_column('budget_policy', 'pool_id',
                    existing_type=sa.String(36), nullable=False,
                    new_column_name='budget_id')
    op.alter_column('constraint_limit_hit', 'pool_id',
                    existing_type=sa.String(36), nullable=True,
                    new_column_name='budget_id')
    op.alter_column('employee', 'default_pool_id',
                    existing_type=sa.String(36), nullable=True,
                    new_column_name='default_budget_id')
    op.alter_column('organization', 'pool_id',
                    existing_type=sa.String(36), nullable=True,
                    new_column_name='budget_id')
    op.alter_column('rule', 'pool_id',
                    existing_type=sa.String(36), nullable=False,
                    new_column_name='budget_id')
    # return old field values
    op.alter_column('budget', 'purpose', existing_type=new_budget_purposes,
                    type_=temp_invite_assignment_scope_types, existing_nullable=False)
    op.alter_column('invite_assignment', 'scope_type', existing_type=new_invite_assignment_scope_types,
                    type_=temp_invite_assignment_scope_types, existing_nullable=False)
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        _update_budget_table(session, 'POOL', 'BUDGET')
        _update_invite_assignment_table(session, 'POOL', 'BUDGET')
        session.commit()
    finally:
        session.close()
    op.alter_column('budget', 'purpose', existing_type=temp_budget_purposes,
                    type_=old_budget_purposes, existing_nullable=False)
    op.alter_column('invite_assignment', 'scope_type', existing_type=temp_invite_assignment_scope_types,
                    type_=old_invite_assignment_scope_types, existing_nullable=False)
