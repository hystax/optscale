""""changed_org_constraints_filter_structure"

Revision ID: 23f9b12582bd
Revises: 32b0d57b4bda
Create Date: 2022-03-28 16:07:05.431745

"""
import json
import os
from datetime import datetime

import sqlalchemy as sa
import uuid

from alembic import op
from collections import defaultdict
from sqlalchemy.orm import Session

from config_client.client import Client as EtcdClient
from pymongo import MongoClient


# revision identifiers, used by Alembic.
revision = '23f9b12582bd'
down_revision = '32b0d57b4bda'
branch_labels = None
depends_on = None

ORGANIZATION_TABLE = sa.table(
    'organization',
    sa.Column('id', sa.String()),
    sa.Column('deleted_at', sa.Integer()),
)

CLOUD_ACCOUNT_TABLE = sa.table(
    'cloudaccount',
    sa.Column('id', sa.String()),
    sa.Column('organization_id', sa.String()),
    sa.Column('type', sa.String()),
    sa.Column('deleted_at', sa.Integer()),
)

ORGANIZATION_CONSTRAINT_TABLE = sa.table(
    'organization_constraint',
    sa.Column('id', sa.String()),
    sa.Column('organization_id', sa.String()),
    sa.Column('created_at', sa.Integer()),
    sa.Column('deleted_at', sa.Integer()),
    sa.Column('filters', sa.String()),
)

FILTERS_TO_MODIFY = (
    'k8s_namespace', 'k8s_node', 'k8s_service', 'region', 'service_name',
    'created_by_kind', 'created_by_name', 'resource_type'
)
SUPPORTED_FILTERS = (
    'owner_id', 'pool_id', 'cloud_account_id', 'service_name',
    'region', 'resource_type', 'created_by_kind',
    'created_by_name', 'k8s_namespace', 'k8s_node',
    'k8s_service', 'tag', 'without_tag',
    'active', 'recommendations', 'constraint_violated',
    'name_like', 'cloud_resource_id_like'
)

NULL_TYPE_RESOURCE_TYPE = 'null'

CLUSTER_IDENTITY = 'cluster'
ENVIRONMENT_IDENTITY = 'environment'

DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80
MONTH_IN_SECONDS = 30 * 24 * 60 * 60


def get_nil_uuid():
    return str(uuid.UUID(int=0))


def get_cloud_accounts(session, organization_ids):
    res = defaultdict(list)
    cloud_accs_q = sa.select([
        CLOUD_ACCOUNT_TABLE.c.id,
        CLOUD_ACCOUNT_TABLE.c.organization_id,
        CLOUD_ACCOUNT_TABLE.c.type
    ]).where(sa.and_(
        CLOUD_ACCOUNT_TABLE.c.organization_id.in_(organization_ids),
        CLOUD_ACCOUNT_TABLE.c.deleted_at == 0
    ))
    for cloud_acc in session.execute(cloud_accs_q):
        res[cloud_acc['organization_id']].append({
            'id': cloud_acc['id'],
            'type': cloud_acc['type'].lower()
        })
    return res


def get_organization_ids(session):
    orgs_q = sa.select([
        ORGANIZATION_TABLE.c.id
    ]).where(ORGANIZATION_TABLE.c.deleted_at == 0)
    return [x[0] for x in session.execute(orgs_q)]


def get_constraints(session, organization_ids):
    filtered_constraints_q = sa.select([
        ORGANIZATION_CONSTRAINT_TABLE.c.id,
        ORGANIZATION_CONSTRAINT_TABLE.c.organization_id,
        ORGANIZATION_CONSTRAINT_TABLE.c.created_at,
        ORGANIZATION_CONSTRAINT_TABLE.c.filters
    ]).where(sa.and_(
        ORGANIZATION_CONSTRAINT_TABLE.c.organization_id.in_(organization_ids),
        ORGANIZATION_CONSTRAINT_TABLE.c.deleted_at == 0,
        ORGANIZATION_CONSTRAINT_TABLE.c.filters != '{}'
    ))
    return session.execute(filtered_constraints_q)


def get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def get_resources_collection():
    config_cl = get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.resources


def get_resource_type_condition(resource_types, identity=None):
    if not resource_types:
        return {}

    resource_type_cond = {
        'cluster_type_id': {'$exists': False},
        'cluster_id': {'$exists': False},
        'is_environment': {'$ne': True},
        'resource_type': {'$in': resource_types}
    }
    if identity == CLUSTER_IDENTITY:
        resource_type_cond.pop('cluster_type_id')
        resource_type_cond.pop('cluster_id')
        resource_type_cond['$or'] = [
            {'cluster_type_id': {'$exists': True}},
            {'cluster_id': {'$exists': True}}
        ]
    elif identity == ENVIRONMENT_IDENTITY:
        resource_type_cond['is_environment'] = True
    return resource_type_cond


def generate_filters_pipeline(organization_id, cloud_account_ids,
                              start_date, end_date, filters):
    query = {
        '$and': [
            {'$or': [
                {'$and': [
                    {'organization_id': organization_id},
                    {'cloud_account_id': None}
                ]},
                {'cloud_account_id': {'$in': cloud_account_ids}}
            ]},
            {'first_seen': {'$lte': end_date}},
            {'last_seen': {'$gte': start_date}},
            {'deleted_at': 0},
            {'cluster_id': None}
        ]
    }

    subquery = []
    identity = filters.pop('type_resource_type', None)
    resource_type_condition = get_resource_type_condition(
         filters.pop('resource_type', []), identity)
    if resource_type_condition:
        subquery.append(
            {'$and': [{k: v} for k, v in resource_type_condition.items()]})

    for filter_key, filter_values in filters.items():
        subquery.append({filter_key: {'$in': list(set(filter_values))}})

    if subquery:
        query['$and'].append({'$or': subquery})
    return query


def aggregate_resource_data(match_query, filters):
    group_stage = {
        f: {'$addToSet': {'$ifNull': ['$%s' % f, None]}}
        for f in FILTERS_TO_MODIFY if f in filters
    }
    group_stage.update({
        '_id': {
            'cloud_account_id': '$cloud_account_id',
            'cluster_type_id': '$cluster_type_id',
            'is_environment': '$is_environment',
        },
    })
    pipeline = [
        {'$match': match_query},
        {'$group': group_stage}
    ]

    return get_resources_collection().aggregate(pipeline, allowDiskUse=True)


def identify_resource(e):
    if e.get('cluster_type_id'):
        return CLUSTER_IDENTITY
    elif e.get('is_environment'):
        return ENVIRONMENT_IDENTITY


def collect_unique_values(resource_data, cloud_accounts_map):
    result = defaultdict(dict)
    for r in resource_data:
        _id = r.pop('_id')
        cloud_account_id = _id.get('cloud_account_id')
        cloud_account = cloud_accounts_map.get(cloud_account_id)

        resource_types = r.pop('resource_type', {})
        rt_identifier = identify_resource(_id)
        for resource_type in resource_types:
            rt_key = resource_type, rt_identifier
            if rt_key not in result['resource_type']:
                result['resource_type'][rt_key] = {
                    'name': rt_key[0], 'type': rt_key[1]
                } if rt_key else rt_key

        for field in FILTERS_TO_MODIFY:
            r_keys = r.pop(field, {})
            for r_key in r_keys:
                if r_key not in result[field]:
                    result[field][r_key] = {
                        'name': r_key,
                        'cloud_type': cloud_account.get('type')
                    } if r_key else r_key
    return result


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        orgs = get_organization_ids(session)

        constraint_filters_map = {}
        org_constraints_map = defaultdict(dict)
        for constraint in get_constraints(session, orgs):
            loaded_filters = json.loads(constraint['filters'])

            type_resource_type = loaded_filters.pop(
                'type_resource_type', [NULL_TYPE_RESOURCE_TYPE])

            # track records that requires unsupported cleanup
            if list(filter(lambda k: k not in SUPPORTED_FILTERS, loaded_filters.keys())):
                org_constraints_map[constraint['organization_id']].update({
                    constraint['id']: loaded_filters
                })

            # leave only target filters
            update_candidates = {k: v for k, v in loaded_filters.items()
                                 if k in FILTERS_TO_MODIFY}
            # clean None values and exclude from processing if empty
            for k, v in update_candidates.copy().items():
                filter_val = [x for x in v if x is not None]
                if not filter_val:
                    update_candidates.pop(k)
                else:
                    update_candidates[k] = filter_val
            if not update_candidates:
                continue

            handled_constraint = {
                'created_at': constraint['created_at'],
                'filters': update_candidates
            }
            # track type_resource_type if it's not common
            if type_resource_type != [NULL_TYPE_RESOURCE_TYPE]:
                handled_constraint['filters']['type_resource_type'] = type_resource_type[0]
            constraint_filters_map[constraint['id']] = handled_constraint

            org_constraints_map[constraint['organization_id']].update({
                constraint['id']: loaded_filters
            })

        # get accs of orgs where changes are required
        org_accounts_map = get_cloud_accounts(
            session, list(org_constraints_map.keys()))

        changes_map = {}
        for org_id, orig_constraints in org_constraints_map.items():
            cloud_accounts_map = {x['id']: x for x in org_accounts_map.get(org_id, [])}
            cloud_account_ids = list(cloud_accounts_map.keys())
            for constraint_id, orig_filters in orig_constraints.items():
                # empty org can't have constraint with filters
                if not cloud_account_ids:
                    changes_map[constraint_id] = {
                        'deleted_at': int(datetime.utcnow().timestamp())}
                    continue

                # preliminary remove unsupported filters
                for k in orig_filters.copy().keys():
                    if k not in SUPPORTED_FILTERS:
                        orig_filters.pop(k)

                search_filters = constraint_filters_map.get(constraint_id)
                # constraint includes only unsupported filters
                # save the changes or remove constraint as empty
                if not search_filters:
                    if orig_filters:
                        changes = {'filters': json.dumps(orig_filters)}
                    else:
                        changes = {'deleted_at': int(datetime.utcnow().timestamp())}
                    changes_map[constraint_id] = changes
                    continue

                # collect details in 1 month interval
                end_date = search_filters.pop('created_at')
                start_date = end_date - MONTH_IN_SECONDS

                # get filters to expand
                search_filters = search_filters.pop('filters')

                # get filter details
                match_query = generate_filters_pipeline(
                    org_id, cloud_account_ids, start_date,
                    end_date, search_filters.copy())
                type_resource_type = search_filters.pop(
                    'type_resource_type', None)
                resource_data = aggregate_resource_data(
                    match_query, search_filters)
                unique_values = collect_unique_values(
                    resource_data, cloud_accounts_map)

                for filter_key, filter_values in orig_filters.copy().items():
                    # skip non-target filters
                    if filter_key not in FILTERS_TO_MODIFY:
                        continue
                    extended_data = unique_values.get(filter_key, {})
                    # clear key if is unable to get details
                    if not extended_data:
                        orig_filters.pop(filter_key)
                        continue

                    new_filter_values = []
                    # apply detailed info 1 by 1 where possible
                    for i, filter_value in enumerate(filter_values):
                        if filter_key == 'resource_type':
                            filter_value = (filter_value, type_resource_type)
                        extended_value = extended_data.get(filter_value)
                        if filter_value and not extended_value:
                            continue
                        new_filter_values.append(extended_value)
                    if not new_filter_values:
                        # clear key if is unable to apply details
                        orig_filters.pop(filter_key)
                    else:
                        orig_filters[filter_key] = new_filter_values
                if orig_filters:
                    # filters are extended where possible. Will save changes
                    changes_map[constraint_id] = {
                        'filters': json.dumps(orig_filters)}
                else:
                    # were unable to extend filters. Will delete constraint as is
                    changes_map[constraint_id] = {
                        'deleted_at': int(datetime.utcnow().timestamp())}
        for constraint_id, payload in changes_map.items():
            session.execute(sa.update(ORGANIZATION_CONSTRAINT_TABLE).values(
                **payload).where(ORGANIZATION_CONSTRAINT_TABLE.c.id == constraint_id))
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        orgs = get_organization_ids(session)

        constraints_to_delete = []
        for constraint in get_constraints(session, orgs):
            loaded_filters = json.loads(constraint['filters'])
            type_resource_types = set()
            # cut extra data from detailed filters and leave only keys
            for filter_key, filter_values in loaded_filters.copy().items():
                if filter_key in FILTERS_TO_MODIFY:
                    for i, filter_value in enumerate(filter_values):
                        if filter_value is None:
                            continue
                        filter_values[i] = filter_value['name']
                        if filter_key == 'resource_type':
                            type_resource_types.add(
                                filter_value['type'] or NULL_TYPE_RESOURCE_TYPE)

            if type_resource_types:
                # type_resource_type based scheme is unable to handle > 1 value
                if len(type_resource_types) > 1:
                    constraints_to_delete.append(constraint['id'])
                    continue
                else:
                    loaded_filters['type_resource_type'] = [type_resource_types.pop()]

            session.execute(sa.update(ORGANIZATION_CONSTRAINT_TABLE).values(
                filters=json.dumps(loaded_filters)).where(
                ORGANIZATION_CONSTRAINT_TABLE.c.id == constraint['id']))
        if constraints_to_delete:
            now = int(datetime.utcnow().timestamp())
            session.execute(sa.update(ORGANIZATION_CONSTRAINT_TABLE).values(
                deleted_at=now).where(
                ORGANIZATION_CONSTRAINT_TABLE.c.id.in_(constraints_to_delete)))
        session.commit()
    finally:
        session.close()
