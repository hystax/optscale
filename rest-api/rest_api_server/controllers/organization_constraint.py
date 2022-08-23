import json
import logging
from collections import defaultdict
from datetime import datetime, time, timedelta

from rest_api_server.controllers.available_filters import (
    AvailableFiltersController)
from rest_api_server.controllers.base import FilterValidationMixin
from rest_api_server.exceptions import Err
from optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException)
from sqlalchemy import Enum, and_
from rest_api_server.models.enums import OrganizationConstraintTypes as OrgCTypes
from rest_api_server.models.models import (CloudAccount, Pool, Employee,
                                           Organization, OrganizationConstraint,
                                           OrganizationLimitHit)
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.constraint_base import ConstraintBaseController
from rest_api_server.utils import (check_int_attribute, get_nil_uuid,
                                   check_dict_attribute, check_string_attribute,
                                   check_float_attribute)

JOINED_ENTITY_MAP = {
    'cloud_account': ('cloud_account_id', ['id', 'name', 'type']),
    'owner': ('owner_id', ['id', 'name']),
    'pool': ('pool_id', ['id', 'name', 'purpose'])
}
LOG = logging.getLogger(__name__)
WITH_SUBPOOLS_SIGN = '+'
MONTH_IN_SECONDS = 60 * 60 * 24 * 30
MIN_THRESHOLD_DAYS = 1
MAX_THRESHOLD_DAYS = 180
DAY_IN_SECONDS = 86400


class FilterDetailsController(AvailableFiltersController):
    @staticmethod
    def _get_base_result(filter_values):
        return filter_values

    def _aggregate_resource_data(self, match_query, **kwargs):
        last_recommend_run = kwargs['last_recommend_run']
        collected_filters = [
            'service_name', 'pool_id', 'employee_id', 'k8s_node', 'region',
            'resource_type', 'k8s_namespace', 'k8s_service', 'cloud_account_id'
        ]
        group_stage = {
            f: {'$addToSet': {'$ifNull': ['$%s' % f, None]}}
            for f in collected_filters if f in kwargs or f == 'resource_type'
        }
        for bool_field in ['active', 'constraint_violated']:
            if bool_field in kwargs:
                group_stage.update({
                    bool_field: {'$addToSet': {'$cond': {
                        'if': {'$eq': ['$%s' % bool_field, True]},
                        'then': True,
                        'else': False
                    }}},
                })
        if 'recommendations' in kwargs:
            group_stage.update({
                'recommendations': {'$addToSet': {'$cond': {
                    'if': {'$and': [
                        {'$ne': ['$recommendations', None]},
                        {'$gte': [
                            '$recommendations.run_timestamp', last_recommend_run
                        ]}
                    ]},
                    'then': True,
                    'else': False
                }}}
            })
        group_stage.update({
            '_id': {
                'cloud_account_id': '$cloud_account_id',
                'cluster_type_id': '$cluster_type_id',
                'is_environment': '$is_environment',
                'day': {'$trunc': {
                    '$divide': ['$first_seen', DAY_IN_SECONDS]}},
            },
            'cloud_resource_ids': {'$addToSet': '$cloud_resource_id'},
        })
        pipeline = [{'$match': match_query}]
        if 'tag' in kwargs or 'without_tag' in kwargs:
            group_stage.update({'tags': {'$addToSet': '$tags.k'}})
            pipeline.extend([
                {'$addFields': {'tags': {'$objectToArray': "$tags"}}},
                {'$unwind': {
                    'path': "$tags",
                    'preserveNullAndEmptyArrays': True
                }},
            ])
        pipeline.append({'$group': group_stage})
        return self.resources_collection.aggregate(pipeline, allowDiskUse=True)

    def _get_filter_values(self, uniq_values_map, filters):
        filter_values = defaultdict(list)
        if not uniq_values_map:
            for filter_key, filter_value in filters.items():
                if filter_value and isinstance(filter_value, list):
                    raise WrongArgumentsException(
                        Err.OE0504, [filter_key, filter_value])
        # check that all filters exists in unique_values_map
        for field, values in filters.items():
            if field in ['start_date', 'end_date']:
                continue
            uniq_values = uniq_values_map.get(field, {})
            if field == 'resource_type':
                result_u_values = {'{0}:{1}'.format(k[0], k[1]): v
                                   for k, v in uniq_values.items()}
            elif field == 'cloud_account':
                result_u_values = uniq_values
                # for cluster data source, also update cloud result map
                result_u_values.update({None: {'id': get_nil_uuid(),
                                               'name': None, 'type': None}})
            elif field in ['traffic_from', 'traffic_to']:
                result_u_values = {}
                for v in uniq_values:
                    key = f"{v['name']}:{v['cloud_type']}" if isinstance(
                        v, dict) else v
                    result_u_values[key] = v
            elif not isinstance(uniq_values, dict):
                result_u_values = {x: x for x in uniq_values}
            else:
                result_u_values = uniq_values
            for filter_value in values:
                if filter_value not in result_u_values.keys():
                    raise WrongArgumentsException(Err.OE0504,
                                                  [field, filter_value])
                filter_values[field].append(result_u_values[filter_value])
        return filter_values

    def _generate_base_filter(self, organization_id, start_date, end_date):
        _, cloud_accs = self.get_organization_and_cloud_accs(organization_id)
        cloud_account_ids = [c.id for c in cloud_accs]
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
                {'deleted_at': 0}
            ]
        }
        return query

    def generate_filters_pipeline(self, organization_id, start_date, end_date,
                                  params, data_filters):
        params.pop('cloud_account_id', None)
        query = self._generate_base_filter(
            organization_id, start_date, end_date)
        query['$and'].append({'cluster_id': None})

        subquery = []
        resource_type_condition = self.get_resource_type_condition(
            params.pop('resource_type', []))
        if resource_type_condition:
            subquery.append({'$or': resource_type_condition})

        nil_uuid = get_nil_uuid()
        for filter_name in ['tag', 'without_tag']:
            tag_params = params.pop(filter_name, None)
            if tag_params:
                tag_filter = []
                for v in tag_params:
                    if v == nil_uuid:
                        tag_filter.append({'tags': {}})
                    else:
                        tag_filter.append(
                            {'tags.%s' % v: {'$exists': True}})
                subquery.append({'$or': tag_filter})

        for filter_key, filter_values in params.items():
            for n, filter_value in enumerate(filter_values):
                if filter_value == nil_uuid:
                    filter_values[n] = None
            subquery.append({filter_key: {'$in': filter_values}})

        for string_field in [
            'service_name', 'created_by_kind', 'created_by_name',
            'k8s_namespace', 'k8s_node', 'k8s_service'
        ]:
            name_set = data_filters.get(string_field)
            if name_set is not None:
                subquery.append(
                    {string_field: {'$in': list(set(name_set))}})

        for bool_field in ['active', 'constraint_violated']:
            bool_value = data_filters.get(bool_field)
            if bool_value is not None:
                value = True if bool_value else {'$ne': True}
                subquery.append({bool_field: value})

        recommend_filter = data_filters.get('recommendations')
        if recommend_filter is not None:
            last_run = self.get_last_run_ts_by_org_id(organization_id)
            if recommend_filter:
                subquery.append({
                    'recommendations.run_timestamp': {'$gte': last_run}
                })
            else:
                subquery.append({'$or': [
                    {'recommendations': None},
                    {'recommendations.run_timestamp': {'$lt': last_run}}
                ]})

        if subquery:
            query['$and'].append({'$or': subquery})
        return query

    def get_resources_data(self, organization_id, query_filters,
                           data_filters, extra_params):
        query = self.generate_filters_pipeline(
            organization_id, self.start_date, self.end_date, query_filters.copy(),
            data_filters.copy())
        return self._aggregate_resource_data(
            query, **query_filters, **data_filters, **extra_params)


class ConstraintRunValidationMixin:
    @staticmethod
    def _check_run_result(key_name, constraint_type, last_run_result):
        if not isinstance(last_run_result, dict):
            raise WrongArgumentsException(Err.OE0344, [key_name])

        last_run_result_ = last_run_result.copy()
        check_dict_attribute(key_name, last_run_result_)
        if constraint_type in [OrgCTypes.EXPENSE_ANOMALY,
                               OrgCTypes.RESOURCE_COUNT_ANOMALY]:
            today = last_run_result_.pop('today', None)
            if constraint_type == OrgCTypes.RESOURCE_COUNT_ANOMALY:
                check_int_attribute('today', today)
            else:
                check_float_attribute('today', today)

            average = last_run_result_.pop('average', None)
            check_float_attribute('average', average)

            breakdown = last_run_result_.pop('breakdown', None)
            # average is always based on breakdown
            if average <= 0 and breakdown:
                raise WrongArgumentsException(Err.OE0522, ['breakdown'])
            elif average > 0:
                if not breakdown:
                    raise WrongArgumentsException(Err.OE0216, ['breakdown'])
                check_dict_attribute('breakdown', breakdown)
        elif constraint_type == OrgCTypes.RESOURCE_QUOTA:
            check_int_attribute('limit', last_run_result_.pop('limit', None))
            check_int_attribute('current', last_run_result_.pop('current', None))
        elif constraint_type in [OrgCTypes.EXPIRING_BUDGET,
                                 OrgCTypes.RECURRING_BUDGET]:
            check_float_attribute('limit', last_run_result_.pop('limit', None))
            check_float_attribute('current', last_run_result_.pop('current', None))
        elif constraint_type == OrgCTypes.TAGGING_POLICY:
            check_int_attribute('value', last_run_result_.pop('value', None))

        unexpected_params = [p for p in last_run_result_.keys()]
        if unexpected_params:
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])


class OrganizationConstraintController(ConstraintBaseController,
                                       FilterValidationMixin,
                                       ConstraintRunValidationMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.str_filters.clear()

    def _get_model_type(self):
        return OrganizationConstraint

    def get_relation_field(self):
        return 'organization_id'

    def get_model_name(self):
        return OrganizationConstraint.__name__

    def get_entity(self, item_id):
        organization = self.session.query(Organization).filter(
            Organization.id == item_id,
            Organization.deleted.is_(False)
        ).one_or_none()
        return organization

    def get_organization_id_from_entity(self, entity):
        return entity.id

    @staticmethod
    def _remove_subpool_sign(pool_ids):
        return [x.removesuffix(WITH_SUBPOOLS_SIGN) for x in pool_ids]

    def _get_object_entities(self, organization_id, model, entity_ids):
        nil_uuid = get_nil_uuid()
        entity_ids = list(filter(
            lambda x: x is not None and x != nil_uuid, entity_ids))
        if model == Pool:
            entity_ids = self._remove_subpool_sign(entity_ids)
        if not entity_ids:
            return {}
        objects = self.session.query(model).filter(
            model.id.in_(list(entity_ids)),
            model.organization_id == organization_id,
            model.deleted.is_(False)
        ).all()
        result = {x.id: x.to_dict() for x in objects}
        not_found = [x for x in entity_ids if x not in result.keys()]
        if not_found:
            raise WrongArgumentsException(Err.OE0002, [
                model.__name__, not_found[0]])
        return result

    def get_filters_entities(self, organization_id, filters):
        entities_map = {'pool_id': Pool,
                        'owner_id': Employee,
                        'cloud_account_id': CloudAccount}
        entities = {}
        for entity, model in entities_map.items():
            if filters.get(entity):
                entity_ids = set(filters[entity])
                entities.update(self._get_object_entities(
                    organization_id, model, entity_ids))
        return entities

    @staticmethod
    def _check_definition(definition, constraint_type):
        if constraint_type in [
          OrgCTypes.EXPENSE_ANOMALY.value,
          OrgCTypes.RESOURCE_COUNT_ANOMALY.value]:
            threshold = definition.get('threshold')
            threshold_days = definition.get('threshold_days')
            # anomalies with negative threshold are not expected
            check_int_attribute('threshold', threshold)
            check_int_attribute('threshold_days', threshold_days,
                                min_length=MIN_THRESHOLD_DAYS, max_length=MAX_THRESHOLD_DAYS)
        elif constraint_type == OrgCTypes.RESOURCE_QUOTA.value:
            check_int_attribute('max_value', definition.get('max_value'))
        elif constraint_type == OrgCTypes.EXPIRING_BUDGET.value:
            check_int_attribute('total_budget', definition.get('total_budget'))
            check_int_attribute('start_date', definition.get('start_date'))
        elif constraint_type == OrgCTypes.RECURRING_BUDGET.value:
            check_int_attribute('monthly_budget',
                                definition.get('monthly_budget'))
        elif constraint_type == OrgCTypes.TAGGING_POLICY.value:
            check_int_attribute('start_date', definition.get('start_date'))
            conditions = definition.get('conditions')
            check_dict_attribute('conditions', conditions)
            tag = conditions.get('tag')
            without_tag = conditions.get('without_tag')
            if tag:
                check_string_attribute('tag', tag)
            if without_tag:
                check_string_attribute('without_tag', without_tag)
            if not tag and not without_tag:
                raise WrongArgumentsException(Err.OE0517, ['tag', 'without_tag'])

    def _check_input(self, entity_id, entity, **kwargs):
        if not entity:
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, entity_id])
        definition = kwargs.get('definition', {})
        type_param = kwargs.get('type')
        check_dict_attribute('definition', definition)
        self._check_definition(definition, type_param)
        if not type_param:
            raise WrongArgumentsException(Err.OE0216, ['type'])
        try:
            Enum(OrgCTypes).enum_class(type_param)
        except ValueError as ex:
            raise WrongArgumentsException(Err.OE0004, [str(ex)])

        filters = kwargs.get('filters', {})
        if filters != {}:
            check_dict_attribute('filters', filters)
        self.check_filters(filters)
        self.get_filters_entities(entity_id, filters)

    def _fill_filters(self, organization_id, created_at, filters):
        filter_details = defaultdict(list)
        if filters:
            fdc = FilterDetailsController(self.session, self._config)
            filter_details = fdc.get(organization_id, **{
                'start_date': created_at - MONTH_IN_SECONDS,
                'end_date': created_at,
                **filters
            })
            nil_value = get_nil_uuid()
            for k, v in JOINED_ENTITY_MAP.items():
                if filter_details.pop(k, None):
                    filter_key = v[0]
                    for v in filters.get(filter_key):
                        filter_details[filter_key].append(
                            None if v == nil_value else v)
        return filter_details

    def _extend_filters(self, organization_id, filters):
        extended_filters = {}
        if filters:
            optscale_filters = [x[0] for x in JOINED_ENTITY_MAP.values()]
            for filter_name, value in filters.items():
                if filter_name not in optscale_filters:
                    extended_filters[filter_name] = value
            entities = self.get_filters_entities(organization_id, filters)
            for entity_name, v in JOINED_ENTITY_MAP.items():
                entity_key, fields = v
                entity_ids = filters.pop(entity_key, [])
                for entity_id in entity_ids:
                    with_subpools = False
                    if (entity_name == 'pool' and entity_id and
                            entity_id.endswith(WITH_SUBPOOLS_SIGN)):
                        with_subpools = True
                        entity_id = entity_id.removesuffix(WITH_SUBPOOLS_SIGN)
                    entity = entities.get(entity_id)
                    if not extended_filters.get(entity_name):
                        extended_filters[entity_name] = []
                    extended_filters[entity_name].append(
                        {key_name: entity[key_name] for key_name in fields}
                        if entity else entity_id)
                    if with_subpools:
                        extended_filters[entity_name][-1]['id'] += WITH_SUBPOOLS_SIGN
        pools = extended_filters.get('pool', [])
        for pool in pools:
            if isinstance(pool, dict) and not isinstance(pool['purpose'], str):
                pool['purpose'] = pool['purpose'].value
        return extended_filters

    def create(self, **kwargs):
        organization_id = kwargs.get(self.get_relation_field())
        organization = self.get_entity(organization_id)
        self._check_input(organization_id, organization, **kwargs)

        now = int(datetime.utcnow().timestamp())
        filled_filters = self._fill_filters(
            organization_id, now, kwargs.get('filters', {}))
        kwargs['filters'] = filled_filters

        result = super(ConstraintBaseController, self).create(**kwargs)
        extended_filters = self._extend_filters(
            organization_id, filled_filters)
        result.filters = json.dumps(extended_filters)
        return result

    def _validate(self, item, is_new=True, **kwargs):
        if not is_new and 'last_run_result' in kwargs:
            self._check_run_result(
                'last_run_result', item.type, kwargs.get('last_run_result'))

    def edit(self, item_id, **kwargs):
        result = super().edit(item_id, **kwargs)
        organization_id = result.organization_id
        extended_filters = self._extend_filters(
            organization_id, result.loaded_filters)
        result.filters = json.dumps(extended_filters)
        return result

    def get_constraint(self, item_id):
        result = super().get(item_id)
        if result:
            organization_id = result.organization_id
            extended_filters = self._extend_filters(
                organization_id, result.to_dict().get('filters', {}))
            result.filters = json.dumps(extended_filters)
        else:
            raise NotFoundException(
                Err.OE0002, [self.get_model_name(), item_id])
        return result

    def get_constraint_limit_hits(self, constraint_ids,
                                  period_start_ts=None):
        query = self.session.query(OrganizationLimitHit).filter(and_(
            OrganizationLimitHit.constraint_id.in_(constraint_ids),
            OrganizationLimitHit.deleted.is_(False)))
        if period_start_ts is not None:
            query = query.filter(
                OrganizationLimitHit.created_at > period_start_ts)
        return query.all()

    def list(self, **kwargs):
        hit_days = kwargs.pop('hit_days', None)
        types = kwargs.pop('type', None)
        organization_id = kwargs['organization_id']
        if self.get_entity(organization_id) is None:
            raise NotFoundException(Err.OE0002, [
                Organization.__name__, organization_id])
        db_types = []
        if types:
            for t in types:
                try:
                    db_types.append(Enum(OrgCTypes).enum_class(t))
                except ValueError:
                    continue
        query = self.session.query(OrganizationConstraint).filter(
            OrganizationConstraint.deleted_at.is_(False)).filter_by(**kwargs)
        if types:
            query = query.filter(OrganizationConstraint.type.in_(db_types))
        result = query.all()
        constraint_ids = [x.id for x in result]
        constraint_hits_map = defaultdict(list)
        if hit_days:
            check_int_attribute('hit_days', hit_days)
            period_start_ts = int(
                (datetime.combine(datetime.today(), time.max) - timedelta(
                    days=hit_days)).timestamp())
            hits = self.get_constraint_limit_hits(constraint_ids,
                                                  period_start_ts)
            for hit in hits:
                constraint_hits_map[hit.constraint_id].append(hit)
        for c in result:
            extended_filters = self._extend_filters(
                organization_id, c.loaded_filters)
            c.filters = json.dumps(extended_filters)
            if hit_days:
                c.limit_hits = constraint_hits_map.get(c.id, [])
        return result

    def delete_constraint_by_id(self, constraint_id):
        now = int(datetime.utcnow().timestamp())
        LOG.info("Deleting %s with id %s", self.get_model_name(),
                 constraint_id)
        self.session.query(OrganizationLimitHit).filter(
            OrganizationLimitHit.constraint_id == constraint_id,
            OrganizationLimitHit.deleted.is_(False)
        ).update({OrganizationLimitHit.deleted_at: now},
                 synchronize_session=False)
        self.session.query(OrganizationConstraint).filter(
            OrganizationConstraint.id == constraint_id,
            OrganizationConstraint.deleted.is_(False)
        ).update({OrganizationConstraint.deleted_at: now},
                 synchronize_session=False)
        self.session.commit()

    def delete_constraints_with_hits(self, organization_id, filters=None):
        now = int(datetime.utcnow().timestamp())
        constraints_to_delete = []
        all_constraints = self.session.query(OrganizationConstraint).filter(
            OrganizationConstraint.organization_id == organization_id,
            OrganizationConstraint.deleted.is_(False)
        ).all()
        for c in all_constraints:
            if filters:
                c_filters = c.loaded_filters
                for k, v in filters.items():
                    values = c_filters.get(k, [])
                    if k == 'pool_id':
                        values = [x.removesuffix(WITH_SUBPOOLS_SIGN)
                                  if x is not None else x
                                  for x in values]
                    if v not in values:
                        continue
                    constraints_to_delete.append(c.id)
            else:
                constraints_to_delete.append(c.id)
        self.session.query(OrganizationLimitHit).filter(
            OrganizationLimitHit.constraint_id.in_(constraints_to_delete),
            OrganizationLimitHit.deleted.is_(False)
        ).update({OrganizationLimitHit.deleted_at: now},
                 synchronize_session=False)
        self.session.query(OrganizationConstraint).filter(
            OrganizationConstraint.id.in_(constraints_to_delete),
            OrganizationConstraint.deleted.is_(False)
        ).update({OrganizationConstraint.deleted_at: now},
                 synchronize_session=False)
        self.session.commit()


class OrganizationConstraintAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return OrganizationConstraintController
